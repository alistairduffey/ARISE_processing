"""
This file contains useful functions for processing netcdf files.

get_time_slice() - This function returns a time slice from the CMIP6 CEDA archive, first concatenating the files in the selected data folder together.
get_seasonal_mean_std() - This function returns 2 xarray datasets for the time-mean and standard deviation calculated over the selected years for the selected season.
get_fixed() - This function returns the fixed area and land fraction variables

"""

import numpy as np
import xarray as xr
import os
#import xclim
import glob

def chunked_mean(ds, n, dim='year'):
    """
    Calculate mean values in even chunks along a specified dimension in an xarray dataset.

    Parameters:
        ds (xr.Dataset): The xarray dataset.
        n (int): Number of even chunks to split the dimension into.
        dim (str): The dimension along which to split the data (default: 'year').

    Returns:
        list: list of the mean value for each chunk.
    """
    # Calculate the size of each chunk
    chunk_size = int(len(ds[dim]) / n)

    # Create an empty list to store mean values
    mean_values = []

    # Loop through and calculate mean for each chunk
    for i in range(n):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size if i < n - 1 else None
        chunk = ds.isel({dim: slice(start_idx, end_idx)})
        mean = chunk.mean(dim=dim).values*1
        mean_values.append(mean)

    return mean_values

def read_in(dir, ocean = False):
    files = []
    for x in os.listdir(dir):
        files.append(dir + x)
    with dask.config.set(**{'array.slicing.split_large_chunks': True}):
        if ocean:
            ds = replace_x_y_nominal_lat_lon(rename_cmip6(xr.open_mfdataset(files)))
        else: 
            ds = rename_cmip6(xr.open_mfdataset(files, use_cftime=True))
    return ds


def read_in_ens_mean(dir, ocean = False):
    files = []
    for x in os.listdir(dir):
        files.append(dir + x)
    with dask.config.set(**{'array.slicing.split_large_chunks': True}):
        if ocean:
            ds = replace_x_y_nominal_lat_lon(rename_cmip6(xr.open_mfdataset(files)))
        else: 
            ds = rename_cmip6(xr.open_mfdataset(files, use_cftime=True))
    return ds





def get_time_from_folder(path, end_string=None):
    # make a list of the full path to all netcdf files in folder
    if end_string:
        dir_files = glob.glob(path + '*{}.nc'.format(end_string))
    else:
        dir_files = glob.glob(path + '*.nc')
    if len(dir_files) == 0: # if folder is empty return None and print error.
        print("empty dir")
        return None
    
    file_list = dir_files
    
    """
    Concatenate files, if necessary, then select time
    """
    if len(file_list) == 1: # if there's just 1 file open it.
        ds = xr.open_dataset(file_list[0])
    elif len(file_list) > 1: # if there's a list, open all of them and concatenate them together.
        ds_list = [ xr.open_dataset(idx) for idx in file_list ]
        ds = xr.concat(ds_list, 'time')
        
    else:
        print("ERROR: file_list:", file_list)
        return
    
    # return ds
    return ds
# end def.

def get_all_time(model, centre, var, domain, exp, project, run, grid):
    """
    This function returns all the data from the selected CMIP6 dataset first concatenating the files in the selected data folder together.
    USAGE:
    model, centre, var, domain, exp, project, run [string].
    """
    
    """
    Collect the files needed from ceda_dir 
    """
    # define the data directory to search for files using lists
    ceda_dir='/badc/cmip6/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/latest/'.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
    # define the data directory for synda:
    synda_dir='~/.synda/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/*/'.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
    synda_dir = os.path.expanduser(synda_dir) # replace '~' with /home/users/<USERNAME>/
    
    # make a list of the full path to all netcdf files in synda or ceda if synda empty.
    dir_files = glob.glob(synda_dir + '*.nc')
    if len(dir_files) == 0: # if synda empty try ceda
        dir_files = glob.glob(ceda_dir + '*.nc')
    if len(dir_files) == 0: # if both ceda and synda are empty return None and print error.
        print("folder not in synda or ceda:",ceda_dir)
        return None
    
    file_list = dir_files
    
    """
    Concatenate files, if necessary, then select time
    """
    if len(file_list) == 1: # if there's just 1 file open it.
        ds = xr.open_dataset(file_list[0])
    elif len(file_list) > 1: # if there's a list, open all of them and concatenate them together.
        ds_list = [ xr.open_dataset(idx) for idx in file_list ]
        ds = xr.concat(ds_list, 'time')
    else:
        print("ERROR: file_list:", file_list)
        return
    
    # return ds
    return ds
