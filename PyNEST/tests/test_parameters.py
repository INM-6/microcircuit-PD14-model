"""Unit tests for the Pydantic parameter workflow."""

from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

from microcircuit import helpers
from microcircuit.parameter_definitions import Parameters


def test_stimulus_defaults():
    params = Parameters()

    assert params.full_mean_rates == (
        0.903,
        2.965,
        4.414,
        5.876,
        7.569,
        8.633,
        1.105,
        7.829,
    )
    assert params.CC_type == "dc"
    assert params.K_CC_full == (1600, 1500, 2100, 1900, 2000, 1900, 2900, 2100)
    assert params.rate_CC == 8.0
    assert params.delay_CC == 1.5
    assert params.thalamic_input is False
    assert params.th_start == 700.0
    assert params.th_duration == 10.0
    assert params.th_rate == 120.0
    assert params.num_th_neurons == 902
    assert params.conn_probs_th == (
        0.0,
        0.0,
        0.0983,
        0.0619,
        0.0,
        0.0,
        0.0512,
        0.0196,
    )
    assert params.dc_transient is False
    assert params.dc_transient_start == 650.0
    assert params.dc_transient_dur == 100.0
    assert params.dc_transient_amp == 0.3


def test_valid_stimulus_assignment():
    params = Parameters()

    params.full_mean_rates = [1.0] * len(params.populations)
    params.CC_type = "poisson"
    params.K_CC_full = [1000] * len(params.populations)
    params.rate_CC = 0.0
    params.delay_CC = 1.0
    params.thalamic_input = True
    params.th_start = 0.0
    params.th_duration = 20.0
    params.th_rate = 0.0
    params.num_th_neurons = 100
    params.dc_transient = True
    params.dc_transient_start = 0.0
    params.dc_transient_dur = 50.0
    params.dc_transient_amp = -0.5

    assert params.full_mean_rates == (1.0,) * len(params.populations)
    assert params.CC_type == "poisson"
    assert params.K_CC_full == (1000,) * len(params.populations)
    assert params.rate_CC == 0.0
    assert params.delay_CC == 1.0
    assert params.thalamic_input is True
    assert params.th_start == 0.0
    assert params.th_duration == 20.0
    assert params.th_rate == 0.0
    assert params.num_th_neurons == 100
    assert params.dc_transient is True
    assert params.dc_transient_start == 0.0
    assert params.dc_transient_dur == 50.0
    assert params.dc_transient_amp == -0.5


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("rate_CC", -1.0),
        ("delay_CC", 0.0),
        ("delay_CC", -1.0),
        ("th_start", -1.0),
        ("th_duration", 0.0),
        ("th_duration", -1.0),
        ("th_rate", -1.0),
        ("num_th_neurons", 0),
        ("num_th_neurons", -1),
        ("dc_transient_start", -1.0),
        ("dc_transient_dur", 0.0),
        ("dc_transient_dur", -1.0),
    ],
)
def test_invalid_stimulus_assignment_is_rejected(field_name, invalid_value):
    params = Parameters()

    with pytest.raises(ValidationError):
        setattr(params, field_name, invalid_value)


def test_invalid_cc_type_is_rejected():
    params = Parameters()

    with pytest.raises(ValidationError):
        params.CC_type = "not_a_valid_type"


@pytest.mark.parametrize("field_name", ["full_mean_rates", "K_CC_full"])
@pytest.mark.parametrize("invalid_value", [-1.0])
def test_invalid_population_vector_element_is_rejected(field_name, invalid_value):
    params = Parameters()
    values = list(getattr(params, field_name))
    values[0] = invalid_value

    with pytest.raises(ValidationError):
        setattr(params, field_name, values)


@pytest.mark.parametrize("field_name", ["full_mean_rates", "K_CC_full"])
@pytest.mark.parametrize("length_offset", [-1, 1])
def test_invalid_population_vector_length_is_rejected(field_name, length_offset):
    params = Parameters()
    values = [0.0] * (len(params.populations) + length_offset)

    with pytest.raises(ValidationError):
        setattr(params, field_name, values)


