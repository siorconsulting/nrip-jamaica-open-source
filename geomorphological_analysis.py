import os
from utils import *

wbt = wbt_setup()

__all__ = ['steep_areas',
           'geomorphological_fluvial_flood_hazard_areas',
           ]

def geomorphological_fluvial_flood_hazard_areas(dem, output_prefix, buffer_distance, facc_threshold = 1000, remove_temp_outputs = True):
    """
    Calculates Flood hazard areas from raster and outputs these areas as polygons
    
    Inputs:
        dem: str <-- path to raster(.tif) file
        output_prefix: str <-- site specific name appended to each output file name
        facc_threshold: int or float <-- flow accumulation threshold defaulted at 1000
        buffer_distance: int or float <-- distance used to buffer flow accumulation raster
    
    Outputs:
        out_facc_setnull_buffer_polygon: str <-- output polygon(.shp) that represents flood hazard areas
    
    Returns:
    None
    """
    
    out_fill = f"{output_prefix}_fill.tif"
    out_fdir = f"{output_prefix}_fdir.tif"
    out_facc = f"{output_prefix}_facc.tif"
    out_facc_setnull = f"{output_prefix}_facc_setnull_{facc_threshold}.tif"
    out_facc_setnull_buffer = f"{output_prefix}_facc_setnull_buffer_{buffer_distance}.tif"
    out_facc_setnull_buffer_polygon = f"{output_prefix}_flood_hazard_areas.shp"
    
    wbt.fill_depressions_planchon_and_darboux(dem, out_fill) # fills depressions of input raster
    wbt.d8_pointer(out_fill, out_fdir, esri_pntr=True) # calcualtes flow direction from filled raster
    wbt.d8_flow_accumulation(out_fdir, out_facc, pntr=True, esri_pntr=True) # calculates flow accumulation from flow direction raster
    wbt.conditional_evaluation(i=out_facc, output=out_facc_setnull, statement=f"value >= {facc_threshold}", true=1, false='null') # provides evaluation on raster based on certain condtional statements
    wbt.buffer_raster(out_facc_setnull, out_facc_setnull_buffer, size=buffer_distance) # buffers raster by specific distance
    wbt.raster_to_vector_polygons(out_facc_setnull_buffer, out_facc_setnull_buffer_polygon) # converts temporary buffered raster to polygons
    
    if remove_temp_outputs: 
        os.remove(os.path.join(wbt.work_dir,out_fill))
        os.remove(os.path.join(wbt.work_dir,out_fdir))
        os.remove(os.path.join(wbt.work_dir,out_facc))
        os.remove(os.path.join(wbt.work_dir,out_facc_setnull))
        os.remove(os.path.join(wbt.work_dir,out_facc_setnull_buffer))
        

def steep_areas(dem, threshold, output_prefix, delete_temp_outputs=True):
    """Create mask of areas with slope equal or higher than a threshold, and export as raster and vector files.
    
    Inputs:
        dem : str <-- path to raster(.tif) file
        threshold : int or float <-- threshold of slope that defines mask
        output_prefix: str <-- site specific name appended to each output file name
        delete_temp_outputs [optional] : boolean <-- if True will delete temporary output files
        
    Outputs:
         polygon_output: str <-- Outputted vector polygon(.shp) file name

    Returns:
        None 
        
    """

    slope_output = f"{output_prefix}_slope.tif"            # defines
    raster_output = f"{output_prefix}_slope_setnull.tif"   # output file 
    polygon_output = f"{output_prefix}_slope_setnull.shp"  # names
    
    wbt.slope(dem, slope_output) # calculates slope gradient of input raster
    wbt.conditional_evaluation(i=slope_output,
                               output=raster_output,
                               statement=f'value > {threshold}', # creates new raster based on slope output under certain conditions
                               true=1,
                               false='null',
                               )


    # temp_polygon_output = 'temp_polygon_output.shp'
    wbt.raster_to_vector_polygons(i=raster_output, output=polygon_output) # converts raster to vector polygons

    # wbt.dissolve(temp_polygon_output, polygon_output)         
    
    if delete_temp_outputs:
        # os.remove(os.path.join(working_dir,temp_polygon_output))
        os.remove(os.path.join(wbt.work_dir,slope_output)) # removes temporary slope output raster file
