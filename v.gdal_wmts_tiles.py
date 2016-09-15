#!/usr/bin/env python

"""
MODULE:    v.gdaltiles

AUTHOR(S): Helmut Kudrnovsky <alectoria AT gmx at>

PURPOSE:   Calculates bbox of every geometry in a vector layer
           and writes GDAL WMTS capapility xml file

COPYRIGHT: (C) 2016 by the GRASS Development Team

           This program is free software under the GNU General Public
           License (>=v2). Read the file COPYING that comes with GRASS
           for details.
"""

#%module
#% description: writing GDAL WMTS capapility xml files for vector geometries
#% keyword: vector
#% keyword: geometry
#%end

#%option G_OPT_V_INPUT 
#% key: input
#% required: yes
#%end

#%flag
#% key: c
#% description: print minimum and maximum cats of vector
#% guisection: print
#%end

#%flag
#% key: b
#% description: print bounding box of vector layer
#% guisection: print
#%end

#%flag
#% key: t
#% description: print bounding box of vector geometries
#% guisection: print
#%end

#%option G_OPT_M_DIR
#% key: dir
#% description: Directory where the output will be found
#% required : no
#% guisection: output
#%end

#%option
#% key: prefix
#% type: string
#% key_desc: prefix
#% description: output prefix (must start with a letter)
#% guisection: output
#%end

#%flag
#% key: s
#% description: export GDAL WMTS xml files for vector geometries
#% guisection: output
#%end

import sys
import os
import csv
import math
import shutil
import tempfile
import grass.script as grass
from grass.pygrass.vector import VectorTopo
from grass.pygrass.vector.geometry import Area
import xml.etree.ElementTree as etree

if not os.environ.has_key("GISBASE"):
    grass.message( "You must be in GRASS GIS to run this program." )
    sys.exit(1)

def main():

    vector = options['input'].split('@')[0]
    directory = options['dir']
    print_min_max_cats = flags['c']
    print_bbox_vector = flags['b']
    print_bbox_vector_geometries = flags['t']
    export_xml = flags['s']
    prefix = options['prefix']

    ######
    # define minimum and maximum cat in vector layer
    ######    
    vcats = grass.read_command("v.category", input = vector,
                                     option = "report",
                                     flags = "g",
                                     quiet = True)
		
    vcats_min = int(vcats.split()[8])
    vcats_max = int(vcats.split()[9])
    vcats_max_plus = vcats_max + 1	

    ######
    # print minimum and maximum cat in vector layer
    ###### 	
    if print_min_max_cats :

		grass.message( "min cat: %s max cat: %s" % (vcats_min, vcats_max))

    ######
    # print bbox of vector layer
    ###### 	
    if print_bbox_vector :
		# open vector
		vtopo = VectorTopo(vector)
		vtopo.open(mode = 'r')
		# bbox call
		bbox_vector = vtopo.bbox()
		# bbox north, south, west, east
		bbv_north = bbox_vector.north
		bbv_south = bbox_vector.south
		bbv_west = bbox_vector.west
		bbv_east = bbox_vector.east
		# close vector
		vtopo.close()	
		grass.message( "north: %s south: %s west: %s east: %s" % (bbv_north, bbv_south, bbv_west, bbv_east))
		
    ######
    # print bbox of vector layer geometries
    ###### 
    if print_bbox_vector_geometries :
		# open vector
		vtopo = VectorTopo(vector)
		vtopo.open(mode = 'r')
		# loop thru vector geometries		
		for i in range(1, vcats_max_plus):
				# get vector geometries area info
				vect_geom_area = Area(v_id = i, c_mapinfo = vtopo.c_mapinfo)
				# get vector geometries bbox info				
				vect_geom_bb = vect_geom_area.bbox()
				# bbox north, south, west, east
				bb_north = vect_geom_bb.north
				bb_south = vect_geom_bb.south
				bb_west = vect_geom_bb.west
				bb_east = vect_geom_bb.east
				grass.message("cat %s: north: %s south: %s west: %s east: %s" %(i, bb_north, bb_south, bb_west, bb_east))
		# close vector
		vtopo.close()				

    ######
    # export xml files
    ###### 
    if export_xml :
		# open vector
		vtopo = VectorTopo(vector)
		vtopo.open(mode = 'r')
		# loop thru vector geometries		
		for i in range(1, vcats_max_plus):
				# get vector geometries area info
				vect_geom_area = Area(v_id = i, c_mapinfo = vtopo.c_mapinfo)
				# get vector geometries bbox info				
				vect_geom_bb = vect_geom_area.bbox()
				# bbox north, south, west, east
				bb_north = vect_geom_bb.north
				bb_south = vect_geom_bb.south
				bb_west = vect_geom_bb.west
				bb_east = vect_geom_bb.east
				# cast bbox north, south, west, east to integer as GDAL needs inter coordinates
				bb_north_i = int(bb_north)
				bb_south_i = int(bb_south)
				bb_west_i = int(bb_west)
				bb_east_i = int(bb_east)
				# increase bbox north and east +1, decrease bbox west and south -1 to get overlapping tiles
				bb_north_i_plus = bb_north_i + 1
				bb_south_i_plus = bb_south_i - 1
				bb_west_i_plus = bb_west_i - 1
				bb_east_i_plus = bb_east_i + 1				
				# cast i to string
				i_str = str(i)
				# define xml file
				xml_file_short = prefix+i_str+'.xml'
				xml_file_long = os.path.join( directory, xml_file_short )
				#construct xml file
				gdal_wmts = etree.Element("GDAL_WMTS")
				getcapurl = etree.SubElement(gdal_wmts, "GetCapabilitiesUrl")
				getcapurl.text = "https://www.basemap.at/wmts/1.0.0/WMTSCapabilities.xml"
				layer = etree.SubElement(gdal_wmts, "Layer")
				layer.text = "bmaporthofoto30cm"
				style = etree.SubElement(gdal_wmts, "Style")
				style.text = "normal"
				tilematrixset = etree.SubElement(gdal_wmts, "TileMatrixSet")
				tilematrixset.text = "google3857"
				datawindow = etree.SubElement(gdal_wmts, "DataWindow")
				upperleftx = etree.SubElement(datawindow, "UpperLeftX")
				upperleftx.text = "%s" % bb_west_i_plus
				upperlefty = etree.SubElement(datawindow, "UpperLeftY")
				upperlefty.text = "%s" % bb_north_i_plus
				lowerrightx = etree.SubElement(datawindow, "LowerRightX")
				lowerrightx.text = "%s" % bb_east_i_plus
				lowerrighty = etree.SubElement(datawindow, "LowerRightY")
				lowerrighty.text = "%s" % bb_south_i_plus
				bandscount = etree.SubElement(gdal_wmts, "BandsCount")
				bandscount.text = "4"
				cache = etree.SubElement(gdal_wmts, "Cache")
				unsafessl = etree.SubElement(gdal_wmts, "UnsafeSSL")
				unsafessl.text = "true"
				zeroblockhttpcodes = etree.SubElement(gdal_wmts, "ZeroBlockHttpCodes")
				zeroblockhttpcodes.text = "204,404"
				zeroblockonserverexception = etree.SubElement(gdal_wmts, "ZeroBlockOnServerException")
				zeroblockonserverexception.text = "true"
				# write xml file
				etree.ElementTree(gdal_wmts).write(xml_file_long)				
		# close vector
		vtopo.close()


if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
