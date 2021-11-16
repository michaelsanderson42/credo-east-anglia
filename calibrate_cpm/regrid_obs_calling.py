import os
import glob
import sys
import subprocess
import getpass


def run_all(user_id, project_name, region_name, var_name, baseline_years, monstart, monend):
    """
    Launches batch jobs to preprocess gridded observations
    Interpolates the HadUK-Grid data (on a 1 km grid OSGB projection)
        to the 2.2km rotated polar grid used by UKCP Local.
    """

    if var_name == 'pr':
        obs_var_name = 'rainfall'
    else:
        obs_var_name = var_name

    dobs0 = '/project/ukcp18/ncic_observations/post_processed/badc/ukmo-hadobs/data/insitu/MOHC/'
    dobs1 = 'HadOBS/HadUK-Grid/v1.0.0.0/1km'

    dout = os.path.join('/net/spice/scratch/', user_id, project_name, 'HadUK_on_2.2km', var_name)

    try:
        os.makedirs(dout)
    except FileExistsError:
# directory already exists
        pass

    obs_dir = os.path.join(dobs0, dobs1, obs_var_name, 'day/v20181126')

# List all filenames needed for the given baseline years and start / end months
    obs_filenames = []
    for the_year in list(range(baseline_years[0], baseline_years[1]+1)):
        if the_year == baseline_years[0] and monstart != 1:
            for the_month in list(range(monstart, 13)):
                filename_template = '{}_hadukgrid_uk_1km_day_{:4d}{:02d}*.nc'.format(obs_var_name, the_year, the_month)
                obs_files = glob.glob(os.path.join(obs_dir, filename_template))
                obs_filenames.extend(obs_files)
        elif the_year == baseline_years[1] and monend != 12:
            for the_month in list(range(1, monend+1)):
                filename_template = '{}_hadukgrid_uk_1km_day_{:4d}{:02d}*.nc'.format(obs_var_name, the_year, the_month)
                obs_files = glob.glob(os.path.join(obs_dir, filename_template))
                obs_filenames.extend(obs_files)
        else:
            filename_template = '{}_hadukgrid_uk_1km_day_{:4d}*.nc'.format(obs_var_name, the_year)
            obs_files = glob.glob(os.path.join(obs_dir, filename_template))
            obs_filenames.extend(obs_files)

    obs_filenames.sort()

    for obs_file in obs_filenames:
        cmd = ' '.join(['sbatch', 'regrid_obs_batch.sh', project_name, region_name, var_name, obs_file, dout])
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

    project_name = 'CReDo'
    region_name = 'East_Anglia'
    user_id = getpass.getuser()
    var_name = 'tasmin'  # ['tasmax','tasmin','pr']
    baseline_years = [1980, 2000]
    monstart = 12
    monend = 11

    run_all(user_id, project_name, region_name, var_name, baseline_years, monstart, monend)

