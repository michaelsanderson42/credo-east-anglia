import os
import iris
import calendar
import getpass
import matplotlib.pyplot as plt
import iris.plot as iplt
import load_data
from matplotlib.colors import Normalize
import matplotlib.cm as cm


def rotate(l, x):
    return l[-x:] + l[:-x]


def load_haduk_observation(user_id, var_name, year_range):

    datadir = os.path.join('/net/spice/scratch/', user_id, 'CLIMAR/HadUK_on_2.2km', var_name)
    fhead = f'{var_name}_cpmgrid_uk_2.2km_day'
    filenames = []
    months = list(range(1, 13))
    month_numbers = rotate(months, 1)
    clist = iris.cube.CubeList()

# Reads in data for years defined as December to November.
# Example: For year range 2000-2010, Reads in December 2000 only.
    for the_year in list(range(year_range[0], year_range[1])):
        for month in month_numbers:
            if month == 12:
                fend = '{0:4d}1201-{0:4d}1231.nc'.format(the_year)
            else:
                yp1 = the_year+1
                ndays = calendar.monthrange(yp1, month)[1]
                fend = f'{yp1:4d}{month:02d}01-{yp1:4d}{month:02d}{ndays:02d}.nc'
            filename = '_'.join([fhead, fend])
            cube = iris.load_cube(os.path.join(datadir, filename))
#           del cube.attributes['creation_date']
            clist.append(cube)

    return clist.concatenate_cube()


def load_calibrated_cpm(user_id, ensemble_member, var_name, year_range):

    ID = '{:02d}'.format(ensemble_member)
    datadir = os.path.join('/net/spice/scratch/', user_id, 'CLIMAR/cpm_calibrated', ID, var_name)
    fhead = f'{var_name}_rcp85_calib_2.2km_{ID}_day'
    fend = '{:4d}1201-{:4d}1130.nc'.format(year_range[0], year_range[1])
    filename = '_'.join([fhead, fend])

    return iris.load_cube(os.path.join(datadir, filename))


def load_raw_cpm(user_id, ensemble_member, var_name, year_range):

    ID = '{:02d}'.format(ensemble_member)
    datadir = os.path.join('/net/spice/scratch/', user_id, 'CLIMAR/cpm_prep', ID, var_name)
    fhead = f'{var_name}_rcp85_land-cpm_uk_2.2km_{ID}_day'
    clist = iris.cube.CubeList()

    for the_year in list(range(year_range[0], year_range[1])):
        yp1 = the_year+1
        fend = f'{the_year:4d}1201-{yp1:4d}1130.nc'
        filename = '_'.join([fhead, fend])
        cube = iris.load_cube(os.path.join(datadir, filename))
        clist.append(cube)

    return clist.concatenate_cube()


def check_bias_correction(user_id, var_name, ensemble_member, year_range):

    fdir = '/home/h03/hadmi/Python/CLIMAR/figures/'

    baseline_year_range = [1980, 2000]
    monstart = 12
    monend = 11

    # Load the observations for the baseline period
    print('Loading observations ...')
    obs_base = load_data.load_UKCP18_obs_2p2km(user_id, var_name, baseline_year_range, monstart=monstart, monend=monend)

    #Load the raw (i.e. uncorrected) modelled baseline data
    print('Loading uncorrected model baseline ...')
    cpm_base_raw = load_data.load_processed_UKCP18_cpm_data(user_id, var_name, baseline_year_range, ensemble_member, monstart=monstart, monend=monend)

    #Load the raw (i.e. uncorrected) modelled scenario data
    print('Loading uncorrected model scenario ...')
    cpm_scen_raw = load_data.load_processed_UKCP18_cpm_data(user_id, var_name, year_range, ensemble_member, monstart=monstart, monend=monend)

    #Load the bias-corrected modelled scenario data
    print('Loading calibrated model scenario ...')
    cpm_scen_cal = load_data.load_corrected_UKCP18_cpm_data(user_id, var_name, year_range, ensemble_member, monstart=monstart, monend=monend)

