# -*- coding: utf-8 -*-
#
# parameter_definitions.py
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

"""
This file contains the definition of all microcircuit-PD14 parameters,
including (default) values, physical units, descriptions, latex notations, and
sections for a classification of parameters.

The parameter definition is an instance of the Pydantic BaseModel class, which
allows for validation of parameters and generation of a JSON schema. The JSON
schema can be used for an automated generation of a YAML configuration file
(see `generate_example_config()`). This YAML file can serve as a template for
user-defined configuration files, which can be loaded into the model and
validated against the JSON schema (see `load_parameters_from_yaml()`).

Secondary parameters are derived from the primary parameters by defining
"computed_fields". When loading user-defined parameters from a YAML
file, the computed fields are automatically updated.

"""

####################################

from ruamel.yaml import YAML
import numpy as np
from typing import Self

from pydantic import BaseModel, Field, computed_field
import rich

import microcircuit.helpers as helpers


################################################################################
class Parameters(BaseModel):

    ##
    #########################################################################
    ## primary parameters

    """
    All parameters that are defined in the model description and that can be
    directly set by the user are defined here as primary parameters. This includes
    network parameters, neuron parameters, synapse parameters, initialization
    parameters, stimulus parameters, and simulation parameters.
    """

    ###################################
    ## network parameters

    N_scaling: float = Field(
        default=1.0,
        description=r"Scaling factor determining network size.",
        json_schema_extra={"unit": "", "latex": r"$\alpha_N$", "section": r"network"},
    )

    K_scaling: float = Field(
        default=1.0,
        description=r"Scaling factor determining synapse numbers.",
        json_schema_extra={"unit": "", "latex": r"$\alpha_K$", "section": r"network"},
    )

    ## TODO: This is not a parameter. Remove it here.
    populations: list = Field(
        default=["L23E", "L23I", "L4E", "L4I", "L5E", "L5I", "L6E", "L6I"],
        description=r"Populations.",
        json_schema_extra={
            "unit": "",
            "latex": r"$x$",
            "section": r"network",
        },
    )

    full_num_neurons: list = Field(
        default=[20683, 5834, 21915, 5479, 4850, 1065, 14395, 2948],
        description=r"Default number of neurons in each population $x$ of the full-scale network.",
        json_schema_extra={
            "unit": "",
            "latex": r"$\tilde{N}_x$",
            "section": r"network",
        },
    )

    conn_probs: list = Field(
        default=[
            [0.1009, 0.1689, 0.0437, 0.0818, 0.0323, 0.0, 0.0076, 0.0],
            [0.1346, 0.1371, 0.0316, 0.0515, 0.0755, 0.0, 0.0042, 0.0],
            [0.0077, 0.0059, 0.0497, 0.135, 0.0067, 0.0003, 0.0453, 0.0],
            [0.0691, 0.0029, 0.0794, 0.1597, 0.0033, 0.0, 0.1057, 0.0],
            [0.1004, 0.0622, 0.0505, 0.0057, 0.0831, 0.3726, 0.0204, 0.0],
            [0.0548, 0.0269, 0.0257, 0.0022, 0.06, 0.3158, 0.0086, 0.0],
            [0.0156, 0.0066, 0.0211, 0.0166, 0.0572, 0.0197, 0.0396, 0.2252],
            [0.0364, 0.001, 0.0034, 0.0005, 0.0277, 0.008, 0.0658, 0.1443],
        ],
        description=r"Connection probabilities for each pair of pre- and postsynaptic populations $x$ and $y$ (first index: target; second index: source)",
        json_schema_extra={
            "unit": "",
            "latex": r"$C_{yx}$",
            "section": r"network",
        },
    )

    ###################################
    ## neuron parameters

    neuron_model: str = Field(
        default="iaf_psc_exp",
        description=r"NEST neuron model name.",
        json_schema_extra={
            "unit": "",
            "latex": r"neuron\_model",
            "section": r"neuron",
        },
    )

    ## TODO: adjust model code to the new parameterization used here
    ## (in the old version, all neuron parameters were kept in a dictionary neuron_params, including the initial conditions)

    ## TODO: rename variable into `V_rest`
    E_L: float = Field(
        default=-65.0,
        description=r"Resting potential.",
        json_schema_extra={
            "unit": "mV",
            "latex": r"V_\text{rest}",
            "section": r"neuron",
        },
    )

    V_th: float = Field(
        default=-50.0,
        description=r"Spike threshold potential.",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$\theta$",
            "section": r"neuron",
        },
    )

    V_reset: float = Field(
        default=-65.0,
        description=r"After-spike reset potential.",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$V_\text{reset}$",
            "section": r"neuron",
        },
    )

    C_m: float = Field(
        default=250.0,
        description=r"Membrane capacitance.",
        json_schema_extra={
            "unit": "pF",
            "latex": r"$C_\text{m}$",
            "section": r"neuron",
        },
    )

    tau_m: float = Field(
        default=10.0,
        description=r"Membrane time constant.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\tau_\text{m}$",
            "section": r"neuron",
        },
    )

    ## TODO: rename variable into `tau_ref`
    t_ref: float = Field(
        default=2.0,
        description=r"Duration of absolute refractory period.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\tau_\text{ref}$",
            "section": r"neuron",
        },
    )

    ###################################
    ## synapse parameters

    ## TODO: rename variable into `weight_exc_mean`
    PSP_exc_mean: float = Field(
        default=0.15,
        description=r"Mean weight of excitatory synapses (PSP amplitude).",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$J$",
            "section": r"synapse",
        },
    )

    ## TODO: rename variable into `weight_cv`
    weight_rel_std: float = Field(
        default=0.1,
        description=r"Coefficient of variation of synaptic weight distributions (ratio between standard deviation and mean).",
        json_schema_extra={
            "unit": "",
            "latex": r"$\text{CV}_\text{w}$",
            "section": r"synapse",
        },
    )

    g: float = Field(
        default=-4.0,
        description=r"Relative weight of inhibitory synapses (ratio of inhibitory and excitatory synaptic weights).",
        json_schema_extra={
            "unit": "",
            "latex": r"$g$",
            "section": r"synapse",
        },
    )

    tau_syn: float = Field(
        default=0.5,
        description=r"Time constant of postsynaptic currents.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\tau_\text{s}$",
            "section": r"synapse",
        },
    )

    delay_exc_mean: float = Field(
        default=1.5,
        description=r"Mean spike transmission delay of excitatory connections.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{E}$",
            "section": r"synapse",
        },
    )

    delay_inh_mean: float = Field(
        default=0.75,
        description=r"Mean spike transmission delay of inhibitory connections.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{I}$",
            "section": r"synapse",
        },
    )

    ## TODO: rename variable into `delay_cv`
    delay_rel_std: float = Field(
        default=0.5,
        description=r"Coefficient of variation of delay distributions (ratio between standard deviation and mean).",
        json_schema_extra={
            "unit": "",
            "latex": r"$\text{CV}_\text{d}$",
            "section": r"synapse",
        },
    )

    ###################################
    ## initialization parameters

    V0_type: str = Field(
        default="optimized",
        description=r"Type of initial condition for the membrane potentials ('original' or 'optimized'). 'original': uniform mean and standard deviation for all populations. 'optimized': population-specific mean and standard deviation (default).",
        json_schema_extra={
            "unit": "",
            "latex": r"V0\_type",
            "section": r"initialization",
        },
    )

    ## TODO: adjust model code to the new parameterization used here
    V0_mean_original: float = Field(
        default=-58.0,
        description=r"Mean of initial membrane potentials in case V0_type = 'original'.",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$V0\_mean\_original$",
            "section": r"initialization",
        },
    )

    V0_std_original: float = Field(
        default=10.0,
        description=r"Standard deviation of initial membrane potentials in case V0_type = 'original'.",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$V0\_std\_original$",
            "section": r"initialization",
        },
    )

    V0_mean_optimized: list = Field(
        default=[-68.28, -63.16, -63.33, -63.45, -63.11, -61.66, -66.72, -61.43],
        description=r"Population-specific mean of initial membrane potentials in case V0_type = 'optimized' (same order as in `populations`).",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$V0\_mean\_optimized$",
            "section": r"initialization",
        },
    )

    V0_std_optimized: list = Field(
        default=[5.36, 4.57, 4.74, 4.94, 4.94, 4.55, 5.46, 4.48],
        description=r"Population-specific standard deviation of initial membrane potentials in case V0_type = 'optimized' (same order as in `populations`).",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$V0\_std\_optimized$",
            "section": r"initialization",
        },
    )

    ###################################
    ## stimulus parameters
    full_mean_rates: list = Field(
        default=[0.903, 2.965, 4.414, 5.876, 7.569, 8.633, 1.105, 7.829],
        description=r"Mean firing rates of the different populations $x$ in the non-scaled version of the microcircuit (same order as in `populations`; required for network scaling).",
        json_schema_extra={
            "unit": "spikes/s",
            "latex": r"$\tilde{\nu}_x$",
            "section": r"stimulus",
        },
    )

    ## TODO: rename variable into `CC_type`
    bg_input_type: str = Field(
        default="dc",
        description=r"Type of cortico-cortical input ('poisson' or 'dc').",
        json_schema_extra={
            "unit": "",
            "latex": r"bg\_input\_type",
            "section": r"stimulus",
        },
    )

    ## TODO: rename variable into `K_CC_full`
    K_ext: list = Field(
        default=[1600, 1500, 2100, 1900, 2000, 1900, 2900, 2100],
        description=r"Number of cortico-cortical inputs per neuron (in-degree) in the full-scalenework for each cortical population $y$ (same order as in `populations`).",
        json_schema_extra={
            "unit": "",
            "latex": r"$\tilde{K}_{\mathcal{C}_y}$",
            "section": r"stimulus",
        },
    )

    ## TODO: rename variable into `rate_CC`
    bg_rate: float = Field(
        default=8.0,
        description=r"Rate of cortico-cortical inputs.",
        json_schema_extra={
            "unit": "spikes/s",
            "latex": r"$\nu_\text{CC}$",
            "section": r"stimulus",
        },
    )

    ## TODO: rename variable into `delay_CC`
    delay_poisson: float = Field(
        default=1.5,
        description=r"Spike transmission delay of cortico-cortical inputs.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{CC}$",
            "section": r"stimulus",
        },
    )

    thalamic_input: bool = Field(
        default=False,
        description=r"Turn (transient) thalamic input on ('True) or off ('False'; default).",
        json_schema_extra={
            "unit": "",
            "latex": r"thalamic\_input",
            "section": r"stimulus",
        },
    )

    th_start: float = Field(
        default=700.0,
        description=r"Onset time of thalamic input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$t_\text{start}$",
            "section": r"stimulus",
        },
    )

    th_duration: float = Field(
        default=10.0,
        description=r"Duration of thalamo-cortical input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\Delta_\text{TC}$",
            "section": r"stimulus",
        },
    )

    th_rate: float = Field(
        default=120.0,
        description=r"Rate of thalamo-cortical input.",
        json_schema_extra={
            "unit": "spikes/s",
            "latex": r"$\nu_\text{TC}$",
            "section": r"stimulus",
        },
    )

    num_th_neurons: int = Field(
        default=902,
        description=r"Number of thalamic neurons.",
        json_schema_extra={
            "unit": "",
            "latex": r"$N_\text{TC}$",
            "section": r"stimulus",
        },
    )

    conn_probs_th: list = Field(
        default=[0.0, 0.0, 0.0983, 0.0619, 0.0, 0.0, 0.0512, 0.0196],
        description=r"Probabilities of connections from the thalamus to each cortical populations $y$ (same order as in `populations`).",
        json_schema_extra={
            "unit": "",
            "latex": r"$C_{y,\mathcal{T}}$",
            "section": r"stimulus",
        },
    )

    ## TODO: in the model description, this is not a separate parameter, but identical to $J$; check model code
    PSP_th: float = Field(
        default=0.15,
        description=r"Mean weight of thalamo-cortical inputs (PSP amplitude).",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$J_\text{TC}$",
            "section": r"stimulus",
        },
    )

    ## TODO: in the model description, this is not a separate parameter, but identical to $d_E$; check model code
    delay_th_mean: float = Field(
        default=1.5,
        description=r"Mean spike transmission delay of thalamo-cortical inputs.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{TC}$",
            "section": r"stimulus",
        },
    )

    ## TODO: in the model description, this is not a separate parameter, but identical to $CV_d$; check model code
    delay_th_rel_std: float = Field(
        default=0.5,
        description=r"Coefficient of variation of thalamo-cortical spike transmission delays (ratio between standard deviation and mean of thalamic delay distribution).",
        json_schema_extra={
            "unit": "",
            "latex": r"$\text{CV}_\text{d,TC}$",
            "section": r"stimulus",
        },
    )

    dc_input: bool = Field(
        default=False,
        description=r"Turn (transient) DC input on ('True) or off ('False'; default).",
        json_schema_extra={
            "unit": "",
            "latex": r"dc\_input",
            "section": r"stimulus",
        },
    )

    dc_transient_start: float = Field(
        default=650.0,
        description=r"Onset time of transient DC input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$t_\text{start}^\text{DC}$",
            "section": r"stimulus",
        },
    )

    dc_transient_dur: float = Field(
        default=100.0,
        description=r"Duration of transient DC input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\Delta_\text{DC}$",
            "section": r"stimulus",
        },
    )

    dc_transient_amp: float = Field(
        default=0.3,
        description=r"Amplitude of transient DC input (final amplitude is population-specific and will be obtained by multiplication with 'K_ext').",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$I_\text{DC}$",
            "section": r"stimulus",
        },
    )

    ###################################
    ## simulation parameters

    t_presim: float = Field(
        default=500.0,
        description=r"Duration of presimulation (warmup).",
        json_schema_extra={
            "unit": "ms",
            "latex": r"t\_presim$",
            "section": r"simulation",
        },
    )

    t_sim: float = Field(
        default=1000.0,
        description=r"Duration of (main) simulation.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"t\_sim$",
            "section": r"simulation",
        },
    )

    sim_resolution: float = Field(
        default=0.1,
        description=r"Simulation time resolution.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"sim\_resolution$",
            "section": r"simulation",
        },
    )

    rec_dev: list = Field(
        default=["spike_recorder"],
        description=r"List of recording devices ('spike_recorder' [default] and/or 'voltmeter'). Nothing will be recorded if an empty list is given.",
        json_schema_extra={
            "unit": "",
            "latex": r"rec\_dev",
            "section": r"simulation",
        },
    )

    ## TODO: make sure that the current working directory is appended when setting derived parameters; "data_path": os.path.join(os.getcwd(), "data/")
    data_path: str = Field(
        default="data/",
        description=r"Path for storage of simulation data and metadata.",
        json_schema_extra={
            "unit": "",
            "latex": r"data\_path",
            "section": r"simulation",
        },
    )

    rng_seed: int = Field(
        default=55,
        description=r"Seed for NEST random number generator (used for connectivity, initial conditions, and Poissonian spike input).",
        json_schema_extra={
            "unit": "",
            "latex": r"rng\_seed",
            "section": r"simulation",
        },
    )

    local_num_threads: int = Field(
        default=4,
        description=r"Number of threads per MPI process. Note: when up-scaling the network, the model may not run correctly if there are < 4 virtual processes (i.e, a thread in an MPI process). If there are 4 or more MPI processes, this value can be set to 1.",
        json_schema_extra={
            "unit": "",
            "latex": r"local\_num\_threads",
            "section": r"simulation",
        },
    )

    rec_V_int: float = Field(
        default=1.0,
        description=r"Time resolution of membrane potential recordings.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"rec\_V\_int",
            "section": r"simulation",
        },
    )

    overwrite_files: bool = Field(
        default=True,
        description=r"If 'True' (default), existing files will be overwritten. If 'False', a NESTError is raised if the files already exist.",
        json_schema_extra={
            "unit": "",
            "latex": r"overwrite\_files",
            "section": r"simulation",
        },
    )

    print_time: bool = Field(
        default=True,
        description=r"If 'True' (default), the simulation progress is printed. This should only be used if the simulation is run on a local machine.",
        json_schema_extra={
            "unit": "",
            "latex": r"print\_time",
            "section": r"simulation",
        },
    )

    store_meta_data: bool = Field(
        default=True,
        description=r"If 'True' (default), metadata (parameter values, node IDs, and software requirements) will be stored together with the simulation data. ",
        json_schema_extra={
            "unit": "",
            "latex": r"store\_meta\_data",
            "section": r"simulation",
        },
    )

    #########################################################################
    ## secondary parameters
    """
    All parameters that are not directly set by the user, but derived from the
    primary parameters are defined here as secondary parameters. When loading
    user-defined parameters from a YAML file, the computed fields are
    automatically updated.
    """

    ###################################
    ## derived network parameters

    ## TODO: sort derived parameters below according to section

    @computed_field(
        ## TODO: extract LaTeX strings of primary parameters when using them in descriptions
        # description=r"Number of neurons in each population; $N_x=$%s%s ($\forall x\in\mathcal{P}$)." % (latex("N_scaling"), latex("full_num_neurons")), ## not working (yet)
        description=r"Number of neurons in each cortical population $x$; $N_x=\alpha_N \tilde{N}_{x,\text{full}}$ ($\forall x\in\mathcal{P}$).",
        json_schema_extra={
            "unit": "",
            "latex": r"$N_x$",
            "section": r"network_derived",
        },
    )
    @property
    def num_neurons(self) -> list:
        return (self.N_scaling * np.array(self.full_num_neurons)).astype(int)

    @computed_field(
        description=r"Number of local cortical populations.",
        json_schema_extra={
            "unit": "",
            "latex": r"$N_\text{pops}$",
            "section": r"network_derived",
        },
    )
    @property
    def num_pops(self) -> int:
        return len(self.populations)

    @computed_field(
        description=r"Total number of connections between cortical populations in the full-scale network, for each pair of presynaptic and postsynaptic populations $x$ and $y$.",
        json_schema_extra={
            "unit": "",
            "latex": r"$\tilde{Q}_{yx}$",
            "section": r"network_derived",
        },
    )
    @property
    def full_num_synapses(self) -> list:
        return helpers.num_synapses_from_conn_probs(
            self.conn_probs, self.full_num_neurons, self.full_num_neurons
        )

    @computed_field(
        description=r"Total number of connections between neuronal populations, for each pair of presynaptic and postsynaptic cortical populations $x$ and $y$; $Q_{yx}=\alpha_N \alpha_K \tilde{Q}_{yx}$",
        json_schema_extra={
            "unit": "",
            "latex": r"$Q_{yx}",
            "section": r"network_derived",
        },
    )
    @property
    def num_synapses(self) -> list:
        return np.round(
            np.array(self.full_num_synapses) * self.N_scaling * self.K_scaling
        ).astype(int)

    ## TODO: rename variable into `K_CC`
    @computed_field(
        description=r"Number of cortico-cortical inputs per neuron (in-degree) for each cortical populations $y$; $K_{\mathcal{C}_x}=\alpha_K \tilde{K}_{\mathcal{C}_x}$",
        json_schema_extra={
            "unit": "",
            "latex": r"$K_{\mathcal{C}_x}",
            "section": r"network_derived",
        },
    )
    @property
    def ext_indegrees(self) -> list:
        return np.round(np.array(self.K_ext) * self.K_scaling).astype(int)

    @computed_field(
        description=r"Unit PSP amplitude (ratio between PSP and PSC amplitude; conversion factor for synaptic weights).",
        json_schema_extra={
            "unit": "mV/pA",
            "latex": r"$J_\text{unit}$",  ## see eq.(11) in https://microcircuit-pd14-model.readthedocs.io/en/latest/_static/microcircuit-pd14-model.pdf
            "section": r"synapse_derived",
        },
    )
    @property
    def J_unit(self) -> float:
        return 1 / helpers.postsynaptic_potential_to_current(
            self.C_m, self.tau_m, self.tau_syn
        )

    @computed_field(
        description=r"Matrix of mean PSC amplitudes for all pairs of presynaptic and postsynaptic cortical populations; $\bar{I}_{yx}=J_{yx}/J_\text{unit}$.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$\bar{I}_{yx}$",
            "section": r"synapse_derived",
        },
    )
    @property
    def PSC_matrix_mean(self) -> list:
        return self.PSP_matrix_mean / self.J_unit

    @computed_field(
        description=r"Mean PSC amplitude of cortico-cortical inputs; $\bar{I}_\text{CC}=J/J_\text{unit}$.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$\bar{I}_\text{CC}$",
            "section": r"synapse_derived",
        },
    )
    @property
    def PSC_ext(self) -> float:
        return self.PSP_exc_mean / self.J_unit

    # # DC input compensates for potentially missing Poisson input
    # if self.net_dict["bg_input_type"] == "poisson":
    #     DC_amp = np.zeros(self.num_pops)
    # # else:
    # elif self.net_dict["bg_input_type"] == "dc":
    #     # if nest.Rank() == 0: # default case should not raise a warning
    #     # warnings.warn("DC input created to compensate missing Poisson input.\n")
    #     DC_amp = helpers.dc_input_compensating_poisson(
    #         self.net_dict["bg_rate"],
    #         self.net_dict["K_ext"],
    #         self.net_dict["neuron_params"]["tau_syn"],
    #         PSC_ext,
    #     )

    # # adjust weights and DC amplitude if the indegree is scaled
    # if self.net_dict["K_scaling"] != 1:
    #     PSC_matrix_mean, PSC_ext, DC_amp = (
    #         helpers.adjust_weights_and_input_to_synapse_scaling(
    #             self.net_dict["full_num_neurons"],
    #             full_num_synapses,
    #             self.net_dict["K_scaling"],
    #             PSC_matrix_mean,
    #             PSC_ext,
    #             self.net_dict["neuron_params"]["tau_syn"],
    #             self.net_dict["full_mean_rates"],
    #             DC_amp,
    #             self.net_dict["bg_input_type"],
    #             self.net_dict["bg_rate"],
    #             self.net_dict["K_ext"],
    #         )
    #     )

    #     # check if all populations are supra-threshold with the changed DC input
    #     if self.net_dict["bg_input_type"] == "dc":
    #         I_rh = helpers.compute_rheo_base_current(
    #             self.net_dict["neuron_params"]["V_th"],
    #             self.net_dict["neuron_params"]["E_L"],
    #             self.net_dict["neuron_params"]["C_m"],
    #             self.net_dict["neuron_params"]["tau_m"],
    #         )
    #         for i, pop in enumerate(self.net_dict["populations"]):
    #             if DC_amp[i] < I_rh:
    #                 warnings.warn(
    #                     "\nPopulation {} is sub-threshold with downscaled DC input amplitude and may not fire. ".format(
    #                         pop
    #                     )
    #                 )

    # # store final parameters as class attributes
    # self.weight_matrix_mean = PSC_matrix_mean
    # self.weight_ext = PSC_ext
    # self.DC_amp = DC_amp

    # # thalamic input
    # if self.stim_dict["thalamic_input"]:
    #     num_th_synapses = helpers.num_synapses_from_conn_probs(
    #         self.stim_dict["conn_probs_th"],
    #         self.stim_dict["num_th_neurons"],
    #         self.net_dict["full_num_neurons"],
    #     )[0]
    #     self.weight_th = self.stim_dict["PSP_th"] * PSC_over_PSP
    #     if self.net_dict["K_scaling"] != 1:
    #         num_th_synapses *= self.net_dict["K_scaling"]
    #         self.weight_th /= np.sqrt(self.net_dict["K_scaling"])
    #     self.num_th_synapses = np.round(num_th_synapses).astype(int)

    # if nest.Rank() == 0:
    #     message = ""
    #     if self.net_dict["N_scaling"] != 1:
    #         message += "Neuron numbers are scaled by a factor of {:.3f}.\n".format(
    #             self.net_dict["N_scaling"]
    #         )
    #     if self.net_dict["K_scaling"] != 1:
    #         message += "Indegrees are scaled by a factor of {:.3f}.".format(
    #             self.net_dict["K_scaling"]
    #         )
    #         message += "\n  Weights and DC input are adjusted to compensate.\n"
    #     print(message)

    ###################################
    ## derived neuron parameters

    @computed_field(
        description=r"Membrane resistance.",
        json_schema_extra={
            "unit": r"M$\Omega$",
            "latex": r"$R_\text{m}=\tau_\text{m}/C_\text{m}$",
            "section": r"neuron_derived",
        },
    )
    @property
    def R_m(self) -> float:
        return self.tau_m / self.C_m * 1000.0  # conversion from ms/pF to MOhm

    ###################################
    ## derived synapse parameters

    @computed_field(
        description=r"Matrix containing mean synaptic weights (PSP amplitudes) all pairs of presynaptic and postsynaptic populations.",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$J_{yx}$ ($\forall y,x\in\mathcal{P}$)",
            "section": r"synapse_derived",
        },
    )
    @property
    def PSP_matrix_mean(self) -> list:
        return helpers.get_exc_inh_matrix(
            self.PSP_exc_mean, self.PSP_exc_mean * self.g, len(self.populations)
        )

    @computed_field(
        description=r"Matrix containing mean spike transmission delays all pairs of presynaptic and postsynaptic populations.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$d_{yx}$ ($\forall y,x\in\mathcal{P}$)",
            "section": r"synapse_derived",
        },
    )
    @property
    def delay_matrix_mean(self) -> list:
        return helpers.get_exc_inh_matrix(
            self.delay_exc_mean, self.delay_inh_mean, len(self.populations)
        )

    ## TODO: synaptic weights $\bar{I})yx$ (PSC amplitude) for different pairs $x$ and $y$

    ## TODO: delay_matrix_mean

    ###################################
    ## derived stimulus parameters

    ## TODO: mean total current of cc inputs $I_{C_x}$
    ## TODO: mean current of each individual cc input
    ## TODO: t_stop

    #########################################################################
    # def model_post_init(self):
    #     assert self.J>0

    #########################################################################
    def print(self) -> None:
        # rich.print(self)
        rich.print(dict(self))
        # rich.print(self.model_dump_json(indent=4))


