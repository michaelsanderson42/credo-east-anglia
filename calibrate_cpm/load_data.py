'''
Routines to load UKCP18 CPM data and HadUK-Grid observations
for CLIMAR project whose focus is Bristol.
'''

import os
import sys
import glob
import iris
import numpy as np
from cf_units import Unit


def ukcp18_callback(cube, field, filename):
    '''
    Ensure cubes read in are converted to common units and common names of variables,
    use masked arrays of 32-bit floats, and do a couple of other bits of tidying,
    which ensure that things all concatenate/merge properly in all cases...
    '''

# Add time coord bounds if not present:
    if not cube.coord('time').has_bounds():
        cube.coord('time').guess_bounds()

# Check and change names of units if needed.
# Convert temperatures in K to C, and rainfall to mm per day (i.e. kg m-2 day-1)
# Ensure non-standard unit names are changed to CF-compliant ones.
    c_units = str(cube.units)
    if 'Celsius' in c_units:
        cube.units = Unit('celsius')
    if c_units == 'K':
        cube.convert_units('celsius')
    elif c_units == 'kg m-2 s-1':
        cube.convert_units('kg m-2 day-1')
    elif c_units == 'mm/day':
        cube.units = Unit('kg m-2 day-1')
    elif c_units == 'mm':
        cube.units = Unit('kg m-2 day-1')

# Add standard_name and long_name if undefined - the standard_name is used by the
# PyCAT bias correction code in 'methods.py' to select the appropriate method
# for the given variable.

    if cube.standard_name is None:
        if cube.var_name in ['tmax', 'tasmax', 'tx', 'mx2t','daily_maximum_2_metre_temperature']:
            cube.standard_name = 'air_temperature'
            cube.long_name = "Daily Maximum Near-Surface Air Temperature"
        elif cube.var_name in ['tmin', 'tasmin', 'tn', 'mn2t','daily_minimum_2_metre_temperature']:
            cube.standard_name = 'air_temperature'
            cube.long_name = "Daily Minimum Near-Surface Air Temperature"
        elif cube.var_name in ['tas', 'daily_mean_2_metre_temperature']:
            cube.standard_name = 'air_temperature'
            cube.long_name = "Daily Mean Near-Surface Air Temperature"
        elif cube.var_name in ['prate', 'prcp', 'pr', 'precip', 'precipitation', 'tp', 'rainfall','precipitation_rate']:
            cube.standard_name = 'precipitation_amount'
            cube.long_name = 'Precipitation'
        elif cube.var_name == 'rhstmax':
            cube.standard_name = 'relative_humidity'
            cube.long_name = 'Near-Surface Relative Humidity at time of maximum temperature'
        elif cube.var_name == 'rh':
            cube.standard_name = 'relative_humidity'
            cube.long_name = 'Relative Humidity'
    elif cube.standard_name == 'precipitation_flux':
        cube.standard_name = 'precipitation_amount'

    elif cube.standard_name == 'lwe_precipitation_rate':
        cube.standard_name = 'precipitation_amount'
    elif cube.standard_name == 'lwe_thickness_of_precipitation_amount':
        cube.standard_name = 'precipitation_amount'


# Modify coordinate names so they are all the same
  #DJB hack for obs on rcm grid
    coord_names = [coord.name() for coord in cube.coords()]
    if ('latitude' not in coord_names) and ('grid_latitude' in coord_names): 
        cube.coord('grid_latitude').var_name = 'latitude'
        cube.coord('grid_latitude').standard_name = 'latitude'
    if ('longitude' not in coord_names) and ('grid_longitude' in coord_names): 
        cube.coord('grid_longitude').var_name = 'longitude'
        cube.coord('grid_longitude').standard_name = 'longitude'

    if 'ensemble_member' in coord_names: #when using RCM directly...
        cube.remove_coord('month_number')
        cube.remove_coord('year')
        cube.remove_coord('yyyymmdd')
#       cube.remove_coord('ensemble_member')
        cube.remove_coord('ensemble_member_id')
  #BJD 

    if cube.coord('latitude').var_name == 'lat':
        cube.coord('latitude').var_name = 'latitude'
    if cube.coord('longitude').var_name == 'lon':
        cube.coord('longitude').var_name = 'longitude'

