Main.ipynb contains code to process ARISE, ssp245 and PiCOntrol runs in UKESM1 into seasonal time means, and ensemble means/stds. It outputs small .nc files containing a set of spatially resolved means and standard deviations variables to /Output_data. For each scenario, we output .nc files containing each the mean state under a given 20-year time-window, both for the full annual data, ('all'), and for individual seasons. This gives 10 files per scenario (4 seasons + annual, for mean and std. There are two outputs for SSP245: the first is the baseline, the second is the warmer world without SAI (i.e. SSP245 scenario at the same time period which we use for assessing ARISE (2050-2069).  

SSP245_baseline: the target state ARISE aims for, i.e. the 20-year period from the concatenated historical and SSP2-4.5 runs with mean temperature closest to 1.5C above pre-industrial (2013-2022). We use only the 5 ensemble members from which the ARISE runs branch. 

Preindustrial: the PiControl run output. In this case only one (long) ensemble member is available. To keep this consistent with the other scenarios, for which we have 5 ensemble members x 20-year periods, we use the first 100 years of this only. 

ARISE: the SAI scenario. finishes at end 2069, so we use the final 20 years as a our SAI assessment period. 

SSP245: the background warming scenario. output is also for 2050-2069 period. 


 
Output data has many variables, named according to CMIP conventions, see here for meanings: https://clipc-services.ceda.ac.uk//dreq/mipVars.html

Main.ipynb needs to be run on JASMIN because file paths are specific to the CEDA archive. 

 
