#!/usr/bin/env bash
# Wenchang Yang (wenchang@princeton.edu)
# Mon Oct  9 15:01:33 EDT 2023
##SBATCH --nodes=1                # node count
##SBATCH --ntasks-per-node=1      # number of tasks per node
# 
#SBATCH --ntasks=1               # total number of tasks across all nodes = nodes x ntasks-per-node
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=16G         # memory per cpu-core (4G is default)
#SBATCH --time=24:00:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=all          # send email when job begins/ends/fails
#SBATCH --mail-user=wenchang@princeton.edu
# 
##SBATCH --array=1-100#%32        # job array with index values 1, 2, ...,; max job # is 32 if specified
##SBATCH --output=slurm-%A.%a.out # stdout file
##SBATCH --error=slurm-%A.%a.err  # stderr file
set -ve
##env settings
#export PATH=/tigress/wenchang/miniconda3/bin:$PATH
#export PYTHONPATH=/tigress/wenchang/wython
#export PYTHONUNBUFFERED=TRUE # see https://stackoverflow.com/questions/230751/how-to-flush-output-of-print-function
#export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK #for multi-threaded job
#ii_job=$SLURM_ARRAY_TASK_ID #for job array
for pyscript in \
Fig01.py \
Fig02.py \
Fig03.py \
Fig04.py \
FigS_heatmaps_corr_liz_lme_HU.py \
FigS_heatmaps_corr_liz_lmr.py \
FigS_maps_corr_tc_sst.py \
FigS_maps_ssta_LME.py \
FigS_maps_ssta_LMR2019.py \
FigS_pdf_corr_sedimentHU_LME.py \
FigS_pdf_corr_sedimentHU_LMR.py \
;do
#echo $pyscript
    python $pyscript savefig 
done
