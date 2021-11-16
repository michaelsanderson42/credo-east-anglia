import os
import sys
import glob
import getpass
import iris
from cf_units import Unit


def regrid_obs(user_id, project_name, region_name, var_name, obs_filename, out_dir):

    #get a target output grid. Need a grid for the subregion (e.g. Bristol), not the full UKCP Local grid.
    dlocal = os.path.join('/net/spice/scratch/', user_id, project_name, 'cpm_prep/01/', var_name)
    filename_template = '_'.join([region_name, var_name]) + '*.nc'
    cpm = iris.load_cube(sorted(glob.glob(os.path.join(dlocal, filename_template)))[0])
 
# Set up and perform the regridding
    obs_1km = iris.load_cube(obs_filename)
    del obs_1km.attributes['creation_date'] # to aid later collapsing
    regridder = iris.analysis.Linear().regridder(obs_1km[0], cpm[0])
    obs_regridded = regridder(obs_1km)

# Add missing coordinates to the regridded observations. Modify the labels to remove the degree symbol.
    obs_regridded.add_aux_coord(cpm.coord('latitude'), data_dims=[1,2])
    obs_regridded.add_aux_coord(cpm.coord('longitude'), data_dims=[1,2])
    if var_name == 'tasmax':
        plot_label = 'Maximum air temperature at 1.5m (degC)'
        obs_regridded.attributes['label_units'] = 'degC'
    elif var_name == 'tasmin':
        plot_label = 'Minimum air temperature at 1.5m (degC)'
        obs_regridded.attributes['label_units'] = 'degC'
    elif var_name == 'pr':
        plot_label = var_name
#       obs_regridded.var_name = 'pr'
        obs_regridded.attributes['label_units'] = 'mm/day'
        obs_regridded.units = Unit('kg m-2 day-1')
    else:
        plot_label = var_name

    obs_regridded.attributes['plot_label'] = plot_label

# Construct the output filename and save the regridded data
    file_parts = os.path.basename(obs_filename).split('_')
    fhead = f'{region_name}_{var_name}_obs'
    fend = '_'.join(file_parts[-5:])
    fout = '_'.join([fhead, fend.replace('1km', '2.2km')])
    print('fout=',fout)
    iris.save(obs_regridded, os.path.join(out_dir, fout))

    return


if __name__ == '__main__':

    user_id = getpass.getuser()
    project_name = sys.argv[1]
    region_name = sys.argv[2]
    var_name = sys.argv[3]
    obs_filename = sys.argv[4]
    out_dir = sys.argv[5]
    print(project_name, region_name, var_name, obs_filename)
    regrid_obs(user_id, project_name, region_name, var_name, obs_filename, out_dir)
