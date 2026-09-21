# -*- coding: utf-8 -*-
#
# test_parameter_legacy_parity.py
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Numerical parity checks between the `Parameters` computed fields and the
legacy dict-based derivation logic (formerly `Network.__derive_parameters()`
in `network.py`, before that module was renamed to `model.py`).

`network_params.py` and `stimulus_params.py` in this directory are the
original legacy dict-based parameter files. They've been moved out of the
shipped `microcircuit` package (they have no other purpose any more) and
live here, next to the one test that still needs them, so that pytest's
default import mode picks them up as plain sibling modules -- no package
`__init__.py`, no `microcircuit.` prefix.

`_legacy_derive_parameters()` below is a frozen re-implementation of
`Network.__derive_parameters()` against those dicts. It does NOT call into `microcircuit.helpers` for its
sub-calculations (`num_synapses_from_conn_probs`,
`postsynaptic_potential_to_current`, `dc_input_compensating_poisson`,
`adjust_weights_and_input_to_synapse_scaling`) -- those are frozen locally
below (`_legacy_*`) too. `helpers.py` is live, shared code that both this
test and the current `Parameters` computed fields depend on; if it called
into the live module, a regression introduced inside `helpers.py` itself
would be invisible here, since both sides of the comparison would go
through the same (possibly broken) implementation. This bit us once
already: an errant `.astype(int)` inside the live
`num_synapses_from_conn_probs` truncated an intermediate float before
scaling, shifting connection counts for 4 of 64 population pairs at
non-default scaling -- and this test still passed, because both sides used
the same buggy helper. Keep these frozen copies in sync with the actual
math `main`'s legacy `Network.__derive_parameters()` used, not with
whatever `helpers.py` currently does.
"""

import copy

import numpy as np
import pytest

from microcircuit.parameter_definitions import Parameters
from network_params import default_net_dict
from stimulus_params import default_stim_dict


def _legacy_num_synapses_from_conn_probs(conn_probs, popsize1, popsize2):
    prod = np.outer(popsize1, popsize2)
    return np.log(1.0 - np.array(conn_probs)) / np.log((prod - 1.0) / prod)


def _legacy_postsynaptic_potential_to_current(C_m, tau_m, tau_syn):
    sub = 1.0 / (tau_syn - tau_m)
    pre = tau_m * tau_syn / C_m * sub
    frac = (tau_m / tau_syn) ** sub
    return 1.0 / (pre * (frac**tau_m - frac**tau_syn))


def _legacy_dc_input_compensating_poisson(rate_CC, K_CC_full, tau_syn, PSC_ext):
    return rate_CC * K_CC_full * PSC_ext * tau_syn * 0.001


def _legacy_adjust_weights_and_input_to_synapse_scaling(
    full_num_neurons,
    full_num_synapses,
    K_scaling,
    mean_PSC_matrix,
    PSC_ext,
    tau_syn,
    full_mean_rates,
    DC_amp,
    CC_type,
    rate_CC,
    K_CC_full,
):
    PSC_matrix_new = mean_PSC_matrix / np.sqrt(K_scaling)
    PSC_ext_new = PSC_ext / np.sqrt(K_scaling)

    indegree_matrix = full_num_synapses / full_num_neurons[:, np.newaxis]
    input_rec = np.sum(mean_PSC_matrix * indegree_matrix * full_mean_rates, axis=1)

    DC_amp_new = DC_amp + 0.001 * tau_syn * (1.0 - np.sqrt(K_scaling)) * input_rec

    if CC_type == "poisson":
        input_ext = PSC_ext * K_CC_full * rate_CC
        DC_amp_new += 0.001 * tau_syn * (1.0 - np.sqrt(K_scaling)) * input_ext

    return PSC_matrix_new, PSC_ext_new, DC_amp_new


def _legacy_derive_parameters(net_dict, stim_dict):
    net_dict = copy.deepcopy(net_dict)
    stim_dict = copy.deepcopy(stim_dict)

    num_pops = len(net_dict["populations"])

    full_num_synapses = _legacy_num_synapses_from_conn_probs(
        net_dict["conn_probs"], net_dict["full_num_neurons"], net_dict["full_num_neurons"]
    )

    num_neurons = np.round(net_dict["full_num_neurons"] * net_dict["N_scaling"]).astype(int)
    num_synapses = np.round(
        full_num_synapses * net_dict["N_scaling"] * net_dict["K_scaling"]
    ).astype(int)
    K_CC = np.round(net_dict["K_ext"] * net_dict["K_scaling"]).astype(int)

    PSC_over_PSP = _legacy_postsynaptic_potential_to_current(
        net_dict["neuron_params"]["C_m"],
        net_dict["neuron_params"]["tau_m"],
        net_dict["neuron_params"]["tau_syn"],
    )
    PSC_matrix_mean = net_dict["PSP_matrix_mean"] * PSC_over_PSP
    PSC_ext = net_dict["PSP_exc_mean"] * PSC_over_PSP

    if net_dict["bg_input_type"] == "poisson":
        DC_amp = np.zeros(num_pops)
    else:
        DC_amp = _legacy_dc_input_compensating_poisson(
            net_dict["bg_rate"],
            net_dict["K_ext"],
            net_dict["neuron_params"]["tau_syn"],
            PSC_ext,
        )

    if net_dict["K_scaling"] != 1:
        PSC_matrix_mean, PSC_ext, DC_amp = _legacy_adjust_weights_and_input_to_synapse_scaling(
            net_dict["full_num_neurons"],
            full_num_synapses,
            net_dict["K_scaling"],
            PSC_matrix_mean,
            PSC_ext,
            net_dict["neuron_params"]["tau_syn"],
            net_dict["full_mean_rates"],
            DC_amp,
            net_dict["bg_input_type"],
            net_dict["bg_rate"],
            net_dict["K_ext"],
        )

    num_th_synapses = _legacy_num_synapses_from_conn_probs(
        stim_dict["conn_probs_th"], stim_dict["num_th_neurons"], net_dict["full_num_neurons"]
    )[0]
    weight_th = stim_dict["PSP_th"] * PSC_over_PSP
    if net_dict["K_scaling"] != 1:
        num_th_synapses = num_th_synapses * net_dict["K_scaling"]
        weight_th = weight_th / np.sqrt(net_dict["K_scaling"])
    num_th_synapses = np.round(num_th_synapses).astype(int)

    # final per-population amplitude of transient DC stimulation, as computed
    # inline in the legacy `__create_dc_stim_input` (not stored in stim_dict)
    dc_amp_stim = stim_dict["dc_transient_amp"] * net_dict["K_ext"]

    return {
        "num_pops": num_pops,
        "full_num_synapses": full_num_synapses,
        "num_neurons": num_neurons,
        "num_synapses": num_synapses,
        "K_CC": K_CC,
        "PSC_matrix_mean": PSC_matrix_mean,
        "PSC_ext": PSC_ext,
        "DC_amp": DC_amp,
        "num_th_synapses": num_th_synapses,
        "weight_th": weight_th,
        "dc_amp_stim": dc_amp_stim,
        "PSP_matrix_mean": net_dict["PSP_matrix_mean"],
        "delay_matrix_mean": net_dict["delay_matrix_mean"],
        "delay_th_mean": stim_dict["delay_th_mean"],
    }


def _assert_matches_legacy(params, legacy):
    assert params.num_pops == legacy["num_pops"]
    assert params.full_num_synapses == legacy["full_num_synapses"].tolist()
    assert params.num_neurons == legacy["num_neurons"].tolist()
    assert params.num_synapses == legacy["num_synapses"].tolist()
    assert params.K_CC == legacy["K_CC"].tolist()
    assert np.array(params.PSC_matrix_mean) == pytest.approx(legacy["PSC_matrix_mean"])
    assert params.PSC_ext == pytest.approx(legacy["PSC_ext"])
    assert np.array(params.DC_amp) == pytest.approx(legacy["DC_amp"])
    assert params.num_th_synapses == legacy["num_th_synapses"].tolist()
    assert params.weight_th == pytest.approx(legacy["weight_th"])
    assert np.array(params.dc_transient_amp_populations) == pytest.approx(legacy["dc_amp_stim"])
    assert np.array(params.PSP_matrix_mean) == pytest.approx(legacy["PSP_matrix_mean"])
    assert np.array(params.delay_matrix_mean) == pytest.approx(legacy["delay_matrix_mean"])
    assert params.delay_th_mean == pytest.approx(legacy["delay_th_mean"])


def test_legacy_parity_at_default_scaling():
    legacy = _legacy_derive_parameters(default_net_dict, default_stim_dict)
    params = Parameters()

    _assert_matches_legacy(params, legacy)


def test_legacy_parity_at_scaled_N_and_K():
    net_dict = copy.deepcopy(default_net_dict)
    net_dict["N_scaling"] = 0.2
    net_dict["K_scaling"] = 0.2
    legacy = _legacy_derive_parameters(net_dict, default_stim_dict)

    params = Parameters()
    params.N_scaling = 0.2
    params.K_scaling = 0.2

    _assert_matches_legacy(params, legacy)


def test_legacy_parity_with_poisson_background_input():
    net_dict = copy.deepcopy(default_net_dict)
    net_dict["bg_input_type"] = "poisson"
    net_dict["K_scaling"] = 0.2
    legacy = _legacy_derive_parameters(net_dict, default_stim_dict)

    params = Parameters()
    params.CC_type = "poisson"
    params.K_scaling = 0.2

    _assert_matches_legacy(params, legacy)
