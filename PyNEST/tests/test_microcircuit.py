# -*- coding: utf-8 -*-
#
# test_microcircuit.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

'''
Unit test including network creation, connection and simulation.
'''

#####################
import nest
import pytest

## import model implementation
from microcircuit.model import Model

## import parameter definitions
from microcircuit.parameter_definitions import Parameters

#####################

def test_simulation():

    P = Parameters()

    ## set scaling factor of simulation
    scaling_factor = 0.2
    P.N_scaling = scaling_factor
    P.K_scaling = scaling_factor

    ## set simulation time
    P.t_sim = 100.0

    def run_simulation():

        ## create instance of the model
        model = Model(P)

        ## create all nodes (neurons, devices)
        model.create()

        ## connect nework
        model.connect()

        ## simulation
        model.simulate(P.t_sim)

        return not None

    try:
        result = run_simulation()

    except Exception as e:
        pytest.fail(f'Simulation raised an exception: {e}')

    assert result is not None

    print('======================================')
    print('')
    print('Test passed')
    print('')
    print('microcircuit.simulate() runs correctly')
    print('')
    print('======================================')

if __name__ == '__main__':
    test_simulation()

