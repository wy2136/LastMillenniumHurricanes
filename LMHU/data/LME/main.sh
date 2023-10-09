#!/usr/bin/env bash
# Wenchang Yang (wenchang@princeton.edu)
# Fri Jan  7 12:36:24 EST 2022
##SBATCH --nodes=1                # node count
##SBATCH --ntasks-per-node=1      # number of tasks per node
#SBATCH --ntasks=1               # total number of tasks across all nodes = nodes x ntasks-per-node
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=4G         # memory per cpu-core (4G is default)
#SBATCH --time=24:00:00          # total run time limit (HH:MM:SS)
##SBATCH --array=1-100#%32        # job array with index values 1, 2, ...,; max job # is 32 if specified
##SBATCH --output=slurm-%A.%a.out # stdout file
##SBATCH --error=slurm-%A.%a.err  # stderr file
#SBATCH --mail-type=all          # send email when job begins/ends/fails
#SBATCH --mail-user=wenchang@princeton.edu
set -ve
##env settings
#export PATH=/tigress/wenchang/miniconda3/bin:$PATH
#export PYTHONPATH=/tigress/wenchang/wython
#export PYTHONUNBUFFERED=TRUE # see https://stackoverflow.com/questions/230751/how-to-flush-output-of-print-function
#export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK #for multi-threaded job
#ii_job=$SLURM_ARRAY_TASK_ID #for job array
pyscript=sst2tc_lme.py

#python $pyscript
python $pyscript fullForcing
python $pyscript GHG
python $pyscript VOLC_GRA
python $pyscript LULC_HurttPongratz
python $pyscript SSI_VSK_L
python $pyscript ORBITAL
python $pyscript OZONE_AER
python $pyscript 0850cntl
python $pyscript 850forcing

pyscript=mcrun_spread_ctl.py
python $pyscript # -> LME_sstTC_0850cntl_HU_smooth40yr_spread.nc

pyscript=combine_cases.py
python $pyscript # -> LME_HU_7cases_smooth40yr_ensmean.nc
python $pyscript rMDRa # -> LME_rMDRa_7cases_smooth40yr_ensmean.nc
python $pyscript TROPa # -> LME_TROPa_7cases_smooth40yr_ensmean.nc

