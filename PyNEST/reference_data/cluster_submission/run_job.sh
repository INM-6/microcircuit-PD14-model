#!/bin/bash -x

# -*- coding: utf-8 -*-
#
# run_job.sh
#
# This file is part of https://github.com/INM-6/microcircuit-PD14-model
#
# SPDX-License-Identifier: GPL-2.0-or-later

#SBATCH --partition=hamsteinZen3
#SBATCH --nodes=1
#SBATCH --tasks-per-node=2
#SBATCH --cpus-per-task=64
#SBATCH --time=05:00:00

set -exo pipefail

date +"%F.%T.%N"

DATA_PATH=$1
if [ -z $DATA_PATH ]; then
    DATA_PATH=data
fi

SEED=$2
if [ -z $SEED ]; then
    SEED=12345
fi

set --

# Load environment
source ~/projects/microcircuit-PD14-model/PyNEST/reference_data/cluster_submission/env.sh

#source jemalloc.sh

export NUMEXPR_MAX_THREADS=64
export OMP_PROC_BIND=TRUE
export OMP_NUM_THREADS=64
export OMP_DISPLAY_ENV=TRUE

env

module list

scontrol show jobid ${SLURM_JOBID} -dd

# Execute script
srun --mpi=pmix python3 ~/projects/microcircuit-PD14-model/PyNEST/reference_data/generate_reference_data.py --seed=$SEED --path=$DATA_PATH
srun --mpi=pmix python3 ~/projects/microcircuit-PD14-model/PyNEST/reference_data/analyze_reference_data.py --seed=$SEED --path=$DATA_PATH

scontrol show jobid ${SLURM_JOBID} -dd
