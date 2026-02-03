# -*- coding: utf-8 -*-
#
# network.py
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

"""PyNEST Microcircuit: Helper Functions
-------------------------------------------

Helper functions for network construction, simulation and evaluation of the
microcircuit.

"""

import json
import os

import matplotlib.pyplot as plt
import nest
import numpy as np
from matplotlib.patches import Polygon

if "DISPLAY" not in os.environ:
    import matplotlib

    matplotlib.use("Agg")


def num_synapses_from_conn_probs(conn_probs, popsize1, popsize2):
    """Computes the total number of synapses between two populations from
    connection probabilities.

    Here it is irrelevant which population is source and which target.

    Parameters
    ----------
    conn_probs
        Matrix of connection probabilities.
    popsize1
        Size of first population.
    popsize2
        Size of second population.

    Returns
    -------
    num_synapses
        Matrix of synapse numbers.
    """
    prod = np.outer(popsize1, popsize2)
    num_synapses = np.log(1.0 - conn_probs) / np.log((prod - 1.0) / prod)
    return num_synapses


def postsynaptic_potential_to_current(C_m, tau_m, tau_syn):
    r"""Computes a factor to convert postsynaptic potentials to currents.

    The time course of the postsynaptic potential ``v`` is computed as
    :math: `v(t)=(i*h)(t)`
    with the exponential postsynaptic current
    :math:`i(t)=J\mathrm{e}^{-t/\tau_\mathrm{syn}}\Theta (t)`,
    the voltage impulse response
    :math:`h(t)=\frac{1}{\tau_\mathrm{m}}\mathrm{e}^{-t/\tau_\mathrm{m}}\Theta (t)`,
    and
    :math:`\Theta(t)=1` if :math:`t\geq 0` and zero otherwise.

    The ``PSP`` is considered as the maximum of ``v``, i.e., it is
    computed by setting the derivative of ``v(t)`` to zero.
    The expression for the time point at which ``v`` reaches its maximum
    can be found in Eq. 5 of [1]_.

    The amplitude of the postsynaptic current ``J`` corresponds to the
    synaptic weight ``PSC``.

    References
    ----------
    .. [1] Hanuschkin A, Kunkel S, Helias M, Morrison A and Diesmann M (2010)
           A general and efficient method for incorporating precise spike times
           in globally time-driven simulations.
           Front. Neuroinform. 4:113.
           DOI: `10.3389/fninf.2010.00113 <https://doi.org/10.3389/fninf.2010.00113>`__.

    Parameters
    ----------
    C_m
        Membrane capacitance (in pF).
    tau_m
        Membrane time constant (in ms).
    tau_syn
        Synaptic time constant (in ms).

    Returns
    -------
    PSC_over_PSP
        Conversion factor to be multiplied to a `PSP` (in mV) to obtain a `PSC`
        (in pA).

    """
    sub = 1.0 / (tau_syn - tau_m)
    pre = tau_m * tau_syn / C_m * sub
    frac = (tau_m / tau_syn) ** sub

    PSC_over_PSP = 1.0 / (pre * (frac**tau_m - frac**tau_syn))
    return PSC_over_PSP


def dc_input_compensating_poisson(bg_rate, K_ext, tau_syn, PSC_ext):
    """Computes DC input if no Poisson input is provided to the microcircuit.

    Parameters
    ----------
    bg_rate
        Rate of external Poisson generators (in spikes/s).
    K_ext
        External indegrees.
    tau_syn
        Synaptic time constant (in ms).
    PSC_ext
        Weight of external connections (in pA).

    Returns
    -------
    DC
        DC input (in pA) which compensates lacking Poisson input.
    """
    DC = bg_rate * K_ext * PSC_ext * tau_syn * 0.001
    return DC


