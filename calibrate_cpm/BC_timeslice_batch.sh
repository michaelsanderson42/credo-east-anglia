#!/bin/bash -l
#SBATCH --mem=2000
#SBATCH --ntasks=2
#SBATCH --output=BC_output.txt
#SBATCH --error=BC_error.err
#SBATCH --time=10
#SBATCH --qos=normal
#SBATCH --export=NONE

echo $1 $2 $3 $4 $5 $6 $7 $8 $9
module load scitools
python BC_timeslice_run.py $1 $2 $3 $4 $5 $6 $7 $8 $9
# python BC_timeslice_run_monthly.py $1 $2 $3 $4 $5 $6 $7 $8 $9
# python BC_Reading_timeslice_run.py $1 $2 $3 $4 $5 $6 $7 $8 $9