################################################################################
################################################################################


# def latex(field):
#     """
#     Extracts the LaTeX string for a given field from the Parameters class.
#     """

#     return Parameters.model_fields[field].json_schema_extra["latex"]


#########################################################################
def generate_example_config(filename="params_default.yaml", mode="validation") -> None:
    """
    Generates a YAML configuration file containing all parameters defined in
    the Parameters class. All metadata (descriptions, units, LaTeX symbols, and
    sections) are included in the YAML file as comments. The parameters are
    listed in the order they are defined in the Parameters class.

    The generated YAML file can be used as a template for user-defined
    configuration files.

    Parameters:
    -----------

    filename: str
        Path to the YAML file to be generated.

    mode: str

          Mode for JSON schema generation.

          'validation' (default): only primary parameters are included.

          'serialization': both primary and secondary parameters are included;
                           secondary parameters are included without values, as
                           they will be automatically updated

    """

    schema = Parameters.model_json_schema(mode=mode)

    with open(filename, "w") as yaml_file:
        yaml_file.write("# This file is autogenerated by generate_example_config().\n")
        yaml_file.write(
            "# To modify the metadata (descriptions, units, LaTeX symbols),\n"
        )
        yaml_file.write(
            "# edit the parameters definition in parameter_definitions.py,\n"
        )
        yaml_file.write("# and run generate_example_config() again.\n")
        yaml_file.write("\n")

        for key in schema["properties"].keys():
            field = schema["properties"][key]

            if "default" in field:
                yaml_file.write(f"{key}: {field['default']}\n")
            else:
                yaml_file.write(f"# {key}: This is a derived parameter.\n")

            yaml_file.write(f"# {field['description']}\n")
            yaml_file.write(f"# unit: {field['unit']}\n")
            yaml_file.write(f"# LaTeX: {field['latex']}\n")
            yaml_file.write(f"# section: {field['section']}\n")
            yaml_file.write("\n")


