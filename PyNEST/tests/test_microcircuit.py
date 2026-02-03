# -*- coding: utf-8 -*-
#
# test_microcircuit.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Unit test including network creation, connection and simulation.
"""

#####################
import nest
import numpy as np
import pytest

## import model implementation
from microcircuit import network

## import (default) parameters (network, simulation, stimulus)
from microcircuit.network_params import default_net_dict as net_dict
from microcircuit.sim_params import default_sim_dict as sim_dict
from microcircuit.stimulus_params import default_stim_dict as stim_dict

#####################

# set scaling factor of simulation
scaling_factor = 0.2
net_dict["N_scaling"] = scaling_factor
net_dict["K_scaling"] = scaling_factor


def test_simulation():

    ## set simulation time
    sim_dict["t_sim"] = 100.0

    def run_simulation():

        ## create instance of the network
        net = network.Network(sim_dict, net_dict, stim_dict)

        ## create all nodes (neurons, devices)
        net.create()

        ## connect nework
        net.connect()

        ## simulation
        net.simulate(sim_dict["t_sim"])

        return not None

    try:
        result = run_simulation()

    except Exception as e:
        pytest.fail(f"Simulation raised an exception: {e}")

    assert result is not None

    print("======================================")
    print("")
    print("Test passed")
    print("")
    print("microcircuit.simulate() runs correctly")
    print("")
    print("======================================")


if __name__ == "__main__":
    test_simulation()
