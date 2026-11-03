#!/usr/bin/env python
# encoding: utf8
# -*- coding: utf-8 -*-
#
# __main__.py
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
PyNEST implementation of the cortical microcircuit model of Potjans & Diesmann (2014).

Usage: microcircuit [options] run
       microcircuit [options] show_config

Options:
    -p FILE, --params FILE  YAML file with parameter overrides. Parameters not
                            listed in the file take their defaults from the
                            Parameters class. Without this option the small
                            override file shipped with the package is used,
                            which scales the network down to 20 %.
    -v, --verbose           increase output
    -h, --help              print this text
"""

import logging
import time

import pprint
from pprint import pformat
from docopt import docopt  # type: ignore

import nest
import numpy as np

from microcircuit.model import Model
from microcircuit.parameter_definitions import Parameters, example_params_file

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def run_example(params):
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

    print(
        f"\nTimes of Rank {nest.Rank()}:\n"
        f"  Total time:          {time_evaluate - time_start:.3f} s\n"
        f"  Time to initialize:  {time_network - time_start:.3f} s\n"
        f"  Time to create:      {time_create - time_network:.3f} s\n"
        f"  Time to connect:     {time_connect - time_create:.3f} s\n"
        f"  Time to presimulate: {time_presimulate - time_connect:.3f} s\n"
        f"  Time to simulate:    {time_simulate - time_presimulate:.3f} s\n"
        f"  Time to evaluate:    {time_evaluate - time_simulate:.3f} s\n"
    )

    model.store_metadata()


def main():
    "Start main CLI entry point."

    args = docopt(__doc__)
    if args["--verbose"]:
        log.setLevel(logging.DEBUG)
    log.debug(pformat(args))

    params_file = args["--params"] or example_params_file()
    log.info("Reading parameter overrides from %s", params_file)
    params = Parameters.from_yaml(params_file)

    if args["run"]:
        run_example(params)

    if args["show_config"]:
        print()
        print("Model parameters:")
        print("-----------------")
        pprint.pprint(params.model_dump())
        print()


if __name__ == "__main__":
    main()
