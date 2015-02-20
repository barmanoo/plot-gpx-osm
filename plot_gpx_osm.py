#!/usr/bin/env python

'''
Plot GPX file

create bitmaps from a GPX trace using OpenStreetMap
(c) Olivier Friard 2014

require:
- osm.py
- python-shapely
- gpx_import.py

2014-07-10: added plotting of waypoints GPX
            added plot dots option (-d)
2014-04-18: added argument parsing function: gpx_map.py -h
2014-04-17: added control: every points must be on the map


INFO:
wpt -> track
gpsbabel -i gpx -f waypoints.gpx -x transform,trk=wpt -o gpx -F 1.gpx

TODO:
* add support to KML files
http://gis.stackexchange.com/questions/89543/get-points-from-a-kml-linestring

* add scale

'''

from __future__ import division, print_function

import argparse
import os
import sys
import osm
import gpx_import
import ImageDraw
import ImageFont
from shapely.geometry import Polygon, Point


def draw_gpx_track( image, top_lat, left_lon, degLat_pix, degLong_pix , points, traceWidth, traceColor, plotDots ):
    '''
    add GPX track on image
    return image modified
    '''
    draw = ImageDraw.Draw(image)
    firstPoint = True

    for point in points:
        p_y2, p_x2 = osm.coord2pix( point['lat'], point['lon'], top_lat, left_lon, degLat_pix, degLong_pix )

        if plotDots or firstPoint:

            draw.ellipse((p_x2 - traceWidth, p_y2 - traceWidth, p_x2 + traceWidth, p_y2 + traceWidth), fill = traceColor)
            memx = p_x2
            memy = p_y2
            firstPoint = False
        else:
            draw.line((memx, memy, p_x2,p_y2), fill = traceColor, width = traceWidth)
            memx = p_x2
            memy = p_y2

    return image


def save_image(image, outDir, outFormat, count):
    '''
    inc count
    save image
    return count
    '''
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('FreeSans.ttf', 12)    
    draw.text((0, 0),'(c) OpenStreetMap contributors', (64, 64, 64), font=font)
    
    count += 1
    
    if outDir:
        outDir += '/'

    image.save( '%s%03d.%s' % (outDir, count, outFormat) )
    if not outDir:
        outDir = 'current directory'
    print('image #%d saved in %s' % (count, outDir))
    return count


