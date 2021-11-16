This directory contains a suite of programs, which extract a region
of the UKCP Local (i.e. CPM) simulations and bias-adjusts the data
using the HadUK-Grid data.

Before running any of the programs, make sure you have typed in
the command below:
       module load scitools

The programs should be run in the following order:

1. Find the coordinates of the area of interest (in latitude-longitude).
2. Run get_bounds_on_rotated_grid.py to convert to rotated polar coordinates
   Note that:
   You will need to edit this program to use the coordinates of the area of interest.
   It has the coordinates of Bristol by default.

2a. Edit lines 15 and 16 of check_bristol_bounds.py, to use the coordinates of the area of interest.
   from step 2. Run this program - it should create a figure showing the whole UK and a box
   showing your area of interest, as a visual check that the coordinate conversion has worked.

3. Edit lines 24 and 25 of prep_cpm_data.py to use the limits from step 2.
4. Edit line 13 of prep_cpm_calling.py to extract the correct variable.
5. At a Linux prompt, type:
       python prep_cpm_calling.py
   This script will submit a series of batch jobs to SPICE, which extract the UKCP Local
   data for your area of interest. The data will be written to a temporary directory
   under SCRATCH.

6. Edit line 68 of regrid_obs_calling.py to select the correct variable.
7. Run program regrid_obs_calling.py, to regrid the HadUK-Grid data to the rotated polar grid.
   This script will submit a series of batch jobs to SPICE, which extracts the required
   region from the HadUK-Grid data and interpolates it to the rotated polar grid.

8. Edit lines 42 and 43 of BC_timeslice_calling.py to select the correct variable.
   Edit lines 7 and 8 of BC_timeslice_calling.py to select the required time period(s).
9. Run program BC_timeslice_calling.py to bias-adjust the UKCP Local data.
   This script will submit a series of batch jobs to SPICE, which calls the bias-adjustment
   routine (Scaled Distribution Mapping) one month at a time. The bias-corrected data will
   be stored in 12 files per time period (i.e. 1 file per month).

10. Run merge_timeseries_calling.py, which will collate the monthly files from step 9
   to produce time series of bias-corrected data.
