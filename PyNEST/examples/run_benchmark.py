# -*- coding: utf-8 -*-
#
# run_benchmark.py
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
Microcircuit performance benchmark (Potjans & Diesmann 2014)
------------------------------------------------------------

Runs the model with the performance setting of the benchmarking recipe (full
scale, DC input, optimized initial conditions, 500 ms warm-up, T_model = 10 s,
no spike recording) and reports the timers and the real-time factor. No
evaluation is performed.

Usage: python run_benchmark.py [--scale S] [--threads N] [--seed SEED]
"""

import argparse
import time

import nest

from microcircuit import network
from microcircuit.network_params import default_net_dict as net_dict
from microcircuit.sim_params import default_sim_dict as sim_dict
from microcircuit.stimulus_params import default_stim_dict as stim_dict


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument("--scale", type=float, default=1.0, help="scaling of neuron and synapse numbers (1 = full scale)")
    parser.add_argument("--threads", type=int, default=64, help="threads per MPI process")
    parser.add_argument("--seed", type=int, default=55, help="seed of the random number generator")
    args = parser.parse_args()

    net_dict.update({"N_scaling": args.scale, "K_scaling": args.scale, "bg_input_type": "dc", "V0_type": "optimized"})
    sim_dict.update(
        {
            "t_presim": 500.0,
            "t_sim": 10000.0,
            "rec_dev": [],
            "rng_seed": args.seed,
            "local_num_threads": args.threads,
            "print_time": False,
            "store_metadata": False,
        }
    )

    time_start = time.time()
    net = network.Network(sim_dict, net_dict, stim_dict)
    time_network = time.time()

    net.create()
    time_create = time.time()

    net.connect()
    time_connect = time.time()

    net.simulate(sim_dict["t_presim"])
    time_presimulate = time.time()

    net.simulate(sim_dict["t_sim"])
    time_simulate = time.time()

    rtf = (time_simulate - time_presimulate) / (sim_dict["t_sim"] / 1000.0)

    print(
        "\nTimes of Rank {}:\n".format(nest.Rank())
        + "  Time to initialize:  {:.3f} s\n".format(time_network - time_start)
        + "  Time to create:      {:.3f} s\n".format(time_create - time_network)
        + "  Time to connect:     {:.3f} s\n".format(time_connect - time_create)
        + "  Time to presimulate: {:.3f} s\n".format(time_presimulate - time_connect)
        + "  Time to simulate:    {:.3f} s\n".format(time_simulate - time_presimulate)
        + "  Real-time factor:    {:.3f}\n".format(rtf)
    )


if __name__ == "__main__":
    main()