def adjust_weights_and_input_to_synapse_scaling(
    full_num_neurons,
    full_num_synapses,
    K_scaling,
    mean_PSC_matrix,
    PSC_ext,
    tau_syn,
    full_mean_rates,
    DC_amp,
    # poisson_input,
    bg_input_type,
    bg_rate,
    K_ext,
):
    """Adjusts weights and external input to scaling of indegrees.

    The recurrent and external weights are adjusted to the scaling
    of the indegrees. Extra DC input is added to compensate for the
    scaling in order to preserve the mean and variance of the input.

    Parameters
    ----------
    full_num_neurons
        Total numbers of neurons.
    full_num_synapses
        Total numbers of synapses.
    K_scaling
        Scaling factor for indegrees.
    mean_PSC_matrix
        Weight matrix (in pA).
    PSC_ext
        External weight (in pA).
    tau_syn
        Synaptic time constant (in ms).
    full_mean_rates
        Firing rates of the full network (in spikes/s).
    DC_amp
        DC input current (in pA).
    #poisson_input
        #True if Poisson input is used.
    bg_input_type
        Type of background input, either "poisson" or "dc".
    bg_rate
        Firing rate of Poisson generators (in spikes/s).
    K_ext
        External indegrees.

    Returns
    -------
    PSC_matrix_new
        Adjusted weight matrix (in pA).
    PSC_ext_new
        Adjusted external weight (in pA).
    DC_amp_new
        Adjusted DC input (in pA).

    """
    PSC_matrix_new = mean_PSC_matrix / np.sqrt(K_scaling)
    PSC_ext_new = PSC_ext / np.sqrt(K_scaling)

    # recurrent input of full network
    indegree_matrix = full_num_synapses / full_num_neurons[:, np.newaxis]
    input_rec = np.sum(
        mean_PSC_matrix * indegree_matrix * full_mean_rates, axis=1
    )  # local input currents in full scale network

    DC_amp_new = DC_amp + 0.001 * tau_syn * (1.0 - np.sqrt(K_scaling)) * input_rec

    if bg_input_type == "poisson":
        input_ext = PSC_ext * K_ext * bg_rate
        DC_amp_new += 0.001 * tau_syn * (1.0 - np.sqrt(K_scaling)) * input_ext

    return PSC_matrix_new, PSC_ext_new, DC_amp_new


def compute_rheo_base_current(V_th, E_L, C_m, tau_m):
    """Computes the rheobase current for a given threshold voltage, resting potential, membrane capacitance, and membrane time constant.

    The rheobase current is the minimum current required to bring the membrane potential to the threshold voltage.

    Parameters
    ----------
    V_th
        Threshold voltage (in mV).
    E_L
        Resting membrane potential (in mV).
    C_m
        Membrane capacitance (in pF).
    tau_m
        Membrane time constant (in ms).

    Returns
    -------
    rheo_base_current
        Rheobase current (in pA).
    """

    I_rh = C_m * (V_th - E_L) / tau_m

    return I_rh


def plot_raster(path, name, begin, end, N_scaling):
    """Creates a spike raster plot of the network activity.

    Parameters
    -----------
    path
        Path where the spike times are stored.
    name
        Name of the spike recorder.
    begin
        Time point (in ms) to start plotting spikes (included).
    end
        Time point (in ms) to stop plotting spikes (included).
    N_scaling
        Scaling factor for number of neurons.

    Returns
    -------
    None

    """

    fig_size = (4, 3)  ## figure size (inch)
    ms = 1  ## marker size
    alpha = 1
    ylabels = ["L2/3", "L4", "L5", "L6"]
    color_list = np.tile(["#595289", "#af143c"], 4)

    sd_names, node_ids, data = __load_spike_times(path, name, begin, end)
    last_node_id = node_ids[-1, -1]
    mod_node_ids = np.abs(node_ids - last_node_id) + 1

    label_pos = [
        (mod_node_ids[i, 0] + mod_node_ids[i + 1, 1]) / 2.0 for i in np.arange(0, 8, 2)
    ]

    ######################
    from matplotlib import rcParams

    rcParams["figure.figsize"] = fig_size
    rcParams["figure.dpi"] = 300
    rcParams["font.family"] = "sans-serif"
    rcParams["font.size"] = 8
    rcParams["legend.fontsize"] = 8
    rcParams["axes.titlesize"] = 10
    rcParams["axes.labelsize"] = 8
    rcParams["ytick.labelsize"] = 8
    rcParams["xtick.labelsize"] = 8
    rcParams["ytick.major.size"] = 0  ## remove y ticks
    rcParams["text.usetex"] = False
    rcParams["legend.framealpha"] = 1.0
    rcParams["legend.edgecolor"] = "k"

    plt.figure(1)
    plt.clf()

    stp = 1

    if N_scaling > 0.1:
        stp = int(10.0 * N_scaling)
        print("  Only every %dth spike is plotted." % stp)

    all_neurons = []
    for i, n in enumerate(sd_names):
        times = data[i]["time_ms"]
        neurons = np.abs(data[i]["sender"] - last_node_id) + 1
        all_neurons += list(neurons)
        if i % 2 == 0:
            plt.hlines(
                mod_node_ids[i, 0], begin, end, color="0.8", ls="-", lw=1, zorder=0
            )
        plt.plot(
            times[::stp],
            neurons[::stp],
            "o",
            ms=ms,
            alpha=alpha,
            color=color_list[i],
            mew=0,
            rasterized=True,
        )
    plt.xlabel("time (ms)")
    plt.ylabel(r"neuron id")
    plt.yticks(label_pos, ylabels, rotation=0)
    plt.xlim(begin, end)
    all_neurons = np.unique(all_neurons)
    plt.ylim(all_neurons[0], all_neurons[-1])

    plt.subplots_adjust(bottom=0.13, left=0.12, top=0.97, right=0.95)
    plt.savefig(os.path.join(path, "raster_plot.png"))


