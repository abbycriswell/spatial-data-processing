# made by Abby Criswell
# with the Havird Lab at
# the University of Texas at Austin
# updated 5-4-2023

import csv
from os import listdir
from os.path import isdir, join, splitext
import geopandas

#Run:
# run in command line: python SpatialDatafromShapefiles.py
# after changing path variables!

#CHANGE THESE:
#path: where output should be put
#shapefile_path: folder containing shapefile folders (labeled by species)
#specieslist_path: path to csv file with list of species to try

path="./Anura/"
shapefile_path = path + "anura_shapefiles/"
specieslist_path = path + "anura_specieslist.csv"

print("Starting...\nPath: ", path)

lookingfor_species = []
with open(specieslist_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            lookingfor_species.append(row[0])

'''
print("Looking for information on:\n")
for species in lookingfor_species:
    print(species, "\n")
'''

haveinfofor_species = [f for f in listdir(shapefile_path) if isdir(join(shapefile_path, f))]
'''
#DEPRICATED (moved from files to folders)
haveinfofor_species = []
for filename in haveinfofor_speciesdirs:
    haveinfofor_species.append(splitext(filename)[0])
'''

info = {}
donthaveinfofor_species = []
species_count = 0
species_notfound_count = 0
for species in lookingfor_species:
    if species in haveinfofor_species:
        species_count += 1
        info[species] = [0 for i in range(3)]
        species_range_data = geopandas.read_file(shapefile_path + species + "/data_0.shp")

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

        info[species][1] = min_lat
        info[species][2] = max_lat

        species_range_cartesian = species_range_data.to_crs(3857)

        area_total = 0
        for index, entry in species_range_cartesian.iterrows():
            area_total += entry["geometry"].area / 10**6

        area_avg = area_total / len(species_range_cartesian)
        info[species][0] = area_avg

    else:
        species_notfound_count += 1
        donthaveinfofor_species.append(species)


info_file = open(path + "species_info.tsv", "w")
info_file.write("Species\tArea (sq km)\t+/-\tMin Lat\t+/-\tMax Lat\n")
for species in info:
    if info[species][1] < 0: min_sign = "-"
    else: min_sign = "+"
    if info[species][2] < 0: max_sign = "-"
    else: max_sign = "+"
    info_file.write(species + "\t" + str(info[species][0]) + "\t" + min_sign + "\t" + str(info[species][1]) + "\t" + max_sign + "\t" + str(info[species][2])+"\n")
info_file.close()

donthaveinfofor_file = open(path + "species_notfound.txt", "w")
for species in donthaveinfofor_species:
    donthaveinfofor_file.write(species + "\n")
donthaveinfofor_file.close()

print("Done! Processed ", species_count, " species' shapefiles. ", species_notfound_count, "species' shapefiles could not be found.\nOutput:\n- Species info output to 'path\species_info.tsv'. \n- Any species that did not have a shapefile are listed in 'path\species_notfound.txt'.")
