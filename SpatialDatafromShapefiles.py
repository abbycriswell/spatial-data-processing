# made by Abby Criswell
# with the University of Texas at Austin
# updated 9-7-2023

import csv
from os import listdir
from os.path import isdir, join, splitext
import geopandas

#To Run:
# run in command line: python SpatialDatafromShapefiles.py
# after changing path variables (path, shapefile_path, specieslist_path)
# and range types of interest list variable (range_types_of_interest)
# in the sections directly below

#PATH VARIABLES:
#CHANGE THESE AS NEEDED
#path: where output should be put
path="./Example/"
#shapefile_path: folder containing shapefile folders (labeled by species)
shapefile_path = "./Example/" + "Data_Folder/"
#specieslist_path: path to csv file with list of species to try
specieslist_path = "./Example/" + "specieslist.csv"

#RANGE TYPE GROUPS:
#all: all range types
all_range_types = ["extant (resident)", "extant (breeding)", "extant (non-breeding)", "extant (passage)", "probably extant (resident)", "possibly extant (resident)", "extant & origin uncertain (resident)", "extant & reintroduced (resident)", "extant & introduced (resident)", "extant & vagrant (seasonality uncertain)", "probably extant & origin uncertain (resident)", "possibly extant & vagrant (seasonality uncertain)", "presence uncertain", "possibly extinct & introduced", "possibly extinct", "extinct & reintroduced", "extinct"]
#historical: extant and extinct resident and breeding areas (includes reintroducted and origin uncertain, but not introduced, non-breeding, vagrant, or passage)
historical_range_types = ["extant (resident)", "extant (breeding)", "probably extant (resident)", "possibly extant (resident)", "extant & origin uncertain (resident)", "extant & reintroduced (resident)", "probably extant & origin uncertain (resident)", "presence uncertain", "possibly extinct", "extinct & reintroduced", "extinct"]
#current: extant resident and breeding areas (includes introduced, reintroduced, possibly extinct, and origin uncertain, but not extinct, non-breeding, vagrant, or passage)
current_range_types = ["extant (resident)", "extant (breeding)", "probably extant (resident)", "possibly extant (resident)", "extant & origin uncertain (resident)", "extant & reintroduced (resident)", "extant & introduced (resident)", "probably extant & origin uncertain (resident)", "presence uncertain", "possibly extinct", "possibly extinct & introduced", "extinct & reintroduced"]
#custom: make your own list of range types to include in the area calcs
custom_range_types = []

#SELECT RANGE TYPE LIST TO USE:
#CHANGE THIS AS NEEDED (use default lists provided or custom list from range type groups section above)
#defaults to historical range group
range_types_of_interest = historical_range_types


print("Starting...\nPath: ", path)

#get list of species to process
lookingfor_species = []
with open(specieslist_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            lookingfor_species.append(row[0])

#check if we have shapefile folders named for each species in list
haveinfofor_species = [f for f in listdir(shapefile_path) if isdir(join(shapefile_path, f))]

#set up species_info output file
species_count = 0
info_file = open(path + "species_info.tsv", "w")
info_file.write("Species\tTotal Area (sq km)\t+/-\tMin Lat\t+/-\tMax Lat\t# Ranges Included\t# Ranges Excluded (Introduced)\n")

#set up species_notfound output file
donthaveinfofor_species = []
species_notfound_count = 0
donthaveinfofor_file = open(path + "species_notfound.txt", "w")

#try to calculate area for each species
for species in lookingfor_species:
    if species in haveinfofor_species:

        #open species' shapefile
        species_range_data = geopandas.read_file(shapefile_path + species + "/data_0.shp")

        #only keep ranges of types we're interested in
        for index, entry in species_range_data.iterrows():
            label = entry["LEGEND"].lower()
            if label not in range_types_of_interest:
                species_range_data.drop(index, inplace=True)
                print(label)

        #find bounds of range
        species_range_bounds = species_range_data.bounds
        south_lat = 90
        north_lat = -90
        for index, entry in species_range_bounds.iterrows():
            if float(entry[1]) < south_lat:
                south_lat = float(entry[1])
            if float(entry[3]) > north_lat:
                north_lat = float(entry[3])

        if abs(south_lat) > abs(north_lat):
            max_lat = south_lat
            min_lat = north_lat
        else:
            max_lat = north_lat
            min_lat = south_lat

        #separately record signs for later processing
        if min_lat < 0: min_sign = "-"
        else: min_sign = "+"
        if max_lat < 0: max_sign = "-"
        else: max_sign = "+"

        #find area of range
        #Eckert IV projection (unit: m) (can't get area from lat/lon coordinates)
        species_range_cartesian = species_range_data.to_crs("+proj=eck4 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")

        #combined range calculations attempt to do a union on all ranges (dissolve()) to account for overlap
        #but may encounter errors due to how geopandas library handles range border conflicts
        #if we encounter an error, we do not report information for that species
        try:
            species_combined_range = species_range_cartesian.dissolve()
            if species_combined_range.shape[0] != 1:
                print("dissolve resulted in multiple entries")
                area_total = -1
            else:
                for index, entry in species_combined_range.iterrows():
                    #convert from sq m to sq km
                    area_total = entry["geometry"].area / 10**6
        except:
            print("Error with unary union")
            area_total = -1

        if area_total == -1:
            #handle area calculation error cases
            species_notfound_count += 1
            donthaveinfofor_file.write(species + "\n")
        else:
            #record species info
            info = [species, str(area_total), min_sign, str(min_lat), max_sign, str(max_lat), str(og_count), str(introduced_count)]
            info_file.write('\t'.join(info) + "\n")

    else:
        #error finding shapefile folder
        species_notfound_count += 1
        donthaveinfofor_file.write(species + "\n")

info_file.close()
donthaveinfofor_file.close()

print("Done! Processed ", species_count, " species' shapefiles. ", species_notfound_count, "species' shapefiles could not be found.\nOutput:\n- Species info output to 'path\species_info.tsv'. \n- Any species that did not have a shapefile are listed in 'path\species_notfound.txt'.")