@pytest.mark.parametrize("invalid_probability", [-0.1, 1.1])
def test_invalid_thalamic_probability_is_rejected(invalid_probability):
    params = Parameters()
    probabilities = list(params.conn_probs_th)
    probabilities[0] = invalid_probability

    with pytest.raises(ValidationError):
        params.conn_probs_th = probabilities


def test_probability_boundaries_are_valid():
    params = Parameters()
    probabilities = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]

    params.conn_probs_th = probabilities

    assert params.conn_probs_th == tuple(probabilities)


@pytest.mark.parametrize("length_offset", [-1, 1])
def test_invalid_thalamic_probability_length_is_rejected(length_offset):
    params = Parameters()
    probabilities = [0.0] * (len(params.populations) + length_offset)

    with pytest.raises(ValidationError):
        params.conn_probs_th = probabilities


def test_stimulus_parameters_are_serializable():
    params = Parameters(thalamic_input=True, dc_transient=True, CC_type="poisson")

    data = params.model_dump(
        mode="json",
        exclude_computed_fields=True,
    )

    assert data["full_mean_rates"] == list(params.full_mean_rates)
    assert data["CC_type"] == "poisson"
    assert data["K_CC_full"] == list(params.K_CC_full)
    assert data["rate_CC"] == params.rate_CC
    assert data["delay_CC"] == params.delay_CC
    assert data["thalamic_input"] is True
    assert data["conn_probs_th"] == list(params.conn_probs_th)
    assert data["dc_transient"] is True
    assert data["dc_transient_amp"] == params.dc_transient_amp
    assert "populations" not in data


@pytest.mark.parametrize(
    "field_name",
    [
        "full_num_neurons",
        "conn_probs",
        "full_mean_rates",
        "K_CC_full",
        "conn_probs_th",
        "V0_mean_optimized",
        "V0_std_optimized",
        "rec_dev",
    ],
)
def test_population_vectors_are_immutable(field_name):
    params = Parameters()
    value = getattr(params, field_name)

    assert isinstance(value, tuple)
    with pytest.raises(TypeError):
        value[0] = value[0]


def test_populations_are_not_editable_parameters():
    assert "populations" not in Parameters.model_fields
    assert "populations" not in Parameters.model_json_schema()["properties"]


def test_simulation_defaults():
    params = Parameters()

    assert params.t_presim == 500.0
    assert params.t_sim == 1000.0
    assert params.sim_resolution == 0.1
    assert params.rec_dev == ("spike_recorder",)
    assert params.data_path == Path("data")
    assert params.rng_seed == 55
    assert params.local_num_threads == 4
    assert params.rec_V_int == 1.0
    assert params.overwrite_files is True
    assert params.print_time is True
    assert params.store_metadata is True


def test_valid_simulation_assignment():
    params = Parameters()

    params.t_presim = 0.0
    params.t_sim = 0.0
    params.sim_resolution = 0.5
    params.rec_dev = ["spike_recorder", "voltmeter"]
    params.data_path = "results"
    params.rng_seed = 1
    params.local_num_threads = 1
    params.rec_V_int = 0.5
    params.overwrite_files = False
    params.print_time = False
    params.store_metadata = False

    assert params.t_presim == 0.0
    assert params.t_sim == 0.0
    assert params.sim_resolution == 0.5
    assert params.rec_dev == ("spike_recorder", "voltmeter")
    assert params.data_path == Path("results")
    assert params.rng_seed == 1
    assert params.local_num_threads == 1
    assert params.rec_V_int == 0.5
    assert params.overwrite_files is False
    assert params.print_time is False
    assert params.store_metadata is False


def test_empty_rec_dev_is_valid():
    params = Parameters()

    params.rec_dev = []

    assert params.rec_dev == ()


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("t_presim", -1.0),
        ("t_sim", -1.0),
        ("sim_resolution", 0.0),
        ("sim_resolution", -1.0),
        ("rng_seed", 0),
        ("rng_seed", -1),
        ("local_num_threads", 0),
        ("local_num_threads", -1),
        ("rec_V_int", 0.0),
        ("rec_V_int", -1.0),
    ],
)
def test_invalid_simulation_assignment_is_rejected(field_name, invalid_value):
    params = Parameters()

    with pytest.raises(ValidationError):
        setattr(params, field_name, invalid_value)


