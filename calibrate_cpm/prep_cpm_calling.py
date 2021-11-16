import os
import subprocess
import sys


def run_all(project_name, region_name):
    """
    Launches batch jobs to preprocess UKCP18 cpm data  
    """
# UKCP Local member IDs
    memberID = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
    varlist = ['tasmax', 'tasmin']  # ['tasmax', 'tasmin', 'pr']

# Set up the UKCP CPM data periods
# Note that the data were produced from December to November
    year_ranges = [[1980, 2000], [2020, 2040], [2060, 2080]]

    for ID in memberID:
        for var_name in varlist:
            for year_range in year_ranges:
                ystr = '{:4d} {:4d}'.format(year_range[0], year_range[1])
                print(ID, var_name, ystr)
                cmd = ' '.join(['sbatch', 'prep_cpm_batch.sh', project_name, region_name, var_name, ID, ystr])
                try:
                    retcode = subprocess.call(cmd, shell=True)
                    if retcode < 0:
                        print("Child was terminated by signal", -retcode, file=sys.stderr)
                    else:
                        print("Child returned", retcode, file=sys.stderr)
                except OSError as e:
                    print("Execution failed:", e, file=sys.stderr)

    return

if __name__ == '__main__':
    project_name = 'CReDo'  #  'CLIMAR'
    region_name = 'East_Anglia'
    run_all(project_name, region_name)