def firing_rates(path, name, begin, end):
    """Computes mean and standard deviation of firing rates per population.

    The firing rate of each neuron in each population is computed and stored
    in a .dat file in the directory of the spike recorders. The mean firing
    rate and its standard deviation are printed out for each population.

    Parameters
    -----------
    path
        Path where the spike times are stored.
    name
        Name of the spike recorder.
    begin
        Time point (in ms) to start calculating the firing rates (included).
    end
        Time point (in ms) to stop calculating the firing rates (included).

    Returns
    -------
    None

    """
    sd_names, node_ids, data = __load_spike_times(path, name, begin, end)
    all_mean_rates = []
    all_std_rates = []
    for i, n in enumerate(sd_names):
        senders = data[i]["sender"]
        # 1 more bin than node ids per population
        bins = np.arange(node_ids[i, 0], node_ids[i, 1] + 2)
        spike_count_per_neuron, _ = np.histogram(senders, bins=bins)
        rate_per_neuron = spike_count_per_neuron * 1000.0 / (end - begin)
        np.savetxt(os.path.join(path, ("rate" + str(i) + ".dat")), rate_per_neuron)
        # zeros are included
        all_mean_rates.append(np.mean(rate_per_neuron))
        all_std_rates.append(np.std(rate_per_neuron))
    print("Mean rates: {} spikes/s".format(np.around(all_mean_rates, decimals=3)))
    print(
        "Standard deviation of rates: {} spikes/s".format(
            np.around(all_std_rates, decimals=3)
        )
    )


def boxplot(path, populations):
    """Creates a boxblot of the firing rates of all populations.

    To create the boxplot, the firing rates of each neuron in each population
    need to be computed with the function ``firing_rate()``.

    Parameters
    -----------
    path
        Path where the firing rates are stored.
    populations
        Names of neuronal populations.

    Returns
    -------
    None

    """

    fig_size = (4, 3)  ## figure size (inch)
    pop_names = [string.replace("23", "2/3") for string in populations]
    label_pos = list(range(len(populations), 0, -1))
    color_list = ["#af143c", "#595289"]
    medianprops = dict(linestyle="-", linewidth=2.5, color="black")
    meanprops = dict(linestyle="--", linewidth=2.5, color="lightgray")

    rates_per_neuron_rev = []
    for i in np.arange(len(populations))[::-1]:
        rates_per_neuron_rev.append(
            np.loadtxt(os.path.join(path, ("rate" + str(i) + ".dat")))
        )

    ######################
    from matplotlib import rcParams

    rcParams["figure.figsize"] = fig_size
    rcParams["figure.dpi"] = 300
    rcParams["font.family"] = "sans-serif"
    rcParams["font.size"] = 8
    rcParams["legend.fontsize"] = 8
    rcParams["axes.titlesize"] = 10
    rcParams["axes.labelsize"] = 8
    rcParams["ytick.labelsize"] = 8
    rcParams["xtick.labelsize"] = 8
    rcParams["text.usetex"] = False
    rcParams["legend.framealpha"] = 1.0
    rcParams["legend.edgecolor"] = "k"

    plt.figure(1)
    plt.clf()

    bp = plt.boxplot(
        rates_per_neuron_rev,
        notch=False,
        sym="rs",
        whis=0,
        medianprops=medianprops,
        meanprops=meanprops,
        meanline=True,
        showmeans=True,
        vert=False,
    )
    plt.setp(bp["boxes"], color="black")
    plt.setp(bp["whiskers"], color="black")
    plt.setp(bp["fliers"], color="red", marker="+")

    # boxcolors
    for i in np.arange(len(populations)):
        boxX = []
        boxY = []
        box = bp["boxes"][i]
        for j in list(range(5)):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        boxCoords = list(zip(boxX, boxY))
        k = i % 2
        boxPolygon = Polygon(boxCoords, facecolor=color_list[k])
        plt.gca().add_patch(boxPolygon)

    plt.ylabel(r"neuron population")
    plt.xlabel("firing rate (spikes/s)")
    plt.yticks(label_pos, pop_names)

    plt.subplots_adjust(bottom=0.13, left=0.14, top=0.97, right=0.95)
    plt.savefig(os.path.join(path, "box_plot.png"))


