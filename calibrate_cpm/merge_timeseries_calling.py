import sys
import subprocess


def run_all(project_name, region_name, var_name, years_start, years_end, memberIDs):

    for member in memberIDs:
        ID = '{:02d}'.format(member)    #   memberID
        for y in list(range(len(years_start))):
            year_min = '{:4d}'.format(years_start[y])
            year_max = '{:4d}'.format(years_end[y])

            cmd = ' '.join(['sbatch', 'merge_timeseries_batch.sh', project_name, region_name, \
                var_name, ID, year_min, year_max])
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


def main():

    project_name = 'CReDo'  #  'CLIMAR'
    region_name = 'East_Anglia'
    var_name = 'tasmax' #  'tasmax', 'tasmin', 'pr'
    years_start = [1980, 2020, 2060]
    years_end = [2000, 2040, 2080]

    memberIDs = [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
#   memberIDs = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
#   memberIDs = [1]

    run_all(project_name, region_name, var_name, years_start, years_end, memberIDs)


if __name__ == '__main__':
    main()