def get_map(filename, outDir, server, size_x, size_y, zoom, overlap, traceColor, traceWidth, plotDots, outFormat ):

    if not os.path.isfile(filename):
        print( 'File not found' )
        return

    gpx = gpx_import.import_gpx(filename)
    

    if gpx['tracks']:

        print( 'Number of track(s): %d' % len( gpx['tracks'] ) )
        print( 'Number of segment(s) in first track: %d' % len( gpx['tracks'][0]['segments'] ) )
        print('Plot first segment of first track')
        points = gpx['tracks'][0]['segments'][0]['points']

    elif gpx['wpt']:

        #print( 'No track found in GPX file!' )
        print( 'Waypoints found, plot waypoints' )
        points = gpx['wpt']

    elif gpx['rte']:
        
        print( 'Route found, plot first route' )
        points = gpx['rte'][0]['points']

    else:
        return
        

    print( 'Number of points: %d' % len(points) )
    
    count = 0
    
    ref_lat = 0
    ref_lon = 0
    
    idx = 0
    polygon = {}
    
    ref = 1
    ref_center = Point(0,0)
    
    ### start
    image, top_lat, left_lon, bottom_lat, right_long, scale_x, scale_y = osm.get_image(size_x,size_y , points[0]['lat'], points[0]['lon'], zoom , server)
    degLat_pix = abs(top_lat - bottom_lat) / size_y
    degLong_pix = abs(left_lon - right_long) / size_x
    
    image = draw_gpx_track( image, top_lat, left_lon, degLat_pix, degLong_pix , points, traceWidth, traceColor, plotDots )
    
    count = save_image(image,  outDir, outFormat, count )
    
    ref_pol = Polygon([(top_lat, left_lon), (top_lat, right_long),(bottom_lat, right_long), (bottom_lat, left_lon)])
    
    
    
    point_idx = 1
    while point_idx < len(points):
    
        image, top_lat, left_lon, bottom_lat, right_long, scale_x, scale_y = osm.get_image(size_x,size_y , points[point_idx]['lat'], points[point_idx]['lon'], zoom , server)
    
        polygon[point_idx] = Polygon([(top_lat, left_lon), (top_lat, right_long),(bottom_lat, right_long), (bottom_lat, left_lon)])
    
        degLat_pix = abs(top_lat - bottom_lat) / size_y
        degLong_pix = abs(left_lon - right_long) / size_x
    

        if not ref_pol.contains( Point( points[point_idx]['lat'], points[point_idx]['lon']) ) :
            
            mem_point_idx = point_idx
    
            while point_idx < len(points):
                image, top_lat, left_lon, bottom_lat, right_long, scale_x, scale_y = osm.get_image(size_x,size_y , points[point_idx]['lat'], points[point_idx]['lon'], zoom , server)
                polygon[point_idx] = Polygon([(top_lat, left_lon), (top_lat, right_long),(bottom_lat, right_long), (bottom_lat, left_lon)])
                
                ### check if all points on map
                all_contained = True
                for i in range(mem_point_idx, point_idx +1):
                    if not polygon[point_idx].contains( Point( points[i]['lat'], points[i]['lon'] ) ):
                        all_contained = False
                        break
                
                if not all_contained:
                    break
    
                ### check overlap
                intersectionArea = ref_pol.intersection( polygon[point_idx]).area / ref_pol.area 
                if intersectionArea <= overlap:
                    break
                
                point_idx += 1
                
            image = draw_gpx_track( image, top_lat, left_lon, degLat_pix, degLong_pix , points, traceWidth, traceColor , plotDots)
    
            count = save_image(image, outDir, outFormat, count )
            print( '%d %%' % round(point_idx/ len(points) *100))
            
            ref_pol = Polygon([(top_lat, left_lon), (top_lat, right_long),(bottom_lat, right_long), (bottom_lat, left_lon)])
            
        point_idx += 1




if __name__ == "__main__":

    parser = argparse.ArgumentParser( description = 'Create maps from a GPX trace using OpenStreetMapFetch' )
    
    parser.add_argument( '-i', '--input', help = 'Input file containing the GPX track', required = True )

    parser.add_argument( '-z', '--zoom', type=int, help = 'Zoom level (4-19)', required=True )

    parser.add_argument( '-s', '--server', help = 'OSM server - default is tile.openstreetmap.org (for cycle: http://a.tile.opencyclemap.org/cycle)',  default = 'http://tile.openstreetmap.org' )
    
    parser.add_argument( '-f', '--output_format', help = 'Output image format (png/jpg) - default is PNG',  default = 'png' )

    parser.add_argument( '-o', '--output',  help = 'Output directory name',  default = '' )

    parser.add_argument( '-over', '--overlap', type=float, help = '% of overlap between consecutive maps', default = 13 )

    parser.add_argument( '-x', '--width', type=int, help = 'Map width (pixels)', default = 800 )
    parser.add_argument( '-y', '--height', type=int, help = 'Map height (pixels)', default = 800 )

    parser.add_argument( '-w', '--trace_width', type=int, help = 'Trace width (pixels)', default = 2 )

    parser.add_argument( '-d', '--plot_dots',  help = 'Plot dots', default=False, action='store_true')

    traceColor = (255, 0, 0)

    args = vars(parser.parse_args())
    
    print(args['plot_dots'])
    
    if args['output'] and not os.path.isdir(args['output']):
        print( '%s is not a valid directory' % args['output'] )
        sys.exit(1)
        
    if not args['output_format'].lower() in ['png','jpg']:
        print( '%s is not an allowed image format' % args['output_format'] )
        sys.exit(2)
        
    
    get_map(args['input'], args['output'], args['server'], args['width'], args['height'],  args['zoom'], args['overlap']/100, traceColor, args['trace_width'], args['plot_dots'], args['output_format'].lower())