def __gather_metadata(path, name):
    """Reads names and ids of spike recorders and first and last ids of
    neurons in each population.

    If the simulation was run on several threads or MPI-processes, one name per
    spike recorder per MPI-process/thread is extracted.

    Parameters
    ------------
    path
        Path where the spike recorder files are stored.
    name
        Name of the spike recorder, typically ``spike_recorder``.

    Returns
    -------
    sd_files
        Names of all files written by spike recorders.
    sd_names
        Names of all spike recorders.
    node_ids
        Lowest and highest id of nodes in each population.

    """
    # load filenames
    sd_files = []
    sd_names = []
    for fn in sorted(os.listdir(path)):
        if fn.startswith(name):
            sd_files.append(fn)
            # spike recorder name and its ID
            fnsplit = "-".join(fn.split("-")[:-1])
            if fnsplit not in sd_names:
                sd_names.append(fnsplit)

    # load node IDs
    node_idfile = open(path + "population_nodeids.dat", "r")
    node_ids = []
    for node_id in node_idfile:
        node_ids.append(node_id.split())
    node_ids = np.array(node_ids, dtype="i4")
    return sd_files, sd_names, node_ids


def __load_spike_times(path, name, begin, end):
    """Loads spike times of each spike recorder.

    Parameters
    ----------
    path
        Path where the files with the spike times are stored.
    name
        Name of the spike recorder.
    begin
        Time point (in ms) to start loading spike times (included).
    end
        Time point (in ms) to stop loading spike times (included).

    Returns
    -------
    data
        Dictionary containing spike times in the interval from ``begin``
        to ``end``.

    """
    sd_files, sd_names, node_ids = __gather_metadata(path, name)
    data = {}
    dtype = {"names": ("sender", "time_ms"), "formats": ("i4", "f8")}  # as in header
    for i, name in enumerate(sd_names):
        data_i_raw = np.array([[]], dtype=dtype)
        for j, f in enumerate(sd_files):
            if name in f:
                # skip header while loading
                ld = np.loadtxt(os.path.join(path, f), skiprows=3, dtype=dtype)
                data_i_raw = np.append(data_i_raw, ld)

        data_i_raw = np.sort(data_i_raw, order="time_ms")
        # begin and end are included if they exist
        low = np.searchsorted(data_i_raw["time_ms"], v=begin, side="left")
        high = np.searchsorted(data_i_raw["time_ms"], v=end, side="right")
        data[i] = data_i_raw[low:high]
    return sd_names, node_ids, data


#################################################
def get_data_file_list(path, label):
    """
    Searches for files with extension "*.dat" in directory "path" with names starting with "label",
    and returns list of file names.

    Arguments
    ---------
    path:           str
                    Path to folder containing spike files.

    label:          str
                    Spike file label (file name root).

    Returns
    -------
    files:          list(str)
                    List of file names


    """

    ## get list of files names
    files = []
    for file_name in os.listdir(path):
        if file_name.endswith(".dat") and file_name.startswith(label):
            files += [file_name]
    files.sort()

    assert len(files) > 0, 'No files of type "%s*.dat" found in path "%s".' % (
        label,
        path,
    )

    return files


