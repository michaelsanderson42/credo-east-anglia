print """ THIS IS NOT A SCRIPT """

"""
  This is just a list of commands to process everything. It's not set up as a script!
  For example many of the sections of this launch batch jobs on SPICE.
  These have to finish before moving on.
"""
#extract a specific urban area. Regrid obs from 1km to 2.2km

import prep_cpm_calling
prep_cpm_calling.run_all()

#Make sure there is some output for PPE 01 (this is used as a template output grid)
import regrid_obs_calling
regrid_obs_calling.run_all()

#BIAS correction - time slices. Make sure everything prior has finished
import BC_timeslice_calling
BC_timeslice_calling.run_all(obsvar='tasmax', rcmvar='tasmax')



############################################

## STOP HERE Check all data has been made - sometimes jobs fall over for no good reason.

############################################


#Check BC file numbers: 144
l rcmr_tasmax_??_19802000_BC/s* | wc -l
l rcmr_tasmax_??_20202040_BC/s* | wc -l


#### MERGE files into timeseries
import merge_timeseries_calling
merge_timeseries_calling.run_all()

#Check BC file numbers: 348, 264, 252 (251 for 4.0)
l rcmr_tasmax_??_19912019_BC/T* | wc -l
l rcmr_tasmin_??_19912019_BC/T* | wc -l
l rcmr_pr_??_19912019_BC/T* | wc -l
l rcmr_tasmax_??_20592080_BC/T* | wc -l 
l rcmr_tasmin_??_20592080_BC/T* | wc -l 
l rcmr_pr_??_20592080_BC/T* | wc -l 
l rcmr_tasmax_??_2.0_BC/T* | wc -l 
l rcmr_tasmin_??_2.0_BC/T* | wc -l 
l rcmr_pr_??_2.0_BC/T* | wc -l 
l rcmr_tasmax_??_4.0_BC/T* | wc -l 
l rcmr_tasmin_??_4.0_BC/T* | wc -l 
l rcmr_pr_??_4.0_BC/T* | wc -l 

#########################

# Consider need to post process any metadata

#import FIX_pan_meta
#FIX_pan_meta.fix()