# end def.
    
def get_all_time_ens(model, centre, var, domain, exp, project, runs, grid):
    """
    This function returns all the data from the selected CMIP6 dataset first concatenating the files in the selected data folder together.
    USAGE:
    model, centre, var, domain, exp, project, 
    runs [list] - to loop over.
    """
    
    # get all runs
    ds_list = [get_all_time(model, centre, var, domain, exp, project, RUN, grid) for RUN in runs]
    # concatenate all runs
    ds_ens = xr.concat(ds_list, "run")
    # return all runs
    return ds_ens
#end def
    
def get_time_slice(dates, model, centre, var, domain, exp, project, run, grid, time_files=0):
    """
    This function returns a time slice from the CMIP6 CEDA archive, first concatenating the files in the selected data folder together.
    USAGE:
    dates [list] = ['2070-01-01','2100-01-01'] - selects the time-slice to calculate over
    model, centre, var, domain, exp, project, run [string] - specifies which files to 
    time_files [integer] = 0, 1, 2... - by default [0] all files will be concatenated before the time-slice is extracted. 
        this may be time-consuming for long experiments. If you know that your time slice spans, e.g. only the last 2 files then enter 2.
    """
    
    """
    Collect the files needed from ceda_dir 
    """
    # define the data directory to search for files using lists
    ceda_dir='/badc/cmip6/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/latest/'.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
    # define the data directory for synda:
    synda_dir='~/.synda/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/*/'.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
    synda_dir = os.path.expanduser(synda_dir) # replace '~' with /home/users/<USERNAME>/
    
    # make a list of the full path to all netcdf files in synda or ceda if synda empty.
    dir_files = glob.glob(synda_dir + '*.nc')
    if len(dir_files) == 0: # if synda empty try ceda
        dir_files = glob.glob(ceda_dir + '*.nc')
    if len(dir_files) == 0: # if both ceda and synda are empty return None and print error.
        print("folder not in synda or ceda:",ceda_dir)
        return None
    
    if time_files == 0: # select all files
        file_list = dir_files
    elif time_files < len(ceda_dir_files): # select number of time files chosen
        file_list = ceda_dir_files[len(dir_files)-time_files:]
    else:
        print("ERROR: time_files >= length of file list")
        return
    
    """
    Concatenate files, if necessary, then select time
    """
    if len(file_list) == 1: # if there's just 1 file open it.
        ds = xr.open_dataset(file_list[0])
    elif len(file_list) > 1: # if there's a list, open all of them and concatenate them together.
        ds_list = [ xr.open_dataset(idx) for idx in file_list ]
        ds = xr.concat(ds_list, 'time')
    else:
        print("ERROR: file_list:", file_list)
        return
    
    # select time period and return
    try:
        ds_slice = ds.sel(time=slice(dates[0],dates[1]))
        return ds_slice # this line returns the output. 
    except ValueError as error:
        print("error in dates:",dates)
        print(error)
        return
# end def.

