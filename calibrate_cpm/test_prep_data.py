import iris
import load_data

path = '/project/ukcp/land-cpm/uk/2.2km/rcp85/01/tasmax/day/v20190731'
var = 'tasmax'
year_range = [1980, 1983]
ensemble_member = 1
monstart = 12
monend=11

lon_con = iris.Constraint(grid_longitude = lambda l: 359.85 < l.point < 360.08)
lat_con = iris.Constraint(grid_latitude = lambda l: -1.12 < l.point < -0.92)
area_con = lat_con & lon_con

cube = load_data.load_raw_UKCP18_cpm_data(var, year_range, ensemble_member, monstart=12, monend=11, con=area_con)

