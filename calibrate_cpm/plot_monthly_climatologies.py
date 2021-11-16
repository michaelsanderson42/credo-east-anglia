'''
Routines to create and plot monthly climatologies of AgMERRA data
and historical RCM simulations
'''

import iris
import iris.coord_categorisation
import iris.palette
import iris.plot as iplt
from iris.util import unify_time_units
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import numpy as np
import calendar
import sys
import glob
from cf_units import Unit
from ukcp_common_analysis.regions import reg_from_cube


def colombia_callback(cube, field, filename):
    '''
    Ensure cubes read in are converted to common units and common names of variables,
    use masked arrays of 32-bit floats, and do a couple of other bits of tidying,
    which ensure that things all concatenate/merge properly in all cases...
    '''

# Add time coord bounds if not present:
    if not cube.coord('time').has_bounds():
        cube.coord('time').guess_bounds()

# Check and change names of units: AgMERRA uses 'degrees Celsius' for temperatures, but Iris uses 'celsius'
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

# Add standard_name and long_name if undefined - the standard_name is used by the
# PyCAT bias correction code in 'methods.py' to select the appropriate method
# for the variable

    if cube.standard_name is None:
        if cube.var_name in ['tmax', 'tasmax', 'tx', 'mx2t']:
            cube.standard_name = 'air_temperature'
            cube.long_name = "Daily Maximum Near-Surface Air Temperature"
        elif cube.var_name in ['tmin', 'tasmin', 'tn', 'mn2t']:
            cube.standard_name = 'air_temperature'
            cube.long_name = "Daily Minimum Near-Surface Air Temperature"
        elif cube.var_name in ['prate', 'prcp', 'pr', 'precip', 'precipitation', 'tp']:
            cube.standard_name = 'precipitation_amount'
            cube.long_name = 'Precipitation'
        elif cube.var_name in ['rhstmax']:
            cube.standard_name = 'relative_humidity'
            cube.long_name = 'Near-Surface Relative Humidity'
    elif cube.standard_name == 'precipitation_flux':
        cube.standard_name = 'precipitation_amount'

# Modify coordinate names so they are all the same
    if cube.coord('latitude').var_name == 'lat':
        cube.coord('latitude').var_name = 'latitude'
    if cube.coord('longitude').var_name == 'lon':
        cube.coord('longitude').var_name = 'longitude'

# When loaded, some of the ERA-Interim cubes have time as an auxilliary coordinate
# if this is the case, promote the time coordinate to a dimension
    coord_names = [coord.name() for coord in cube.coords()]
    if coord_names[-1] == 'time':
        old_time = cube.coord('time')
        new_time = iris.coords.DimCoord.from_coord(old_time)
        cube.remove_coord(old_time)
        cube.add_dim_coord(new_time, 0)

# Remove attributes as they can prevent the cubes from concatenating
    cube.attributes = ""

# Now do the datatype conversion:
    if cube.data.dtype != np.float32:
# Add mask and change data type:
        print("---> Changing cube data type from file "+filename+"...",) # <-- no newline
        cube.data = np.ma.asarray(cube.data, dtype=np.float32)
        print("---> Done.")
        sys.stdout.flush()
    else:
# Just mask it:
        #print "---> Adding mask to cube from file "+filename+"...", # <-- no newline
        cube.data = np.ma.array(cube.data)
        #print "---> Done."
        sys.stdout.flush()


def get_agmerra_var_name(var):
    '''
    The variable names used in the AgMERRA filenames are different to those used by CORDEX.
    Create a dictionary to map the CORDEX and AgMERRA variable names
    var -- Variable name used in CORDEX
    '''

    ag_dict = {'tasmax': 'tmax', 'tasmin': 'tmin', 'pr': 'prate', 'sfcWind': 'wndspd'}

    if var in ag_dict:
        return ag_dict[var]
    else:
        raise ValueError("get_agmerra_var_name: {} not recognised".format(var))


def make_monthly_climatology(cube):

# First, make a series of monthly means or monthly totals
    # DJB added in conditional creation of month_number and year
    if len(cube.coords(var_name = 'month_number')) == 0:
        iris.coord_categorisation.add_month_number(cube, 'time', name='month_number')
    if len(cube.coords(var_name = 'year')) == 0:
        iris.coord_categorisation.add_year(cube, 'time', name='year')

    monthly_series = cube.aggregated_by(['month_number', 'year'], iris.analysis.MEAN)

# Now create the monthly climatology
    return monthly_series.aggregated_by('month_number', iris.analysis.MEAN)


def load_data_as_climatol(var, source, years_0, **options):
    '''
    Loads in the data for variable 'var' from the source 'source', and returns
    a monthly climatology.
    '''

    ycon_0 = iris.Constraint(time=lambda cell: years_0[0] <= cell.point.year <= years_0[1])

    co_limits = None
    scenario = 'evaluation'
    if "co_limits" in options:
        co_limits = options["co_limits"]
    if "scenario" in options:
        scenario = options["scenario"]

# For now, hard-code these names
    rcm = 'SMHI-RCA4'
#   gcm = 'CCCma-CanESM2'
    gcm = 'ECMWF-ERAINT'
    version = 'r1i1p1'
    ag_var = get_agmerra_var_name(var)

    if co_limits is not None:
