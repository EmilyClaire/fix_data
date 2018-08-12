"""Standardizes csv data

This module has a function for standardizing the csv astronomy data.

Attributes:

Todo:
    * Find out if should throw exceptions or have the code just blow up
    * Find out what license type is used for the project
    * Find out how to add an author to this header
"""


import pandas as pd 
import numpy as np
import re

def fix_data(csv):
    """Standardizes the "Region" data into core, center, outer, outsk,
    and icl. And coreA, coreB, ..., coreZ when there are multiple cores.

    For multiple cores, it labels the cores in ascending order 
    from coreA -> coreZ. It also removes "reg" from CNames

    Args:
        csv: The csv file to be read into a DataFrame and then standardized

    Returns:
        A pandas DataFrame with standardized "Region" values and CNames
    """

    #Reading the data from the csv into the DataFrame
    std_data = pd.read_csv(csv)
    
    #This function sets the region names to the standard versions    
    std_data = standardize_region_names(std_data)

    #this function handles any galaxies with multiple cores.
    #it lables the cores coreA-coreZ based on the "R" distance.
    #coreA is has a smaller "R" value than coreB and so on etc.
    std_data = fix_mult_core(std_data)
    
    #This function removes reg from the end of galaxy names
    std_data = standardize_CNames(std_data)

    # resets index of table so that column CName is now index
    std_data.set_index('CName', inplace=True) 
    
    return std_data
    
def fix_mult_core(data):
    """Fixes galaxies with multiple cores by labeling the cores 
    in ascending order from coreA -> coreZ

    Args:
        data: The DataFrame containing the galaxy data

    Returns:
        A pandas DataFrame where galaxies with multiple core "Regions" are 
        now coreA->coreZ
    """
        
    new_df = pd.DataFrame(data)
    galaxy_names = new_df.CName.unique()
    
    for name in galaxy_names:

        #Creates a dataframe with all the rows for a particular galaxy that 
        #have a region value of "core"
        temp_df = new_df[(new_df["CName"] == name) \
        & (new_df["Region"] == "core")]
        
        #if there is more than one row that has a region value of "core"
        #than sort by radius (R) and name them coreA, coreB,..., coreZ 
        #in ascending order by radius (R)
        if(temp_df.shape[0] > 1):
            temp_df.sort_values(by = "R")
            
            #reset the index to 0,1,2,... instead of CName for easier access
            temp_df.reset_index(inplace=True)
            
            #rename the cores from core to coreA, coreB,...,coreZ
            for index in range (0, temp_df.shape[0]):            
                new_df.loc[temp_df.loc[index,"index"], "Region"] = \
                "core" + chr(ord('A') + index)

            #Print message when you have more than 26 cores. 
            #Because I"m not sure what happens when you +1 to Z
            #TODO: maybe add an exception
            if(temp_df.shape[0] > 26):
                print ("\nThis program was only meant to handle data with less" 
                "than 26 cores. Your data has a galaxy that has more than 26 "
                "cores. Naming may be strange.")

    return new_df

def standardize_CNames(data):
    """standardizes the CNames by removing "reg" from the end of galaxy names

    Args:
        data: The DataFrame containing the galaxy data

    Returns:
        A pandas DataFrame where CNames no longer contain "reg"
    """
    #Getting the number of rows in the DataFrame
    max = data.shape[0]

    #for 0 through the last row in the dataframe
    for index in range(0, max):

        #slices the CName, getting the last 3 characters
        #and checks to see if the 3 characters are 'reg'
        if data.loc[index, "CName"][-3:] == "reg":

            #slices the CName getting everything but the last three characters
            #thus removing 'reg' from the CName and replaces the old CName
            #with the standardized CName
            data.loc[index, "CName"] = data.loc[index, "CName"][:-3]

    return data

def standardize_region_names(data):
    """Standardizes the region names into core, center, outer, outsk, icl

    Args:
        data: The DataFrame containing the galaxy data

    Returns:
        A pandas DataFrame where regions are now renamed into core, center,
        outer, outsk, icl
    """

    #Getting the number of rows in the DataFrame
    max = data.shape[0]
    
    #looping through each row to change the Region value to a standardized value
    for index in range (0, max):
        if "co" in data.loc[index, "Region"]:
            data.loc[index, "Region"] = "core"
        elif "ce" in data.loc[index, "Region"]:
            data.loc[index, "Region"] = "center"
        elif ("outsk" in data.loc[index, "Region"]) \
        or ("ot" in data.loc[index, "Region"]):
            data.loc[index, "Region"] = "outsk"
        elif "ic" in data.loc[index, "Region"]:
            data.loc[index, "Region"] = "icl"
        
        #Checking to see if the Region value contains a "c" followed by a number
        #if yes, than replace that value with 'core'
        elif re.match(r"c\d", data.loc[index, "Region"]):
            data.loc[index, "Region"] = "core"

        #Make sure outer elif is after outsk or else outskirts will be replaced 
        #by outer and there will be no outsk values
        elif "ou" in data.loc[index, "Region"]:
            data.loc[index, "Region"] = "outer"

        #catchall that should never ever happen
        else:
            data.loc[index, "Region"] = "other"

    return data
