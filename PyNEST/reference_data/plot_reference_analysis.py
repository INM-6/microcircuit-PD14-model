# -*- coding: utf-8 -*-
#
# plot_reference_analysis.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

#####################
'''
Compute and plot ensemble statistics across seeds from reference data generated with generate_reference_data.py.
'''

import time
import nest
import numpy as np
import json
from scipy.stats import ks_2samp as ks
import matplotlib.pyplot as plt
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

sim_dict['data_path'] = ref_dict['data_path'] + '/data_T' + str( int( ref_dict['t_sim'] * 1.0e-3 ) ) + 's/'


## set path for storing spike data and figures
### TODO revise data path
#sim_dict['data_path'] = '../examples/data_scale_%.2f/' % scaling_factor
seeds = ref_dict['RNG_seeds'] # list of seeds

########################################################################################################################
#                                   Define auxiliary functions to plot data                                            #
########################################################################################################################

def compute_data_dist( observable: dict, observable_name: str, observable_limits: tuple[float, float] = None, units: str='', bin_size: float=None ) -> tuple[dict, dict, dict]:
    '''
    Compute histograms and statistics for given observable for each population across all seeds.
    --------------------------------------------------------------------------------------------
    Parameters:
    - observable: dict
        Dictionary containing the concatenated observable data over seeds for each population.
    - observable_name: str
        Name of the observable to analyze (e.g., 'rates', 'spike_cvs', 'spike_ccs').
        Needs to match the filename used to store the data per seed in 'analyze_reference_data.py'.
    - observable_limits: tuple[float, float]
        Tuple specifying the (min, max) limits for the observable histograms.
    - units: str
        Units of the observable (for labeling purposes).
    - bin_size: float
        Bin size for the histograms. If None, the best bin size is computed from the data.
    --------------------------------------------------------------------------------------------
    Returns: (observable_hist_mat, observable_best_bins, observable_stats)
    - observable_hist_mat: dict
        Dictionary containing the histograms for each population across all seeds.
    - observable_best_bins: dict
        Dictionary containing the best binning for each population.
    - observable_stats: dict
        Dictionary containing the statistics for each population across all seeds.
    '''

    # compute the best binning for each histogram
    if bin_size is None:
        binsizes = np.zeros( ( len( seeds ), len( populations ) ) )
        min_bin_vals = np.zeros( ( len( seeds ), len( populations ) ) )
        max_bin_vals = np.zeros( ( len( seeds ), len( populations ) ) )
        for cseed, seed in enumerate( seeds ):
            cseed_str = str( cseed )
            for cpop, pop in enumerate( populations ):
                _, bins, _ = helpers.data_distribution( np.array( observable[cseed_str][pop] ), pop, f'{units}' ) # calculate histogram for each population across seeds
                min_bin_vals[cseed][cpop] = np.min( bins ).tolist() # store min bin values for each seed and population
                max_bin_vals[cseed][cpop] = np.max( bins ).tolist() # store max bin value for each seed and population
                binsizes[cseed][cpop] = np.diff( bins )[0] # store all bin sizes

        min_binsizes = np.min( binsizes, axis=0 ) # get min bin size across seeds for each population
        min_min_bin_vals = np.min( min_bin_vals, axis=0 ) # get min of min bin value across seeds for each population
        max_max_bin_vals = np.max( max_bin_vals, axis=0 ) # get max of max bin value across seeds for each population

        binsize = np.min( min_binsizes ) # use min of min bin sizes across populations as bin size
        min_min_min_bin_val = np.min( min_min_bin_vals ) # use min of min bin values across populations as min bin value
        max_max_max_bin_val = np.max( max_max_bin_vals ) # use max of max bin values across populations as max bin value

        min_range = observable_limits[0] if observable_limits is not None else min_min_min_bin_val.tolist() # get min range (can either be given or from data)
        max_range = observable_limits[1] if observable_limits is not None else max_max_max_bin_val.tolist() # get max range (can either be given or from data)
        min_width = min_binsizes[cpop].tolist() # get min bin size

        observable_best_bins = {}
        for cpop, pop in enumerate( populations ):
            observable_best_bins[cpop] = (min_range, max_range, min_width, np.arange( min_range, max_range + min_width, min_width ).tolist()) # store best binning for each population (min, max, bin_size, bin_edges)

    # If bin size is given, compute binning vectors accordingly
    else:
        bin_min_vals = np.zeros( ( len( seeds ), len( populations ) ) )
        bin_max_vals = np.zeros( ( len( seeds ), len( populations ) ) )
        for cseed, seed in enumerate( seeds ):
            cseed_str = str( cseed )
            # calculate histogram for each population
            for cpop, pop in enumerate( populations ):
                bin_min_vals[cseed][cpop] = np.min( np.array( observable[cseed_str][pop] ) ).tolist() # store min observable value
                bin_max_vals[cseed][cpop] = np.max( np.array( observable[cseed_str][pop] ) ).tolist() # store max observable value

        min_min_bin_vals = np.min( bin_min_vals, axis=0 ) # get min of min bin values across seeds for each population
        max_max_bin_vals = np.max( bin_max_vals, axis=0 ) # get max of max bin values across seeds for each population

        min_min_min_bin_val = np.min( min_min_bin_vals ) # use min of min bin values across populations as min bin value
        max_max_max_bin_val = np.max( max_max_bin_vals ) # use max of max bin values across populations as max bin value

        min_range = observable_limits[0] if observable_limits is not None else min_min_min_bin_val.tolist() # get min range (can either be given or from data)
        max_range = observable_limits[1] if observable_limits is not None else max_max_max_bin_val.tolist() # get max range (can either be given or from data)
        min_width = bin_size # use given bin size
        observable_best_bins = {}
        for cpop, pop in enumerate( populations ):
            observable_best_bins[cpop] = (min_range, max_range, min_width, np.arange( min_range, max_range + min_width, min_width ).tolist()) # store best binning for each population (min, max, bin_size, bin_edges)

    # calculate histogram for each seed and each population (data_distribution(...))
    observable_hists = [] # list of histograms [seed][pop][histogram]
    observable_hist_mat = {} # matrix of histograms [pop][seed][histogram]
    observable_stats = {} # list of statistics [seed][pop][stats] (mean, std, etc.)
    for cseed, seed in enumerate( seeds ):
        cseed_str = str( cseed )
        observable_stats[cseed] = {}
        observable_hists.append([])
        for cpop, pop in enumerate( populations ):
            observable_stats[cseed][pop] = {}
            observable_pop = np.array( observable[cseed_str][pop] ) # get observable data for current seed and population
            observable_hist, bins, stats = helpers.data_distribution( observable_pop, pop, f'{units}', np.array( observable_best_bins[cpop][3] ) ) # calculate histogram and statistics for each population across seeds
            observable_hists[cseed].append( observable_hist.tolist() ) # store histogram
            if not cpop in observable_hist_mat:
                observable_hist_mat[cpop] = np.zeros( ( len( seeds ), len( observable_hist ) ) ) # initialize histogram matrix for each population
            observable_hist_mat[cpop][cseed] = observable_hist / stats['sample_size'] # store relative histogram in histogram matrix
            observable_stats[cseed][pop] = stats # store statistics

    helpers.dict2json( observable_stats, sim_dict['data_path'] + f'{observable_name}_stats.json' ) # save statistics as json file

    return observable_hist_mat, observable_best_bins, observable_stats

