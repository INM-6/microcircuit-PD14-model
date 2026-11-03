#!/bin/bash -x

# -*- coding: utf-8 -*-
#
# submit.sh
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

sim_time=$(python3 -c "from microcircuit.parameter_definitions import Parameters; print(int(Parameters.from_yaml('../model_params.yaml').t_sim * 1.0e-3))" | tail -n 1)
range=$(python3 -c "from ruamel.yaml import YAML; print(' '.join(YAML(typ='safe').load(open('../reference_params.yaml'))['RNG_seeds']))")

results="../data/data_T${sim_time}s"
results_log="../log_T${sim_time}s"

for seed in $range; do
    seed=$seed
    data_path=$results/seed-$seed #/time-$(date +"%F-%H-%M-%S")
    log_path=$results_log/seed-$seed
    mkdir -p $data_path
    mkdir -p $log_path
    sbatch --output=$log_path/job.out --error=$log_path/job.err run_job.sh $data_path $seed |& tee $log_path/job.id
done