# Plot the long-term averages of the observed and modelled data
    obs_lta = obs_base.collapsed('time', iris.analysis.MEAN)
    cpm_base_raw_lta = cpm_base_raw.collapsed('time', iris.analysis.MEAN)
    cpm_scen_raw_lta = cpm_scen_raw.collapsed('time', iris.analysis.MEAN)
    cpm_scen_cal_lta = cpm_scen_cal.collapsed('time', iris.analysis.MEAN)

    mx = max([obs_lta.data.max(), cpm_base_raw_lta.data.max(), cpm_scen_cal_lta.data.max()])
    mn = min([obs_lta.data.min(), cpm_base_raw_lta.data.min(), cpm_scen_cal_lta.data.min()])
    normalizer = Normalize(mn, mx)
    im = cm.ScalarMappable(norm=normalizer)

    fig = plt.figure(figsize=(8,12))

    plt.subplot(3,2,1)
    iplt.pcolormesh(obs_lta, vmin=mn, vmax=mx)
    plt.title('HadUK Obs')

    plt.subplot(3,2,3)
    iplt.pcolormesh(cpm_base_raw_lta, vmin=mn, vmax=mx)
    plt.title('CPM Baseline Raw')

    plt.subplot(3,2,5)
    iplt.pcolormesh(cpm_scen_raw_lta, vmin=mn, vmax=mx)
    plt.title('CPM Scenario Raw')

    pos = plt.gca().get_position()
    width = pos.x1 - pos.x0
    cbar_pos = [pos.x0, pos.y0-0.07, width, 0.03]
    cbar_ax = fig.add_axes(cbar_pos)
    fig.colorbar(im, cax=cbar_ax, orientation='horizontal', norm=normalizer)

# Difference Plots. cpm_cal_change and cpm_raw_change should be essentially identical.
    cpm_bias = cpm_base_raw_lta - obs_lta
    cpm_cal_change = cpm_scen_cal_lta - obs_lta
    cpm_raw_change = cpm_scen_raw_lta - cpm_base_raw_lta

# Get the range of changes in the variable, and set the plot limits accordingly
#   mx = max([cpm_bias.data.max(), cpm_raw_change.data.max(), cpm_cal_change.data.max()])
#   mn = min([cpm_bias.data.min(), cpm_raw_change.data.min(), cpm_cal_change.data.min()])
    mx = max([cpm_raw_change.data.max(), cpm_cal_change.data.max()])
    mn = min([cpm_raw_change.data.min(), cpm_cal_change.data.min()])
    if abs(mx) > abs(mn):
        r = abs(mx)
    else:
        r = abs(mn)

# Set up an image showing the plot range and associated colours - it will
# be used to create a colour bar.
#   mn = -r
#   mx = r
    normalizer = Normalize(mn, mx)
    im = cm.ScalarMappable(norm=normalizer, cmap='coolwarm')

    plt.subplot(3,2,2)
    iplt.pcolormesh(cpm_bias, cmap='coolwarm', vmin=mn, vmax=mx)
    plt.title('CPM Bias')

    plt.subplot(3,2,4)
    iplt.pcolormesh(cpm_cal_change, cmap='coolwarm', vmin=mn, vmax=mx)
    plt.title('CPM Change (Cal - Obs)')

    plt.subplot(3,2,6)
    iplt.pcolormesh(cpm_raw_change, cmap='coolwarm', vmin=mn, vmax=mx)
    plt.title('CPM Change (Raw)')

    pos = plt.gca().get_position()
    width = pos.x1 - pos.x0
    cbar_pos = [pos.x0, pos.y0-0.07, width, 0.03]
    cbar_ax = fig.add_axes(cbar_pos)
    fig.colorbar(im, cax=cbar_ax, orientation='horizontal', norm=normalizer)

    plt.show()


if __name__ == '__main__':

    user_id = getpass.getuser()
    var_name = 'tasmax'
    ensemble_member = 12
    year_range = [1980, 2000]
#   year_range = [2060, 2080]

    check_bias_correction(user_id, var_name, ensemble_member, year_range)
