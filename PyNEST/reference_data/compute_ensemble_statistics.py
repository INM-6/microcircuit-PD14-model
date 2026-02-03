# -*- coding: utf-8 -*-
#
# compute_ensemble_statistics.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

#####################

'''
Compute spike statistics across the ensemble of network realizations (RNG seeds)
from the single-realization analysis performed with analyze_reference_data.py.
'''

import time
import nest
import numpy as np
import json
from scipy.stats import ks_2samp as ks
import random

## import model implementation
from microcircuit import network
from microcircuit import helpers

## import (default) parameters (network, simulation, stimulus)
from microcircuit.network_params import default_net_dict as net_dict
from microcircuit.sim_params import default_sim_dict as sim_dict
from microcircuit.stimulus_params import default_stim_dict as stim_dict

## import analysis parameters
from params import params as ref_dict

#####################
populations = net_dict['populations'] # list of populations
#####################

## set network scale
scaling_factor = ref_dict['scaling_factor']
net_dict["N_scaling"] = scaling_factor
net_dict["K_scaling"] = scaling_factor

random.seed( ref_dict['seed_subsampling'] )  # set seed for reproducibility

seeds = ref_dict['RNG_seeds'] # list of seeds

sim_dict['data_path'] = ref_dict['data_path'] + '/data_T' + str( int( ref_dict['t_sim'] * 1.0e-3 ) ) + 's/'

#######################################################
# Define auxiliary functions to analyze and plot data #
#######################################################
def concatenate_data( observable_name: str ) -> dict:
    '''
    Concatenate data across different seeds.
    ----------------------------------------
    Parameters:
    - observable_name: str
        Name of the observable to concatenate (e.g., 'rates', 'spike_cvs', 'spike_ccs').
        Needs to match the filename used to store the data per seed in 'analyze_reference_data.py'.
    -----------------------------------------
    Returns:
    - observable: dict
        Dictionary containing the concatenated data across seeds.
    '''

    observable = {}

    for cseed, seed in enumerate( seeds ):
        observable[cseed] = {}
        data_path = sim_dict['data_path'] + 'seed-%s/' % seed

        data_per_seed = helpers.json2dict( f'{data_path}{observable_name}.json' ) # load data per seed as dictionary sorted by populations

        observable[cseed] = data_per_seed # concatenate data

    helpers.dict2json( observable, sim_dict['data_path'] + f'{observable_name}.json' ) # store concatenated data as json file

    return observable

def compute_ks_distances( observable: dict, observable_name: str ) -> dict:
    '''
    Compute Kolmogorov-Smirnov distances between distributions of an observable across different seeds.
    ---------------------------------------------------------------------------------------------------
    Parameters:
    - observable: dict
        Dictionary containing the concatenated data across seeds.
    - observable_name: str
        Name of the observable to compute KS distances for (e.g., 'rate', 'spike_cvs', 'spike_ccs').
    ---------------------------------------------------------------------------------------------------
    Returns:
    - observable_ks_distances: dict
        Dictionary containing the KS distances between distributions of the observable across different seeds.
    '''

    observable_ks_distances = {} # list of ks distances [pop][seed][ks_distance to other seed]
    for cpop, pop in enumerate( populations ):
        observable_ks_distances[pop] = {
            "seeds": {},    # values across seeds
            "list": []      # to compute mean and std
        }

        for cseed, seed in enumerate( seeds ):
            observable[cseed][pop] = np.delete( observable[cseed][pop], np.where( np.isnan( observable[cseed][pop] ) ) ) # clean data: remove NaNs

        n_seeds = len( seeds )

        for i in range( n_seeds ):
            observable_ks_distances[pop]["seeds"][i] = {}
            for j in range( i+1, n_seeds ):
                observable_ks_distance = ks( observable[i][pop], observable[j][pop] )[0].tolist()
                observable_ks_distances[pop]["seeds"][i][j] = observable_ks_distance
                observable_ks_distances[pop]["list"].append( observable_ks_distance )

    helpers.dict2json( observable_ks_distances, sim_dict['data_path'] + f'{observable_name}_ks_distances.json' ) # save ks distances as json file

    return observable_ks_distances

def main():
    rates = concatenate_data( 'rates' )
    spike_cvs = concatenate_data( 'spike_cvs' )
    spike_ccs = concatenate_data( 'spike_ccs' )

    compute_ks_distances( rates, 'rate' )
    compute_ks_distances( spike_cvs, 'spike_cvs' )
    compute_ks_distances( spike_ccs, 'spike_ccs' )

    ## current memory consumption of the python process (in MB)
    import psutil
    mem = psutil.Process().memory_info().rss / ( 1024 * 1024 )
    print( f"Current memory consumption: {mem:.2f} MB" )

if __name__ == "__main__":
    main()
