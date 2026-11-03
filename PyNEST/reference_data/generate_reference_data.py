# -*- coding: utf-8 -*-
#
# generate_reference_data.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Generation of reference data for the microcircuit model.
"""

#####################
import time
import nest
import numpy as np

## import model implementation
from microcircuit.model import Model

## import parameter class
from microcircuit.parameter_definitions import Parameters

from pathlib import Path
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--seed", type=int, default=12345)
parser.add_argument("--path", type=str, default="data")
args = parser.parse_args()

## load model parameters (network scale, simulation times, threads) and set the
## seed and data path of this network realization
params = Parameters.from_yaml(
    Path(__file__).parent / "model_params.yaml", data_path=Path(args.path), rng_seed=args.seed
)


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

    ## current memory consumption of the python process (in MB)
    import psutil

    mem = psutil.Process().memory_info().rss / (1024 * 1024)
    # TODO store benchmark data in store_metadata
    # net.benchmark_data = {}
    # net.benchmark_data['memory'] = mem

    #####################
    ## plot spikes and firing rate distribution
    print()
    print("##########################################")
    print()
    observation_interval = np.array([params.t_presim, params.t_presim + params.t_sim])
    model.evaluate(observation_interval, observation_interval)
    print()
    print(f'Raster plot                  : see {params.data_path / "raster_plot.png"} ')
    print(f'Distributions of firing rates: see {params.data_path / "box_plot.png"} ')
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

    model.store_metadata()


#####################

if __name__ == "__main__":
    main()
