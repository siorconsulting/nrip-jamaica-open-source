import os 
from utils import * 

wbt = wbt_setup()

__all__ = ['hydrological_routing']

def clipping_by_elevation(dem, output_clipped_dem):
    '''
    Clips the dem boundary based on specific threshold

    Inputs:
        dem : str <-- path to raster(.tif) file

    Outputs:
        output clipped dem : str <-- output raster(.tif) clipped to the define extent

    Returns:
        None
    
    '''

    # provides evaluation on raster based on certain condtional statements
    wbt.conditional_evaluation(i=dem,                               
                                output=output_clipped_dem, 
                                statement="value > 0",               # threshold for the clipping boundary
                                true=dem, 
                                false="null")


def hydrological_routing(dem, output_prefix, facc_threshold=1000, remove_temp_outputs=True):


    """
    Performs the Hydrological Analysis on the input dem and calculates flow lines, basins and sinks derived from input dem
    
    Inputs:
        dem : str <-- path to raster(.tif) file
        output_prefix : str <-- site specific name appended to each output file name
        facc_threshold : int or float <-- flow accummulation threshold value
        remove_temp_ouputs : boolean <-- deafulted at true, removes temporary outputs

    Outputs:
        fill raster [temp] : temporary output generated for analysis
        flow direction raster [temp] : temporary output generated for analysis
        flow accumulation raster [temp] : temporary output generated for analysis
        flow accumulation setnull raster [temp] : temporary output generated for analysis
        flow accumulation setnull lines: str <-- output line(.shp) that represents flow accummulation lines
        basins raster [temp]: temporary output generated for analysis
        basins polygon : str <-- output polygon(.shp) that represents drainage basins
        fill depth raster : str <-- output raster(.tif) that represents sinks
        fill extent raster [temp] : temporary output generated for analysis
        fill extent polygons :  str <-- output polygon(.shp) that represents sinks
    
    Returns:
        None 
    
    """

    out_fill = f"{output_prefix}_fill.tif"
    out_fdir = f"{output_prefix}_fdir.tif"
    out_facc = f"{output_prefix}_facc.tif"
    out_facc_setnull = f"{output_prefix}_facc_setnull_{facc_threshold}.tif"
    out_facc_setnull_lines = f"{output_prefix}_facc_setnull_polygon_{facc_threshold}.shp"
    out_basins = f"{output_prefix}_basins.tif"
    out_basins_polygon = f"{output_prefix}_basins_polygon.shp"
    out_calculator = f"{output_prefix}_fill_depth.tif"
    out_conditional = f"{output_prefix}_fill_extent.tif"
    out_conditional_polygon = f"{output_prefix}_fill_extent_polygon.shp"

    wbt.fill_depressions_planchon_and_darboux(dem, out_fill) # fills depressions of input raster
    wbt.d8_pointer(out_fill, out_fdir, esri_pntr=True) # calcualtes flow direction from filled raster
    wbt.d8_flow_accumulation(out_fdir, out_facc, pntr=True, esri_pntr=True) # calculates flow accumulation from flow direction raster
    wbt.conditional_evaluation(i=out_facc, output=out_facc_setnull, statement=f"value >= {facc_threshold}", true=1, false='null') # provides evaluation on raster based on certain condtional statements
    wbt.raster_to_vector_lines(i=out_facc_setnull, output=out_facc_setnull_lines) # converts temporary buffered raster to lines
    wbt.basins(out_fdir, out_basins, esri_pntr=True) # calculates basins by delineating all of the drainage basins and drainging to the edge of the data
    wbt.raster_to_vector_polygons(i=out_basins, output=out_basins_polygon) # converts temporary buffered raster to polygons

    wbt.raster_calculator(output=out_calculator, statement=f"'{out_fill}'-'{dem}'") # performs comples mathematical operations on raster based on mathematical expression, or statement
    wbt.conditional_evaluation(i=out_calculator, output=out_conditional, statement="value>0", true=1, false="null") # provides evaluation on raster based on certain condtional statements
    wbt.raster_to_vector_polygons(i=out_conditional, output=out_conditional_polygon) # converts temporary buffered raster to polygons

    if remove_temp_outputs:
        os.remove(os.path.join(wbt.work_dir,out_fill))
        os.remove(os.path.join(wbt.work_dir,out_fdir))
        os.remove(os.path.join(wbt.work_dir,out_facc))
        os.remove(os.path.join(wbt.work_dir,out_facc_setnull))
        os.remove(os.path.join(wbt.work_dir,out_basins))
        os.remove(os.path.join(wbt.work_dir,out_conditional))