# Remove attributes as they can prevent the cubes from concatenating
    cube.attributes = {}

# Now do the datatype conversion:
    if cube.data.dtype != np.float32:
# Add mask and change data type:
#       print("---> Changing cube data type from file "+filename+"...",)# <-- no newline
        cube.data = np.ma.asarray(cube.data, dtype=np.float32)
#       print("---> Done.")
        sys.stdout.flush()
    else:
# Just mask it:
        #print "---> Adding mask to cube from file "+filename+"...", # <-- no newline
        cube.data = np.ma.array(cube.data)
        #print "---> Done."
        sys.stdout.flush()


def load_UKCP18_obs_1km(var, year_range, monstart=1, monend=12):
    '''
    Reads in the HadUK-Grid data on the native 1 km grid on the OSGB.

    var -- The name of the variable as used in the climate data files
    year_range -- The first and last years of data to load
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    '''

    ddir='/project/ukcp18/ncic_observations/post_processed/badc/ukmo-hadobs/' + \
        'data/insitu/MOHC/HadOBS/HadUK-Grid/v1.0.0.0/1km/'+var+'/day/v20181126/'

    # NEW CONSTRAINT - allow for starting in december rather than january (if needed)
    dtlims = [iris.time.PartialDateTime(year=year_range[0], month=monstart), \
      iris.time.PartialDateTime(year=year_range[1], month=monend) ]

    ycon = iris.Constraint(time = lambda t: dtlims[0] <= t.point <= dtlims[1])

    filenames_template = var + '*nc'
    filenames = glob.glob(os.path.join(ddir, filenames_template))
    filenames.sort()

    clist = iris.load(filenames, ycon, callback=ukcp18_callback)

    return clist.concatenate_cube()


def make_filename(user_id, project_name, area_name, var_type, var_name, year_range,
        ensemble_member=1, monstart=12, monend=11, resolution='2.2km'):
    '''
    Constructs the directory and filenames for the observed and modelled data files
    '''

    dir_head = os.path.join('/net/spice/scratch', user_id, project_name)
    if var_type == 'obs':
        subdir = f'HadUK_on_2.2km/{var_name}'
        fhead = f'{area_name}_{var_name}_obs_hadukgrid_uk_{resolution}_day'
        fend = f'{year_range[0]:04d}{monstart:02d}01-{year_range[1]:04d}{monend:02d}30.nc'
    else:
        subdir = f'cpm_prep/{ensemble_member:02d}/{var_name}'
        fhead = f'{area_name}_{var_name}_rcp85_land-cpm_uk_{resolution}_{ensemble_member:02d}'
        fend = f'{year_range[0]:04d}{monstart:02d}01-{year_range[1]:04d}{monend:02d}30.nc'

    datadir = os.path.join(dir_head, subdir)
    filename = '_'.join([fhead, fend])

    return datadir, filename


def load_UKCP18_obs_2p2km(user_id, var, year_range, monstart=1, monend=12):
    '''
    Reads in the HadUK-Grid data that have been aggregated to the 2.2 km rotated grid
    used by the UKCP Local projections.

    user_id -- The user's id, as returned by getpass.getuser()
    var -- The name of the variable as used in the climate data files
    year_range -- The first and last years of data to load
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    '''

    ddir = os.path.join('/net/spice/scratch', user_id, 'CLIMAR/HadUK_on_2.2km/', var)

    # NEW CONSTRAINT - allow for starting in december rather than january (if needed)
    dtlims = [iris.time.PartialDateTime(year=year_range[0], month=monstart), \
      iris.time.PartialDateTime(year=year_range[1], month=monend) ]

    ycon = iris.Constraint(time = lambda t: dtlims[0] <= t.point <= dtlims[1])

    filenames_template = var + '*nc'
    filenames = glob.glob(os.path.join(ddir, filenames_template))
    filenames.sort()

    clist = iris.load(filenames, ycon, callback=ukcp18_callback)

    return clist.concatenate_cube()


