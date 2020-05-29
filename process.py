from netCDF4 import Dataset
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from typing import Iterable, Any, Tuple

def signal_last(it:Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
  iterable = iter(it)
  ret_var = next(iterable)
  for val in iterable:
    yield False, ret_var
    ret_var = val
  yield True, ret_var

filename = 'OR_GLM-L2-LCFA_G16_s20191472305000_e20191472305200_c20191472305228.nc'
ncin = Dataset(filename, 'r', format='NETCDF4')

latitude = ncin.variables['event_lat']
longitude = ncin.variables['event_lon']

nlat = len(latitude)
nlon = len(longitude)

correctedLatitude = latitude * latitude.scale_factor + latitude.add_offset
correctedLongitude = longitude * longitude.scale_factor + longitude.add_offset

merged_list = list(set([i for i in tuple(zip(latitude, longitude))]))

open('lightning.json', 'w').close()
with open('lightning.json', 'a') as file:
  file.write('{\n\t"type": "FeatureCollection",\n\t"features": [\n')
  for is_last_element, point in signal_last(merged_list):
    file.write('\t\t{\n\t\t\t"type": "Feature",\n\t\t\t"geometry": {\n')
    file.write('\t\t\t\t"type": "Point",\n\t\t\t\t"coordinates": [' + str(point[1]) + ', ' + str(point[0]) + ']\n')
    if is_last_element:
      file.write('\t\t\t}\n\t\t}\n')
    else:
      file.write('\t\t\t}\n\t\t},\n')
  file.write('\t]\n}')