import os
import glob
import subprocess
import sys

def run_all(var_name, memberID, year_ranges, monstart, monend):
    """
    Launches batch jobs to preprocess UKCP18 cpm data  
    """

    mstart = '{:02d}'.format(monstart)
    mend = '{:02d}'.format(monend)

# Set up the UKCP CPM data periods
# Note that the data were produced from December to November

    for ID in memberID:
        for year_range in year_ranges:
            ystr = '{:4d} {:4d}'.format(year_range[0], year_range[1])
            print(ID, var_name, ystr)
            cmd = ' '.join(['sbatch', 'area_average_batch.sh', var_name, ID, ystr, mstart, mend])
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

# UKCP Local member IDs
    memberID=['01']  #, '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

    var_name = 'tasmax'  #, ['tasmax', 'tasmin', 'pr']
    year_ranges = [[1980, 2000], [2020, 2040], [2060, 2080]]
    monstart = 12
    monend = 11

    run_all(var_name, memberID, year_ranges, monstart, monend)

