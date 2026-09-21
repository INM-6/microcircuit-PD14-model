# -*- coding: utf-8 -*-
#
# generate_reference_data.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

'''
Generation of reference data for the microcircuit model.
'''

#####################
import time
import nest
import numpy as np

## import model implementation
from microcircuit.model import Model

## import parameter class
from microcircuit.parameter_definitions import Parameters

## import analysis parameters
from params import params as ref_dict

from pathlib import Path
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--seed", type=int, default=12345)
parser.add_argument("--path", type=str, default="data")
args = parser.parse_args()

path = Path(args.path)
P = Parameters()
P.data_path = str(path) + "/"
P.rng_seed = args.seed

#####################

## set network scale
scaling_factor = ref_dict['scaling_factor']
P.N_scaling = scaling_factor
P.K_scaling = scaling_factor

## set pre-simulation time to 0 and desired simulation time
P.t_presim = ref_dict["t_presim"]
P.t_sim = ref_dict["t_sim"] # simulate for 10.0s

## set number of local number of threads
P.local_num_threads = ref_dict['local_num_threads']

def main():

    ## start timer 
    time_start = time.time()

    ## create instance of the model
    model = Model(P)
    time_network = time.time()

    ## create all nodes (neurons, devices)
    model.create()
    time_create = time.time()

    ## connect nework
    model.connect()
    time_connect = time.time()

    ## pre-simulation (warm-up phase)
    model.simulate(P.t_presim)
    time_presimulate = time.time()

    ## simulation
    model.simulate(P.t_sim)
    time_simulate = time.time()

    ## current memory consumption of the python process (in MB)
    import psutil
    mem = psutil.Process().memory_info().rss / (1024 * 1024)
    #TODO store benchmark data in store_metadata
    #net.benchmark_data = {}
    #net.benchmark_data['memory'] = mem

    #####################
    ## plot spikes and firing rate distribution
    print()
    print('##########################################')
    print()
    observation_interval = np.array([P.t_presim, P.t_presim + P.t_sim])
    model.evaluate(observation_interval , observation_interval )
    print()
    print('Raster plot                  : see %s ' % (P.data_path / 'raster_plot.png') )
    print('Distributions of firing rates: see %s ' % (P.data_path / 'box_plot.png'   ) )
    time_evaluate = time.time()

    #####################
    ## print timers and memory consumption

    print()
    print('##########################################')
    print()
    print('Times of Rank %d:' % nest.Rank())
    print('    Total time:')
    print('    Time to initialize  : %.3fs' % (time_network - time_start))
    print('    Time to create      : %.3fs' % (time_create - time_network))
    print('    Time to connect     : %.3fs' % (time_connect - time_create))
    print('    Time to presimulate : %.3fs' % (time_presimulate - time_connect))
    print('    Time to simulate    : %.3fs' % (time_simulate - time_presimulate))
    print('    Time to evaluate    : %.3fs' % (time_evaluate - time_simulate))
    print()
    print("Memory consumption: %dMB" % mem)
    print()
    print('##########################################')
    print()

    model.store_metadata()
    
#####################

if __name__== '__main__':
    main()
