#!/bin/bash -l
#SBATCH --mem=3000
#SBATCH --ntasks=2
#SBATCH --output=merge_bc_timeseries.txt
#SBATCH --error=merge_bc_timeseries.err
#SBATCH --time=3
#SBATCH --qos=normal
#SBATCH --export=NONE

module load scitools
python merge_timeseries.py $1 $2 $3 $4 $5 $6