def load_raw_UKCP18_cpm_data(var, year_range, ensemble_member, monstart=1, monend=12, con=None):
    '''
    Reads in the raw UKCP18 CPM data (i.e. UKCP Local) on the native 2.2 km rotated polar grid.
    These data are the whole CPM domain, which is the UK, NW France, and parts of the Atlantic ocean.

    var -- The name of the variable as used in the climate data files
    year_range -- The first and last years of data to load
    ensemble_member -- The UKCP18 CPM ensemble member, an integer between 1 and 15
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    con -- Additional constraints applied whne loading the data (optional)
    '''

    ID = '{:02d}'.format(ensemble_member)

    dir_head = '/project/ukcp/land-cpm/uk/2.2km/rcp85/'
    subdir = f'{ID}/{var}/day/v20210615/'

    filenames_template = f'{var}_rcp85_land-cpm_uk_2.2km' + '*nc'

    # NEW CONSTRAINT - allow for starting in December rather than January (if needed)
    dtlims = [iris.time.PartialDateTime(year=year_range[0], month=monstart), \
      iris.time.PartialDateTime(year=year_range[1], month=monend) ]

    ycon = iris.Constraint(time = lambda t: dtlims[0] <= t.point <= dtlims[1])
    if con is not None:
        ycon = ycon & con

    filenames = glob.glob(os.path.join(dir_head, subdir, filenames_template))
    filenames.sort()

    clist = iris.load(filenames, ycon, callback=ukcp18_callback)

    return clist.concatenate_cube()


def load_processed_UKCP18_cpm_data(user_id, var, year_range, ensemble_member, monstart=1, monend=12, con=None):
    '''
    Reads in the UKCP18 CPM data (i.e. UKCP Local) on the native 2.2 km rotated polar grid.
    These data have been extracted for a subregion, e.g., Bristol, but *not* bias-corrected.

    user_id -- The user's id, as returned by getpass.getuser()
    var -- The name of the variable as used in the climate data files
    year_range -- The first and last years of data to load
    ensemble_member -- The UKCP18 CPM ensemble member, an integer between 1 and 15
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    '''

    ID = '{:02d}'.format(ensemble_member)

    ddir = os.path.join('/net/spice/scratch/', user_id, 'CLIMAR/cpm_prep', ID, var)

    fhead = f'{var}_rcp85_land-cpm_uk_2.2km_{ID}'
    fend = '{:4d}{:02d}01-{:4d}{:02d}30.nc'.format(year_range[0], monstart, year_range[1], monend)
    filename = '_'.join([fhead, fend])

    return iris.load_cube(os.path.join(ddir, filename), con)

#   # NEW CONSTRAINT - allow for starting in December rather than January (if needed)
#   dtlims = [iris.time.PartialDateTime(year=year_range[0], month=monstart), \
#     iris.time.PartialDateTime(year=year_range[1], month=monend) ]

#   ycon = iris.Constraint(time = lambda t: dtlims[0] <= t.point <= dtlims[1])

#   filenames = glob.glob(os.path.join(ddir, filenames_template))
#   filenames.sort()

#   clist = iris.load(filenames, ycon, callback=ukcp18_callback)

#   return clist.concatenate_cube()


def load_corrected_UKCP18_cpm_data(user_id, var, year_range, ensemble_member, monstart=1, monend=12):
    '''
    Reads in the bias-corrected UKCP18 CPM data (i.e. UKCP Local) on the native 2.2 km rotated polar grid.
    These data have been extracted for a subregion, e.g., Bristol.

    user_id -- The user's id, as returned by getpass.getuser()
    var -- The name of the variable as used in the climate data files
    year_range -- The first and last years of data to load
    ensemble_member -- The UKCP18 CPM ensemble member, an integer between 1 and 15
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    '''

    ID = '{:02d}'.format(ensemble_member)

# Construct the directory holding the calibrated CPM data.
    ddir = os.path.join('/net/spice/scratch/', user_id, 'CLIMAR/cpm_calibrated/', ID, var)

# Construct the file name
    fhead = f'{var}_rcp85_calib_2.2km_{ID}_day'
    fend = '{:04d}{:02d}01-{:04d}{:02d}30.nc'.format(year_range[0], monstart, year_range[1], monend)
    filename = '_'.join([fhead, fend])

    return iris.load_cube(os.path.join(ddir, filename))
