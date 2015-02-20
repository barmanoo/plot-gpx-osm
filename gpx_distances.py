#!/usr/bin/env python

'''
Calculate the distances between consecutive points in a GPX track file

require:
- osm.py
- gpx_import.py

usage:
python gpx_distances.py file.gpx

'''
from __future__ import division, print_function

import sys
import osm
import gpx_import

gpx = gpx_import.import_gpx(sys.argv[1])


#print(gpx['rte'][0]['points'])


if gpx['tracks']:

    print( 'Number of track(s): %d' % len( gpx['tracks'] ) )
    print( 'Number of segment(s) in first track: %d' % len( gpx['tracks'][0]['segments'] ) ) 
    
    GPXtrack = gpx['tracks'][0]['segments'][0]['points']

elif gpx['rte']:
    
    print( 'Number of route(s) found in GPX file: %d' % len( gpx['rte'] ) )
    GPXtrack = gpx['rte'][0]['points']


else:
    sys.exit(0)




dmax = 0
dmin = 1e9
totDist = 0

idx = 0
while True:
    if idx + 1 < len(GPXtrack):

        dist = osm.distance([GPXtrack[idx]['lat'] , GPXtrack[idx]['lon']] , [ GPXtrack[idx + 1]['lat'] , GPXtrack[idx + 1]['lon'] ])

        totDist += dist

        #print( idx,[GPXtrack[idx]['lat'] , GPXtrack[idx]['lon']] , [ GPXtrack[idx + 1]['lat'] , GPXtrack[idx + 1]['lon'] ],dist)
        
        if dist > dmax:
            dmax = dist
            if 'time' in GPXtrack[idx]:
                dmax_time = GPXtrack[idx]['time']
            else:
                dmax_time = '-'

        if dist < dmin:
            dmin = dist
            if 'time' in GPXtrack[idx]:
                dmin_time = GPXtrack[idx]['time']
            else:
                dmin_time = '-'
    else:
        break
    idx += 1

print( '%d points' % (idx+1))
print( 'Total distance: %.3f Km' % (totDist/1000))
print( 'Mean distance between points: %.1f m' % (totDist/(idx+1)))
print( 'min distance: %.1f m (%s)\nmax distance: %.1f m (%s)' % (dmin, dmin_time, dmax, dmax_time) )