#################################################
def load_spike_data(path, label, time_interval=None, pop=None, skip_rows=3):
    """
    Load spike data from files.

    Arguments
    ---------
    path:           str
                    Path to folder containing spike files.

    label:          str
                    Spike file label (file name root).

    time_interval:  None (default) or tuple (optional)
                    Start and stop of observation interval (ms). All spikes outside this interval are discarded.
                    If None, all recorded spikes are loaded.

    pop:            None (default), list, or nest.NodeCollection (optional)
                    Oberserved neuron population. All spike senders that are not part of this population are discarded.
                    If None, all recorded spikes are loaded.

    skip_rows:      int (optional)
                    Number of rows to be skipped while reading spike files (to remove file headers). The default is 3.

    Returns
    -------
    spikes:   numpy.ndarray
              Lx2 array of spike senders spikes[:,0] and spike times spikes[:,1] (L = number of spikes).

    """

    if type(time_interval) == tuple:
        print(
            "Loading spike data in interval (%.1f ms, %.1f ms] ..."
            % (time_interval[0], time_interval[1])
        )
    else:
        print("Loading spike data...")

    files = get_data_file_list(path, label)

    ## open spike files and read data
    spikes = []
    for file_name in files:
        try:
            buf = np.loadtxt(
                "%s/%s" % (path, file_name), skiprows=skip_rows
            )  ## load spike file while skipping the header
            if buf.shape[0] > 0:
                if buf.shape == (2,):
                    buf = np.reshape(
                        buf, (1, 2)
                    )  ## needs to be reshaped to 2-dimensional array in case there is only a single row
                spikes += [buf]
        except:
            print("Error: %s" % sys.exc_info()[1])
            print(
                'Remove non-numeric entries from file %s (e.g. in file header) by specifying (optional) parameter "skip_rows".\n'
                % (file_name)
            )

    if len(spikes) > 1:
        spikes = np.concatenate(spikes)
    elif len(spikes) == 1:
        spikes = np.array(spikes[0])
    elif len(spikes) == 0:
        spikes = np.array([])

    spike_dict = {}

    if spikes.shape == (0,):
        print("WARNING: No spikes contained in %s/%s*." % (path, label))
        spike_dict["senders"] = np.array([])
        spike_dict["times"] = np.array([])
    else:
        ## extract spikes in specified time interval
        if time_interval != None:
            if type(time_interval) == tuple:
                ind = (spikes[:, 1] >= time_interval[0]) * (
                    spikes[:, 1] <= time_interval[1]
                )
                spikes = spikes[ind, :]
            else:
                print(
                    "Warning: time_interval must be a tuple or None. All spikes are loaded."
                )

        if type(pop) == nest.NodeCollection or type(pop) == list:
            spikes_subset = []
            for cn, nid in enumerate(pop):  ## loop over all neurons
                print(
                    "Spike extraction from %d/%d (%d%%) neurons completed"
                    % (cn + 1, len(pop), 1.0 * (cn + 1) / len(pop) * 100),
                    end="\r",
                )
                ind = np.where(spikes[:, 0] == nid)[0]
                spikes_subset += list(spikes[ind, :])
            spikes = np.array(spikes_subset)
        elif pop == None:
            pass
        else:
            print(
                "Warning: pop must be a list, a NEST NodeCollection, or None. All spikes are loaded."
            )
        print()

        spike_dict["senders"] = spikes[:, 0]
        spike_dict["times"] = spikes[:, 1]

        ind = np.argsort(spike_dict["times"])

        spike_dict["senders"] = spike_dict["senders"][ind]
        spike_dict["times"] = spike_dict["times"][ind]

    return spike_dict


##########################################################################
def dict2json(dictionary, filename):
    """
    Writes python dictionary to json file.

    Arguments:
    ----------
    dictionary: dict
                Python dictionary.

    filename: str
              Name of json file.

    Returns:
    --------
    -

    """
    to_list = lambda x: x.tolist() if isinstance(x, np.ndarray) else str(x)

    with open(filename, "w") as file:
        json.dump(dictionary, file, indent=4, default=to_list)


##########################################################################
def json2dict(filename):
    """
    Read python dictionary from json file.

    Arguments:
    ----------
    filename: str
              Name of json file.

    Returns:
    --------
    dictionary: dict
                Python dictionary.

    """

    with open(filename, "r") as file:
        dictionary = json.load(file)

    return dictionary