def plot_data_dists( observable_name: str, x_label: str, observable_hist_mat: dict, observable_best_bins: np.ndarray, observable_ks_distances: dict, observable_limits: tuple[float,float]=None ) -> None:
    '''
    Plots histograms and KS-distance distributions for different populations.
    -------------------------------------------------------------------------
    Parameters:
    - observable_name : str
        The name of the observable being plotted (used for figure file name).
    - x_label : str
        The label for the x-axis of the histogram plots.
    - observable_hist_mat : dict
        A dictionary containing the histograms for each population, where keys are population indices.
    - observable_best_bins : ndarray
        An array containing the best bin edges for each population.
    - observable_ks_distances : dict
        A dictionary containing KS-distance values for each population, where keys are population names.
    - observable_limits : tuple[float,float], optional
        The limits for the x-axis of the histogram plots. If None, limits are determined from the data.
    -------------------------------------------------------------------------
    Returns:
    - None
    '''

    from matplotlib import rcParams
    rcParams['figure.figsize']    = (ref_dict['max_fig_width'] / 3., (4. / 9.) * ref_dict['max_fig_width'])
    rcParams['figure.dpi']        = 300
    rcParams['font.family']       = 'sans-serif'
    rcParams['font.size']         = 8
    rcParams['legend.fontsize']   = 8
    rcParams['axes.titlesize']    = 10
    rcParams['axes.labelsize']    = 8
    rcParams['ytick.labelsize']   = 8
    rcParams['xtick.labelsize']   = 8
    rcParams['ytick.major.size']  = 0   ## remove y ticks
    rcParams['text.usetex']       = False
    rcParams['legend.framealpha'] = 1.0
    rcParams['legend.edgecolor']  = 'k'
    data_path = sim_dict['data_path']

    x_max_hist = 0
    x_min_hist = 0
    for cpop, pop in enumerate( populations ):
        bin_edges = observable_best_bins[cpop][3]
        x_max_hist = max( x_max_hist, np.max( bin_edges ) )
        x_min_hist = min( x_min_hist, np.min( bin_edges ) )

    ks_max = 0
    for cpop, pop in enumerate( populations ):
        ks_values = observable_ks_distances[pop]["list"]
        ks_max = max( ks_max, np.max( ks_values ) )

    # plot of histograms for all populations
    fig_hist, axes_hist = plt.subplots( 4, 2, sharex=True, gridspec_kw={'hspace': 0.0, 'wspace': 0.0} )

    # plot of distributions of KS -distances
    fig_ks, axes_ks = plt.subplots( 4, 2, sharex=True, sharey=True, gridspec_kw={'hspace': 0.0, 'wspace': 0.0} )

    for cpop, pop in enumerate( populations ):
        ax_hist = axes_hist[cpop // 2, cpop % 2]     # axes for each population
        ax_ks = axes_ks[cpop // 2, cpop % 2]

        bin_edges = observable_best_bins[cpop][3]
        bin_centers = bin_edges[:-1]

        pop_rel_hists = observable_hist_mat[cpop]

        # calculate population mean and std histograms across seeds
        pop_mean_hist = np.mean( pop_rel_hists, axis=0 )
        pop_std_hist  = np.std( pop_rel_hists, axis=0 )

        n_seeds = len( seeds )
        grayscale = np.linspace( 0.2, 0.8, n_seeds )
        colors = [(g, g, g) for g in grayscale]

        for cseed in range( n_seeds ):
            ax_hist.plot( bin_centers, pop_rel_hists[cseed], '-', color=colors[-1], label=f'Seed {cseed}' )

        ax_hist.plot( bin_centers, pop_mean_hist, 'k--', label='Mean' )
        ax_hist.fill_between( bin_centers, pop_mean_hist - pop_std_hist, pop_mean_hist + pop_std_hist, alpha=0.3 )

        # set x and y limits
        if observable_limits is not None:
            ax_hist.set_xlim( observable_limits[0], observable_limits[1] )
            ax_hist.set_xticks( [observable_limits[0], (observable_limits[0] + observable_limits[1]) / 2],
                              [r'$%.1f$' % observable_limits[0], r'$%.1f$' % ((observable_limits[0] + observable_limits[1]) / 2)] )
            if observable_name == 'spike_ccs':
                ax_hist.set_xticks( [observable_limits[0]/2, 0, observable_limits[1]/2],
                                  [r'$%.2f$' % (observable_limits[0]/2), r'$0$', r'$%.2f$' % (observable_limits[1]/2)] )

        else:
            ax_hist.set_xlim( 0, x_max_hist )
            ax_hist.set_xticks([0, x_max_hist/2], [r'$0$', r'$%.0f$' % (x_max_hist/2)] )
            if observable_name == 'spike_ccs':
                ax_hist.set_xlim(x_min_hist, x_max_hist)
                ax_hist.set_xticks([x_min_hist/2, 0, x_max_hist/2], [r'$%.2f$' % (x_min_hist/2), r'$0$', r'$%.2f$' % (x_max_hist/2)] )

        ax_hist.set_ylim( 0, np.max( pop_mean_hist ) * 1.2 )

        ks_values = observable_ks_distances[pop]["list"]
        mean = std = None
        if len( ks_values ) > 0:
            mean = np.mean( ks_values )
            std = np.std( ks_values )

        textbox = r'%s' % pop
        if mean is not None:
            #textbox += r'\\{\tiny $D_\mathsf{KS} = %.2f$}' % mean
            textbox += '\n$D_\mathsf{KS} = %.2f$' % mean

            ax_ks.hist( ks_values, bins=n_seeds, color='gray', alpha=0.5 )
            ax_ks.axvline( mean, color='red', linestyle='--', label='Mean KS-distance' )
            ax_ks.axvline( mean + std, color='blue', linestyle='--', label='Mean + Std' )
            ax_ks.axvline( mean - std, color='blue', linestyle='--', label='Mean - Std' )

        ax_hist.text( 0.95, 0.95, textbox, transform=ax_hist.transAxes, fontsize=8,
                verticalalignment='top', horizontalalignment='right' )
        ax_ks.text( 0.95, 0.95, r'%s' % pop, transform=ax_ks.transAxes, fontsize=8,
                verticalalignment='top', horizontalalignment='right' )

        if cpop % 2 == 0:
            ax_hist.set_ylabel( r'rel. freq.' )
            ax_hist.set_yticks( [] )
            ax_ks.set_ylabel( r'rel. freq.' )
            ax_ks.set_yticks( [] )
        else:
            ax_hist.set_yticks( [] )

    ax_ks.set_xlim( 0, ks_max * 1.1)
    ax_ks.set_xticks( [0, ks_max / 2], [r'$0$', r'$%.2f$' % (ks_max / 2)] )

    fig_hist.text(0.5, -0.01, x_label, ha="center", va="center")
    fig_hist.savefig(f'{data_path}{observable_name}_distributions.pdf',
                 bbox_inches="tight", pad_inches=0.02)
    fig_ks.text(0.5, 0.0, r'KS-distance', ha="center", va="center")
    fig_ks.savefig(f'{data_path}{observable_name}_KS_distances.pdf',
               bbox_inches="tight", pad_inches=0.02)

    # save figures for README.md
    fig_hist.savefig(f'figures/{observable_name}_distributions_T' + str( int( ref_dict['t_sim'] * 1.0e-3 ) ) + 's.png',
                 bbox_inches="tight", pad_inches=0.02)
    fig_ks.savefig(f'figures/{observable_name}_KS_distances_T' + str( int( ref_dict['t_sim'] * 1.0e-3 ) ) + 's.png',
               bbox_inches="tight", pad_inches=0.02)


def main():
    data_path = sim_dict['data_path']

    # Read in the data from json files
    rates = helpers.json2dict( f'{data_path}rates.json' )
    spike_cvs = helpers.json2dict( f'{data_path}spike_cvs.json' )
    spike_ccs = helpers.json2dict( f'{data_path}spike_ccs.json' )

    rate_ks_distances = helpers.json2dict( f'{data_path}rate_ks_distances.json' )
    spike_cvs_ks_distances = helpers.json2dict( f'{data_path}spike_cvs_ks_distances.json' )
    spike_ccs_ks_distances = helpers.json2dict( f'{data_path}spike_ccs_ks_distances.json' )

    # Compute distributions and statistics
    rate_hist_mat, rate_best_bins, rate_stats = compute_data_dist( observable=rates, observable_name='rate', observable_limits=ref_dict['rate_lim'], units='1/s', bin_size=ref_dict['rate_binsize'] )
    spike_cvs_hist_mat, spike_cvs_best_bins, spike_cvs_stats = compute_data_dist( observable=spike_cvs, observable_name='spike_cvs', observable_limits=ref_dict['cv_lim'], bin_size=ref_dict['cv_binsize'] )
    spike_ccs_hist_mat, spike_ccs_best_bins, spike_ccs_stats = compute_data_dist( observable=spike_ccs, observable_name='spike_ccs', observable_limits=ref_dict['cc_lim'], bin_size=ref_dict['cc_binsize'] )

    # Plot distributions and KS distances
    plot_data_dists( 'rate', 'time averaged single neuron\nfiring rate (s$^{-1}$)', rate_hist_mat, rate_best_bins, rate_ks_distances, observable_limits=ref_dict['rate_lim'] )
    #plot_data_dists( 'rate', r'\begin{center} time averaged single neuron\\firing rate (s$^{-1}$) \end{center}', rate_hist_mat, rate_best_bins, rate_ks_distances, observable_limits=ref_dict['rate_lim'] )
    plot_data_dists( 'spike_cvs', r'spike irregularity (ISI CV)', spike_cvs_hist_mat, spike_cvs_best_bins, spike_cvs_ks_distances, observable_limits=ref_dict['cv_lim'] )
    plot_data_dists( 'spike_ccs', 'spike correlation coefficient\n(bin size $%.1f$ ms)' % ref_dict['binsize'], spike_ccs_hist_mat, spike_ccs_best_bins, spike_ccs_ks_distances, observable_limits=ref_dict['cc_lim'] )
    #plot_data_dists( 'spike_ccs', r'\begin{center} spike correlation coefficient\\(bin size $%.1f$ ms) \end{center}' % ref_dict['binsize'], spike_ccs_hist_mat, spike_ccs_best_bins, spike_ccs_ks_distances, observable_limits=ref_dict['cc_lim'] )

    ## current memory consumption of the python process (in MB)
    import psutil
    mem = psutil.Process().memory_info().rss / ( 1024 * 1024 )
    print( f"Current memory consumption: {mem:.2f} MB" )

if __name__ == "__main__":
    main()
