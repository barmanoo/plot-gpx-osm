#!/usr/bin/env python

'''
#  gpx_import.py - Used to import GPX XML files into applications
#
#  Copyright (C) 2009 Andrew Gee
#
#  GPX Viewer is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  GPX Viewer is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.

#
#  If you're having any problems, don't hesitate to contact: andrew@andrewgee.org
#

modified by Olivier Friard


'''
 
import xml.dom.minidom as minidom
#from iso8601 import parse_date as parse_xml_date

__all__ = ['import_gpx_trace']


class ParseError(Exception):
    """Raised when there is a problem parsing any part of the GPX XML"""
    pass

def fetch_metadata(node):
    metadata = {}
    for mnode in node.childNodes:
        if mnode.nodeName == 'name':
            metadata['name'] = mnode.childNodes[0].nodeValue
            
        elif mnode.nodeName == 'desc':
            try:
                metadata['description'] = mnode.childNodes[0].nodeValue
            except:
                metadata['description'] = "" #no description
            
        elif mnode.nodeName == "time":
            metadata['time'] = mnode.childNodes[0].nodeValue
            
        elif mnode.nodeName == "author":
            metadata['author'] = {}
            for anode in mnode.childNodes:
                if anode.nodeName == "name":
                    metadata['author']['name'] = anode.childNodes[0].nodeValue
                elif anode.nodeName == "email":
                    metadata['author']['email'] = anode.childNodes[0].nodeValue
                elif anode.nodeName == "link":
                    metadata['author']['link'] = anode.childNodes[0].nodeValue
                    
        elif mnode.nodeName == "copyright":
            metadata['copyright'] = {}
            if mnode.attributes["author"].value != "":
                metadata['copyright']['author'] = mnode.attributes["author"].value
            for cnode in mnode.childNodes:
                if cnode.nodeName == "year":
                    metadata['copyright']['year'] = cnode.childNodes[0].nodeValue
                elif cnode.nodeName == "license":
                    metadata['copyright']['license'] = cnode.childNodes[0].nodeValue
                    
        elif mnode.nodeName == "link":
            metadata['link'] = {}
            if mnode.attributes["href"].value != "":
                metadata['link']['href'] = mnode.attributes["href"].value
            for lnode in mnode.childNodes:
                if lnode.nodeName == "text":
                    metadata['link']['text'] = lnode.childNodes[0].nodeValue
                elif lnode.nodeName == "type":
                    metadata['link']['type'] = lnode.childNodes[0].nodeValue
                    
        elif mnode.nodeName == "time":
            metadata['time'] = parse_xml_date(mnode.childNodes[0].nodeValue)
                    
        elif mnode.nodeName == "keywords":
            metadata['keywords'] = mnode.childNodes[0].nodeValue
        
    return metadata


def fetch_track_point(tsnode):
    point = {}
    if tsnode.attributes["lat"] != "" and tsnode.attributes["lon"] != "":
        point['lat'] = float(tsnode.attributes["lat"].value)
        point['lon'] = float(tsnode.attributes["lon"].value)
    
    for tpnode in tsnode.childNodes:
        if tpnode.nodeName == "ele":
            point['ele'] = float(tpnode.childNodes[0].nodeValue)
        elif tpnode.nodeName == "desc":
            point['description'] = tpnode.childNodes[0].nodeValue
        elif tpnode.nodeName == "time":
            #point['time'] = parse_xml_date(tpnode.childNodes[0].nodeValue)
            point['time'] = tpnode.childNodes[0].nodeValue
        elif tpnode.nodeName == "name":
            point['name'] = tpnode.childNodes[0].nodeValue

    return point


def fetch_track_segment(tnode):
    trkseg = {}
    trkseg['points'] = []
    for tsnode in tnode.childNodes:
        if tsnode.nodeName == "trkpt":
            trkseg['points'].append(fetch_track_point(tsnode))

    return trkseg



def fetch_track(node):
    track = {}
    track['segments'] = []
    track['name'] = ''

    for tnode in node.childNodes:
        if tnode.nodeName == "name":
            track['name'] = tnode.childNodes[0].nodeValue
        if tnode.nodeName == "trkseg":
            track_segment = fetch_track_segment(tnode)
            if len(track_segment['points']) > 0:
                track['segments'].append(fetch_track_segment(tnode))

    return track


def fetch_route(node):
    route = {}
    route['points'] = []
    route['name'] = ''

    for tnode in node.childNodes:
        if tnode.nodeName == 'name':
            route['name'] = tnode.childNodes[0].nodeValue
        if tnode.nodeName == 'rtept':
            route['points'].append( fetch_track_point( tnode ) )

    return route



def fetch_waypoint(node):
    wpt = {}
    if node.attributes["lat"] != "" and node.attributes["lon"] != "":
        wpt['lat'] = float(node.attributes["lat"].value)
        wpt['lon'] = float(node.attributes["lon"].value)
        
    for mnode in node.childNodes:
        if mnode.nodeName == 'name':
            wpt['name'] = mnode.childNodes[0].nodeValue
        if mnode.nodeName == 'ele':
            wpt['ele'] = float(mnode.childNodes[0].nodeValue)
    return wpt
            


def import_gpx(filename):
    '''
    import GPX file
    returns a dictionary
    '''
    doc = minidom.parse(filename)

    doce = doc.documentElement

    if doce.nodeName != 'gpx':
        raise Exception

    gpx = {}
    gpx['filename'] = filename
    gpx['tracks'] = []
    gpx['wpt'] = []
    gpx['rte'] = []

    '''try:'''
    e = doce.childNodes
    for node in e:
        if node.nodeName == 'metadata':
            gpx['metadata'] = fetch_metadata(node)
        if node.nodeName == 'trk':
            gpx['tracks'].append(fetch_track(node))
        if node.nodeName == 'wpt':
            gpx['wpt'].append( fetch_waypoint(node) )
        if node.nodeName == 'rte':
            gpx['rte'].append( fetch_route(node) )
                
    '''
    except:
        raise Exception
    '''

    return gpx




def pointsToGeoJSON(points):
    '''
    convert list of Points (from GPX file) in GeoJSON coordinates list
    '''
    coordinates = []
    for p in points:
        coordinates.append( [ p['lon'],p['lat'] ] )
    return coordinates
