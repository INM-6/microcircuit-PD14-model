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
import pytest

## import model implementation
from microcircuit.model import Model

## import parameter definitions
from microcircuit.parameter_definitions import Parameters

#####################


def test_simulation():

    params = Parameters()

    ## set scaling factor of simulation
    scaling_factor = 0.2
    params.N_scaling = scaling_factor
    params.K_scaling = scaling_factor

    ## set simulation time
    params.t_sim = 100.0

    def run_simulation():

        ## create instance of the model
        model = Model(params)

        ## create all nodes (neurons, devices)
        model.create_nodes()

        ## connect nework
        model.connect()

        ## simulation
        model.simulate(params.t_sim)

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


def run_and_evaluate(data_path, rec_dev, scaling):
    """Runs a short simulation, evaluates it and stores the metadata."""

    params = Parameters(
        data_path=data_path,
        rec_dev=rec_dev,
        N_scaling=scaling,
        K_scaling=scaling,
        t_sim=100.0,
        print_time=False,
    )

    model = Model(params)
    model.create_nodes()
    model.connect()
    model.simulate(params.t_sim)
    model.evaluate([0.0, params.t_sim], [0.0, params.t_sim])
    model.store_metadata()


def test_evaluate_without_spike_recorder(tmp_path):
    """Evaluation is skipped, but metadata is stored, if no spike recorder was used."""

    run_and_evaluate(tmp_path, rec_dev=[], scaling=0.05)

    assert not (tmp_path / "raster_plot.png").exists()
    assert not (tmp_path / "box_plot.png").exists()
    assert (tmp_path / "params.json").is_file()


def test_evaluate_with_spike_recorder(tmp_path):
    """Evaluation creates the raster plot and the box plot if a spike recorder was used."""

    run_and_evaluate(tmp_path, rec_dev=["spike_recorder"], scaling=0.1)

    assert (tmp_path / "raster_plot.png").is_file()
    assert (tmp_path / "box_plot.png").is_file()


if __name__ == "__main__":
    test_simulation()