def get_seasonal_mean_std(season, dates, data_dir, model, centre, var, domain, exp, project, run, grid, time_files=0, over_write=False):
    """
    This function returns 2 xarray datasets for the time-mean and standard deviation calculated over the selected years for the selected season.
    A netcdf copy of this processes file will be saved in the ~/data/ folder. The function will check to see if the file is already present before 
    processing the raw files again, saving time.
    
    USAGE:
    season [string] = 'ANN', 'DJF', 'MAM', 'JJA', or 'SON' - selects the season to calculate
    dates [list] = ['2070-01-01','2100-01-01'] - selects the time-slice to calculate over
    data_dir = '/home/users/<USERNAME>/data/' - enter your username here!
    model, centre, var, domain, exp, project, run [string] - specifies which files to 
    time_files [integer] = 0, 1, 2... - by default [0] all files will be concatenated before the time-slice is extracted. 
        this may be time-consuming for long experiments. If you know that your time slice spans, e.g. only the last 2 files then enter 2.
    """
    
    """
    First define directories and filenames
    """
    # define the data directory to search for files using lists
    ceda_dir='/badc/cmip6/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/latest/'.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
    # define the base of the filename for the output file(s) using lists, note this matches the file format in the data directory except for the date_4_file section and the missing .nc. 
    out_base='{var}_{domain}_{model}_{exp}_{run}_{grid}_{time_range}'.format(var=var, domain=domain, model=model, exp=exp, run=run, grid=grid, time_range=dates[0]+'_'+dates[1])
    # define a simplified folder structure for our output data directory.
    data_dir_full=data_dir + '{model}/{exp}/{var}/'.format(model=model, exp=exp, var=var)
    
    # Format the output filenames
    fname_mean = out_base + '_' + season + '_mean.nc'
    fname_std = out_base + '_' + season + '_std.nc'
    
    # specify the full output file paths
    fpath_mean = os.path.join(data_dir_full,fname_mean)
    fpath_std = os.path.join(data_dir_full,fname_std)
    
    """
    Check if processed files already exist, if so return those and end.
    """
    if os.path.isfile(fpath_mean) and os.path.isfile(fpath_std) and not over_write: # and not over_write:
        ds_mean = xr.open_dataset(fpath_mean)
        ds_std = xr.open_dataset(fpath_std)
        print("loading existing files", out_base, season)
        return ds_mean, ds_std
    
    print("processing files", out_base, season)
    
    # make directory to store output netcdfs
    os.makedirs(data_dir_full, exist_ok=True)
    
    """
    Use get_time_slice() to collect the needed data and take the time-slice needed.
    """
    args=[dates,model,centre,var,domain,exp,project,run,grid,time_files]
    ds_tslice = get_time_slice(*args) # *args passes the list of values in as arguments to the get_time_slice function.
    
    """
    Take seasonal mean and standard deviation
    """
    season_list = ['DJF','MAM','JJA','SON']
    if season == 'ANN':
        # calculate annual mean and standard deviation
        ds_yearly = ds_tslice.groupby('time.year').mean(dim='time') # take mean over every year
        ds_seas_mean = ds_yearly.mean(dim='year')
        ds_seas_std = ds_yearly.std(dim='year')

    elif season in season_list:
        ds_seasonal = list(ds_tslice.groupby('time.season')) # split into seasons
        # take mean over each season to produce a timeseries
        ds_seasonal_series = [ idx[1].groupby('time.year').mean('time') for idx in ds_seasonal if idx[0] == season ]
        # calculate mean and standard deviation across this seasonal timeseries.
        ds_seas_mean = ds_seasonal_series[0].mean('year')
        ds_seas_std = ds_seasonal_series[0].std('year')
    else:
        print("only ANN, DJF, MAM, JJA, or SON allowed, you entered:", season)
        return
    
    """
    Finally, save output to netcdf to use again later and also return result
    """
    # output datasets to netcdf
    ds_seas_mean.to_netcdf(fpath_mean)
    ds_seas_std.to_netcdf(fpath_std)
    # return seasonal (or annual) mean and standard deviation
    return ds_seas_mean, ds_seas_std

# end def

"""
Note to self - add print "file missing: ..." and return None for missing file.
"""

