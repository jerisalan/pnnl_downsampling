# PNNL Downsampling of data
A python program to down sample time-series data from a NetCDF4 file to a lower frequency

## How to run
To run the above project, first clone the project to your local system using the command `git clone https://github.com/jerisalan/pnnl_downsampling.git`

Then navigate into the project directory using the command `cd pnnl_downsampling`

Once you are in the directory, run the following command in the terminal
`python pnnl.py`

The output CDFNet4 file will be generated in the main project directory with the filename `sgpmetavgE13.b1.20180101.000000.cdf`.

To tun the tests and assertions, run the following command in the terminal `pytest test.py`

## Packages required
* netCDF4
* numpy
* pandas
* pytest
