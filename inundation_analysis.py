import os
from utils import *

wbt = wbt_setup(verbose=True)
working_dir = wbt.work_dir

__all__ = ['inundation_extents',
           'inundation_extents_between',
           'print_work_dir',
           'set_work_dir',
           'set_verbose_mode']

def set_verbose_mode(verbose_mode=False):
    wbt.verbose = verbose_mode

def print_work_dir():
    print(wbt.work_dir)

def set_work_dir(working_dir):
    wbt.work_dir = working_dir

def inundation_extents(input_raster, threshold, output_name=None, output_raster_flag=True, output_polygons_flag=False, value=1):
    """
    Calculates inundation extents based on specific threshold
    
    Inputs:
        input_raster: str <-- path to raster(.tif) file
        threshold : int or float <-- threshold value
        output_name : str <-- name of output files without extension (e.g., .shp or .tif)
        output_raster_flag : boolean <-- if True, it exports the output in raster format
        output_polygons_flag : boolean <-- if True, it exports the output in polygon format
        value : int <-- hazard score value
    
    Outputs:
        output: str <-- Output raster (.tif) or vector polygon (.shp) file name
    
    Returns:
    None
    """

    if output_name is None:
        output_name = f'inundation_extents_{threshold}'

    output_raster_name = f'{output_name}.tif' # string of temporary raster file
    output_polygons_name = f'{output_name}.shp' 
    
    wbt.work_dir = working_dir

    wbt.conditional_evaluation(i=input_raster, # string raster input from argugment of function
                               output=output_raster_name, # assigning temporary raster file string as output raster
                               statement=f"value <= {threshold}", # conditional Rust statement
                               true = value, # assigned value of gird cell if condition is met
                               false = 'null') # assigned value of grid cell if condition is not met
    
    wbt.work_dir = working_dir

    if output_polygons_flag:
        wbt.raster_to_vector_polygons(i=output_raster_name, output=output_polygons_name) # converts temporary raster file to vector of polygon type

    wbt.work_dir = working_dir
    
    if not(output_raster_flag):
        os.remove(os.path.join(wbt.work_dir, output_raster_name)) # removes temporary raster file 

def inundation_extents_between(input_raster, low_threshold, high_threshold, output_name=None, output_raster_flag=True, output_polygons_flag=False, value=1):
    """
    Calculates inundation extents between two threshold, based on low and high thresholds values.
    
    Inputs:
        input_raster: str <-- path to raster(.tif) file
        low_threshold : int or float <-- low threshold value
        high_threshold : int or float <-- high threshold value
        output_name : str <-- name of output files without extension (e.g., .shp or .tif)
        output_raster_flag : boolean <-- if True, it exports the output in raster format
        output_polygons_flag : boolean <-- if True, it exports the output in polygon format
        value : int <-- hazard score value
    
    Outputs:
        output: str <-- Output raster (.tif) or vector polygon (.shp) file name
    
    Returns:
    None
    """

    if output_name is None:
        output_name = f'inundation_extents_between_{low_threshold}_and_{high_threshold}'

    output_raster_name = f'{output_name}.tif' # string of temporary raster file
    output_polygons_name = f'{output_name}.shp' 
    
    wbt.work_dir = working_dir

    wbt.conditional_evaluation(i=input_raster, # string raster input from argugment of function
                               output=output_raster_name, # assigning temporary raster file string as output raster
                               statement=f"(value > {low_threshold}) && (value <= {high_threshold})", # conditional Rust statement
                               true = value, # assigned value of gird cell if condition is met
                               false = 'null') # assigned value of grid cell if condition is not met
    
    wbt.work_dir = working_dir

    if output_polygons_flag:
        wbt.raster_to_vector_polygons(i=output_raster_name, output=output_polygons_name) # converts temporary raster file to vector of polygon type

    wbt.work_dir = working_dir
    
    if not(output_raster_flag):
        os.remove(os.path.join(wbt.work_dir, output_raster_name)) # removes temporary raster file 

