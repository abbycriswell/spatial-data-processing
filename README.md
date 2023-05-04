# Species Spaces

## Using shape files from IUCN database to determine habitat area (km²) for a given species.

made by Abby Criswell
with the Havird Lab at
the University of Texas at Austin
updated 5-4-2023

## Dependencies: 
- python
- geopandas 0.9.0 +

## To Use:
 1) download SpatialDatafromShapefiles.py 
 2) setup dependencies 
   [I recommend using pip: https://geopandas.org/en/stable/getting_started/install.html#installing-with-pip)]
 3) gather folder containing folders (name: species) with shapefile (1 per species, name: 'data_0.shp') 
   [This should be the default file structure when downloading shapefiles from IUCN.]
   [Example: For the species Bufo japonicus, need the file Data_Folder/Bufo japonicus/data_0.shp. See example files in repository.]
 4) gather list of species to process as a csv file (default to skipping first line for column header)
   [See the example file 'specieslist.csv' in repository.]
 5) change path variables in SpatialDatafromShapefiles.py
     - path: where output should be put 
           [Example: "./Example/" puts output as shown in example files in repository.]
     - shapefile_path: folder containing shapefile folders (labeled by species)
           [Example: "./Example/Data_Folder/" takes in shapefiles as shown in example files in repository.]
     - specieslist_path: path to csv file with list of species to try
           [Example: "./Example/specieslist.csv" reads list file as shown in example files in repository.]
 6) run SpatialDatafromShapefiles.py
 7) output:
     - Species area results listed in 'species_info.tsv' [See the example file 'species_info.tsv' in repository.]
     - If analysis for a species was unsuccessful (data missing, mislabeled, computation error), listed in 'species_notfound.txt' [See the example file 'species_info.tsv' in repository.]

Thank you to IUCN for data used in analysis.
