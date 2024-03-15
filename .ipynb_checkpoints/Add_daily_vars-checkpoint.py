import os
import glob
import pandas as pd
import numpy as np
import xarray as xr
from xmip.preprocessing import rename_cmip6
import matplotlib
import matplotlib.pyplot as plt
from nc_processing import calc_spatial_mean
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")


### options

# Model
model = 'UKESM1-0-LL' 

# SAI reference baseline (to be taken from joined historical-into-ssp245 runs)
baseline_start, baseline_end = '2013','2032' # years are INCLUSIVE. gives warming of 1.49 in UKESM1, closest 20-year period to 1.5

# SAI assessment period
SAI_assessment_period_start, SAI_assessment_period_end = '2050', '2069' # years are INCLUSIVE

# ARISE ensemble_members. We also only use these same members for the baseline
ens_mems = ['r1i1p1f2', 'r2i1p1f2', 'r3i1p1f2', 'r4i1p1f2', 'r8i1p1f2']

# seasons
seasons = ['DJF', 'MAM', 'JJA', 'SON']

# make SSP245 ensemble mean pr ds
def get_ssp245_ds(variable, table='Amon'):
    ds_list = []
    for es in ens_mems:
        path = '/badc/cmip6/data/CMIP6/ScenarioMIP/MOHC/UKESM1-0-LL/ssp245/{e}/{t}/{v}/*/latest/'.format(e=es, t=table,v=variable)
        ds = rename_cmip6(xr.open_mfdataset(path+'*.nc'))
        
        path_hist = glob.glob('/badc/cmip6/data/CMIP6/*/*/UKESM1-0-LL/historical/{e}/{t}/{v}/*/latest/'.format(
        t=table, v=variable, e=es))[0]
        ds_hist = rename_cmip6(xr.open_mfdataset(path_hist+'*.nc'))    
        ds = xr.concat([ds_hist, ds], dim='time')
        ds = ds.sel(time=slice('1990', '2150'))
        if 'height' in ds.variables:
            ds = ds.drop('height')
        if 'type' in ds.variables:
            ds = ds.drop('type')
        ds_list.append(ds)
    
    DS = xr.concat(ds_list, dim='Ensemble_member')
    return DS

## similar, for PiControl
def get_pi(model, variable='tas', table='Amon'):
    dir_pi = glob.glob('/badc/cmip6/data/CMIP6/*/*/{m}/piControl/r1i*/{t}/{v}/*/latest/'.format(m=model, t=table, v=variable))
    files_pi = os.listdir(dir_pi[0])[0:3] # don't need the full length run
    paths_pi = []
    for x in files_pi:
        paths_pi.append(dir_pi[0]+x)
    ds = rename_cmip6(xr.open_mfdataset(paths_pi))
    if 'height' in ds.variables:
        ds = ds.drop('height')
    if 'type' in ds.variables:
        ds = ds.drop('type')
    return ds

## for ARISE
def get_ARISE_UKESM(variable='tas', table='Amon'):
    ds_list = []
    paths = glob.glob('/badc/deposited2022/arise/data/ARISE/MOHC/UKESM1-0-LL/arise-sai-1p5/*/{t}/{v}/*/*/'.format(
    t=table, v=variable))
    for path in paths:
        ds = rename_cmip6(xr.open_mfdataset(path+'*.nc'))
        if 'height' in ds.variables:
            ds = ds.drop('height')
        if 'type' in ds.variables:
            ds = ds.drop('type')
        ds_list.append(ds)
    DS = xr.concat(ds_list, dim='Ensemble_member')
    return DS

def process_and_save(ds, ds_seasonal, label, seasons=seasons):
    """ 
    Inputs
    ds: a time resolved, quarterly resampled, spatial dataset, with an ensemble_member dimension
    label: 'baseline', 'sai', or 'preindustrial'. Defines naming of outputs. 
    
    Function saves the mean and standard deviation across the whole time+ens_mems combined dimension
    """
    path = 'Output_data/{l}/'.format(l=label)
    if not os.path.isdir(path):
        os.mkdir(path)
    
    for season in seasons:
        ds_season = ds_seasonal.where(ds_seasonal.time.dt.season == season, drop=True)
        std = ds_season.std(dim=['time', 'Ensemble_member'])
        mean = ds_season.mean(dim=['time', 'Ensemble_member'])
        #except:
        #    std = ds_season.std(dim=['time'])
        #    mean = ds_season.mean(dim=['time'])

        std.to_netcdf('Output_data/{l}/pr_max_{l}_{s}_std.nc'.format(l=label, s=season))
        mean.to_netcdf('Output_data/{l}/pr_max_{l}_{s}_mean.nc'.format(l=label, s=season))
        
    # repeat for the annual mean:
    #try:
    ds.std(dim=['time', 'Ensemble_member']).to_netcdf('Output_data/{l}/pr_max_{l}_all_std.nc'.format(l=label))
    ds.mean(dim=['time', 'Ensemble_member']).to_netcdf('Output_data/{l}/pr_max_{l}_all_mean.nc'.format(l=label))
    #except:
    #    ds.std(dim=['time']).to_netcdf('Output_data/{l}/pr_max_{l}_all_std.nc'.format(l=label))
    #    ds.mean(dim=['time']).to_netcdf('Output_data/{l}/pr_max_{l}_all_mean.nc'.format(l=label))



################
var = 'pr'
################

ds = get_ssp245_ds(variable=var, table='day')
ds_seasonal = ds.resample(time="QS-DEC").max()
ds_annual = ds.resample(time="1Y").max()

out_baseline, out_baseline_seasonal = ds_annual.sel(time=slice(baseline_start, baseline_end)), ds_seasonal.sel(time=slice(baseline_start, baseline_end))
out_baseline.attrs['t_bnds'] = [baseline_start, baseline_end]
out_baseline_seasonal.attrs['t_bnds'] = [baseline_start, baseline_end]

out_ssp245, out_ssp245_seasonal = ds_annual.sel(time=slice(SAI_assessment_period_start, SAI_assessment_period_end)), ds_seasonal.sel(time=slice(SAI_assessment_period_start, SAI_assessment_period_end))
out_ssp245.attrs['t_bnds'] = [SAI_assessment_period_start, SAI_assessment_period_end]
out_ssp245_seasonal.attrs['t_bnds'] = [SAI_assessment_period_start, SAI_assessment_period_end]

process_and_save(ds = out_baseline,
                 ds_seasonal = out_baseline_seasonal,
                 label = 'SSP245_baseline',
                 seasons=seasons)

process_and_save(ds = out_ssp245,
                 ds_seasonal = out_ssp245_seasonal,
                 label = 'SSP245',
                 seasons=seasons)

### now repeat for ARISE:
ds = get_ARISE_UKESM(variable=var, table='day')
ds_seasonal = ds.resample(time="QS-DEC").max()
ds_annual = ds.resample(time="1Y").max()

out_arise, out_arise_seasonal = ds_annual.sel(time=slice(SAI_assessment_period_start, SAI_assessment_period_end)), ds_seasonal.sel(time=slice(SAI_assessment_period_start, SAI_assessment_period_end))
out_arise.attrs['t_bnds'] = [SAI_assessment_period_start, SAI_assessment_period_end]
out_arise_seasonal.attrs['t_bnds'] = [SAI_assessment_period_start, SAI_assessment_period_end]

process_and_save(ds = out_arise,
                 ds_seasonal = out_arise_seasonal,
                 label = 'ARISE',
                 seasons=seasons)