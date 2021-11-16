import os
import sys
import getpass
import datetime
import iris
import load_data
from pycat.esd.methods import scaled_distribution_mapping


def make_output_filename(var_name, ID, year_start, year_end, monstart, monend):
    '''

    var_name -- The name of the variable
    ID -- The UKCP18 ensemble member, a 2-element string (01, 04, ... 15)
    year_start -- The first year of data to correct
    year_end -- The last year of data to correct
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    '''

    fhead = f'{var_name}_rcp85_calib_2.2km_{ID}_day'
    fend = '{:4d}{:02d}01-{:4d}{:02d}30.nc'.format(year_start, monstart, year_end, monend)

    return '_'.join([fhead, fend])


def calibrate_ukcp_local(user_id, varobs, varrcm, ensemble_member, year_start, year_end, monstart, monend):
    '''
    Bias-corrects climate projections using Scaled Distribution Mapping

    user_id -- The user's id, e.g., hadxx, jdoe
    varobs -- The name of the variable as used in the observation files
    varrcm -- The name of the variable as used in the climate data files
    ensemble_member -- The UKCP18 ensemble member, an integer between 1 and 15
    year_start -- The first year of data to correct
    year_end -- The last year of data to correct
    monstart -- The first month of data to correct
    monend -- The last month of data to correct

    monstart and monend should be 12 and 11 respectively, as UKCP projections run from December to
    November in each year
    '''

    print('start: '+datetime.datetime.now().strftime("%H:%M:%S"))

# Baseline period of the UKCP Local projections
    bl_year_start = 1980
    bl_year_end = 2000 
    blmonstart = 12
    blmonend = 11

    ID = '{:02d}'.format(ensemble_member)

# Create directory for the calibrated data if it does not exist
    dout = '/net/spice/scratch/hadmi/Reading'
    try:
        os.makedirs(dout)
    except FileExistsError:
# directory already exists
        pass

    print('loading obs hist: '+datetime.datetime.now().strftime("%H:%M:%S"))
    obs = load_data.load_UKCP18_obs_2p2km(user_id, varobs, [bl_year_start,bl_year_end],
        monstart=blmonstart, monend=blmonend)

    print('loading rcm hist: '+datetime.datetime.now().strftime("%H:%M:%S"))
    rcm_hist = load_data.load_processed_UKCP18_cpm_data(user_id, varrcm, [bl_year_start,bl_year_end],
        ensemble_member, monstart=monstart, monend=monend)

    print('loading rcm proj: '+datetime.datetime.now().strftime("%H:%M:%S")+' '+str(monstart)+' '+str(monend))
    rcm_proj = load_data.load_processed_UKCP18_cpm_data(user_id, varrcm, [year_start, year_end],
        ensemble_member, monstart=monstart, monend=monend)

# The SDM implementation needs the scenario data in a cubelist
    clist = iris.cube.CubeList()
    clist.append(rcm_proj)

    print('calibrating and writing data: '+datetime.datetime.now().strftime("%H:%M:%S"))
    scaled_distribution_mapping(obs, rcm_hist, clist)

    fout = make_output_filename(varrcm, ID, year_start, year_end, monstart, monend)
    iris.save(rcm_proj, os.path.join(dout, fout))

    print('end: '+datetime.datetime.now().strftime("%H:%M:%S"))


if __name__ == '__main__':

    user_id = 'vramsey'
    varobs = sys.argv[1]
    varrcm = sys.argv[2]
    ensemble_member_ID = int(sys.argv[3])
    year_start = int(sys.argv[4])
    year_end = int(sys.argv[5])
    monstart = int(sys.argv[6])
    monend = int(sys.argv[7])

    calibrate_ukcp_local(user_id, varobs, varrcm, ensemble_member_ID, year_start, year_end, monstart, monend)
