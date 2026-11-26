# -*- coding: utf-8 -*-
#
# simulation.py
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
Complete simulation run of the microcircuit: build, simulate, evaluate, store metadata.

Shared by the command line interface (`microcircuit run`), `examples/run_microcircuit.py`,
and user scripts (`microcircuit.run("params.yaml")`).
"""

import os
import time

import nest
import numpy as np

from microcircuit.model import Model
from microcircuit.parameter_definitions import Parameters


def run(params: "Parameters | str | os.PathLike") -> dict:
    """
    Builds, simulates and evaluates the microcircuit, stores the metadata, and prints the timers.

    Parameters:
    -----------

    params: Parameters, str or path-like
        A `Parameters` instance, or the path of a YAML file with parameter overrides
        (see `Parameters.from_yaml()`).

    Returns:
    --------

    dict
        Wall-clock times of the phases of this rank in s (`initialize`, `create`, `connect`,
        `presimulate`, `simulate`, `evaluate`, `total`).
    """

    if not isinstance(params, Parameters):
        params = Parameters.from_yaml(params)

    time_start = time.time()
    model = Model(params)

    ###############################################################################
    # Initialize the network with simulation, network and stimulation parameters,
    # then create and connect all nodes, and finally simulate.
    # The times for a presimulation and the main simulation are taken
    # independently. A presimulation is useful because the spike activity typically
    # exhibits a startup transient. In benchmark simulations, this transient should
    # be excluded from a time measurement of the state propagation phase. Besides,
    # statistical measures of the spike activity should only be computed after the
    # transient has passed.

    time_network = time.time()

    model.create_nodes()
    time_create = time.time()

    model.connect()
    time_connect = time.time()

    model.simulate(params.t_presim)
    time_presimulate = time.time()

    model.simulate(params.t_sim)
    time_simulate = time.time()

    ###############################################################################
    # Plot a spike raster of the simulated neurons and a box plot of the firing
    # rates for each population.
    # For visual purposes only, spikes 100 ms before and 100 ms after the thalamic
    # stimulus time are plotted here by default. If the simulation ends before that
    # window, the last 200 ms of the simulation are plotted instead.
    # The computation of spike rates discards the presimulation time to exclude
    # initialization artifacts.

    t_end = params.t_presim + params.t_sim
    raster_plot_interval = np.array(
        [max(0.0, min(params.th_start - 100.0, t_end - 200.0)), min(params.th_start + 100.0, t_end)]
    )
    firing_rates_interval = np.array([params.t_presim, params.t_presim + params.t_sim])
    model.evaluate(raster_plot_interval, firing_rates_interval)
    time_evaluate = time.time()

    ###############################################################################
    # Summarize time measurements. Rank 0 usually takes longest because of the
    # data evaluation and print calls.

    timers = {
        "initialize": time_network - time_start,
        "create": time_create - time_network,
        "connect": time_connect - time_create,
        "presimulate": time_presimulate - time_connect,
        "simulate": time_simulate - time_presimulate,
        "evaluate": time_evaluate - time_simulate,
        "total": time_evaluate - time_start,
    }

    print(
        f"\nTimes of Rank {nest.Rank()}:\n"
        f"  Total time:          {timers['total']:.3f} s\n"
        f"  Time to initialize:  {timers['initialize']:.3f} s\n"
        f"  Time to create:      {timers['create']:.3f} s\n"
        f"  Time to connect:     {timers['connect']:.3f} s\n"
        f"  Time to presimulate: {timers['presimulate']:.3f} s\n"
        f"  Time to simulate:    {timers['simulate']:.3f} s\n"
        f"  Time to evaluate:    {timers['evaluate']:.3f} s\n"
    )

    model.store_metadata()

    return timers