#################################################
def truncate_spike_data(spikes, interval):
    """
    Extracts spike data from a specified time interval (including left an right bound).

    Parameters:
    -----------

    spikes:                dict
                           Dictionary containing 'senders' IDs and spike 'times'.

    interval:              tuple
                           Tuple containing left and right bound of time interval.

    Returns:
    --------

    spikes_trunc:          dict
                           Truncated spike data.

    """

    assert type(spikes) == dict
    assert "senders" in spikes
    assert "times" in spikes
    assert len(spikes["senders"]) == len(spikes["times"])

    ind1 = np.where(spikes["times"] >= interval[0])[0]
    ind2 = np.where(spikes["times"][ind1] <= interval[1])[0]

    spikes_trunc = {}
    spikes_trunc["senders"] = spikes["senders"][ind2]
    spikes_trunc["times"] = spikes["times"][ind2]

    return spikes_trunc


#################################################
def time_averaged_single_neuron_firing_rates(spikes, pop, interval):
    """
    Computes single-neuron firing rates for a specified population of neurons,
    averaged across a speficied time interval.

    Parameters:
    -----------
    spikes:                dict
                           Dictionary containing 'senders' IDs and spike 'times'.

    pop:                   numpy.ndarray
                           Array of IDs of observed neurons.

    interval:              tuple
                           Tuple containing left and right bound of time interval (ms).

    Returns:
    --------
    rates:                 numpy.ndarray
                           List of time averaged single neuron firing rates (spikes/s).

    """
    assert type(spikes) == dict
    assert "senders" in spikes
    assert "times" in spikes
    assert len(spikes["senders"]) == len(spikes["times"])

    spikes = truncate_spike_data(spikes, interval)

    rates = []
    D = interval[1] - interval[0]
    for n in pop:
        rates += [len(np.where(spikes["senders"] == n)[0]) * 1.0 / D * 1e3]
    return rates


#################################################
def single_neuron_isi_cvs(spikes, pop, interval):
    """
    Computes coefficient of variation (CV) of inter-spike intervals (ISIs)
    for each neuron in the specified population within a given observation time interval.

    Parameters:
    -----------
    spikes:                dict
                           Dictionary containing 'senders' IDs and spike 'times'.

    pop:                   numpy.ndarray
                           Array of IDs of observed neurons.

    interval:              tuple
                           Tuple containing left and right bound of observation time interval (ms).

    Returns:
    --------
    cvs:                   numpy.ndarray
                           Array of single neuron ISI CVs.

    """

    assert type(spikes) == dict
    assert "senders" in spikes
    assert "times" in spikes
    assert len(spikes["senders"]) == len(spikes["times"])

    spikes = truncate_spike_data(spikes, interval)

    cvs = []
    for n in pop:
        ind = np.where(spikes["senders"] == n)
        spike_times = np.sort(spikes["times"][ind])
        if len(spike_times) > 2:
            intervals = np.diff(spike_times)
            cv = np.std(intervals) / np.mean(intervals)
            assert all(cv != err for err in (np.nan, np.inf)), (
                cv,
                n,
                intervals,
                spike_times,
            )
            cvs.append(cv)

    return np.array(cvs)


#################################################
def generate_spike_counts(spikes, pop, interval, binsize):
    """
    Converts spike data into spike-count signals.

    Parameters:
    -----------
    spikes:                dict
                           Dictionary containing 'senders' IDs and spike 'times'.

    pop:                   numpy.ndarray
                           Array of IDs of observed neurons.

    interval:              tuple
                           Tuple containing left and right bound of observation time interval (ms).

    binsize:               float
                           Bin size (ms).

    Returns:
    --------
    spike_counts:          numpy.ndarray
                           Array of spike-count signals for all neurons in specified population.
                           dim(spike_counts) = (number of neurons in pop, number of bins)

    times:                 numpy.ndarray
                           Time grid.
    """

    assert type(spikes) == dict
    assert "senders" in spikes
    assert "times" in spikes
    assert len(spikes["senders"]) == len(spikes["times"])

    times = np.arange(interval[0], interval[1] + binsize, binsize)
    spike_counts = []
    for n in pop:
        ind = np.where(spikes["senders"] == n)
        spike_times = spikes["times"][ind]
        spike_counts += [list(np.histogram(spike_times, times)[0])]

    spike_counts = np.array(spike_counts)
    return spike_counts, times


