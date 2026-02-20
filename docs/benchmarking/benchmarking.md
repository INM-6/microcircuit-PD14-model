# Performance benchmarking

<img src="figures/Senk26_012001.png" width="800"/>

Spiking network model (PD14) of full circuitry below $1\ \text{mm}^2$ surface area of cerebral cortex serves as benchmark for neuromorphic technologies.
The statistics (dark cyan curve) of the simulated activity (dark cyan dots) is compared to reference data (thick yellow curve). Once sufficient accuracy is confirmed, the power measured during the simulation phase (light gray background) yields the consumed energy (dark cyan area corresponds to end point of light red curve, dark blue area indicates network construction phase, dark gray idle phase). The performance benchmark result (dark cyan star) contrasts the real-time factor (defined as the ratio of required wall-clock time and biological time covered by the model) against the required energy (expressed as energy per synaptic event). Figure from [(Senk et al., 2026)][1].

## Performance data of different computing platforms

<img src="figures/performance_summary.png" width="800"/>

Progress of the community in reduction of time to solution and energy consumption for the PD14 model. Colors group
hardware architectures and shapes indicate algorithmic approach (legend). Abbreviations in panels further disambiguate 
individual studies. (a) Ratio between time passed on wall-clock and stretch of time covered by the model (real-time factor) versus the
year of publication in semi logarithmic representation. (b) Real-time factor as a function of energy per synaptic event in double
logarithmic representation. Dashed line from fit through all data points with a slope of one. (c) Real-time factor versus process
node in double logarithmic representation. Dashed line from fit through CPU and GPU data points with a slope of two. Citations
of studies and values are given in this [table](figures/performance_summary.md). Figure from [(Senk et al., 2026)][1].

## Benchmarking recipe

| | |
|----------------|-----------------|
| External drive | State whether DC or Poisson is used|
| Initial conditions | Amended initial conditions: distribute membrane potentials normally with population-specific mean and variance|
| Warm-up time  | Discard the initial 500 ms of model time from the data to be analyzed|
| Simulation duration | Accuracy: $T_\text{model}=15\ \text{min}$, performance:  $T_\text{model}\ge 10\ \text{s}$|
| Repeated simulations | Average across ten random seeds|
| Spike recording | Accuracy: yes, performance: no|
| Accuracy | Compute distributions of 1) single-neuron *firing rate* (FR), 2) *coefficient of variation* (CV) of the inter-spike intervals (ISI), and 3) short-term spike-count *correlation coefficients* (CC), and compare with reference data|
| Performance | Measure real-time factor $q_\text{RTF}$ and the energy per synaptic event $E_\text{syn}$ (include all contributions necessary for running the simulations at the power outlet)|

Checklist with recommended model and simulation parameters for the PD14 model. Table from [(Senk et al., 2026)][1].

## References

[1]: <https://doi.org/10.1088/2634-4386/ae379a> "Senk et al. (2026). Constructive community race: full-density spiking neural network model drives neuromorphic computing. Neuromorphic Computing and Engineering 6(1):012001. doi:10.1088/2634-4386/ae379a" 
[Senk et al. (2026). Constructive community race: full-density spiking neural network model drives neuromorphic computing. Neuromorphic Computing and Engineering 6(1):012001. doi:10.1088/2634-4386/ae379a](https://doi.org/10.1088/2634-4386/ae379a)



