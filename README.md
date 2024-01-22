Main.ipynb contains code to process ARISE, ssp245 and PiControl runs in UKESM1 into maps showing the ensemble and time means (+standard deviations). It outputs small .nc files containing a set of spatially resolved means and standard deviations variables to /Output_data. For each scenario, we output .nc files containing each the mean state under a given 20-year time-window, both for the full annual data, ('all'), and for individual seasons. This gives 10 files per scenario (4 seasons + annual, for mean and std. There are two outputs for SSP245: the first is the baseline, the second is the warmer world without SAI (i.e. SSP245 scenario at the same time period which we use for assessing ARISE (2050-2069).  


SSP245_baseline: the target state ARISE aims for, i.e. the 20-year period from the concatenated historical and SSP2-4.5 runs with mean temperature closest to 1.5C above pre-industrial (2013-2022). We use only the 5 ensemble members from which the ARISE runs branch. /n
Preindustrial: the PiControl run output. In this case only one (long) ensemble member is available. To keep this consistent with the other scenarios, for which we have 5 ensemble members x 20-year periods, we use the first 100 years of this only. 
ARISE: the SAI scenario. finishes at end 2069, so we use the final 20 years as a our SAI assessment period. 
SSP245: the background warming scenario. output is also for 2050-2069 period. 

![image](https://github.com/alistairduffey/ARISE_processing/assets/47328986/59304ec2-7c64-4034-bc52-5098b041dd38)



Output data has 14 variables, named according to CMIP conventions, see here for meanings: https://clipc-services.ceda.ac.uk//dreq/mipVars.html

The processing chain to produce these output data for ARISE and SSP2-4.5 is as follows:

1. Read in monthly data from the [CEDA archive]([url](https://archive.ceda.ac.uk/)) for each scenario, and for all 5 ensemble members. 
2. Resample this data to quarterly, starting at December (so DJF, MAM, JJA, SON).
3. Select the apprpriate 20-year window. For ARISE and SSP2-4.5, this is 2050-2069 inclusive (i.e. the last 20 years available). For SSP2-4.5 baseline this is 2013-2022, which is the 1.5C crossing point.
4. Repeat the above for all variables (14 were used) and combine into one xarray dataset per scenario.
5. Take the mean and standard deviation across both years and ensemble members (that is, the five ensemble members are combined to generate 100 years' worth of climate state at the window).
6. Output the seasonal data to seperate files by season, with the format: 'Output_data/{scenario}/{scenario}_{season}_mean.nc' and 'Output_data/{scenario}/{scenario}_{season}_std.nc'
7. Output the anual mean data to files with the format: 

The pre-industrial baseline (piControl) follows a similar set of steps, except it uses only 1 ensemble member, from which we take a 100 year extract over which we calculate the mean and std, for consistency with the other scenarios. 


References:

ARISE scenario: [Richter et al., 2022]([url](https://gmd.copernicus.org/articles/15/8221/2022/))
UKESM1 model: [Sellar et al., 2019]([url](https://onlinelibrary.wiley.com/doi/abs/10.1029/2019MS001739))  
UKESM1 simulations of the ARISE scenario: [Henry et al., 2023]([url](https://acp.copernicus.org/articles/23/13369/2023/acp-23-13369-2023.html))
SSP2-4.5 scenario: [O'Neill et al., 2016]([url](https://gmd.copernicus.org/articles/9/3461/2016/))


N.B:
Main.ipynb needs to be run on JASMIN because file paths are specific to the CEDA archive. 

 
