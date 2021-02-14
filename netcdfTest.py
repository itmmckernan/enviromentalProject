import netCDF4

path = 'C:/Users/itmm/Downloads/vwnd.10m.gauss.2020.nc'

rootGroup = netCDF4.Dataset(path, "r", format='NETCDF4_CLASSIC')


breakpoint()