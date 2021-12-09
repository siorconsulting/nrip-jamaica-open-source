import whitebox
import os
import numpy

__all__ = ['wbt_setup']

def wbt_setup(working_dir=None, verbose=False):
    """Setup for whitebox toolset. 
    
    Inputs: 
        working_dir : str
        verbose [optional] : boolean 
    
    Returns:
        wbt : WhiteboxTools object
    """
    wbt = whitebox.WhiteboxTools()
    if working_dir is None:
        wbt.set_working_dir(os.getcwd())
    else:
        wbt.set_working_dir(working_dir)
    wbt.verbose = verbose
    return wbt

def vector_points_to_raster(i, output):
    wbt.vector_points_to_raster(
        i, 
        output, 
        field="FID", 
        assign="last", 
        nodata=True, 
        cell_size=None, 
        base=None, 
        callback=default_callback
    )
    
def vector_lines_to_raster(i, output):
    wbt.vector_lines_to_raster(
        i, 
        output, 
        field="FID", 
        nodata=True, 
        cell_size=None, 
        base=None, 
        callback=default_callback
    )

def vector_polygons_to_raster(i, output):
    wbt.vector_polygons_to_raster(
        i, 
        output, 
        field="FID", 
        nodata=True, 
        cell_size=None, 
        base=None, 
        callback=default_callback
    )