#########################################################################

## move to io.py
yaml = YAML()


def load_parameters_from_yaml(filename) -> Parameters:
    """
    Loads parameters from a YAML file and validates them against the Parameters
    class.

    Parameters:
    -----------

    filename: str
        Path to the YAML file containing the parameters.

    Returns:
    --------

    Parameters
        An instance of the Parameters class containing the loaded parameters.

    """

    with open(filename, "r") as yaml_file:
        loaded_params = yaml.load(yaml_file)
        return Parameters.model_validate(loaded_params)


#########################################################################


def test_parameter_loading(filename) -> None:
    """
    Test function for loading parameters from a YAML file. It loads parameters
    from a YAML file, and checks if they match the original parameters defined
    in the Parameters class.

    Parameters:
    -----------

    filename: str
              Path to the YAML file containing the parameters to be loaded and
              tested.

    """
    params = Parameters()

    # filename = "params_default.yaml"
    # generate_example_config(filename)

    test_params = load_parameters_from_yaml(filename)

    assert (
        params == test_params
    ), "Validation failed: Loaded parameters do not match the original defaults."


#########################################################################


# if __name__ == "__main__":
def illustrate_parameter_usage():

    filename = "params_default.yaml"

    ## to include primary parameters only (without derived parameters)
    # generate_example_config(filename, mode="validation")

    ## to include both primary and secondary parameters
    ## (secondary parameters without values)
    generate_example_config(filename, mode="serialization")

    # test_parameter_loading(filename)
    # print("All tests passed.")

    ## load parameters from YAML file and print them
    P = load_parameters_from_yaml(filename)
    P.print()

    ## illustrate usage
    print()

    P = Parameters()  ## create instance of Parameters class with default values

    print("default:")
    print("\tfull_num_neurons=", P.full_num_neurons)
    print("\tnum_neurons=", P.num_neurons)
    print()

    scaling_factor = 0.2
    P.N_scaling = scaling_factor
    P.K_scaling = scaling_factor

    print("after scaling with factor %.1f:" % scaling_factor)
    print("\tnum_neurons=", P.num_neurons)


#########################################################################

if __name__ == "__main__":
    illustrate_parameter_usage()
