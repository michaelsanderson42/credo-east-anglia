#!/bin/bash -l
#SBATCH --mem=2000
#SBATCH --ntasks=2
#SBATCH --output=regrid_obs_batch.out
#SBATCH --error=regrid_obs_batch.err
#SBATCH --time=10
#SBATCH --qos=normal
#SBATCH --export=NONE

module load scitools
python regrid_obs.py $1 $2 $3 $4 $5

