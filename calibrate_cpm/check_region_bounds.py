import os
import glob
import numpy as np
import iris
from iris.time import PartialDateTime
import iris.plot as iplt
import matplotlib.pyplot as plt

project_name = 'CReDo'
region_name = 'East_Anglia'

# Load a single UKCP Local field (2.2 km resolution, rotated polar grid)
ukcp_local_dir = '/project/ukcp/land-cpm/uk/2.2km/rcp85/01/tasmax/day/v20210615/'
filename = 'tasmax_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.nc'
ensemble_member = 1
cube = iris.load_cube(os.path.join(ukcp_local_dir, filename),
    iris.Constraint(time = lambda t: t.point < PartialDateTime(year=1980, month=12, day=3)))
cube = cube.extract(iris.Constraint(ensemble_member = ensemble_member))

datadir = f'/home/h03/hadmi/Python/{project_name}/data_files/'
bounds_filename = f'{region_name}_rotgrid_limits.dat'

# Load the bounds of a box around the area of interest in rotated polar coordinates
# The final line contains the bounds
with open (os.path.join(datadir, bounds_filename), "r") as ifp:
    for line in ifp:
        pass

x0, x1, y0, y1 = [float(b) for b in line.split(',')]
x = np.array([x0, x0, x1, x1, x0])
y = np.array([y0, y1, y1, y0, y0])

# Plot the CPM data and the box around the region of interest as a visual check that the box is in the correct area
iplt.pcolormesh(cube[0])
plt.plot(x, y, 'k-')
plt.gca().coastlines(resolution='10m', color='grey')
plt.show()
