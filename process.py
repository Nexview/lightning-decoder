from netCDF4 import Dataset
from math import radians, cos, sin, asin, sqrt
import argparse, csv, os

def haversine(lon1, lat1, lon2, lat2):
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
  c = 2 * asin(sqrt(a))
  r = 6371
  return c * r

parser = argparse.ArgumentParser(description='Process lightning data for a specific radar site.')
parser.add_argument('site', action='store', type=str, help='Station Code')

args = parser.parse_args()

site = args.site.upper()

sites = open(os.fsencode(os.path.dirname(os.path.abspath(__file__)) + '/wsr.tsv'))
read_site = csv.reader(sites, delimiter='\t')

center_point = []
for line in read_site:
  if line[0] == site:
    center_point.append({'lat': float(line[1]), 'lon': float(line[2])})
    break
sites.close()
open(os.fsencode(os.path.dirname(os.path.abspath(__file__)) + '/lightning.json'), 'w').close()
with open(os.fsencode(os.path.dirname(os.path.abspath(__file__)) + '/lightning.json'), 'a') as file:
  directory = os.fsencode(os.path.dirname(os.path.abspath(__file__)) + '/data/')
  file.write('{\n\t"type": "FeatureCollection",\n\t"features": [')

  numFiles = len(os.listdir(directory))

  for ncfile in os.listdir(directory):
    filename = os.fsdecode(directory + ncfile)
    ncin = Dataset(filename, 'r', format='NETCDF4')

    latitude = ncin.variables['flash_lat']
    longitude = ncin.variables['flash_lon']

    numFiles = numFiles - 1

    nlat = len(latitude)
    nlon = len(longitude)

    correctedLatitude = latitude[:]
    correctedLongitude = longitude[:]

    if all(x in latitude.ncattrs() for x in ['scale_factor', 'add_offset']):
      correctedLatitude = latitude * latitude.scale_factor + latitude.add_offset
    if all(x in longitude.ncattrs() for x in ['scale_factor', 'add_offset']):
      correctedLongitude = longitude * longitude.scale_factor + longitude.add_offset

    merged_list = list(set([i for i in tuple(zip(correctedLatitude, correctedLongitude))]))

    lat1 = center_point[0]['lat']
    lon1 = center_point[0]['lon']
    file.write('\n\t\t{\n\t\t\t"type": "Feature",\n\t\t\t"geometry": {\n')
    file.write('\t\t\t\t"type": "MultiPoint",\n\t\t\t\t"coordinates": [\n\t\t\t\t\t')
    for point in merged_list:
      lat2 = point[0]
      lon2 = point[1]

      radius = 230.0

      a = haversine(lon1, lat1, lon2, lat2)
      if a <= radius:
        file.write('[' + str(point[1]) + ', ' + str(point[0]) + '], ')
    file.seek(0, os.SEEK_END)
    file.seek(file.tell() - 2, os.SEEK_SET)
    file.truncate()
    file.write('\n\t\t\t\t]\n\t\t\t},\n\t\t\t"properties": {\n\t\t\t\t"time_offset": ' + str(numFiles) + '\n\t\t\t}\n\t\t},')
  file.seek(0, os.SEEK_END)
  file.seek(file.tell() - 1, os.SEEK_SET)
  file.truncate()
  file.write('\n\t]\n}')
  file.close()