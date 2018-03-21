from pnnl import downsample
import pytest
from  netCDF4 import Dataset
import pandas as pd
import numpy as np

# Test to check if the downsampling function gives correct results
def test_downsampling():
	index = pd.date_range('1/1/2000', periods=10, freq='2T')
	series = pd.Series(range(10), index=index)
	series = downsample(series, '5T')
	assert series[1] == 3.5
	
# Test to verify the frequency of records after downsampling
def test_number_of_downsamples():
	index = pd.date_range('1/1/2000', periods=10, freq='10T')
	series = pd.Series(range(10), index=index)
	series = downsample(series, '5T')
	assert len(series) == 19

# Test to check the file format for the given netCDF4 files
def test_file_format():
	dataset = Dataset('data/sgpmetE13.b1.20180105.000000.cdf')
	assert dataset.data_model == "NETCDF4" or dataset.data_model == 'NETCDF3_CLASSIC' or dataset.data_model == 'NETCDF4_CLASSIC'

