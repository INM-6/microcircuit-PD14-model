# -*- coding: utf-8 -*-
#
# run_microcircuit.py
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
Microcircuit example (Potjans & Diesmann 2014)
----------------------------------------------

Example illustrating usage of the `microcircuit` python package.
"""

#####################
import sys
import time
from pathlib import Path

import nest
import numpy as np

from microcircuit.model import Model

## import parameter definitions
from microcircuit.parameter_definitions import Parameters

#####################

## Parameters are read from a YAML override file: everything not listed there
## takes its default from the Parameters class. By default the `params.yaml`
## next to this script is used (it scales the network down to 20 %); an
## alternative file can be passed as the first command line argument:
##
##     python run_microcircuit.py my_params.yaml

params_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "params.yaml"
params = Parameters.from_yaml(params_file)


def main():
    ## start timer
    time_start = time.time()

    ## create instance of the model
    model = Model(params)

    time_network = time.time()

    ## create all nodes (neurons, devices)
    model.create_nodes()
    time_create = time.time()

    ## connect nework
    model.connect()
    time_connect = time.time()

    ## pre-simulation (warm-up phase)
    model.simulate(params.t_presim)
    time_presimulate = time.time()

    ## simulation
    model.simulate(params.t_sim)
    time_simulate = time.time()

    ## store metadata
    model.store_metadata()

    ## current memory consumption of the python process (in MB)
    import psutil

    mem = psutil.Process().memory_info().rss / (1024 * 1024)

    #####################
    ## plot spikes and firing rate distribution
    print()
    print("##########################################")
    print()
    observation_interval = np.array([params.t_presim, params.t_presim + params.t_sim])
    model.evaluate(observation_interval, observation_interval)
    print()
    print(f"Raster plot                  : see {params.data_path / 'raster_plot.png'} ")
    print(f"Distributions of firing rates: see {params.data_path / 'box_plot.png'} ")
    time_evaluate = time.time()

    #####################
    ## print timers and memory consumption

    print()
    print("##########################################")
    print()
    print(f"Times of Rank {nest.Rank()}:")
    print("    Total time:")
    print(f"    Time to initialize  : {time_network - time_start:.3f}s")
    print(f"    Time to create      : {time_create - time_network:.3f}s")
    print(f"    Time to connect     : {time_connect - time_create:.3f}s")
    print(f"    Time to presimulate : {time_presimulate - time_connect:.3f}s")
    print(f"    Time to simulate    : {time_simulate - time_presimulate:.3f}s")
    print(f"    Time to evaluate    : {time_evaluate - time_simulate:.3f}s")
    print()
    print(f"Memory consumption: {int(mem)}MB")
    print()
    print("##########################################")
    print()


#####################

if __name__ == "__main__":
    main()