# Construct the regional constraint for the CORDEX data using the domain limits.
# N.B. The lons / lats in the CAM-CORDEX cubes do not have bounds
        lat_con = iris.Constraint(latitude = lambda l: co_limits['lats'][0] <= l <= co_limits['lats'][1])
        lon_con = iris.Constraint(longitude = lambda l: co_limits['lons'][0] <= l <= co_limits['lons'][1])
        area_con = lat_con & lon_con

    if source == 'agmerra':
# Load in the AgMERRA data for this variable. These data are for Colombia and surrounding areas
# 'agmerra' contains a list of cubes.
        print('Loading the AgMERRA data')
        ag_fname_template = '/data/users/hadmi/AgMERRA/AgMERRA_*_' + ag_var + '.nc4'
        ag_fnames = glob.glob(ag_fname_template)
        agmerra_cubes = iris.load(ag_fnames, ycon_0, callback=colombia_callback)
        unify_time_units(agmerra_cubes)
        agmerra = agmerra_cubes.concatenate_cube()
        del agmerra_cubes
        clim = make_monthly_climatology(agmerra)

    elif source == 'rcm':
# Load in the historical CAM-CORDEX RCM data
        print('Loading the historical RCM data')
        fheader_0 = '_'.join([var, 'CAM-AG', gcm, scenario, version, rcm, 'v1', 'day'])
        hist_fname_template = '/scratch/hadmi/CAMCORDEX/' + fheader_0 + '_*nc'
        rcm_fnames = glob.glob(hist_fname_template)
        rcm_cubes = iris.load(rcm_fnames, ycon_0 & area_con, callback=colombia_callback)
        unify_time_units(rcm_cubes)
        rcm = rcm_cubes.concatenate_cube()
        del rcm_cubes
        clim = make_monthly_climatology(rcm)

    elif source == 'erai':
# Load in the historical CAM-CORDEX RCM data
        print('Loading the ERA-Interim data')
        fheader_0 = '_'.join([var, 'CAM-AG', 'ECMWF-ERAINT'])
        era_fname_template = '/data/users/hadmi/ERAI/' + fheader_0 + '_*nc'
        era_fnames = glob.glob(era_fname_template)
        era_cubes = iris.load(era_fnames, ycon_0, callback=colombia_callback)
        for i, c in enumerate(era_cubes):
            print(i)
            print(', '.join([coord.name() for coord in c.coords()]))
#       era_cubes = iris.load(era_fnames, ycon_0 & area_con, callback=colombia_callback)
        unify_time_units(era_cubes)
        era = era_cubes.concatenate_cube()
        del era_cubes
        clim = make_monthly_climatology(era)

    return clim


def make_colour_map(long_name):

    if 'Max' in long_name:
        lo = 16
        hi = 44
        gap = 2
    elif 'Min' in long_name:
        lo = 0
        hi = 32
        gap = 4
    elif long_name == 'Precipitation':
        lo = 0
        hi = 10
        gap = 1
    elif 'Humidity' in long_name:
        lo = 10
        hi = 100
        gap = 10

    bounds = range(lo, hi+gap, gap)
    cmap = plt.get_cmap("YlOrRd")
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=256)

    return cmap, norm


def plot_monthly_climatology(cube, var, source, scenario):
    '''
    cube -- Iris cube containing 12 monthly climatological values
    '''

    cmap, norm = make_colour_map(cube.long_name)

# Set up the plot
    fig = plt.figure(figsize=(10, 14))
    proj = ccrs.PlateCarree(central_longitude=285.0)

    for i, m in enumerate(cube.coord('month_number').points):

        plt.subplot(4, 3, i+1, projection=proj)
        block_result = iplt.pcolormesh(cube[i], norm=norm, cmap=cmap)
        plt.title('{}'.format(calendar.month_name[m]))
        plt.gca().coastlines()

        if i == 9:
            plt0_ax = plt.gca()
        if i == 11:
            plt1_ax = plt.gca()
 
    left, bottom, width, height = plt1_ax.get_position().bounds
    first_plot_left = plt0_ax.get_position().bounds[0]

# Calculate the width of the colorbar
    width = left - first_plot_left + width

# Add axes to the figure, to place the colour bar
    colorbar_axes = fig.add_axes([first_plot_left, bottom-0.06, width, 0.02])

# Add the colour bar
    cbar = plt.colorbar(block_result, colorbar_axes, orientation='horizontal')
    cbar.set_label('$^\circ$C')

    fdir = '/home/h03/hadmi/Python/MedGOLD/figures/'
    plt.savefig(fdir + '{}_{}_{}_monthly_climatology.png'.format(var, source, scenario))
#   plt.tight_layout()
#   plt.show()
    plt.close()


def main():

    var = 'sfcWind'
    years_0 = [1981, 2000]
    scenario = 'evaluation'
    scenario_0 = 'historical'
    scenario_1 = 'rcp85'

    ag_clim = load_data_as_climatol(var, 'agmerra', years_0)

# Calculate the domain limits from the AgMERRA cube
    co_limits = reg_from_cube(ag_clim[0], lat_name="latitude", lon_name="longitude")

    rcm_clim = load_data_as_climatol(var, 'rcm', years_0, scenario=scenario, co_limits=co_limits)
    era_clim = load_data_as_climatol(var, 'erai', years_0, co_limits=co_limits)

    plot_monthly_climatology(ag_clim, var, 'agmerra', scenario)
    plot_monthly_climatology(rcm_clim, var, 'rcm', scenario)
    plot_monthly_climatology(era_clim, var, 'erai', scenario)


if __name__ == '__main__':
    main()
