import os
import sys
import getpass
import datetime
import load_data
from pyCAT.pycat.io import Dataset
from pyCAT.pycat.esd import ScaledDistributionMapping


def make_output_filename(var_name, ID, year_start, year_end, monstart, monend, month_number):
    '''

    var_name -- The name of the variable
    ID -- The UKCP18 ensemble member, a 2-element string (01, 04, ... 15)
    year_start -- The first year of data to correct
    year_end -- The last year of data to correct
    monstart -- The first month of data to correct
    monend -- The last month of data to correct
    month_number -- The month number of data to correct
    '''

    fhead = f'{var_name}_rcp85_calib_2.2km_{ID}_day'
    fend = '{:4d}{:02d}01-{:4d}{:02d}30_month{:02d}.nc'.format(year_start, monstart, year_end, monend, month_number)

    return '_'.join([fhead, fend])


def calibrate_ukcp_local(user_id, project_name, area_name, varobs, varrcm, ensemble_member,
    year_start, year_end, monstart, monend, resolution='2.2km'):
    '''
    Bias-corrects climate projections using Scaled Distribution Mapping

    user_id -- The user's id, e.g., hadxx, jdoe
    varobs -- The name of the variable as used in the observation files
    varrcm -- The name of the variable as used in the climate data files
    ensemble_member -- The UKCP18 ensemble member, an integer between 1 and 15
    year_start -- The first year of data to correct in the scenario data
    year_end -- The last year of data to correct in the scenario data
    monstart -- The first month of data to correct in the scenario data
    monend -- The last month of data to correct in the scenario data

    monstart and monend should be 12 and 11 respectively, as UKCP projections run from December to
    November in each year
    '''

    print('start: '+datetime.datetime.now().strftime("%H:%M:%S"))

# Baseline period of the UKCP Local projections, and obs data
    bl_year_start = 1980
    bl_year_end = 2000 
    bl_mon_start = 12
    bl_mon_end = 11

# Create directory for the calibrated data if it does not exist
    dout = os.path.join('/net/spice/scratch/', user_id, 'CReDo/cpm_calibrated/intermediate',
        f'{ensemble_member:02d}')
    try:
        os.makedirs(dout)
    except FileExistsError:
        pass

# Set up directories and filenames for obs, model baseline and model scenario data
    obs_dir, obs_filename = load_data.make_filename(user_id, project_name, area_name, 'obs', varobs,
        [bl_year_start,bl_year_end], monstart=bl_mon_start, monend=bl_mon_end, resolution=resolution)
    mod_dir, mod_filename = load_data.make_filename(user_id, project_name, area_name, 'mod', varrcm,
        [bl_year_start,bl_year_end], ensemble_member=ensemble_member, monstart=bl_mon_start, monend=bl_mon_end,
        resolution=resolution)
    sce_dir, sce_filename = load_data.make_filename(user_id, project_name, area_name, 'mod', varrcm,
        [year_start,year_end], ensemble_member=ensemble_member, monstart=monstart, monend=monend,
        resolution=resolution)

    print('loading obs hist: '+datetime.datetime.now().strftime("%H:%M:%S"))
    obs = Dataset(obs_dir, obs_filename)
    print('loading rcm hist: '+datetime.datetime.now().strftime("%H:%M:%S"))
    mod = Dataset(mod_dir, mod_filename)
    print('loading rcm proj: '+datetime.datetime.now().strftime("%H:%M:%S"))
    sce = Dataset(sce_dir, sce_filename)

# Perform the bias correction
    sdm = ScaledDistributionMapping(obs, mod, sce, work_dir=dout)
    sdm.correct()

    print('end: '+datetime.datetime.now().strftime("%H:%M:%S"))


if __name__ == '__main__':

    user_id = getpass.getuser()
    project_name = sys.argv[1]
    region_name = sys.argv[2]
    varobs = sys.argv[3]
    varrcm = sys.argv[4]
    ensemble_member_ID = int(sys.argv[5])
    year_start = int(sys.argv[6])
    year_end = int(sys.argv[7])
    monstart = int(sys.argv[8])
    monend = int(sys.argv[9])

    calibrate_ukcp_local(user_id, project_name, region_name, varobs, varrcm, ensemble_member_ID, \
        year_start, year_end, monstart, monend)