def test_invalid_rec_dev_entry_is_rejected():
    params = Parameters()

    with pytest.raises(ValidationError):
        params.rec_dev = ["not_a_device"]


def test_unknown_simulation_field_is_rejected():
    with pytest.raises(ValidationError):
        Parameters(not_a_real_simulation_field=1)


def test_simulation_parameters_are_serializable():
    params = Parameters(data_path="results", rec_dev=["spike_recorder", "voltmeter"])

    data = params.model_dump(
        mode="json",
        exclude_computed_fields=True,
    )

    assert data["t_presim"] == params.t_presim
    assert data["t_sim"] == params.t_sim
    assert data["sim_resolution"] == params.sim_resolution
    assert data["rec_dev"] == ["spike_recorder", "voltmeter"]
    assert data["data_path"] == "results"
    assert data["rng_seed"] == params.rng_seed
    assert data["local_num_threads"] == params.local_num_threads
    assert data["rec_V_int"] == params.rec_V_int
    assert data["overwrite_files"] is True
    assert data["print_time"] is True
    assert data["store_metadata"] is True


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("C_m", 0.0),
        ("C_m", -1.0),
        ("tau_m", 0.0),
        ("tau_m", -1.0),
        ("tau_syn", 0.0),
        ("tau_syn", -1.0),
        ("tau_ref", 0.0),
        ("tau_ref", -1.0),
    ],
)
def test_invalid_neuron_assignment_is_rejected(field_name, invalid_value):
    params = Parameters()

    with pytest.raises(ValidationError):
        setattr(params, field_name, invalid_value)


## derived (secondary) parameters


def test_stimulus_stop_times_default():
    params = Parameters()

    assert params.th_stop == params.th_start + params.th_duration
    assert (
        params.dc_transient_stop == params.dc_transient_start + params.dc_transient_dur
    )
    assert params.th_stop == 710.0
    assert params.dc_transient_stop == 750.0


@pytest.mark.parametrize(
    ("start_field", "duration_field", "stop_field"),
    [
        ("th_start", "th_duration", "th_stop"),
        ("dc_transient_start", "dc_transient_dur", "dc_transient_stop"),
    ],
)
def test_stimulus_stop_times_track_primary_parameters(
    start_field, duration_field, stop_field
):
    params = Parameters()

    setattr(params, start_field, 100.0)
    setattr(params, duration_field, 50.0)

    assert getattr(params, stop_field) == 150.0


def test_I_CC_default():
    params = Parameters()

    assert params.I_CC == pytest.approx(
        params.rate_CC
        * (params.weight_exc_mean / params.J_unit)
        * params.tau_syn
        * 0.001
    )


@pytest.mark.parametrize("field_name", ["rate_CC", "weight_exc_mean", "tau_syn"])
def test_I_CC_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.I_CC

    setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.I_CC != pytest.approx(baseline)


def test_I_CC_populations_scales_with_K_CC_full():
    params = Parameters()

    assert params.I_CC_populations == [
        pytest.approx(k * params.I_CC) for k in params.K_CC_full
    ]


def test_I_CC_populations_tracks_K_CC_full():
    params = Parameters()

    params.K_CC_full = [1.0] * len(params.populations)

    assert params.I_CC_populations == [pytest.approx(params.I_CC)] * len(
        params.populations
    )


def test_num_neurons_rounds_rather_than_truncates():
    params = Parameters()
    params.N_scaling = 0.2

    assert params.num_neurons == [round(n * 0.2) for n in params.full_num_neurons]
    # regression check: 20683 * 0.2 = 4136.6, which truncates to 4136 but
    # rounds to 4137 -- catches a silent switch back to `.astype(int)`.
    assert params.num_neurons[0] == 4137


