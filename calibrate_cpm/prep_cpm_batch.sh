#!/bin/bash -l
#SBATCH --mem=2000
#SBATCH --ntasks=2
#SBATCH --output=prep_cpm_data.out
#SBATCH --error=prep_cpm_data.err
#SBATCH --time=10
#SBATCH --qos=normal
#SBATCH --export=NONE

module load scitools
python prep_cpm_data.py $1 $2 $3 $4 $5 $6

