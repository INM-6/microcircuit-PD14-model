# -*- coding: utf-8 -*-
#
# model.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""PyNEST implementation of microcircuit-PD14-model
-------------------------------------------------------

Main file of the microcircuit defining the ``Model`` class with functions to build and simulate the network.
"""

import os
import warnings

import nest
import numpy as np

from microcircuit import helpers


class Model:
    """
    Model class for the microcircuit.

    Model instances are equipped with model parameters given by an instance of the `Parameters` class
    (see: `parameter_definitions.py`), as well as with functions to create and connect the network, to simulate the model,
    and to evaluate the resulting spike data.

    Instantiating a Model object initializes the NEST kernel;
    all derived parameters are available as computed fields on `params`.

    Parameters
    ----------
    params: Parameters
        Object containing all model parameters.
    """

    def __init__(self, params):

        self.params = params

        self._create_data_directory()

        # initialize the NEST kernel
        self._setup_nest()

    def create_nodes(self):
        """Creates all network nodes.

        Neuronal populations and recording and stimulation devices are created.
        """

        self._create_neuronal_populations()
        if len(self.params.rec_dev) > 0:
            self._create_recording_devices()
        if self.params.CC_type == "poisson":
            self._create_poisson_bg_input()
        if self.params.dc_transient:
            self._create_dc_stim_input()
        if self.params.thalamic_input:
            self._create_thalamic_stim_input()

    def connect(self):
        """Connects the network.

        Recurrent connections among neurons of the neuronal populations are established,
        and recording and stimulation devices are connected.
        This also triggers the construction of the presynaptic connection infrastructure.
        """

        self._connect_neuronal_populations()

        if len(self.params.rec_dev) > 0:
            self._connect_recording_devices()
        if self.params.CC_type == "poisson":
            self._connect_poisson_bg_input()
        if self.params.dc_transient:
            self._connect_dc_stim_input()
        if self.params.thalamic_input:
            self._connect_thalamic_stim_input()

        # trigger construction of the presynaptic connection infrastructure here,
        # so that it counts as part of connecting rather than of the first nest.Simulate() call
        nest.Prepare()
        nest.Cleanup()

    def store_metadata(self):
        """Stores parameters, node ids and package versions in the data directory."""

        if not self.params.store_metadata or nest.Rank() != 0:
            return

        print()
        print("####################################################################")
        print()
        print(f"Storing simulation metadata to {self.params.data_path}")
        print()
        print("####################################################################")
        print()

        # parameters (primary + derived, in one snapshot)
        helpers.dict2json(self.params.model_dump(), self.params.data_path / "params.json")

        # nodes (populations, readout neurons, recording/stimulus devices)
        nodes = {}
        for i, pop in enumerate(self.pops):
            pop_name = self.params.populations[i]
            nodes[str(pop_name)] = pop.tolist()

        if "spike_recorder" in self.params.rec_dev:
            for i, spike_recorder in enumerate(self.spike_recorders):
                pop_name = self.params.populations[i]
                nodes[f"spike_recorder_{pop_name}"] = spike_recorder.tolist()

        helpers.dict2json(nodes, self.params.data_path / "nodes.json")

        # python packages and versions
        os.system(f"pip freeze > {self.params.data_path / 'requirements.txt'}")

        # store system metadata
        # os.system('cd %s; gathermetadata system_metadata' % self.params.data_path)

    def simulate(self, t_sim):
        """Simulates the microcircuit.

        Parameters
        ----------
        t_sim
            Simulation time (in ms).
        """

        helpers.message(f"Simulating {t_sim} ms.")

        nest.Simulate(t_sim)

    def evaluate(self, raster_plot_interval, firing_rates_interval):
        """Displays simulation results.
        Creates a spike raster plot.
        Calculates the firing rate of each population and displays them as a box plot.
        Does nothing if ``spike_recorder`` is not in ``params.rec_dev``.

        Parameters
        ----------
        raster_plot_interval
            Times (in ms) to start and stop loading spike times for raster plot (included).
        firing_rates_interval
            Times (in ms) to start and stop loading spike
            times for computing firing rates (included).

        Returns
        -------
            None
        """

        if nest.Rank() != 0:
            return

        if "spike_recorder" not in self.params.rec_dev:
            print("No spike recorder in rec_dev, skipping evaluation.")
            return

        print(f"Interval to plot spikes: {raster_plot_interval} ms")
        helpers.plot_raster(
            self.params.data_path,
            "spike_recorder",
            raster_plot_interval[0],
            raster_plot_interval[1],
            self.params.N_scaling,
        )

        print(f"Interval to compute firing rates: {firing_rates_interval} ms")
        helpers.firing_rates(
            self.params.data_path,
            "spike_recorder",
            firing_rates_interval[0],
            firing_rates_interval[1],
        )
        helpers.boxplot_firing_rates(self.params.data_path, self.params.populations)

    def _create_data_directory(self):
        """Creates the directory for the simulation data if it does not exist."""

        if nest.Rank() != 0:
            return

        data_path = self.params.data_path
        if data_path.is_dir():
            parts = [f"Data directory {data_path} already existed."]
            if self.params.overwrite_files:
                parts.append("Old data will be overwritten.")
        else:
            data_path.mkdir()
            parts = [f"Data directory {data_path} has been created."]

        print(" ".join(parts))
        print()

    def _setup_nest(self):
        """Initializes the NEST kernel.

        Reset the NEST kernel and pass parameters to it.
        """

        nest.ResetKernel()

        nest.set(
            local_num_threads=self.params.local_num_threads,
            resolution=self.params.sim_resolution,
            rng_seed=self.params.rng_seed,
            overwrite_files=self.params.overwrite_files,
            print_time=self.params.print_time,
        )

        helpers.message(f"RNG seed: {nest.rng_seed}")
        helpers.message(f"Total number of virtual processes: {nest.total_num_virtual_procs}")

    def _create_neuronal_populations(self):
        """Creates the neuronal populations.

        The neuronal populations are created and the parameters are assigned to them.
        The initial membrane potential of the neurons is drawn from normal distributions
        dependent on the parameter ``V0_type``.

        The first and last neuron id of each population is written to file.
        """

        helpers.message("Creating neuronal populations.")

        self.pops = []
        for i in np.arange(self.params.num_pops):
            pop_params = {
                "tau_syn_ex": self.params.tau_syn,
                "tau_syn_in": self.params.tau_syn,
                # NEST's iaf_psc_exp kwarg is fixed as `E_L`, unlike renamed field
                "E_L": self.params.V_rest,
                "V_th": self.params.V_th,
                "V_reset": self.params.V_reset,
                # NEST's iaf_psc_exp kwarg is fixed as `t_ref`, unlike renamed field
                "t_ref": self.params.tau_ref,
                "I_e": self.params.DC_amp[i],
            }

            if self.params.V0_type == "optimized":
                pop_params["V_m"] = nest.random.normal(
                    self.params.V0_mean_optimized[i],
                    self.params.V0_std_optimized[i],
                )
            else:
                pop_params["V_m"] = nest.random.normal(
                    self.params.V0_mean_original,
                    self.params.V0_std_original,
                )

            population = nest.Create(
                self.params.neuron_model,
                n=self.params.num_neurons[i],
                params=pop_params,
            )

            self.pops.append(population)

        if nest.Rank() != 0:
            return

        if self.params.subthreshold_populations:
            warnings.warn(
                "DC-compensated populations below rheobase (may go silent): "
                f"{self.params.subthreshold_populations}"
            )

        # write node ids to file
        with open(self.params.data_path / "population_nodeids.dat", "w+") as f:
            for pop in self.pops:
                f.write(f"{pop[0].global_id} {pop[-1].global_id}\n")

    def _create_recording_devices(self):
        """Creates one recording device of each kind per population.

        Only devices which are given in ``params.rec_dev`` are created.
        """

        helpers.message("Creating recording devices.")

        if "spike_recorder" in self.params.rec_dev:
            helpers.message("  Creating spike recorders.")
            sd_params = {
                "record_to": "ascii",
                "label": str(self.params.data_path / "spike_recorder"),
            }
            self.spike_recorders = nest.Create(
                "spike_recorder", n=self.params.num_pops, params=sd_params
            )

        if "voltmeter" in self.params.rec_dev:
            helpers.message("  Creating voltmeters.")
            vm_params = {
                "interval": self.params.rec_V_int,
                "record_to": "ascii",
                "record_from": ["V_m"],
                "label": str(self.params.data_path / "voltmeter"),
            }
            self.voltmeters = nest.Create("voltmeter", n=self.params.num_pops, params=vm_params)

    def _create_poisson_bg_input(self):
        """Creates the Poisson generators for ongoing background input.

        Used if ``params.CC_type`` is ``"poisson"``. If ``CC_type`` is ``"dc"`` instead,
        DC input is applied for compensation in ``_create_neuronal_populations()``.
        """

        helpers.message("Creating Poisson generators for background input.")

        self.poisson_bg_input = nest.Create(
            "poisson_generator",
            n=self.params.num_pops,
            params={"rate": (np.array(self.params.K_CC) * self.params.rate_CC).tolist()},
        )

    def _create_thalamic_stim_input(self):
        """Creates the thalamic neuronal population if specified in ``params``.

        Each neuron of the thalamic population is supposed to transmit the same Poisson spike train
        to all of its targets in the cortical neuronal population, and spike trains elicited by
        different thalamic neurons should be statistically independent. In NEST, this is achieved
        with a single Poisson generator connected to all thalamic neurons which are of type
        ``parrot_neuron``; Poisson generators send independent spike trains to each of their targets
        and parrot neurons just repeat incoming spikes.

        Note that the number of thalamic neurons is not scaled with ``N_scaling``.
        """

        helpers.message("Creating thalamic input for external stimulation.")

        self.thalamic_population = nest.Create("parrot_neuron", n=self.params.num_th_neurons)

        self.poisson_th = nest.Create(
            "poisson_generator",
            n=1,
            params={
                "rate": self.params.th_rate,
                "start": self.params.th_start,
                "stop": self.params.th_start + self.params.th_duration,
            },
        )

    def _create_dc_stim_input(self):
        """Creates DC generators for external stimulation if specified in ``params``.

        The final amplitude is ``params.dc_transient_amp * params.K_CC_full``.
        """

        dc_amp_stim = self.params.dc_transient_amp_populations

        helpers.message("Creating DC generators for external stimulation.")

        dc_params = {
            "amplitude": dc_amp_stim,
            "start": self.params.dc_transient_start,
            "stop": self.params.dc_transient_start + self.params.dc_transient_dur,
        }
        self.dc_stim_input = nest.Create("dc_generator", n=self.params.num_pops, params=dc_params)

    def _connect_neuronal_populations(self):
        """Creates the recurrent connections between neuronal populations."""

        helpers.message("Connecting neuronal populations recurrently.")

        delay_matrix_mean = self.params.delay_matrix_mean
        num_synapses = self.params.num_synapses
        PSC_matrix_mean = self.params.PSC_matrix_mean

        for i, target_pop in enumerate(self.pops):
            for j, source_pop in enumerate(self.pops):
                ## this case distinction would not have been necessary if
                ## nest.random.normal(mean,std) permitted std=0
                if self.params.delay_cv == 0:
                    delay = delay_matrix_mean[i][j]
                else:
                    delay = nest.math.redraw(
                        nest.random.normal(
                            mean=delay_matrix_mean[i][j],
                            std=(delay_matrix_mean[i][j] * self.params.delay_cv),
                        ),
                        min=nest.resolution - 0.5 * nest.resolution,
                        max=np.inf,
                    )
                    # resulting minimum delay is equal to resolution, see:
                    # https://nest-simulator.readthedocs.io/en/latest/nest_behavior
                    # /random_numbers.html#rounding-effects-when-randomizing-delays

                if num_synapses[i][j] >= 0.0:
                    conn_dict_rec = {
                        "rule": "fixed_total_number",
                        "N": num_synapses[i][j],
                    }

                    if PSC_matrix_mean[i][j] < 0:
                        w_min = -np.inf
                        w_max = 0.0
                    else:
                        w_min = 0.0
                        w_max = np.inf

                    syn_dict = {
                        "synapse_model": "static_synapse",
                        "weight": nest.math.redraw(
                            nest.random.normal(
                                mean=PSC_matrix_mean[i][j],
                                std=abs(PSC_matrix_mean[i][j] * self.params.weight_cv),
                            ),
                            min=w_min,
                            max=w_max,
                        ),
                        "delay": delay,
                    }
                    nest.Connect(
                        source_pop,
                        target_pop,
                        conn_spec=conn_dict_rec,
                        syn_spec=syn_dict,
                    )

    def _connect_recording_devices(self):
        """Connects the recording devices to the microcircuit."""

        helpers.message("Connecting recording devices.")

        for i, target_pop in enumerate(self.pops):
            if "spike_recorder" in self.params.rec_dev:
                nest.Connect(target_pop, self.spike_recorders[i])
            if "voltmeter" in self.params.rec_dev:
                nest.Connect(self.voltmeters[i], target_pop)

    def _connect_poisson_bg_input(self):
        """Connects the Poisson generators to the microcircuit."""

        helpers.message("Connecting Poisson generators for background input.")

        for i, target_pop in enumerate(self.pops):
            conn_dict_poisson = {"rule": "all_to_all"}

            syn_dict_poisson = {
                "synapse_model": "static_synapse",
                "weight": self.params.PSC_ext,
                "delay": self.params.delay_CC,
            }

            nest.Connect(
                self.poisson_bg_input[i],
                target_pop,
                conn_spec=conn_dict_poisson,
                syn_spec=syn_dict_poisson,
            )

    def _connect_thalamic_stim_input(self):
        """Connects the thalamic input to the neuronal populations."""

        helpers.message("Connecting thalamic input.")

        # connect Poisson input to thalamic population
        nest.Connect(self.poisson_th, self.thalamic_population)

        # connect thalamic population to neuronal populations
        for i, target_pop in enumerate(self.pops):
            conn_dict_th = {
                "rule": "fixed_total_number",
                "N": self.params.num_th_synapses[i],
            }

            syn_dict_th = {
                "weight": nest.math.redraw(
                    nest.random.normal(
                        mean=self.params.weight_th,
                        std=self.params.weight_th * self.params.weight_cv,
                    ),
                    min=0.0,
                    max=np.inf,
                ),
                "delay": nest.math.redraw(
                    nest.random.normal(
                        mean=self.params.delay_th_mean,
                        std=self.params.delay_th_mean * self.params.delay_cv,
                    ),
                    # resulting minimum delay is equal to resolution, see:
                    # https://nest-simulator.readthedocs.io/en/latest/nest_behavior
                    # /random_numbers.html#rounding-effects-when-randomizing-delays
                    min=nest.resolution - 0.5 * nest.resolution,
                    max=np.inf,
                ),
            }

            nest.Connect(
                self.thalamic_population,
                target_pop,
                conn_spec=conn_dict_th,
                syn_spec=syn_dict_th,
            )

    def _connect_dc_stim_input(self):
        """Connects the DC generators to the neuronal populations."""

        helpers.message("Connecting DC generators.")

        for i, target_pop in enumerate(self.pops):
            nest.Connect(self.dc_stim_input[i], target_pop)