def test_dc_transient_amp_populations_scales_with_K_CC_full():
    params = Parameters()

    assert params.dc_transient_amp_populations == [
        pytest.approx(k * params.dc_transient_amp) for k in params.K_CC_full
    ]


@pytest.mark.parametrize("field_name", ["dc_transient_amp", "K_CC_full"])
def test_dc_transient_amp_populations_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.dc_transient_amp_populations

    if field_name == "K_CC_full":
        setattr(params, field_name, [2.0 * k for k in params.K_CC_full])
    else:
        setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.dc_transient_amp_populations != pytest.approx(baseline)


def test_num_pops_default():
    params = Parameters()

    assert params.num_pops == 8 == len(params.populations)


def test_J_unit_default():
    params = Parameters()

    PSC_over_PSP = helpers.postsynaptic_potential_to_current(
        params.C_m, params.tau_m, params.tau_syn
    )
    assert params.J_unit == pytest.approx(1 / PSC_over_PSP)


@pytest.mark.parametrize("field_name", ["C_m", "tau_m", "tau_syn"])
def test_J_unit_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.J_unit

    setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.J_unit != pytest.approx(baseline)


def test_R_m_default():
    params = Parameters()

    assert params.R_m == pytest.approx(params.tau_m / params.C_m * 1000.0)


@pytest.mark.parametrize("field_name", ["tau_m", "C_m"])
def test_R_m_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.R_m

    setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.R_m != pytest.approx(baseline)


def test_full_num_synapses_default():
    params = Parameters()

    expected = helpers.num_synapses_from_conn_probs(
        params.conn_probs, params.full_num_neurons, params.full_num_neurons
    )
    assert params.full_num_synapses == expected.tolist()


def test_num_synapses_scales_with_N_and_K_scaling():
    params = Parameters()
    params.N_scaling = 0.5
    params.K_scaling = 0.5

    expected = [[round(s * 0.25) for s in row] for row in params.full_num_synapses]

    assert params.num_synapses == expected


@pytest.mark.parametrize("field_name", ["N_scaling", "K_scaling", "conn_probs"])
def test_num_synapses_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.num_synapses

    if field_name == "conn_probs":
        setattr(params, field_name, [[0.5] * 8] * 8)
    else:
        setattr(params, field_name, 0.5 * getattr(params, field_name))

    assert params.num_synapses != baseline


def test_K_CC_rounds_rather_than_truncates():
    params = Parameters()
    params.K_scaling = 0.3

    # regression check: matches the `num_neurons` rounding fix -- must not
    # silently regress to `.astype(int)` truncation.
    assert params.K_CC == [round(k * 0.3) for k in params.K_CC_full]


@pytest.mark.parametrize("field_name", ["K_CC_full", "K_scaling"])
def test_K_CC_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.K_CC

    if field_name == "K_CC_full":
        setattr(params, field_name, [2.0 * k for k in params.K_CC_full])
    else:
        setattr(params, field_name, 2.0 * params.K_scaling)

    assert params.K_CC != baseline


def test_PSC_ext_default_matches_unscaled_formula():
    params = Parameters()  # K_scaling == 1.0 -> adjustment is a no-op

    expected = params.weight_exc_mean / params.J_unit
    assert params.PSC_ext == pytest.approx(expected)


def test_DC_amp_zero_when_CC_type_poisson():
    params = Parameters()
    params.CC_type = "poisson"

    assert params.DC_amp == [0.0] * params.num_pops


def test_DC_amp_matches_unscaled_formula_when_CC_type_dc():
    params = Parameters()  # default CC_type == "dc", K_scaling == 1.0

    expected = helpers.dc_input_compensating_poisson(
        params.rate_CC, np.array(params.K_CC_full), params.tau_syn, params.PSC_ext
    )
    assert params.DC_amp == pytest.approx(expected.tolist())


@pytest.mark.parametrize("field_name", ["weight_exc_mean", "K_scaling"])
def test_PSC_ext_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.PSC_ext

    setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.PSC_ext != pytest.approx(baseline)


