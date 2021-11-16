import os
import glob
import getpass
import iris


def load_and_join_obs(datadir_in, region_name, var_name, resolution):
    '''
    The HadUK-Grid data are stored as 1 file per month, so the data for CReDo
    also exist as 1 file per month. Join the files together for bias correction.
    '''

    # Make the filename template
    fname_template = f'{region_name}_{var_name}_obs_hadukgrid_uk_{resolution}_*nc'
    print(datadir_in)
    print(fname_template)

    # Get the names of all files
    filenames = glob.glob(os.path.join(datadir_in, fname_template))
    filenames.sort()

    obs_cubes = iris.cube.CubeList()
    for f in filenames:
        obs_cube = iris.load_cube(f)
        obs_cube.attributes = {}
        obs_cubes.append(obs_cube)

    obs_cube = obs_cubes.concatenate_cube()

# Correct the standard name and variable name for the precipitation observations
    if 'precipitation_amount' in obs_cube.standard_name:
        obs_cube.standard_name = 'precipitation_amount'
        obs_cube.var_name = var_name

    return obs_cube


def main():

    user_id = getpass.getuser()
    project_name = 'CReDo'
    region_name = 'East_Anglia'
    var_name = 'tasmax'
    resolution = '2.2km'

    datadir_in = f'/scratch/{user_id}/{project_name}/HadUK_on_{resolution}/intermediate/{var_name}'
    datadir_out = f'/scratch/{user_id}/{project_name}/HadUK_on_{resolution}/{var_name}'

    obs_cube = load_and_join_obs(datadir_in, region_name, var_name, resolution)
    print(obs_cube)

    # Create directory for the merged data if it does not exist
    try:
        os.makedirs(datadir_out)
    except FileExistsError:
        pass

    # Save the combined data
    fout = f'{region_name}_{var_name}_obs_hadukgrid_uk_{resolution}_day_19801201-20001130.nc'
    iris.save(obs_cube, os.path.join(datadir_out, fout))


if __name__ == '__main__':
    main()