#################################################
def pairwise_spike_count_correlations(spikes, pop, interval, binsize):
    """
    Computes pairwise spike-count correlation coefficients.

    Parameters:
    -----------
    spikes:                dict
                           Dictionary containing 'senders' IDs and spike 'times'.

    pop:                   numpy.ndarray
                           Array of IDs of observed neurons.

    interval:              tuple
                           Tuple containing left and right bound of observation time interval (ms).

    binsize:               float
                           Bin size (ms).

    Returns:
    --------
    ccs:                   numpy.ndarray
                           Array of spike-count correlation coefficients for all pairs of neurons in specified population.

    """

    assert type(spikes) == dict
    assert "senders" in spikes
    assert "times" in spikes
    assert len(spikes["senders"]) == len(spikes["times"])

    spikes = truncate_spike_data(spikes, interval)

    spike_counts, times = generate_spike_counts(spikes, pop, interval, binsize)

    ## calculate correlation coefficients for each pair
    cc_matrix = np.corrcoef(spike_counts)

    ## extract elements above diagonal
    ccs = []
    for cn, n in enumerate(pop):
        ccs += list(cc_matrix[cn, cn + 1 :])

    # ccs=np.array(ccs)
    # ind = np.where(np.isnan(ccs))
    # ccs = np.delete(ccs,ind)

    return np.array(ccs)


#################################################
def data_distribution(data, label, unit="", hist_bin=None):
    """
    Calculates distribution (histogram) of a given data array, and basic statistics.

    If data is empty or contains only NaNs, the resulting histogram is set to zero for all bins and a warning is raised.

    Parameters:
    -----------
    data:      numpy.ndarray
               Data samples.

    label:     str
               Data type (name).

    unit:      str
               Data unit.

    hist_bin   None or float
               Bin width for calculation of histogram.
               None (default): Use Doane estimator.

    Returns:
    --------

    data_hist: numpy.ndarray
               Histogram of data.

    bins:      numpy.ndarray
               Histogram bins.

    stats:     dict
               Dictionary containing basic data statistics.

    """

    assert len(data) > 0

    nans = np.isnan(data)
    if all(nans):
        print(
            "WARNING: Data contains only NaNs. Histogram is set to zero for all bins."
        )
        # return np.zeros(len(data)), np.zeros(len(data)), {
        #'sample_size': 0,
        #'mean': np.nan,
        #'median': np.nan,
        #'min': np.nan,
        #'max': np.nan,
        #'sd': np.nan
        # }
        return None, None, None
    else:
        print(
            "WARNING: Data contains %d NaNs. These are ignored in the statistics."
            % sum(nans)
        )
        data = np.delete(data, np.where(nans))

    stat = {}

    stat["sample_size"] = len(data)
    # stat['samples']     = data.tolist()
    stat["mean"] = np.mean(data).item()
    stat["median"] = np.median(data).item()
    stat["min"] = np.min(data).item()
    stat["max"] = np.max(data).item()
    stat["sd"] = np.std(data).item()

    print()
    print("%s statistics:" % label)
    print("\tsample size = %d" % (stat["sample_size"]))
    print("\tmean        = %.3f %s" % (stat["mean"], unit))
    print("\tmedian      = %.3f %s" % (stat["median"], unit))
    print("\tSD          = %.3f %s" % (stat["sd"], unit))
    print("\tmin         = %.3f %s" % (stat["min"], unit))
    print("\tmax         = %.3f %s" % (stat["max"], unit))

    ## histogram
    if hist_bin is None:
        print()
        print("\tUsing Doane estimator for histogram binsize.")
        print()
        bins = "doane"  ## Doane estimator
    else:
        if isinstance(hist_bin, (int, float)):
            if hist_bin > 0:
                bins = np.arange(
                    stat["min"] - hist_bin, stat["max"] + 1.1 * hist_bin, hist_bin
                )
            else:
                bins = np.array([0, stat["min"], 2 * stat["min"]])
        elif isinstance(hist_bin, (list, np.ndarray)):
            bins = hist_bin

    data_hist, bins = np.histogram(data, bins=bins)

    return data_hist, bins[:-1], stat


##########################################################################
