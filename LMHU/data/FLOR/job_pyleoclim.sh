#!/usr/bin/env bash
# Wenchang Yang (wenchang@princeton.edu)
# Thu Jan  6 14:20:34 EST 2022
##SBATCH --nodes=1                # node count
##SBATCH --ntasks-per-node=1      # number of tasks per node
#
#SBATCH --ntasks=1               # total number of tasks across all nodes = nodes x ntasks-per-node
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=32G         # memory per cpu-core (4G is default)
#SBATCH --time=48:00:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=all          # send email when job begins/ends/fails
#SBATCH --mail-user=wenchang@princeton.edu
#
##SBATCH --array=1-100#%32        # job array with index values 1, 2, ...,; max job # is 32 if specified
##SBATCH --output=slurm-%A.%a.out # stdout file
##SBATCH --error=slurm-%A.%a.err  # stderr file
#
set -ve
##env settings
#export PATH=/tigress/wenchang/miniconda3/bin:$PATH
#export PYTHONPATH=/tigress/wenchang/wython
#export PYTHONUNBUFFERED=TRUE # see https://stackoverflow.com/questions/230751/how-to-flush-output-of-print-function
#export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK #for multi-threaded job
#ii_job=$SLURM_ARRAY_TASK_ID #for job array
pyscript=linregress_map_FLOR_SST_TC.py
#savefig=savefig
#overwritefig=overwritefig
savefig=" "
overwritefig=" "

python $pyscript $savefig $overwritefig pyleoclim
