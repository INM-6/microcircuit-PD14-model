# PyNEST implementation

[![www.python.org](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org) 
<a href="http://www.nest-simulator.org"> <img src="https://github.com/nest/nest-simulator/blob/master/doc/logos/nest-simulated.png" alt="NEST simulated" width="50"/></a> 

## Installing the python package `microcircuit`

The PyNEST implementation of the model is provided in the form of a python package `microcircuit`.

We recommend installing the python package inside a python environment:
- Create a python environment
  ```bash
  python -m venv venv
  ```
- Activate the python environment:
  ```
  source venv/bin/activate
  ```
- Update pip: 
  ```
  pip install -U pip
  ```

The `microcircuit` python package can be installed by one of the following methods:

1) Install the package directly from PyPI:
    ```bash
    pip install microcircuit
    ```
    
    Optionally, you may want to install additional dependencies by using extra flags:
    | Option | Flag |
    |--|--|
    | runtime testing | `test` |
    | development tools | `dev` |
    | documentation build tools | `doc` |
   
    Example: 
  
    ```bash
    pip install microcircuit[dev,doc] 
    ```

1) Clone the repository and install the python package from the local sources:
   ```bash
    git clone https://github.com/inm-6/microcircuit-PD14-model
    pip install microcircuit-PD14-model/PyNEST
    ```
  
1) Install the package from the repository without cloning the entire repository:
    ```
    pip install "git+https://github.com/INM-6/microcircuit-PD14-model.git/#egg=microcircuit&subdirectory=PyNEST"
    ```

## Software requirements

- NEST (see [NEST installation](https://nest-simulator.readthedocs.io/en/stable/installation))

  We recommend installing NEST locally within the virtual environment:
  ```bash
  git clone https://github.com/nest/nest-simulator
  ## for a specific <VERSION> (e.g. <VERSION>=v3.9), use
  ## git clone --depth 1 --branch <VERSION> https://github.com/nest/nest-simulator
  cd nest-simulator
  mkdir build
  cd build
  pip install -r ../requirements_pynest.txt
  cmake ..
  make
  make install
  ```
- Python 3.x
- docopt-ng, matplotlib, numpy, psutil, ruamel.yaml, scipy (handled by python package dependencies)

## Testing

To enable testing, make sure that the microcircuit package is installed with testing dependencies:
```bash
pip install microcircuit[test]
```

Executing
```bash
pytest
```
in the root directory of the repository `microcircuit-PD14-model` runs the test(s) in `microcircuit-PD14-model/PyNEST/tests`.

## Usage

After installation, the `microcircuit` python package can be imported in a python application using

```python
import microcircuit
```

See [this example](https://microcircuit-pd14-model.readthedocs.io/en/latest/microcircuit_example.html) for a more detailed illustrations of how the package can be used.

### Configuring via YAML

Model, simulation, and stimulus parameters can be set from a YAML file instead of in Python. The YAML file is a *sparse override file*: it only needs to contain the parameters that should differ from the defaults defined in the `Parameters` class. Everything else takes its default from the class, which remains the single source of truth.

Construct the parameters from a file, optionally with per-job overrides on top:

```python
from microcircuit.model import Model
from microcircuit.parameter_definitions import Parameters

P = Parameters.from_yaml("params.yaml")               # defaults + file
P = Parameters.from_yaml("params.yaml", rng_seed=7)   # defaults + file + job-specific values
model = Model(P)
```

`from_yaml()` validates the whole result against the same schema as `Parameters()` itself, so an unknown key, wrong type, or out-of-range value fails immediately at load time rather than surfacing later as a wrong simulation result. If anything is invalid, no instance is created. Derived parameters (e.g. `num_neurons`, `PSC_matrix_mean`) are always recomputed from the primary parameters and cannot be set from a file.

To get a template listing every parameter, commented out, with its default value, description, and unit:

```python
from microcircuit.parameter_definitions import generate_example_config

generate_example_config("params.yaml")
```

Uncomment and edit the lines you want to change. A ready-made example is [examples/params.yaml](examples/params.yaml), which scales the network down to 20 %.

### Bundled entry points

All bundled entry points read their parameters from a YAML file and hardcode nothing else:

| Entry point | Parameter file |
|--|--|
| `python examples/run_microcircuit.py [FILE]` | `examples/params.yaml` next to the script, or `FILE` if given |
| `microcircuit run [--params FILE]` | the small override file shipped with the package (`example_params.yaml`, 20 % scale), or `FILE` if given |
| `microcircuit config [--params FILE]` | same as `run`; prints the full resolved parameter set including derived values |

None of them runs the full-scale model unless a file says so. For setting parameters directly in Python instead, e.g. `P = Parameters(); P.N_scaling = 0.2`, see [this example](https://microcircuit-pd14-model.readthedocs.io/en/latest/microcircuit_example.html).

## Memory requirements

| scaling factor (`= N_scaling = K_scaling`)  | Memory    |
|---------------------------------------------|-----------|
| 0.1 (default)                               |  490 MB   |
| 0.2                                         | 1200 MB   |
| 0.5                                         | 4400 MB   |
| 1                                           |   14 GB   |

## Performance benchmarking
Recent performance benchmarking results for the microcircuit model can be found [here](https://nest-simulator.org/documentation/benchmark_results.html).

## Implementation details

This implementation uses the [`iaf_psc_exp`](https://nest-simulator.org/documentation/models/iaf_psc_exp.html) neuron and the [`static_synapse`](https://nest-simulator.org/documentation/models/static_synapse.html) synapse models provided in [NEST]. 
The network is connected according to the [`fixed_total_number`](https://nest-simulator.org/documentation/synapses/connectivity_concepts.html#random-fixed-total-number) connection rule in NEST. 
The neuron dynamics is integrated in a time-driven manner using exact integration with a simulation step size `sim_resolution` [(Rotter & Diesmann, 1999)][1].

The PyNEST implementation runs with [NEST 3.9](https://github.com/nest/nest-simulator.git) [(Terhorst et al., 2025)][2].

### Simulation parameters (defaults)

| Name             | Value            | Description                                                  |
|------------------|------------------|--------------------------------------------------------------|
| `sim_resolution` | 0.1 ms           | simulation time resolution (duration of one simulation step) |
| `t_presim`       | 500 ms           | duration of pre-simulation phase (warm-up)                   |
| `t_sim`          | 1000 ms          | duration of simulation phase                                 |
| `rec_dev`        | `spike_recorder` | recording device                                             |

## References

[1]: <https://doi.org/10.1007/s004220050570> "Rotter & Diesmann (1999). Exact digital simulation of time-invariant linear systems with applications to neuronal modeling. Biological Cybernetics 81(5-6):381-402. doi:10.1007/s004220050570"
[Rotter & Diesmann (1999), Exact digital simulation of time-invariant linear systems with applications to neuronal modeling. Biological Cybernetics 81(5-6):381-402. doi:10.1007/s004220050570](https://doi.org/10.1007/s004220050570)

[2]: <https://doi.org/10.5281/zenodo.17036827> "Terhorst et al. (2025). NEST 3.9. Zenodo. doi:10.5281/zenodo.17036827"
[Terhorst et al. (2025). NEST 3.9. Zenodo. doi:10.5281/zenodo.17036827](https://doi.org/10.5281/zenodo.17036827)

License
-------

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

This project is licensed under GNU General Public License v2.0 or later.  For details, see [here](https://github.com/INM-6/microcircuit-PD14-model/blob/main/LICENSES/GPL-2.0-or-later.txt).
