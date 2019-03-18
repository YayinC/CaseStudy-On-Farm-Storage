#!/usr/bin/env python
# coding: utf-8

## Case Study: On-Farm Storage Capacity Analysis

# Import the modules required for the analysis
import pandas as pd
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import math


# Check if a string contains municipal info
def isMuni(string):
    '''
    :param string: the owner name
    :return: if the owner is a municipal institution
    '''
    if len(string)==0:
        return 0
    else:
        stringlst = string.split(" ")
        if ("INC" in stringlst) or ("CO" in stringlst) or ("CORP" in stringlst) or ("LLC" in stringlst) or ("LTD" in stringlst) or ("COMPANY" in stringlst):
            return 0
        elif "CITY" in stringlst:
            return 1
        elif "COUNTY" in stringlst:
            return 1
        elif "STATE" in stringlst:
            return 1
        elif "DEPT" in stringlst:
            return 1
        elif "BUREAU" in stringlst:
            return 1
        else:
            return 0

# Check if the owner of the parcel is municipal organization
def checkMuni(df):
    '''
    :param df: the parcel geodataframe
    :return: the geodataframe labeld with municipal info
    '''
    df["OWNER"] = df["OWNER"].fillna("")
    df["OWNER_copy"] = df["OWNER"]
    df["muni"] = df["OWNER"].apply(lambda x: isMuni(x))

#Remove the buildings in the municipal parcels
def removeMuni(bldg, parcels):
    '''
    :param bldg: original grain bin buildings geodataframe
    :param parcels: the parcel geodataframe
    :return: the geodataframe of the grain bins located on non-municipal parcels
    '''
    #Add an unique ID to the buildings
    bldg["UID"] = bldg.index
    #Spatial join the buildings and the parcels
    bldg2 = gpd.sjoin(bldg, parcels, how="inner", op='intersects')
    bldg2 = bldg2[["UID","muni"]]
    #Check if any part of the building located on the municipal parcel
    bldgunique = bldg2.groupby("UID").agg({"muni":"max"})
    bldgunique.reset_index(inplace=True)
    #Join the municipal info to the original geodataframe
    bldg = bldg.merge(bldgunique,on="UID")
    bldg["muni"] = bldg["muni"].fillna(0)
    bldg = bldg[bldg["muni"]==0]
    bldg.drop(["muni"],axis=1,inplace=True)
    return bldg

#Select out the agricultural parcels based on the farm land area
def selectAgri(df):
    '''
    :param df: the parcels geodataframe
    :return: the geodataframe of only agricultural parcels
    '''
    df1 = df[df["FARM_ACRES"]>0]
    return df1


# Define the functions to calculate the radius, area, volume, and # of bushels
def calRadius(df):
    '''
    :param df: the grain bins geodataframe
    :return: the geodataframe with the radius in feet
    '''
    # Calculate radius in feet
    df["radius"] = (df["DIAMETER"] * 3.28084) / 2


def calArea(df):
    '''
    :param df: the grain bins geodataframe
    :return: the geodataframe with the bottom area in square feet
    '''
    # Calculate the bottom area of the grain bins
    df["area"] = math.pi * df["radius"] * df["radius"]


def calVolume(df, height):
    '''
    :param df: the grain bins geodataframe
    :param height: the given height in feet
    :return: the geodataframe with the volume in cubic feet
    '''
    # Calculate the volume of the grain bins
    df["volume_" + str(height)] = df["area"] * height


def calBushels(df, height):
    '''
    :param df: the grain bins geodataframe
    :param height: the given height in feet
    :return: the geodataframe with estimated # of bushels
    '''
    # Calculate the maximum # of bushels in the grain bins
    df["bushels_" + str(height)] = df["volume_" + str(height)] * 0.85

# Separate the dissolved parcels if they are not adjacent
# Reference code: https://github.com/geopandas/geopandas/issues/369
def multi2single(gpdf):
    '''
    :param gpdf: any given geodataframe
    :return: the exploded geodataframe
    '''
    gpdf_singlepoly = gpdf[gpdf.geometry.type == 'Polygon']
    gpdf_multipoly = gpdf[gpdf.geometry.type == 'MultiPolygon']

    for i, row in gpdf_multipoly.iterrows():
        Series_geometries = pd.Series(row.geometry)
        df = pd.concat([gpd.GeoDataFrame(row, crs=gpdf_multipoly.crs).T]*len(Series_geometries), ignore_index=True)
        df['geometry']  = Series_geometries
        gpdf_singlepoly = pd.concat([gpdf_singlepoly, df])

    gpdf_singlepoly.reset_index(inplace=True, drop=True)
    return gpdf_singlepoly

#Plot the map
def plotMap(geodf, figwidth, figheight, column):
    '''
    :param geodf: the geodataframe to plot
    :param figwidth: the figure width
    :param figheight: the figure height
    :param column: which column to plot
    :return: plot the figure and save it
    '''
    vmin, vmax = geodf[column].min(),geodf[column].max()
    fig, ax = plt.subplots(1, figsize=(figwidth, figheight))
    geodf.plot(column=column, cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')
    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm)
    plt.savefig('Max_Capacity_Map.png')


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>Starts Here<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def main():
    print("Data preparation and wrangling...")
    # Set the path
    path = "/Users/yayincai/Documents/Job Hunting/Employer List/Indigo"
    os.chdir(path)

    # Read the data
    parcels = gpd.read_file("parcels_ilmenard.shp")
    bldg = gpd.read_file("silos_ilmenard.shp")

    checkMuni(parcels)
    grainbins = removeMuni(bldg, parcels)
    agriparcels = selectAgri(parcels)

    #Calculate the radius and the area of the grain bins
    calRadius(grainbins)
    calArea(grainbins)

    print("Spatial Analysis...")
    #Dissolve the parcels by owner name and separate the multipolygon
    agriparcels_byowners = agriparcels.dissolve(by='OWNER')

    agriparcels_byowners_explode = multi2single(agriparcels_byowners)

    #Reset the index to make each row have a unique id
    agriparcels_byowners_explode.reset_index(inplace=True)

    #Spatial join the parcels and grain bins to find the parcels which intersect with one or more bins
    parcels_bins = gpd.sjoin(agriparcels_byowners_explode, grainbins, how="inner", op='intersects')

    #Calculate the total bottom areas of the grain bins in a parcel
    parcels_bins_sum = parcels_bins.groupby("index").agg({"area":"sum"})

    #Assume that the height of the grain bins varies from 15ft to 54ft
    #Reference: https://www.brockmfg.com/uploads/pdf/BR_2286_201702_Brock_Non_Stiffened_Storage_Capacities_Fact_Sheet_EM.pdf
    parcels_bins_sum.reset_index(inplace=True)
    calVolume(parcels_bins_sum,15)
    calVolume(parcels_bins_sum,54)
    calBushels(parcels_bins_sum,15)
    calBushels(parcels_bins_sum,54)

    #Add the capacity info
    parcels_bins = parcels_bins.merge(parcels_bins_sum,on="index")

    print("Export the map...")
    plotMap(parcels_bins, 15, 9, "bushels_54")

    #Save to geojson files, which will be used in the data visualization part
    parcels_bins.to_file("parcels_bins.geojson", driver="GeoJSON")
    agriparcels_byowners_explode.to_file("parcels_agri.geojson", driver="GeoJSON")
    grainbins.to_file("grainbins.geojson", driver="GeoJSON")

if __name__ == '__main__':
    main()
