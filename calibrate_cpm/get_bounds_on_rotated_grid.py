import os
import iris
import numpy as np
import pandas as pd
from iris.analysis.cartography import rotate_pole
from iris.time import PartialDateTime

project_name = 'CReDo'
datadir = f'/home/h03/hadmi/Python/{project_name}/data_files/'

# Read in sample data on the UKCP Local 2.2 km grid
ukcp_local_dir = '/project/ukcp/land-cpm/uk/2.2km/rcp85/01/tasmax/day/v20210615/'
ukcp_sample_filename = 'tasmax_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.nc'

# Set up a time constraint - we ony need 1 day's data
con = iris.Constraint(time = lambda t: t.point < PartialDateTime(year=1980, month=12, day=2))
cube = iris.load_cube(os.path.join(ukcp_local_dir, ukcp_sample_filename), con)

# Get the poles of the rotated grid
pole_lat = cube.coord('grid_longitude').coord_system.grid_north_pole_latitude
pole_lon = cube.coord('grid_longitude').coord_system.grid_north_pole_longitude

# Read in the coordinates of the shapefile of the area around King's Lynn.
df = pd.read_csv(os.path.join(datadir, 'East_Anglia_shape_0_coordinates.csv'),
    header=0, usecols=[2,3])

# Find the maximim and minimum lons and lats on the regular (plate carree) grid
lon_max = df['longitude'].max()
lon_min = df['longitude'].min()
lat_max = df['latitude'].max()
lat_min = df['latitude'].min()

lon_lims = (lon_min, lon_max)
lat_lims = (lat_min, lat_max)

# Set up the corners of the domain
corners_lons = np.array([lon_lims[0], lon_lims[0], lon_lims[1], lon_lims[1]])
corners_lats = np.array([lat_lims[0], lat_lims[1], lat_lims[1], lat_lims[0]])

# Get the corners in rotated polar coordinates
rot_lons, rot_lats = rotate_pole(corners_lons, corners_lats, pole_lon, pole_lat)

# Print out the min/max values of the rotated polar coordinates
# Note that the longitude values will be of the order of -3 to +3,
# whereas the coordinates in the CPM data have longitude values centred around 360.
print('Lon Limits: ', 360.0+min(rot_lons), 360.0+max(rot_lons))
print('Lat Limits: ', min(rot_lats), max(rot_lats))

# Save the limits to a file
ofilename = 'East_Anglia_rotgrid_limits.dat'
oline0 = 'min(rot_lons),max(rot_lons),min(rot_lats),max(rot_lats)'
oline1 = '{:f},{:f},{:f},{:f}'.format(min(rot_lons), max(rot_lons), min(rot_lats), max(rot_lats))
with open(os.path.join(datadir, ofilename), "w") as ofp:
    ofp.write(oline0+'\n')
    ofp.write(oline1)