def get_ens_seasonal_mean_std(season, dates, data_dir, model, centre, var, domain, exp, project, runs, grid, time_files=0, over_write=False, stat='mean'):
    """
    This function returns 2 xarray datasets for the time-mean and standard deviation calculated over the selected years and runs for the selected season.
    it is the same as get_seasonal_mean_std except that a list of runs must be provided rather than a single 
    
    USAGE:
    season [string] = 'ANN', 'DJF', 'MAM', 'JJA', or 'SON' - selects the season to calculate
    dates [list] = ['2070-01-01','2100-01-01'] - selects the time-slice to calculate over
    data_dir = '/home/users/<USERNAME>/data/' - enter your username here!
    model, centre, var, domain, exp, project [string] - specifies which files to work on
    runs [list of strings] - specifies the runs to combine for the ensemble-mean
    time_files [integer] = 0, 1, 2... - by default [0] all files will be concatenated before the time-slice is extracted. 
        this may be time-consuming for long experiments. If you know that your time slice spans, e.g. only the last 2 files then enter 2.
    
    For max / min day in year statistics set stat = 'max' / 'min' in the function call, and ensure that you set domain to 'day'
    """
    
    """
    First define directories and filenames
    """
    # define the data directory but leave {run} undefined
    ceda_dir='/badc/cmip6/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/latest/'.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run='{run}', grid=grid)
    # define the base of the filename for the output ensemble-mean file(s).
    out_base='{var}_{domain}_{model}_{exp}_ens-mean_{grid}_{time_range}'.format(var=var, domain=domain, model=model, exp=exp, grid=grid, time_range=dates[0]+'_'+dates[1])
    # define a simplified folder structure for our output data directory.
    data_dir_full=data_dir + '{model}/{exp}/{var}/'.format(model=model, exp=exp, var=var)
    
    # Format the output filenames
    if stat == 'mean':
        fname_mean = out_base + '_' + season + '_mean.nc'
        fname_std = out_base + '_' + season + '_std.nc'
    elif stat == 'max':
        fname_mean = out_base + '_' + season + '_max_mean.nc' # add max to name for max
        fname_std = out_base + '_' + season + '_max_std.nc'
    elif stat == 'min':
        fname_mean = out_base + '_' + season + '_min_mean.nc' # add min to name for min
        fname_std = out_base + '_' + season + '_min_std.nc'
    else:
        print('stat must be mean, max or min:', stat)
        return None
    
    # specify the full output file paths
    fpath_mean = os.path.join(data_dir_full,fname_mean)
    fpath_std = os.path.join(data_dir_full,fname_std)
    
    """
    Check if processed files already exist, if so return those and end.
    """
    if os.path.isfile(fpath_mean) and os.path.isfile(fpath_std): # and not over_write:
        ds_mean = xr.open_dataset(fpath_mean)
        ds_std = xr.open_dataset(fpath_std)
        print("loading existing files", out_base, season, stat)
        return ds_mean, ds_std
    
    print("processing files", out_base, season, stat)
    
    # make directory to store output netcdfs
    os.makedirs(data_dir_full, exist_ok=True)
    
    """
    Use get_time_slice() to collect the needed data and take the time-slice needed.
    """
    
    # test if runs are a list.
    if type(runs) is not list:
        print('runs must be a list. you entered:',runs)
        return 
    
    # Run get_time_slice() once for each run.
    args_list=[[dates,model,centre,var,domain,exp,project,IDX,grid,time_files] for IDX in runs] # make X lists of input arguments
    tslices = [get_time_slice(*ARGS) for ARGS in args_list] # make a list of X timeslice outputs
    
    # Combine the X runs into an ensemble dataset along a new "run" dimension
    ds_ens = xr.concat(tslices, "run")
    
    """
    Take seasonal mean and standard deviation
    """
    season_list = ['DJF','MAM','JJA','SON']
    if season == 'ANN':
        if stat == 'mean':
            ds_yearly = ds_ens.groupby('time.year').mean(dim='time') # take mean over every year
        elif stat == 'max':
            ds_yearly = ds_ens.groupby('time.year').max(dim='time') # take mean over every year
        elif stat == 'min':
            ds_yearly = ds_ens.groupby('time.year').min(dim='time') # take mean over every year
        # calculate annual mean and standard deviation
        ds_seas_mean = ds_yearly.mean(dim=['year','run']) # take mean over years and runs
        ds_seas_std = ds_yearly.std(dim=['year','run'])

    elif season in season_list:
        ds_seasonal = list(ds_ens.groupby('time.season')) # split into seasons
        # take mean over each season to produce a timeseries
        if stat == 'mean':
            ds_seasonal_series = [ idx[1].groupby('time.year').mean('time') for idx in ds_70_100_seasons if idx[0] == season ]
        elif stat == 'max':
            ds_seasonal_series = [ idx[1].groupby('time.year').max('time') for idx in ds_70_100_seasons if idx[0] == season ]
        elif stat == 'min':
            ds_seasonal_series = [ idx[1].groupby('time.year').min('time') for idx in ds_70_100_seasons if idx[0] == season ]
        # calculate mean and standard deviation across this seasonal timeseries.
        ds_seas_mean = ds_seasonal_series[0].mean(dim=['year','run']) # take mean over years and runs
        ds_seas_std = ds_seasonal_series[0].std(dim=['year','run'])
    else:
        print("only ANN, DJF, MAM, JJA, or SON allowed, you entered:", season)
        return
    
    """
    Finally, save output to netcdf to use again later and also return result
    """
    # output datasets to netcdf
    ds_seas_mean.to_netcdf(fpath_mean)
    ds_seas_std.to_netcdf(fpath_std)
    # Open the files to gather the output, to ensure the function passes the same output regardless of whether file created or read.
    ds_seas_mean_file = xr.open_dataset(fpath_mean)
    ds_seas_std_file = xr.open_dataset(fpath_std)
    # return seasonal (or annual) mean and standard deviation
    return ds_seas_mean_file, ds_seas_std_file

