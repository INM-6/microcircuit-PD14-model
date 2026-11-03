# -*- coding: utf-8 -*-
#
# analyze_reference_data.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

#####################
"""
Analyze reference data generated with generate_reference_data.py.
"""

import time
import nest
import numpy as np
import json
from scipy.stats import ks_2samp as ks
import random

## import model implementation
from microcircuit import helpers

## import parameter class
from microcircuit.parameter_definitions import Parameters

from pathlib import Path
from argparse import ArgumentParser
from ruamel.yaml import YAML

parser = ArgumentParser()
parser.add_argument("--seed", type=int, default=12345)
parser.add_argument("--path", type=str, default="data")
args = parser.parse_args()

## load model parameters and analysis settings
params = Parameters.from_yaml(
    Path(__file__).parent / "model_params.yaml", data_path=Path(args.path), rng_seed=args.seed
)
ref_dict = YAML(typ="safe").load(Path(__file__).parent / "reference_params.yaml")

#####################
populations = params.populations  # list of populations
#####################

random.seed(ref_dict["analysis"]["seed_subsampling"])  # set seed for reproducibility

####################################################################################################
#                       Define auxiliary functions to analyze and plot data                        #
####################################################################################################


def analyze_single_neuron_stats(observable_name: str, func: callable) -> dict:
    """
    Analyze single neuron statistics such as time avaraged firing rates and ISI CVs.
    --------------------------------------------------------------------------------
    Parameters:
    - observable_name : str
        Name of the observable to be analyzed and stored. Name will be used to store the observable
        as json file and used in further analysis.
    - func : function
        Function to compute the single neuron statistic. Are part
        of the microcircuit package and can be find in helpers.py.
        - 'helpers.time_averaged_single_neuron_firing_rates': computes time averaged firing rates
          per neuron
        - 'helpers.single_neuron_isi_cvs': computes interval spike irregularity as count variance
          per neuron
    --------------------------------------------------------------------------------
    Returns:
    - observable : dict
        Dictionary containing the single neuron statistic for all populations.
    """

    observable = {}  # list of single neuron observable [pop][neuron]
    recording_interval = (
        max(ref_dict["analysis"]["t_min"], params.t_presim),
        params.t_presim + params.t_sim,
    )

    data_path = Path(params.data_path)
    nodes = helpers.json2dict(data_path / "nodes.json")

    for pop in populations:
        observable[pop] = {}

        # label of spike recorder device
        label = f"spike_recorder-{nodes[f'spike_recorder_{pop}'][0]}"
        spikes = helpers.load_spike_data(data_path, label)  # load spike data for population
        # compute single neuron statistic
        observable[pop] = list(func(spikes, nodes[pop], recording_interval))

    # store observable as json file
    helpers.dict2json(observable, data_path / f"{observable_name}.json")

    return observable


def analyze_pairwise_stats(observable_name: str, func: callable) -> dict:
    """
    Analyze pairwise statistics such as spike count correlations.
    -------------------------------------------------------------
    Parameters:
    - observable_name : str
        Name of the observable to be analyzed and stored. Name will be used to store the observable
        as json file and used in further analysis.
    - func : function
        Function to compute the pairwise statistic. Are part of
        the microcircuit package and can be find in helpers.py.
        - 'helpers.pairwise_spike_count_correlations': computes pairwise spike count correlations
          for a subsample of neurons of each population.
    -------------------------------------------------------------
    Returns:
    - observable : dict
        Dictionary containing the pairwise statistic for all populations.
    """

    recording_interval = (
        max(ref_dict["analysis"]["t_min"], params.t_presim),
        params.t_presim + params.t_sim,
    )

    # cc_binsize = 2. # in ms
    observable = {}  # list of pairwise spike count correlations [pop][correlation]

    data_path = Path(params.data_path)
    nodes = helpers.json2dict(data_path / "nodes.json")

    for pop in populations:
        observable[pop] = {}

        pop_nodes = nodes[pop]  # list of neuron nodes for the population
        # label of spike recorder device
        label = f"spike_recorder-{nodes[f'spike_recorder_{pop}'][0]}"
        spikes = helpers.load_spike_data(data_path, label)  # load spike data for population

        # Generate random subsample of neuron nodes for the population for pairwise analysis
        # (without replacement)
        selected_nodes = random.sample(pop_nodes, ref_dict["analysis"]["subsample_size"])

        # compute pairwise statistic
        observable[pop] = list(
            func(spikes, selected_nodes, recording_interval, ref_dict["analysis"]["binsize"])
        )

    # store observable as json file
    helpers.dict2json(observable, data_path / f"{observable_name}.json")

    return observable


def main():

    # compute and store time averaged firing rates
    analyze_single_neuron_stats("rates", helpers.time_averaged_single_neuron_firing_rates)
    # compute and store single neuron ISI CVs
    analyze_single_neuron_stats("spike_cvs", helpers.single_neuron_isi_cvs)
    # compute and store pairwise spike count correlations
    analyze_pairwise_stats("spike_ccs", helpers.pairwise_spike_count_correlations)

    ## current memory consumption of the python process (in MB)
    import psutil

    mem = psutil.Process().memory_info().rss / (1024 * 1024)
    print(f"Current memory consumption: {mem:.2f} MB")


if __name__ == "__main__":
    main()
