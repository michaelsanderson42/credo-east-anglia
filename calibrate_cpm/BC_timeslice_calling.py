import sys
import subprocess


def run_all(project_name, region_name, obsvar, rcmvar, memberIDs, monstart=12, monend=11):

    year_start = [1980, 2020, 2060]  #  1980, 2020, 2060]
    year_end =   [2000, 2040, 2080]  #  2000, 2040, 2080]

# Replace any spaces in the region name with underscores
    rname = '_'.join(region_name.split())

    for m in memberIDs:
        for y in list(range(len(year_start))):
            ID = '{:02d}'.format(m)
            start_month = '{:02d}'.format(monstart)
            end_month = '{:02d}'.format(monend)

            cmd = ' '.join(['sbatch', 'BC_timeslice_batch.sh', project_name, rname, \
                 obsvar, rcmvar, ID, str(year_start[y]), str(year_end[y]), \
                 start_month, end_month])

            print(cmd)

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
    '''
    Bias-correct the CPM data

    Variables must be in pairs with the following names:
    obs var: pr, tasmin, tasmax
    rcm var: pr, tasmin, tasmax
    '''

    project_name = 'CReDo'
    region_name = 'East Anglia'

    obsvar = 'tasmin'
    rcmvar = 'tasmin'
    memberIDs = [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
#   memberIDs = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
#   memberIDs = [1]
    run_all(project_name, region_name, obsvar, rcmvar, memberIDs)

