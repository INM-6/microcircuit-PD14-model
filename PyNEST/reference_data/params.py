# -*- coding: utf-8 -*-
#
# params.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

#####################
"""
Parameters for generation and analysis of reference data.
"""

params = {
    #########################
    # Adapted model and simulation parameters
    #########################
    # scaling factor of the network
    "scaling_factor": 0.2,
    #'scaling_factor': 1.0,
    # RNG seeds for generating model relizations
    #'RNG_seeds': ['12345' + str(i) for i in range(0, 10)],
    "RNG_seeds": ["12345" + str(i) for i in range(0, 5)],
    # pre-simulation time (for network stabilization) in ms
    "t_presim": 500.0,
    # simulation time in ms
    "t_sim": 1e3,
    #'t_sim': 1.0e+4,
    #'t_sim': 9.0e+5,
    # local number of threads
    #'local_num_threads': 64,
    "local_num_threads": 4,
    # data path
    "data_path": "data",
    ##
    #########################
    # analysis parameters
    #########################
    # start of analysis time interval in ms
    "t_min": 500.0,
    # RNG seed for random neuron subsampling (for CC anlysis)
    "seed_subsampling": 12345,
    # number of neurons per population for pairwise statistics
    #'subsample_size': 250,
    "subsample_size": 50,
    # bin size for generation of spike-count signals (for CC analysis)
    "binsize": 2.0,
    ##
    #########################
    # plotting parameters
    #########################
    # limits for rate, CV, and CC histograms
    "cc_lim": [-0.015, 0.015],
    "rate_lim": [0.0, 20.0],
    "cv_lim": [0.5, 1.5],
    # binsizes for histograms
    "cc_binsize": 0.001,
    "rate_binsize": 1.0,
    "cv_binsize": 0.05,
    # maximal figure width in inches
    "max_fig_width": 7.5,
}
