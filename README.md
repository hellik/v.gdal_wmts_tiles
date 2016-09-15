# v.gdal_wmts_tiles
v.gdal_wmts_tiles - prototype to generate GDAL's local service description XML file to tile WMTS

the script works as a GRASS GIS addon.

workflow:

- v.mkgrid - to create a vector map of a user-defined grid
- v.gdal_wmts_tiles -s input=quads10@user1 dir=data prefix=a - to generate GDAL's local service description XML file to tile WMTS
