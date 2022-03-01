import os
from utils import *

wbt = wbt_setup()
working_dir = wbt.work_dir


__all__ = ['inundation_extents',
           'inundation_extents_between']

def inundation_extents(input_raster, output_polygons, threshold):
    """
    Calculates inundation extents based on specific threshold
    
    Inputs:
        input_raster: str <-- path to raster(.tif) file
        output_polygons: str <-- name for polygons(.shp) file outputted from raster to vector polygons calculation
        threshold: int or float <-- max threshold value
    
    Outputs:
        output: str <-- Outputted vector polygon(.shp) file name
    
    Returns:
    None
    """

    output_raster = 'temp_raster_inundation_extents.tif' # string of temporary raster file
    
    wbt.work_dir = working_dir

    wbt.conditional_evaluation(i=input_raster, # string raster input from argugment of function
                               output=output_raster, # assigning temporary raster file string as output raster
                               statement=f"value <= {threshold}", # conditional Rust statement
                               true = 1, # assigned value of gird cell if condition is met
                               false = 'null') # assigned value of grid cell if condition is not met
    
    wbt.work_dir = working_dir

    # wbt.raster_to_vector_polygons(i=output_raster, output=output_polygons) # converts temporary raster file to vector of polygon type

    # wbt.work_dir = working_dir
    
    # os.remove(os.path.join(wbt.work_dir, output_raster)) # removes temporary raster file 



def inundation_extents_between(input_raster, output_polygons, low_threshold, high_threshold):
    """
    Calculates inundation extents between two threshold, based on low and high thresholds values.
    
    Inputs:
        input_raster: str <-- path to raster(.tif) file
        output_polygons: str <-- name for polygons(.shp) file outputted from raster to vector polygons calculation
        threshold: int or float <-- max threshold value
    
    Outputs:
        output: str <-- Outputted vector polygon(.shp) file name
    
    Returns:
    None
    """

    output_raster = 'temp_raster_inundation_extents.tif' # string of temporary raster file
    
    wbt.work_dir = working_dir

    wbt.conditional_evaluation(i=input_raster, # string raster input from argugment of function
                               output=output_raster, # assigning temporary raster file string as output raster
                               statement=f"(value >= {low_threshold}) && (value < {high_threshold})", # conditional Rust statement
                               true = 1, # assigned value of gird cell if condition is met
                               false = 'null') # assigned value of grid cell if condition is not met
    
    wbt.work_dir = working_dir

    # wbt.raster_to_vector_polygons(i=output_raster, output=output_polygons) # converts temporary raster file to vector of polygon type

    # wbt.work_dir = working_dir
    
    # os.remove(os.path.join(wbt.work_dir, output_raster)) # removes temporary raster file 

