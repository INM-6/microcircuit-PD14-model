#!/bin/bash -x

# -*- coding: utf-8 -*-
#
# submit.sh
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

sim_time=$(python3 -c "import sys; sys.path.append('../'); from params import params as ref_dict; print(int(ref_dict['t_sim'] * 1.0e-3))")
range=$(python3 -c "import sys; sys.path.append('../'); from params import params as ref_dict; print(' '.join(ref_dict['RNG_seeds']))")

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
