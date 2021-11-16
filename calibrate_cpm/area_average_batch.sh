#!/bin/bash -l
#SBATCH --mem=2000
#SBATCH --ntasks=2
#SBATCH --output=area_average_output.txt
#SBATCH --error=area_average_error.err
#SBATCH --time=10
#SBATCH --qos=normal
#SBATCH --export=NONE

module load scitools
python area_average_cpm.py $1 $2 $3 $4 $5 $6

