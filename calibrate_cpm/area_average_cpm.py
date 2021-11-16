import os
import sys
import getpass
import datetime
import numpy as np
import iris
from scipy import signal
import load_data


def make_output_filename(var_name, ID, year_start, year_end, monstart, monend):
    '''

    var_name -- The name of the variable
    ID -- The UKCP18 ensemble member, a 2-element string (01, 04, ... 15)
    year_start -- The first year of data to correct
    year_end -- The last year of data to correct
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    '''

    fhead = f'{var_name}_rcp85_smoothed_2.2km_{ID}_day'
    fend = '{:4d}{:02d}01-{:4d}{:02d}30.nc'.format(year_start, monstart, year_end, monend)

    return '_'.join([fhead, fend])


def smooth_data(cube, filter_size=3):
    '''
    Smooths the data in the cube by calculating spatial average of grid boxes in a
    block filter_size x filter_size
    Example: if filter_size = 3:

        1 2 3
        4 5 6
        7 8 9

    Box 5 will contain the average of boxes 1-9 after the smoothing
    '''

    cube_out = cube.copy()
    conv_array = np.full((filter_size, filter_size), 1/(filter_size*filter_size), dtype=np.float)

    for i, c in enumerate(cube.slices_over('time')):
        c_smooth = signal.convolve2d(c.data.data, conv_array, boundary='symm', mode='same')
        cube_out[i].data[:,:] = c_smooth

    return cube_out


def calculate_area_average(user_id, var_name, ensemble_member, year_start, year_end, monstart, monend):
    '''
    Bias-corrects climate projections using Scaled Distribution Mapping

    user_id -- The user's id, e.g., hadxx, jdoe
    var_name -- The name of the variable as used in the climate data files
    ensemble_member -- The UKCP18 ensemble member, an integer between 1 and 15
    year_start -- The first year of data to correct
    year_end -- The last year of data to correct
    monstart -- The first month of data to correct
    monend -- The last month of data to correct

    monstart and monend should be 12 and 11 respectively, as UKCP projections run from December to
    November in each year
    '''

    print('start: '+datetime.datetime.now().strftime("%H:%M:%S"))

    ID = '{:02d}'.format(ensemble_member)

# Create directory for the smoothed data if it does not exist
    dout = os.path.join('/net/spice/scratch/', user_id, 'CLIMAR/cpm_smoothed/', ID, var_name)
    try:
        os.makedirs(dout)
    except FileExistsError:
# directory already exists
        pass

    print('loading bias-corrected rcm: '+datetime.datetime.now().strftime("%H:%M:%S")+' '+str(monstart)+' '+str(monend))
    rcm_corr = load_data.load_corrected_UKCP18_cpm_data(user_id, var_name, [year_start, year_end],
        ensemble_member, monstart=monstart, monend=monend)

    rcm_corr_smoothed = smooth_data(rcm_corr)

    fout = make_output_filename(var_name, ID, year_start, year_end, monstart, monend)
    iris.save(rcm_corr_smoothed, os.path.join(dout, fout))

    print('end: '+datetime.datetime.now().strftime("%H:%M:%S"))


if __name__ == '__main__':

    user_id = getpass.getuser()
    varrcm = sys.argv[1]
    ensemble_member = int(sys.argv[2])
    year_start = int(sys.argv[3])
    year_end = int(sys.argv[4])
    monstart = int(sys.argv[5])
    monend = int(sys.argv[6])

    calculate_area_average(user_id, varrcm, ensemble_member, year_start, year_end, monstart, monend)