@pytest.mark.parametrize("field_name", ["weight_exc_mean", "g", "K_scaling"])
def test_PSC_matrix_mean_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.PSC_matrix_mean

    setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.PSC_matrix_mean != baseline


def test_subthreshold_populations_empty_when_CC_type_poisson():
    params = Parameters()
    params.CC_type = "poisson"

    assert params.subthreshold_populations == []


def test_subthreshold_populations_flags_when_dc_amp_too_low():
    params = Parameters()
    params.CC_type = "dc"
    params.weight_exc_mean = 1e-6  # collapses PSC_ext/DC_amp toward ~0

    I_rh = helpers.compute_rheo_base_current(
        params.V_th, params.V_reset, params.C_m, params.tau_m
    )
    assert I_rh > 0  # sanity: rheobase is positive with defaults
    assert set(params.subthreshold_populations) == set(params.populations)


def test_PSP_matrix_mean_exc_inh_pattern_and_doubled_entry():
    params = Parameters()
    matrix = params.PSP_matrix_mean

    assert matrix[1][0] == pytest.approx(params.weight_exc_mean)  # exc column
    assert matrix[1][1] == pytest.approx(
        params.weight_exc_mean * params.g
    )  # inh column
    assert matrix[0][2] == pytest.approx(
        2.0 * params.weight_exc_mean
    )  # doubled L4E->L2/3E


@pytest.mark.parametrize("field_name", ["weight_exc_mean", "g"])
def test_PSP_matrix_mean_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.PSP_matrix_mean

    setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.PSP_matrix_mean != baseline


def test_delay_matrix_mean_exc_inh_pattern():
    params = Parameters()
    matrix = params.delay_matrix_mean

    assert matrix[0][0] == pytest.approx(params.delay_exc_mean)
    assert matrix[0][1] == pytest.approx(params.delay_inh_mean)


def test_num_th_synapses_default():
    params = Parameters()

    expected = helpers.num_synapses_from_conn_probs(
        params.conn_probs_th, params.num_th_neurons, params.full_num_neurons
    )[0]
    assert params.num_th_synapses == np.round(expected).astype(int).tolist()


@pytest.mark.parametrize("field_name", ["conn_probs_th", "num_th_neurons", "K_scaling"])
def test_num_th_synapses_tracks_primary_parameters(field_name):
    params = Parameters()
    baseline = params.num_th_synapses

    if field_name == "conn_probs_th":
        setattr(params, field_name, [0.5] * 8)
    else:
        setattr(params, field_name, 2.0 * getattr(params, field_name))

    assert params.num_th_synapses != baseline


def test_weight_th_default_matches_unscaled_formula():
    params = Parameters()  # K_scaling == 1

    assert params.weight_th == pytest.approx(params.weight_exc_mean / params.J_unit)


def test_weight_th_scales_by_inverse_sqrt_K_scaling():
    params = Parameters()
    baseline = params.weight_th

    params.K_scaling = 0.25

    assert params.weight_th == pytest.approx(baseline / (0.25**0.5))


def test_delay_th_mean_matches_delay_exc_mean():
    params = Parameters()

    assert params.delay_th_mean == pytest.approx(params.delay_exc_mean)

    params.delay_exc_mean = 2.0
    assert params.delay_th_mean == pytest.approx(2.0)


@pytest.mark.parametrize(
    "field_name",
    [
        "th_stop",
        "dc_transient_stop",
        "I_CC",
        "I_CC_populations",
        "num_neurons",
        "dc_transient_amp_populations",
        "num_pops",
        "J_unit",
        "R_m",
        "full_num_synapses",
        "num_synapses",
        "K_CC",
        "PSC_matrix_mean",
        "PSC_ext",
        "DC_amp",
        "subthreshold_populations",
        "PSP_matrix_mean",
        "delay_matrix_mean",
        "num_th_synapses",
        "weight_th",
        "delay_th_mean",
    ],
)
def test_derived_secondary_fields_are_read_only(field_name):
    params = Parameters()

    with pytest.raises(AttributeError):
        setattr(params, field_name, 0.0)
