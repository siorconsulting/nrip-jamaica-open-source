import os
from utils import *

wbt = wbt_setup()

__all__ = ['inundation_extents']

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
    
    wbt.conditional_evaluation(i=input_raster, # string raster input from argugment of function
                               output=output_raster, # assigning temporary raster file string as output raster
                               statement=f"value <= {threshold}", # conditional Rust statement
                               true = 1, # assigned value of gird cell if condition is met
                               false = 'null') # assigned value of grid cell if condition is not met

    wbt.raster_to_vector_polygons(i=output_raster, output=output_polygons) # converts temporary raster file to vector of polygon type

    os.remove(os.path.join(wbt.work_dir, output_raster)) # removes temporary raster file 