# end def

def get_fixed(centre, model, grid='gn', runs_2_check=['r1i1p1f1','r1i1p1f2']):
    """
    This function returns the fixed area and land fraction variables:
    areacella - area of gridcells
    sftlf - fraction of each grid cell that is land
    
    You'll need to find which run is the pre-industrial baseline. Search here: https://esgf-index1.ceda.ac.uk/search/cmip6-ceda/
    search for 'areacella' and the model name.
    """
    
    project='CMIP'
    exp='piControl'
    domain='fx'
    
    # define the folder and filenames
    ceda_dir='/badc/cmip6/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/latest/'
    fname='{var}_{domain}_{model}_{exp}_{run}_{grid}.nc'
    
    for run in runs_2_check:
    
        # Get area
        var = 'areacella'
        dir_path = ceda_dir.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
        f_path = fname.format(var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
        
        # Check if files are there before trying to open them
        if os.path.isfile(dir_path + f_path):
        
            ds_area = xr.open_dataset(dir_path + f_path)

            # Get land fraction
            var = 'sftlf'
            dir_path = ceda_dir.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
            f_path = fname.format(var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
            ds_land = xr.open_dataset(dir_path + f_path)
            
            return ds_area, ds_land
        #endif
# end def

def get_index_series(dates, data_dir, model, centre, var, domain, exp, project, run, grid, index_name, index_kwargs, time_files=0, index_name_file=None, index_args=[], over_write=False):
    """
    This function returns the output of the xclim index called on the time-slice of the file(s) specified, i.e. a timeseries of index values
    It will only work for indices that require a single variable. 
    
    USAGE:
    dates [list] = ['2070-01-01','2100-01-01'] - selects the time-slice to calculate over
    data_dir = '/home/users/<USERNAME>/data/' - enter your username here!
    model, centre, var, domain, exp, project, run [string] - specifies which files to 
    time_files [integer] = 0, 1, 2... - by default [0] all files will be concatenated before the time-slice is extracted. 
        this may be time-consuming for long experiments. If you know that your time slice spans, e.g. only the last 2 files then enter 2.
    index_name [string] - the name of the xclim index, e.g. 'growing_degree_days'.
    index_name_file [string] - the index name for use in the file, defaults to index_name. may need to be changed if underscores or long names problematic.
    index_args [array] - the arguments to pass to xclim. defaults to an empty list as most (all?) indices use only keyword args
    index_kwargs [dictionary] - a dictionary containing the list of keyword arguments to pass to the xclim.indices.<index_name> function. e.g.
        index_kwargs={'tas':None, # where ds_day is a dataset that has been previously loaded.
            'thresh':'10.0 degC',
            'freq':'YS',}
    
    !!!!! CRITICAL !!!!! - for the keyword argument that specifies the input variable dataarray, 'tas' in this case, enter the value: None (no quotes, 
        None is a special variable like True and False). This None entry will be replaced with the results of a call to get_time_slice()
    
    WARNING - this function will not distinguish between different calls to the same index (different index_kwargs) for a given input file,
    they will all write to the same file.
    """
    
    """
    First define directories and filenames
    """
   
    # define the data directory to search for files using lists
    ceda_dir='/badc/cmip6/data/CMIP6/{project}/{centre}/{model}/{exp}/{run}/{domain}/{var}/{grid}/latest/'.format(project=project, centre=centre, var=var, domain=domain, model=model, exp=exp, run=run, grid=grid)
    # define the base of the filename for the output file(s) using lists, note this matches the file format in the data directory except for the date_4_file section and the missing .nc. 
    out_base='{var}_{domain}_{model}_{exp}_{run}_{grid}_{time_range}'.format(var='{var}', domain=domain, model=model, exp=exp, run=run, grid=grid, time_range=dates[0]+'_'+dates[1])
    
    # use index_name_file if specified, else use index_name for the filename.
    if index_name_file is None:
        index_name_file = index_name    

    # define a simplified folder structure for our output data directory.
    data_dir_full=data_dir + '{model}/{exp}/{var}/'.format(model=model, exp=exp, var=index_name_file)
    
    # Format the output filenames
    fname_out = out_base.format(var=index_name_file) + '.nc'
    
    # specify the full output file paths
    fpath = os.path.join(data_dir_full,fname_out)
    
    """
    Check if processed files already exist, if so return those and end.
    """
    if os.path.isfile(fpath):# and not over_write: # and not over_write:
        ds_index = xr.open_dataset(fpath)
        print("loading existing files", fname_out)
        return ds_index
    
    print("processing files", fname_out)
    
    # make directory to store output netcdfs
    os.makedirs(data_dir_full, exist_ok=True)
    
    """
    Use get_time_slice() to collect the needed data and take the time-slice needed.
    """
    args=[dates,model,centre,var,domain,exp,project,run,grid,time_files]
    ds_tslice = get_time_slice(*args) # *args passes the list of values in as arguments to the get_time_slice function.

    """
    Call the xclim index function
    """
    
    func_kwargs = index_kwargs.copy() # copy needed so we don't edit the original!
    # First replace the None item in the index_kwargs with the output of get_time_slice()
    for key, value in func_kwargs.items():
        if value is None: # replace None value in dictionary with something:
            func_kwargs[key] = ds_tslice[var] # xclim.index() is expecting a dataarray so we specify the variable within the dataset
    
    # define index_to_call as the function xclim.indices.index_name() with python's getattr() function
    index_to_call = getattr(xclim.indices, index_name)
    
    # calculate the index function, filling in the arguments and keyword arguments defined previously
    ds_index = index_to_call(*index_args, **func_kwargs)
    
    """
    Finally, save output to netcdf to use again later and also return result
    """
    
    # output datasets to netcdf
    ds_index.to_netcdf(fpath)
    # overwrite ds_index with output saved to file so that pre-processed and new are identical
    ds_index_file = xr.open_dataset(fpath)
    # return index timeseries
    return ds_index_file

def get_ens_index(dates, data_dir, model, centre, var, domain, exp, project, runs, grid, index_name, index_kwargs, time_files):
    """
    This function calculates an ensemble mean for indices
    """
    ds_list = [get_index_series(dates, data_dir, model, centre, var, domain, exp, project, RUN, grid, index_name, index_kwargs, time_files=time_files) 
               for RUN in runs]
    
    # Combine the X runs into an ensemble dataset along a new "run" dimension
    ds_ens = xr.concat(ds_list, 'run')

    # Take the mean over the time (years in this case) and run dimensions
    ds_ens_mean = ds_ens.mean(dim=['time','run'])
    ds_ens_std = ds_ens.std(dim=['time','run'])
    
    # return mean and std
    return ds_ens_mean, ds_ens_std




# -*- coding: utf-8 -*-
"""Operations on cartesian geographical grid."""
import numpy as np

EARTH_RADIUS = 6371000.0  # m


def _guess_bounds(points, bound_position=0.5):
    """
    Guess bounds of grid cells.
    
    Simplified function from iris.coord.Coord.
    
    Parameters
    ----------
    points: numpy.array
        Array of grid points of shape (N,).
    bound_position: float, optional
        Bounds offset relative to the grid cell centre.
    Returns
    -------
    Array of shape (N, 2).
    """
    diffs = np.diff(points)
    diffs = np.insert(diffs, 0, diffs[0])
    diffs = np.append(diffs, diffs[-1])

    min_bounds = points - diffs[:-1] * bound_position
    max_bounds = points + diffs[1:] * (1 - bound_position)

    return np.array([min_bounds, max_bounds]).transpose()


def _quadrant_area(radian_lat_bounds, radian_lon_bounds, radius_of_earth):
    """
    Calculate spherical segment areas.
    Taken from SciTools iris library.
    Area weights are calculated for each lat/lon cell as:
        .. math::
            r^2 (lon_1 - lon_0) ( sin(lat_1) - sin(lat_0))
    The resulting array will have a shape of
    *(radian_lat_bounds.shape[0], radian_lon_bounds.shape[0])*
    The calculations are done at 64 bit precision and the returned array
    will be of type numpy.float64.
    Parameters
    ----------
    radian_lat_bounds: numpy.array
        Array of latitude bounds (radians) of shape (M, 2)
    radian_lon_bounds: numpy.array
        Array of longitude bounds (radians) of shape (N, 2)
    radius_of_earth: float
        Radius of the Earth (currently assumed spherical)
    Returns
    -------
    Array of grid cell areas of shape (M, N).
    """
    # ensure pairs of bounds
    if (
        radian_lat_bounds.shape[-1] != 2
        or radian_lon_bounds.shape[-1] != 2
        or radian_lat_bounds.ndim != 2
        or radian_lon_bounds.ndim != 2
    ):
        raise ValueError("Bounds must be [n,2] array")

    # fill in a new array of areas
    radius_sqr = radius_of_earth ** 2
    radian_lat_64 = radian_lat_bounds.astype(np.float64)
    radian_lon_64 = radian_lon_bounds.astype(np.float64)

    ylen = np.sin(radian_lat_64[:, 1]) - np.sin(radian_lat_64[:, 0])
    xlen = radian_lon_64[:, 1] - radian_lon_64[:, 0]
    areas = radius_sqr * np.outer(ylen, xlen)

    # we use abs because backwards bounds (min > max) give negative areas.
    return np.abs(areas)


def grid_cell_areas(lon1d, lat1d, radius=EARTH_RADIUS):
    """
    Calculate grid cell areas given 1D arrays of longitudes and latitudes
    for a planet with the given radius.
    
    Parameters
    ----------
    lon1d: numpy.array
        Array of longitude points [degrees] of shape (M,)
    lat1d: numpy.array
        Array of latitude points [degrees] of shape (M,)
    radius: float, optional
        Radius of the planet [metres] (currently assumed spherical)
    Returns
    -------
    Array of grid cell areas [metres**2] of shape (M, N).
    """
    lon_bounds_radian = np.deg2rad(_guess_bounds(lon1d))
    lat_bounds_radian = np.deg2rad(_guess_bounds(lat1d))
    area = _quadrant_area(lat_bounds_radian, lon_bounds_radian, radius)
    return area


def calc_spatial_mean(
    xr_da, lon_name="longitude", lat_name="latitude", radius=EARTH_RADIUS
):
    """
    Calculate spatial mean of xarray.DataArray with grid cell eding.
    
    Parameters
    ----------
    xr_da: xarray.DataArray
        Data to average
    lon_name: str, optional
        Name of x-coordinate
    lat_name: str, optional
        Name of y-coordinate
    radius: float
        Radius of the planet [metres], currently assumed spherical (not important anyway)
    Returns
    -------
    Spatially averaged xarray.DataArray.
    """
    lon = xr_da[lon_name].values
    lat = xr_da[lat_name].values

    area_weights = grid_cell_areas(lon, lat, radius=radius)
    #aw_factor = area_weights / area_weights.max()

    #return (xr_da * aw_factor).mean(dim=[lon_name, lat_name])
    return ((xr_da * area_weights).sum(dim=[lon_name, lat_name]))/area_weights.sum()


def calc_spatial_integral(
    xr_da, lon_name="longitude", lat_name="latitude", radius=EARTH_RADIUS
):
    """
    Calculate spatial integral of xarray.DataArray with grid cell weighting.
    
    Parameters
    ----------
    xr_da: xarray.DataArray
        Data to average
    lon_name: str, optional
        Name of x-coordinate
    lat_name: str, optional
        Name of y-coordinate
    radius: float
        Radius of the planet [metres], currently assumed spherical (not important anyway)
    Returns
    -------
    Spatially averaged xarray.DataArray.
    """
    lon = xr_da[lon_name].values
    lat = xr_da[lat_name].values

    area_weights = grid_cell_areas(lon, lat, radius=radius)

    return (xr_da * area_weights).sum(dim=[lon_name, lat_name])