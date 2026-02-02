# Cortical microcircuit model (Potjans & Diesmann, 2014)

## Overview

[This repository](https://github.com/INM-6/microcircuit-PD14-model) contains a detailed mathematical description and a reference implementation of the model of a cortical microcircuit proposed by [Potjans & Diesmann (2014, The cell-type specific cortical microcircuit: relating structure and activity in a full-scale spiking network model. Cerebral Cortex, 24(3), 785-806)](https://doi.org/10.1093/cercor/bhs358).
The model describes the neuronal circuitry under one square millimeter of cortical surface.
It comprises four cortical layers (L2/3, L4, L5, L6), each represented by a randomly connected network of excitatory and inhibitory point neurons.
The network connectivity is derived from anatomical and electrophysiological data.
Connection probabilities between neurons in the network are highly specific and depend on the cell type (excitatory, inhibitory) and on the locations (cortical layers) of the pre- and postsynaptic neurons.
In contrast to this high specificity in the connectivity, all neurons in the network are identical and share the same dynamics and parameters, irrespective of their type and location.
Similarly, all synapses are described by an identical dynamics, and differ only in the synaptic weight and spike-transmission latencies.
Synaptic weights and spike transmission latencies are randomly drawn from distributions which depend only on the type of the presynaptic neuron (excitatory or inhibitory), but are otherwise identical for all neurons and connections (with one exception).
In addition to inputs from the local network, neurons receive external inputs representing thalamic afferents and cortico-cortical inputs from more distant cortical regions.

The original purpose of this model was to understand the relationship between the connectivity and the spiking activity within local cortical circuits.
Specifically, the model demonstrates that the observed cell-type and layer specificity of in-vivo firing rates is largely explained by the specificity in the number of connections between cortical subpopulations, and doesn't require a specificity in single neuron or synapse dynamics.

|  |  |  |
|--|--|--|
| <img src="figures/potjans_2014_microcircuit.png" width="300"/> | <img src="figures/potjans_2014_raster_plot.png" width="400"/> | <img src="figures/potjans_2014_box_plot.png" width="400"/> |

*Sketch of the cortical microcircuit model (left), spiking activity (middle) and distributions of time averaged single-neuron firing rates across neurons in each subpopulation (right). Adapted from ([van Albada et al., 2018](https://doi.org/10.3389/fnins.2018.00291))*

In recent years, the model became an established Computational Neuroscience benchmark for various soft- and hardware architectures ([van Albada et al., 2018](https://doi.org/10.3389/fnins.2018.00291); [Jordan et al., 2018](https://doi.org/10.3389/fninf.2018.00002); [Rhodes et al., 2020](https://doi.org/10.1098/rsta.2019.0160); [Dasbach et al., 2021](https://doi.org/10.3389/fnins.2021.757790); [Albers et al., 2022](https://doi.org/10.3389/fninf.2022.837549); [Kurth et al., 2022](https://doi.org/10.1088/2634-4386/ac55fc); [Heittmann et al., 2022](https://doi.org/10.3389/fnins.2021.728460); [Pronold et al., 2022](https://doi.org/10.3389/fninf.2021.785068); [Pronold et al., 2022](https://doi.org/10.1016/j.parco.2022.102952); [Golosio et al., 2023](https://doi.org/10.3390/app13179598); [Kauth et al., 2023](https://doi.org/10.3389/fncom.2023.1144143); [Schmidt et al., 2024](https://doi.org/10.48550/arXiv.2412.02619); [Senk et al., 2025](https://doi.org/10.48550/arXiv.2505.21185)).

A community review ([Plesser et al., 2025](https://doi.org/10.1093/cercor/bhaf295)) prepared on the occassion of the 10th anniversary of the original publication of the model provides an historical account of the impact of the model.

## Model description
[<img src="figures/modeldescription_icon.png" height="200"/>](https://microcircuit-pd14-model.readthedocs.io/en/latest/_static/microcircuit-pd14-model.pdf)

<!-- https://microcircuit-PD14-model.readthedocs.io/en/latest/model_description.html -->

A detailed mathematical, implementation-agnostic description of the model and its parameters is provided [here](https://microcircuit-pd14-model.readthedocs.io/en/latest/_static/microcircuit-pd14-model.pdf).

## Model implementations
[<img src="figures/modelimplementation_icon.png" height="200"/>](https://microcircuit-PD14-model.readthedocs.io/en/latest/pynest_implementation.html)

A PyNEST implementation in the form of a Python package is found [here](https://microcircuit-PD14-model.readthedocs.io/en/latest/pynest_implementation.html).

## Publications
[<img src="figures/publications_icon.png" height="200"/>](https://microcircuit-PD14-model.readthedocs.io/en/latest/publications/publications.html)

A list of studies citing and/or using the microcircuit model is given [here](https://microcircuit-PD14-model.readthedocs.io/en/latest/publications/publications.html).

## Repository contents

|  |  |
|--|--|
| [`docs`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/docs) | documentation|
| &emsp;[`docs/model_description`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/docs/model_description) | model description (implementation agnostic) |
| &emsp;[`docs/benchmarking`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/docs/benchmarking) | performance benchmarking |
| &emsp;[`docs/publications`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/docs/publications) | publications citing/using the microcircuit model|
| [`PyNEST`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/PyNEST) | PyNEST implementation (python package)|
| &emsp;[`PyNEST/src/microcircuit`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/PyNEST/src/microcircuit) | source code |
| &emsp;[`PyNEST/examples`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/PyNEST/examples) | examples illustrating usage of the python package |
| &emsp;[`PyNEST/reference_data`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/PyNEST/reference_data) | reference spike data (generation and verification) |
| &emsp;[`PyNEST/tests`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/PyNEST/tests) | unit tests |
| [`figures`](https://github.com/INM-6/microcircuit-PD14-model/blob/main/figures) | overview figures |

## Contact
- [Johanna Senk](mailto:j.senk@fz-juelich.de)
- [Tom Tetzlaff](mailto:t.tetzlaff@fz-juelich.de)

## Contribute
We welcome contributions to the documentation and the code. For bug reports, feature requests, documentation improvements, or other issues, please create a [GitHub issue](https://github.com/INM-6/microcircuit-PD14-model/issues/new/choose).

## License

The material in this repository is subject to different licenses:

- All material outside the `PyNEST` folder is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa]. For details, see [here](LICENSES/CC-BY-NC-SA-4.0.txt).
  [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

- The material inside the `PyNEST` folder is licensed under the [GNU General Public License v2.0 or later](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html). For details, see [here](LICENSES/GPL-2.0-or-later.txt).
  [![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

