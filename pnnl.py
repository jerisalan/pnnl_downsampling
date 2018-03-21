import os
import numpy as np 
import pandas as pd
from netCDF4 import Dataset

def ncdump(nc_fid, verb=True):
    '''
    ncdump outputs dimensions, variables and their attribute information.
    ncdump requires a valid instance of Dataset.

    Parameters
    ----------
    nc_fid : netCDF4.Dataset
        A netCDF4 dateset object
    verb : Boolean
        whether or not nc_attrs, nc_dims, and nc_vars are printed

    Returns
    -------
    nc_attrs : list
        A Python list of the NetCDF file global attributes
    nc_dims : list
        A Python list of the NetCDF file dimensions
    nc_vars : list
        A Python list of the NetCDF file variables
    '''
    def print_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        try:
            print "\t\ttype:", repr(nc_fid.variables[key].dtype)
            for ncattr in nc_fid.variables[key].ncattrs():
                print '\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr))
        except KeyError:
            print "\t\tWARNING: %s does not contain variable attributes" % key

    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        print "NetCDF Global Attributes:"
        for nc_attr in nc_attrs:
            print '\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        print "NetCDF dimension information:"
        for dim in nc_dims:
            print "\tName:", dim 
            print "\t\tsize:", len(nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        print "NetCDF variable information:"
        for var in nc_vars:
            if var not in nc_dims:
                print '\tName:', var
                print "\t\tdimensions:", nc_fid.variables[var].dimensions
                print "\t\tsize:", nc_fid.variables[var].size
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

# 
def downsample(df, format):
    '''
    downsample function downsamples the dataframe df as per given format 

    Parameters
    ----------
    df : Pandas.DataFrame
        A pandas dataframe object
    format : String
        A string representation of the downsampling frequency

    Returns
    -------
    df : Pandas.DataFrame
        A Python pandas dataframe object
    '''
    return df.resample(format).mean()

# Python lists to store the dataframes from CDF files
atmos_pressure = []
temp_mean = []
rh_humidity = []
datetime = []


for subdir, dirs, files in os.walk('data'):
    for file in files:
        filename = subdir + os.sep + file # iterate over all files in the directory
        if filename.endswith(".cdf"):
            # print(filename)
            nc_fid = Dataset(filename, "r", format="NETCDF4")

            basetime = nc_fid.variables['base_time'][:]
            atmos = nc_fid.variables['atmos_pressure'][:] 
            temp = nc_fid.variables['temp_mean'][:]
            humidity = nc_fid.variables['rh_mean'][:]
            time = nc_fid.variables['time_offset'][:] + basetime # Add base_time to the time_offset of each row value

            atmos_pressure = np.append(atmos_pressure, atmos)
            temp_mean = np.append(temp_mean, temp)
            rh_humidity = np.append(rh_humidity, humidity)
            datetime = np.append(datetime, time)            
            datetime = datetime[:].astype(int) # type cast the time from float to int

            nc_fid.close()

# Combine all the lists to for a single dataframe
df = np.stack((datetime, atmos_pressure, temp_mean, rh_humidity), axis=-1)
df = pd.DataFrame(df)
df.columns = ['time', 'atmos_pressure', 'temp_mean', 'rh_humidity']
df = df.sort_values(by=['time']) # Sort the dataframe based on the time values

df = df.replace(-9999, np.nan) # Replacing missing values with NaN so they dont affect the downsampled mean value.

df['time'] = pd.to_datetime(df['time'], unit='s')
df = df.set_index('time') # Index the dataframe on time column

rdf = downsample(df, '5T') # downsample the data

# Write the results to a new file
w_nc_fid = Dataset('sgpmetavgE13.b1.20180101.000000.cdf', 'w', format='NETCDF4')
w_nc_fid.description = "Downsampled 5 minute average of atmospheric_pressure, mean temperature and relative humidity data "

atm_p = w_nc_fid.createDimension('atmos_pressure', len(rdf))
t_mean = w_nc_fid.createDimension('temp_mean', len(rdf))
rt_hum = w_nc_fid.createDimension('rh_humidity', len(rdf))

# Create new variables and set metadata
atmp_var = w_nc_fid.createVariable('atmospheric_pressure', np.float32, ('atmos_pressure'))
atmp_var.long_name = u'Atmospheric pressure'
atmp_var.units = u'kPa'

tmean_var = w_nc_fid.createVariable('mean_temperature', np.float32, ('temp_mean'))
tmean_var.long_name = u'Temperature mean'
tmean_var.units = u'degC'

rhum_var = w_nc_fid.createVariable('relative_humidity', np.float32, ('rh_humidity'))
rhum_var.long_name = u'Relative humidity mean'
rhum_var.units = u'%'

# Add the list to the variables created
w_nc_fid.variables['atmospheric_pressure'][:] = rdf['atmos_pressure'].as_matrix()
w_nc_fid.variables['relative_humidity'][:] = rdf['rh_humidity'].as_matrix()
w_nc_fid.variables['mean_temperature'][:] = rdf['temp_mean'].as_matrix()

w_nc_fid.close() # Close the new file

nc_fid = Dataset("sgpmetavgE13.b1.20180101.000000.cdf", "r", format="NETCDF4")
nc_attrs, nc_dims, nc_vars = ncdump(nc_fid)
print(nc_fid.variables.keys())
atmos = nc_fid.variables['atmospheric_pressure'][:] 
print(atmos)
