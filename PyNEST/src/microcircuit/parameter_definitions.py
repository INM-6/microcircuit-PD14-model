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

import os
from importlib.resources import files
from pathlib import Path
from typing import Annotated, ClassVar, Literal

import numpy as np
import rich
from pydantic import BaseModel, ConfigDict, Field, computed_field
from ruamel.yaml import YAML

import microcircuit.helpers as helpers


class Parameters(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    populations: ClassVar[tuple[str, ...]] = (
        "L23E",
        "L23I",
        "L4E",
        "L4I",
        "L5E",
        "L5I",
        "L6E",
        "L6I",
    )
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
        gt=0,
        description=r"Scaling factor determining network size.",
        json_schema_extra={"unit": "", "latex": r"$\alpha_N$", "section": r"network"},
    )

    K_scaling: float = Field(
        default=1.0,
        gt=0,
        description=r"Scaling factor determining synapse numbers.",
        json_schema_extra={"unit": "", "latex": r"$\alpha_K$", "section": r"network"},
    )

    full_num_neurons: tuple[Annotated[int, Field(gt=0)], ...] = Field(
        default=(20683, 5834, 21915, 5479, 4850, 1065, 14395, 2948),
        max_length=len(populations),
        min_length=len(populations),
        description=r"Default number of neurons in each population $x$ of the full-scale network.",
        json_schema_extra={
            "unit": "",
            "latex": r"$\tilde{N}_x$",
            "section": r"network",
        },
    )

    conn_probs: tuple[
        Annotated[
            tuple[Annotated[float, Field(ge=0.0, le=1.0)], ...],
            Field(min_length=len(populations), max_length=len(populations)),
        ],
        ...,
    ] = Field(
        default=(
            (0.1009, 0.1689, 0.0437, 0.0818, 0.0323, 0.0, 0.0076, 0.0),
            (0.1346, 0.1371, 0.0316, 0.0515, 0.0755, 0.0, 0.0042, 0.0),
            (0.0077, 0.0059, 0.0497, 0.135, 0.0067, 0.0003, 0.0453, 0.0),
            (0.0691, 0.0029, 0.0794, 0.1597, 0.0033, 0.0, 0.1057, 0.0),
            (0.1004, 0.0622, 0.0505, 0.0057, 0.0831, 0.3726, 0.0204, 0.0),
            (0.0548, 0.0269, 0.0257, 0.0022, 0.06, 0.3158, 0.0086, 0.0),
            (0.0156, 0.0066, 0.0211, 0.0166, 0.0572, 0.0197, 0.0396, 0.2252),
            (0.0364, 0.001, 0.0034, 0.0005, 0.0277, 0.008, 0.0658, 0.1443),
        ),
        max_length=len(populations),
        min_length=len(populations),
        description=r"Connection probabilities for each pair of pre- and postsynaptic "
        r"populations $x$ and $y$ (first index: target; second index: source)",
        json_schema_extra={
            "unit": "",
            "latex": r"$C_{yx}$",
            "section": r"network",
        },
    )

    ###################################
    ## cortico-cortical (background) input parameters

    full_mean_rates: tuple[Annotated[float, Field(ge=0.0)], ...] = Field(
        default=(0.903, 2.965, 4.414, 5.876, 7.569, 8.633, 1.105, 7.829),
        max_length=len(populations),
        min_length=len(populations),
        description=r"Mean firing rates of the different populations $x$ in the non-scaled version of the microcircuit "
        "(same order as in `populations`; required for network scaling).",
        json_schema_extra={
            "unit": "spikes/s",
            "latex": r"$\tilde{\nu}_x$",
            "section": r"network",
        },
    )

    CC_type: Literal["poisson", "dc"] = Field(
        default="dc",
        description=r"Type of cortico-cortical input ('poisson' or 'dc').",
        json_schema_extra={
            "unit": "",
            "latex": r"bg\_input\_type",
            "section": r"network",
        },
    )

    K_CC_full: tuple[Annotated[float, Field(ge=0.0)], ...] = Field(
        default=(1600, 1500, 2100, 1900, 2000, 1900, 2900, 2100),
        max_length=len(populations),
        min_length=len(populations),
        description=r"Number of cortico-cortical inputs per neuron (in-degree) "
        "in the full-scalenework for each cortical population $y$ (same order as in `populations`).",
        json_schema_extra={
            "unit": "",
            "latex": r"$\tilde{K}_{\mathcal{C}_y}$",
            "section": r"network",
        },
    )

    rate_CC: float = Field(
        default=8.0,
        ge=0,
        description=r"Rate of cortico-cortical inputs.",
        json_schema_extra={
            "unit": "spikes/s",
            "latex": r"$\nu_\text{CC}$",
            "section": r"network",
        },
    )

    delay_CC: float = Field(
        gt=0,
        default=1.5,
        description=r"Spike transmission delay of cortico-cortical inputs.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{CC}$",
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

    V_rest: float = Field(
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
        gt=0,
        description=r"Membrane capacitance.",
        json_schema_extra={
            "unit": "pF",
            "latex": r"$C_\text{m}$",
            "section": r"neuron",
        },
    )

    tau_m: float = Field(
        default=10.0,
        gt=0,
        description=r"Membrane time constant.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\tau_\text{m}$",
            "section": r"neuron",
        },
    )

    tau_ref: float = Field(
        default=2.0,
        gt=0,
        description=r"Duration of absolute refractory period.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\tau_\text{ref}$",
            "section": r"neuron",
        },
    )

    ###################################
    ## synapse parameters

    weight_exc_mean: float = Field(
        default=0.15,
        gt=0,
        description=r"Mean weight of excitatory synapses (PSP amplitude).",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$J$",
            "section": r"synapse",
        },
    )

    weight_cv: float = Field(
        default=0.1,
        ge=0,
        description=r"Coefficient of variation of synaptic weight distributions"
        " (ratio between standard deviation and mean).",
        json_schema_extra={
            "unit": "",
            "latex": r"$\text{CV}_\text{w}$",
            "section": r"synapse",
        },
    )

    g: float = Field(
        default=-4.0,
        lt=0,
        description=r"Relative weight of inhibitory synapses "
        "(ratio of inhibitory and excitatory synaptic weights).",
        json_schema_extra={
            "unit": "",
            "latex": r"$g$",
            "section": r"synapse",
        },
    )

    tau_syn: float = Field(
        default=0.5,
        gt=0,
        description=r"Time constant of postsynaptic currents.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\tau_\text{s}$",
            "section": r"synapse",
        },
    )

    delay_exc_mean: float = Field(
        default=1.5,
        gt=0,
        description=r"Mean spike transmission delay of excitatory connections.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{E}$",
            "section": r"synapse",
        },
    )

    delay_inh_mean: float = Field(
        default=0.75,
        gt=0,
        description=r"Mean spike transmission delay of inhibitory connections.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{I}$",
            "section": r"synapse",
        },
    )

    delay_cv: float = Field(
        default=0.5,
        ge=0,
        description=r"Coefficient of variation of delay distributions (ratio between standard deviation and mean).",
        json_schema_extra={
            "unit": "",
            "latex": r"$\text{CV}_\text{d}$",
            "section": r"synapse",
        },
    )

    ###################################
    ## initialization parameters

    V0_type: Literal["original", "optimized"] = Field(
        default="optimized",
        description=r"Type of initial condition for the membrane potentials ('original' or 'optimized'). 'original': uniform mean and standard deviation for all populations. 'optimized': population-specific mean and standard deviation (default).",
        json_schema_extra={
            "unit": "",
            "latex": r"V0\_type",
            "section": r"initialization",
        },
    )

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

    V0_mean_optimized: tuple[float, ...] = Field(
        default=(-68.28, -63.16, -63.33, -63.45, -63.11, -61.66, -66.72, -61.43),
        max_length=len(populations),
        min_length=len(populations),
        description=r"Population-specific mean of initial membrane potentials in case V0_type = 'optimized' (same order as in `populations`).",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$V0\_mean\_optimized$",
            "section": r"initialization",
        },
    )

    V0_std_optimized: tuple[float, ...] = Field(
        default=(5.36, 4.57, 4.74, 4.94, 4.94, 4.55, 5.46, 4.48),
        max_length=len(populations),
        min_length=len(populations),
        description=r"Population-specific standard deviation of initial membrane potentials in case V0_type = 'optimized' (same order as in `populations`).",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$V0\_std\_optimized$",
            "section": r"initialization",
        },
    )

    ###################################
    # stimulus parameters
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
        ge=0,
        description=r"Onset time of thalamic input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$t_\text{start}$",
            "section": r"stimulus",
        },
    )

    th_duration: float = Field(
        default=10.0,
        gt=0,
        description=r"Duration of thalamo-cortical input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\Delta_\text{TC}$",
            "section": r"stimulus",
        },
    )

    th_rate: float = Field(
        default=120.0,
        ge=0,
        description=r"Rate of thalamo-cortical input.",
        json_schema_extra={
            "unit": "spikes/s",
            "latex": r"$\nu_\text{TC}$",
            "section": r"stimulus",
        },
    )

    num_th_neurons: int = Field(
        default=902,
        gt=0,
        description=r"Number of thalamic neurons.",
        json_schema_extra={
            "unit": "",
            "latex": r"$N_\text{TC}$",
            "section": r"stimulus",
        },
    )

    conn_probs_th: tuple[Annotated[float, Field(ge=0.0, le=1.0)], ...] = Field(
        default=(0.0, 0.0, 0.0983, 0.0619, 0.0, 0.0, 0.0512, 0.0196),
        max_length=len(populations),
        min_length=len(populations),
        description=r"Probabilities of connections from the thalamus to each cortical populations $y$ (same order as in `populations`).",
        json_schema_extra={
            "unit": "",
            "latex": r"$C_{y,\mathcal{T}}$",
            "section": r"stimulus",
        },
    )

    dc_transient: bool = Field(
        default=False,
        description=r"Turn (transient) DC input on ('True) or off ('False'; default).",
        json_schema_extra={
            "unit": "",
            "latex": r"dc\_transient",
            "section": r"stimulus",
        },
    )

    dc_transient_start: float = Field(
        default=650.0,
        ge=0,
        description=r"Onset time of transient DC input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$t_\text{start}^\text{DC}$",
            "section": r"stimulus",
        },
    )

    dc_transient_dur: float = Field(
        default=100.0,
        gt=0,
        description=r"Duration of transient DC input.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\Delta_\text{DC}$",
            "section": r"stimulus",
        },
    )

    dc_transient_amp: float = Field(
        default=0.3,
        description=r"Amplitude of transient DC input (final amplitude is population-specific and will be obtained by multiplication with 'K_CC_full').",
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
        ge=0,  # greater than or equal to 0
        description=r"Duration of presimulation (warmup).",
        json_schema_extra={
            "unit": "ms",
            "latex": r"t\_presim$",
            "section": r"simulation",
        },
    )

    t_sim: float = Field(
        default=1000.0,
        ge=0,
        description=r"Duration of (main) simulation.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"t\_sim$",
            "section": r"simulation",
        },
    )

    sim_resolution: float = Field(
        default=0.1,
        gt=0,  # greater than 0
        description=r"Simulation time resolution.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"sim\_resolution$",
            "section": r"simulation",
        },
    )

    rec_dev: tuple[Literal["spike_recorder", "voltmeter"], ...] = Field(
        # Literal rejects unsupported device names; the tuple is immutable so no shared-default risk.
        default=("spike_recorder",),
        description=r"List of recording devices ('spike_recorder' [default] and/or 'voltmeter'). "
        r"Nothing will be recorded if an empty list is given.",
        json_schema_extra={
            "unit": "",
            "latex": r"rec\_dev",
            "section": r"simulation",
        },
    )

    data_path: Path = Field(
        default=Path("data"),
        description=(
            "Path for storage of simulation data and metadata. "
            "Relative paths are resolved against the current working directory."
        ),
        json_schema_extra={
            "unit": "",
            "latex": r"data\_path",
            "section": r"simulation",
        },
    )

    rng_seed: int = Field(
        default=55,
        gt=0,
        description=(
            "Seed for NEST random number generator "
            "(used for connectivity, initial conditions, and Poissonian spike input)."
        ),
        json_schema_extra={
            "unit": "",
            "latex": r"rng\_seed",
            "section": r"simulation",
        },
    )

    local_num_threads: int = Field(
        default=4,
        ge=1,
        description=(
            "Number of threads per MPI process. "
            "Note: when up-scaling the network, "
            "the model may not run correctly if there are < 4 virtual processes "
            "(i.e, a thread in an MPI process)."
            " If there are 4 or more MPI processes, this value can be set to 1."
        ),
        json_schema_extra={
            "unit": "",
            "latex": r"local\_num\_threads",
            "section": r"simulation",
        },
    )

    rec_V_int: float = Field(
        default=1.0,
        gt=0,
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

    store_metadata: bool = Field(
        default=True,
        description=r"If 'True' (default), metadata (parameter values, node IDs, and software requirements) will be stored together with the simulation data. ",
        json_schema_extra={
            "unit": "",
            "latex": r"store\_metadata",
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
        return (
            np.round(self.N_scaling * np.array(self.full_num_neurons))
            .astype(int)
            .tolist()
        )

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
        ).tolist()

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
        return (
            np.round(np.array(self.full_num_synapses) * self.N_scaling * self.K_scaling)
            .astype(int)
            .tolist()
        )

    @computed_field(
        description=r"Number of cortico-cortical inputs per neuron (in-degree) for each cortical populations $y$; $K_{\mathcal{C}_x}=\alpha_K \tilde{K}_{\mathcal{C}_x}$",
        json_schema_extra={
            "unit": "",
            "latex": r"$K_{\mathcal{C}_x}",
            "section": r"network_derived",
        },
    )
    @property
    def K_CC(self) -> list:
        return np.round(np.array(self.K_CC_full) * self.K_scaling).astype(int).tolist()

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

    def _scaled_recurrent_weights_and_dc(self) -> tuple:
        """Base recurrent/external weights and DC input, jointly adjusted for
        K_scaling (see helpers.adjust_weights_and_input_to_synapse_scaling;
        a no-op when K_scaling == 1). Computes bases inline rather than via
        self.PSC_ext/self.DC_amp, since those properties return this method's
        *output* - reusing them here would recurse.
        """
        base_psc_matrix = np.array(self.PSP_matrix_mean) / self.J_unit
        base_psc_ext = self.weight_exc_mean / self.J_unit

        if self.CC_type == "poisson":
            base_dc_amp = np.zeros(self.num_pops)
        else:
            base_dc_amp = helpers.dc_input_compensating_poisson(
                self.rate_CC, np.array(self.K_CC_full), self.tau_syn, base_psc_ext
            )

        return helpers.adjust_weights_and_input_to_synapse_scaling(
            np.array(self.full_num_neurons),
            np.array(self.full_num_synapses),
            self.K_scaling,
            base_psc_matrix,
            base_psc_ext,
            self.tau_syn,
            np.array(self.full_mean_rates),
            base_dc_amp,
            self.CC_type,
            self.rate_CC,
            np.array(self.K_CC_full),
        )

    @computed_field(
        description=r"Matrix of mean PSC amplitudes for all pairs of presynaptic and postsynaptic cortical populations; $\bar{I}_{yx}=J_{yx}/J_\text{unit}$, adjusted for indegree scaling ($\alpha_K\neq 1$) to preserve the mean and variance of the recurrent input.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$\bar{I}_{yx}$",
            "section": r"synapse_derived",
        },
    )
    @property
    def PSC_matrix_mean(self) -> list:
        return self._scaled_recurrent_weights_and_dc()[0].tolist()

    @computed_field(
        description=r"Mean PSC amplitude of cortico-cortical inputs; $\bar{I}_\text{CC}=J/J_\text{unit}$, adjusted for indegree scaling ($\alpha_K\neq 1$).",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$\bar{I}_\text{CC}$",
            "section": r"synapse_derived",
        },
    )
    @property
    def PSC_ext(self) -> float:
        return float(self._scaled_recurrent_weights_and_dc()[1])

    @computed_field(
        description=r"DC input amplitude compensating for the potentially missing "
        r"cortico-cortical Poisson input, for each cortical population $x$; "
        r"$I_{DC,x}=0$ if $\mathcal{C}_\text{type}=\text{poisson}$, else "
        r"$I_{DC,x}=\nu_\mathcal{C}\,\tilde{K}_{\mathcal{C}_x}\,\bar{I}_\text{CC}\,\tau_\text{syn}\cdot 10^{-3}$, "
        r"adjusted for indegree scaling ($\alpha_K\neq 1$) to preserve the mean and variance of the input.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$I_{DC,x}$",
            "section": r"neuron_derived",
        },
    )
    @property
    def DC_amp(self) -> list:
        return self._scaled_recurrent_weights_and_dc()[2].tolist()

    @computed_field(
        description=r"Cortical populations whose (indegree-scaling-adjusted) DC input "
        r"amplitude falls below the rheobase current; always empty unless "
        r"$\mathcal{C}_\text{type}=\text{dc}$.",
        json_schema_extra={
            "unit": "",
            "latex": r"\{x : I_{DC,x} < I_\text{rh}\}",
            "section": r"neuron_derived",
        },
    )
    @property
    def subthreshold_populations(self) -> list:
        if self.CC_type != "dc":
            return []
        I_rh = helpers.compute_rheo_base_current(
            self.V_th, self.V_rest, self.C_m, self.tau_m
        )
        dc_amp = self._scaled_recurrent_weights_and_dc()[2]
        return [pop for pop, dc in zip(self.populations, dc_amp) if dc < I_rh]

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
        description=r"Matrix containing mean synaptic weights (PSP amplitudes) for all pairs "
        r"of presynaptic and postsynaptic populations. The L4E$\to$L2/3E connection "
        r"($[0,2]$) is doubled relative to the other excitatory connections.",
        json_schema_extra={
            "unit": "mV",
            "latex": r"$J_{yx}$ ($\forall y,x\in\mathcal{P}$)",
            "section": r"synapse_derived",
        },
    )
    @property
    def PSP_matrix_mean(self) -> list:
        matrix = helpers.get_exc_inh_matrix(
            self.weight_exc_mean, self.weight_exc_mean * self.g, len(self.populations)
        )
        matrix[0, 2] = 2.0 * self.weight_exc_mean
        return matrix.tolist()

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
        ).tolist()

    ###################################
    ## derived stimulus parameters
    @computed_field(
        description=r"Number of thalamocortical synapses onto each cortical population $x$; "
        r"$Q_{x,\text{th}}=\alpha_K \tilde{Q}_{x,\text{th}}$.",
        json_schema_extra={
            "unit": "",
            "latex": r"$Q_{x,\text{th}}$",
            "section": r"stimulus_derived",
        },
    )
    @property
    def num_th_synapses(self) -> list:
        num_th_synapses = helpers.num_synapses_from_conn_probs(
            self.conn_probs_th, self.num_th_neurons, self.full_num_neurons
        )[0]
        if self.K_scaling != 1:
            num_th_synapses = num_th_synapses * self.K_scaling
        return np.round(num_th_synapses).astype(int).tolist()

    @computed_field(
        description=r"Mean PSC amplitude of thalamocortical inputs; "
        r"$\bar{I}_\text{th}=\bar{I}_\text{CC}/\sqrt{\alpha_K}$.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$\bar{I}_\text{th}$",
            "section": r"stimulus_derived",
        },
    )
    @property
    def weight_th(self) -> float:
        # Not `self.PSC_ext`: that will carry the joint K-scaling adjustment
        # (adjust_weights_and_input_to_synapse_scaling) once ported, while
        # thalamic input scales only by 1/sqrt(K_scaling).
        weight_th = self.weight_exc_mean / self.J_unit
        if self.K_scaling != 1:
            weight_th /= np.sqrt(self.K_scaling)
        return float(weight_th)

    @computed_field(
        description=r"Mean spike transmission delay of thalamocortical inputs; "
        r"tied to `delay_exc_mean` (same convention as `weight_th`/`weight_exc_mean`).",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$\bar{d}_\text{th}$",
            "section": r"stimulus_derived",
        },
    )
    @property
    def delay_th_mean(self) -> float:
        return self.delay_exc_mean

    @computed_field(
        description=r"Mean current generated by a single cortico-cortical "
        r"input spike train with rate $\nu_\mathcal{C}$, convolved with an "
        r"exponential kernel of amplitude $\bar{I}_\text{CC}$ and time "
        r"constant $\tau_\text{syn}$;"
        r"$I_\text{CC}=\bar{I}_\text{CC}\,\tau_\text{syn}\,\nu_\mathcal{C}\cdot 10^{-3}$. "
        r"Always computed at full (unscaled) amplitude, independent of "
        r"$\mathcal{C}_\text{type}$ or indegree scaling.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$I_\text{CC}$",
            "section": r"neuron_derived",
        },
    )
    @property
    def I_CC(self) -> float:
        # Deliberately not scaled by 1/sqrt(K_scaling), unlike `weight_th`
        # (same root: weight_exc_mean / J_unit). I_CC represents the
        # unscaled, full-network cortico-cortical input current and must
        # stay independent of K_scaling by design.
        return float(
            helpers.dc_input_compensating_poisson(
                self.rate_CC, 1.0, self.tau_syn, self.weight_exc_mean / self.J_unit
            )
        )

    @computed_field(
        description=r"Mean total current generated by cortico-cortical inputs "
        r"onto each cortical population $x$; "
        r"$I_{\mathcal{C}_x}=\tilde{K}_{\mathcal{C}_x}\,I_\text{CC}$. "
        r"Always computed at full (unscaled) amplitude, independent of "
        r"$\mathcal{C}_\text{type}$ or indegree scaling.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$I_{\mathcal{C}_x}$",
            "section": r"neuron_derived",
        },
    )
    @property
    def I_CC_populations(self) -> list:
        return (np.array(self.K_CC_full) * self.I_CC).tolist()

    @computed_field(
        description=r"Stop time of thalamic input; "
        r"$t_\text{stop}^\text{TC}=t_\text{start}+\Delta_\text{TC}$.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$t_\text{stop}^\text{TC}$",
            "section": r"stimulus_derived",
        },
    )
    @property
    def th_stop(self) -> float:
        return self.th_start + self.th_duration

    @computed_field(
        description=r"Stop time of transient DC input; "
        r"$t_\text{stop}^\text{DC}=t_\text{start}^\text{DC}+\Delta_\text{DC}$.",
        json_schema_extra={
            "unit": "ms",
            "latex": r"$t_\text{stop}^\text{DC}$",
            "section": r"stimulus_derived",
        },
    )
    @property
    def dc_transient_stop(self) -> float:
        return self.dc_transient_start + self.dc_transient_dur

    @computed_field(
        description=r"Population-specific amplitude of transient DC input onto "
        r"each cortical population $x$; $I_{DC,x}^\text{transient}=A_\text{DC}\,\tilde{K}_{\mathcal{C}_x}$.",
        json_schema_extra={
            "unit": "pA",
            "latex": r"$I_{DC,x}^\text{transient}$",
            "section": r"stimulus_derived",
        },
    )
    @property
    def dc_transient_amp_populations(self) -> list:
        return (np.array(self.K_CC_full) * self.dc_transient_amp).tolist()

    #########################################################################
    # def model_post_init(self):
    #     assert self.J>0

    #########################################################################
    @classmethod
    def from_yaml(cls, filename: "str | os.PathLike", **overrides) -> "Parameters":
        """
        Constructs a Parameters instance from class defaults, overlaid with the
        values in a YAML file, overlaid with keyword overrides.

        The YAML file only needs to contain the parameters that should differ
        from the defaults (see `generate_example_config()` for a template).
        Keyword overrides are meant for per-job values that do not belong in
        a shared experiment file, e.g. `rng_seed` or `data_path`.

        The result is validated as a whole: if any value is invalid, no
        instance is created.

        Parameters:
        -----------

        filename: str or path-like
            Path to the YAML file. An empty file (or one with only comments)
            is valid and yields the defaults.

        **overrides
            Parameter values applied on top of the file contents.

        Returns:
        --------

        Parameters
            A new, validated instance.

        """

        with open(filename, "r") as yaml_file:
            loaded = YAML(typ="safe").load(yaml_file)

        # A file with no active (uncommented) entries parses as None; that is a
        # valid override file meaning "all defaults".
        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            raise TypeError(
                f"{filename}: expected a YAML mapping of parameter names to values, "
                f"got {type(loaded).__name__}."
            )

        return cls.model_validate({**loaded, **overrides})

    def print(self) -> None:
        rich.print(self)
        # rich.print(dict(self))
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
    Generates a YAML template listing all primary parameters defined in the
    Parameters class. Every parameter is written as a commented-out line
    showing its default value, followed by its metadata (description, unit,
    LaTeX symbol, and section) as comments. The parameters are listed in the
    order they are defined in the Parameters class.

    The template is meant as a sparse override file: the user uncomments and
    edits only the parameters that should differ from the defaults. Every
    parameter not present in the file takes its default value from the
    Parameters class when the file is loaded with `load_parameters_from_yaml()`.
    The class therefore remains the single source of truth for default values.

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
        yaml_file.write("#\n")
        yaml_file.write(
            "# Uncomment and edit only the parameters you want to change.\n"
        )
        yaml_file.write(
            "# Every parameter that stays commented out takes its default value\n"
        )
        yaml_file.write("# from the Parameters class (parameter_definitions.py).\n")
        yaml_file.write("# The values shown here are those defaults.\n")
        yaml_file.write("#\n")
        yaml_file.write(
            "# To modify defaults or metadata (descriptions, units, LaTeX symbols),\n"
        )
        yaml_file.write(
            "# edit the parameter definitions in parameter_definitions.py\n"
        )
        yaml_file.write("# and run generate_example_config() again.\n")
        yaml_file.write("\n")

        for key in schema["properties"].keys():
            field = schema["properties"][key]

            if "default" in field:
                yaml_file.write(f"# {key}: {field['default']}\n")
            else:
                yaml_file.write(f"# {key}: This is a derived parameter and cannot be set.\n")

            yaml_file.write(f"# {field['description']}\n")
            yaml_file.write(f"# unit: {field['unit']}\n")
            yaml_file.write(f"# LaTeX: {field['latex']}\n")
            yaml_file.write(f"# section: {field['section']}\n")
            yaml_file.write("\n")


#########################################################################

def load_parameters_from_yaml(filename) -> Parameters:
    """
    Loads parameters from a YAML file and validates them against the Parameters
    class. Thin wrapper around `Parameters.from_yaml()`, kept for backwards
    compatibility.

    """

    return Parameters.from_yaml(filename)


def example_params_file() -> Path:
    """
    Returns the path of the small parameter override file shipped with the
    package (`example_params.yaml`). It scales the network down so that the
    bundled entry points (`microcircuit run`, the reference data generator)
    never run the full-scale model by accident.

    """

    return Path(str(files("microcircuit") / "example_params.yaml"))


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

    assert params == test_params, (
        "Validation failed: Loaded parameters do not match the original defaults."
    )


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
