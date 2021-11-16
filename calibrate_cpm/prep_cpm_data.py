import os
import sys
import glob
import getpass
import iris
import load_data


def make_output_filename(region_name, var, year_range, ID, monstart, monend):
    '''
    Construct the output filename for the processed UKCP18 CPM data
    These data have been extracted for a subregion, e.g., the city of Bristol.

    var -- The name of the variable
    year_range -- A 2-element list containing the first and last years to process
    ID -- a 2-character string containing the ensemble member (01 to 15)
    monstart -- The first month processed
    monend -- The last month processed
    '''

    fhead = f'{region_name}_{var}_rcp85_land-cpm_uk_2.2km_{ID}'
    fend = '{:4d}{:02d}01-{:4d}{:02d}30.nc'.format(year_range[0], monstart, year_range[1], monend)

    return '_'.join([fhead, fend])


def prep_cpm(user_id, project_name, region_name, var, year_range,
    ID, monstart, monend, lon_limits, lat_limits):
    '''
    Extracts UKCP Local data within the area of interest.

    user_id -- The user's ID
    project_name -- Name of the project, e.g., 'CLIMAR', 'CReDo'
    region_name -- Name of the region/place under study, e.g., 'Bristol', 'East_Anglia'
    var -- The name of the variable
    year_range -- A 2-element list containing the first and last years to process
    ID -- a 2-character string containing the ensemble member (01 to 15)
    monstart -- The first month to process
    monend -- The last month to process

    N.B. For UKCP18 data, monstart=12, monend=11, as the simulations run from
        December to November
    '''

    dout = os.path.join('/net/spice/scratch/', user_id, project_name, 'cpm_prep', ID, var)

# If directory doesn't exist, create it.
    try:
        os.makedirs(dout)
    except FileExistsError:
# directory already exists
        pass

    ensemble_member = int(ID)

# Add 360 to the longitude limits, to match the CPM coordinates
    lon_edges = [l+360 for l in lon_limits]
    lon_con = iris.Constraint(grid_longitude = lambda l: lon_edges[0] <= l.point <= lon_edges[1])
    lat_con = iris.Constraint(grid_latitude = lambda l: lat_limits[0] <= l.point <= lat_limits[1])
    area_con = lat_con & lon_con

# Read the UKCP18 2.2 km data, returned as a single cube. Data are extracted for the region defined above.
    cube = load_data.load_raw_UKCP18_cpm_data(var, year_range, ensemble_member, monstart=12, monend=11, con=area_con)

# Remove the fourth dimension 'ensemble_member' from the cube
    cube = cube.extract(iris.Constraint(ensemble_member = ensemble_member))

# Modify the labels to remove the degree symbol (prevents the cubes from being printed within Python).
#   cube.attributes['label_units'] = 'degC'
#   cube.attributes['plot_label'] = 'Maximum air temperature at 1.5m (degC)'

# Save the cube
    fout = make_output_filename(region_name, var, year_range, ID, monstart, monend)
    iris.save(cube, os.path.join(dout, fout))

    return


def read_boundary_edges(project_name, region_name):

    datadir = f'/home/h03/hadmi/Python/{project_name}/data_files/'
    bounds_filename = f'{region_name}_rotgrid_limits.dat'

# Load the bounds of a box around the area of interest in rotated polar coordinates
# The final line contains the bounds
    with open (os.path.join(datadir, bounds_filename), "r") as ifp:
        for line in ifp:
            pass

# Get the longitude and latitude limits
    x0, x1, y0, y1 = [float(b) for b in line.split(',')]

    return [x0, x1], [y0, y1]


if __name__ == '__main__':

    user_id = getpass.getuser()
    project_name = sys.argv[1]
    region_name = sys.argv[2]
    var = sys.argv[3]
    ID = sys.argv[4]
    y0 = int(sys.argv[5])
    y1 = int(sys.argv[6])
    monstart = 12
    monend = 11
    print(project_name, region_name, var, ID, y0, y1)

# Read in the boundary edges of the area of interest
    lon_limits, lat_limits = read_boundary_edges(project_name, region_name)

    prep_cpm(user_id, project_name, region_name, var, [y0, y1], ID,
        monstart, monend, lon_limits, lat_limits)

