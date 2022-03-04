import os
# from re import L
# from tabnanny import verbose
import whitebox

class nrip_toolbox:
    """Class to be defined"""

    def __init__(self, working_directory=None, verbose=False):
        
        if working_directory is None:
            self.working_dir = os.getcwd()
        else:
            self.working_dir = working_directory

        self.wbt = whitebox.WhiteboxTools()

        self.wbt.set_working_dir(self.working_dir)

        self.wbt.verbose = verbose

    def set_verbose_mode(self, verbose_flag=False):
        self.wbt.verbose = verbose_flag

    def reset_directories(self):
        os.chdir(self.working_dir)
        self.wbt.work_dir = self.working_dir

    def inundation_extents(self, input_raster, threshold, output_name=None, output_raster_flag=True, output_polygons_flag=False, value=1):
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

        self.reset_directories()

        self.wbt.conditional_evaluation(i=input_raster, # string raster input from argugment of function
                                output=output_raster_name, # assigning temporary raster file string as output raster
                                statement=f"value <= {threshold}", # conditional Rust statement
                                true = value, # assigned value of gird cell if condition is met
                                false = 'null') # assigned value of grid cell if condition is not met
        
        self.reset_directories()

        if output_polygons_flag:
            self.wbt.raster_to_vector_polygons(i=output_raster_name, output=output_polygons_name) # converts temporary raster file to vector of polygon type

        self.reset_directories()
        
        if not(output_raster_flag):
            os.remove(os.path.join(self.wbt.work_dir, output_raster_name)) # removes temporary raster file 

    def inundation_extents_between(self, input_raster, low_threshold, high_threshold, output_name=None, output_raster_flag=True, output_polygons_flag=False, value=1):
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
        
        self.reset_directories()

        self.wbt.conditional_evaluation(i=input_raster, # string raster input from argugment of function
                                output=output_raster_name, # assigning temporary raster file string as output raster
                                statement=f"(value > {low_threshold}) && (value <= {high_threshold})", # conditional Rust statement
                                true = value, # assigned value of gird cell if condition is met
                                false = 'null') # assigned value of grid cell if condition is not met
        
        self.reset_directories()

        if output_polygons_flag:
            self.wbt.raster_to_vector_polygons(i=output_raster_name, output=output_polygons_name) # converts temporary raster file to vector of polygon type

        self.reset_directories()
        
        if not(output_raster_flag):
            os.remove(os.path.join(self.wbt.work_dir, output_raster_name)) # removes temporary raster file 

    def hydrological_routing(self, dem, output_prefix, facc_threshold=1000, remove_temp_outputs=False):

        """
        Performs the Hydrological Analysis on the input dem and calculates flow lines, basins and sinks derived from input dem
        
        Inputs:
            dem : str <-- path to raster(.tif) file
            output_prefix : str <-- site specific name appended to each output file name
            facc_threshold : int or float <-- flow accummulation threshold value
            remove_temp_outputs : boolean <-- defaults to False, removes temporary outputs

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

        self.reset_directories()

        self.wbt.fill_depressions_planchon_and_darboux(dem, out_fill) # fills depressions of input raster
        self.reset_directories()

        self.wbt.d8_pointer(out_fill, out_fdir, esri_pntr=True) # calcualtes flow direction from filled raster
        self.reset_directories()

        self.wbt.d8_flow_accumulation(out_fdir, out_facc, pntr=True, esri_pntr=True) # calculates flow accumulation from flow direction raster
        self.reset_directories()

        self.wbt.conditional_evaluation(i=out_facc, output=out_facc_setnull, statement=f"value >= {facc_threshold}", true=1, false='null') # provides evaluation on raster based on certain condtional statements
        self.reset_directories()

        self.wbt.raster_to_vector_lines(i=out_facc_setnull, output=out_facc_setnull_lines) # converts temporary buffered raster to lines
        self.reset_directories()

        self.wbt.basins(out_fdir, out_basins, esri_pntr=True) # calculates basins by delineating all of the drainage basins and drainging to the edge of the data
        self.reset_directories()

        # self.wbt.raster_to_vector_polygons(i=out_basins, output=out_basins_polygon) # converts temporary buffered raster to polygons

        self.wbt.raster_calculator(output=out_calculator, statement=f"'{out_fill}'-'{dem}'") # performs comples mathematical operations on raster based on mathematical expression, or statement
        self.reset_directories()

        self.wbt.conditional_evaluation(i=out_calculator, output=out_conditional, statement="value>0", true=1, false="null") # provides evaluation on raster based on certain condtional statements
        self.reset_directories()

        # self.wbt.raster_to_vector_polygons(i=out_conditional, output=out_conditional_polygon) # converts temporary buffered raster to polygons

        if remove_temp_outputs:
            os.remove(os.path.join(self.wbt.work_dir,out_fill))
            os.remove(os.path.join(self.wbt.work_dir,out_fdir))
            os.remove(os.path.join(self.wbt.work_dir,out_facc))
            os.remove(os.path.join(self.wbt.work_dir,out_facc_setnull))
            os.remove(os.path.join(self.wbt.work_dir,out_basins))
            os.remove(os.path.join(self.wbt.work_dir,out_conditional)) 

        self.reset_directories() 

    def geomorphological_fluvial_flood_hazard_areas(self, dem, output_prefix, buffer_distance, facc_threshold = 1000, remove_temp_outputs = True):
    
        """Calculates Flood hazard areas from raster and outputs these areas as polygons
        
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
        
        self.wbt.fill_depressions_planchon_and_darboux(dem, out_fill) # fills depressions of input raster
        self.reset_directories()

        self.wbt.d8_pointer(out_fill, out_fdir, esri_pntr=True) # calcualtes flow direction from filled raster
        self.reset_directories()

        self.wbt.d8_flow_accumulation(out_fdir, out_facc, pntr=True, esri_pntr=True) # calculates flow accumulation from flow direction raster
        self.reset_directories()

        self.wbt.conditional_evaluation(i=out_facc, output=out_facc_setnull, statement=f"value >= {facc_threshold}", true=1, false='null') # provides evaluation on raster based on certain condtional statements
        self.reset_directories()

        self.wbt.buffer_raster(out_facc_setnull, out_facc_setnull_buffer, size=buffer_distance) # buffers raster by specific distance
        self.reset_directories()

        self.wbt.raster_to_vector_polygons(out_facc_setnull_buffer, out_facc_setnull_buffer_polygon) # converts temporary buffered raster to polygons
        self.reset_directories()

        if remove_temp_outputs: 
            os.remove(os.path.join(self.wbt.work_dir,out_fill))
            os.remove(os.path.join(self.wbt.work_dir,out_fdir))
            os.remove(os.path.join(self.wbt.work_dir,out_facc))
            os.remove(os.path.join(self.wbt.work_dir,out_facc_setnull))
            os.remove(os.path.join(self.wbt.work_dir,out_facc_setnull_buffer))
  
        self.reset_directories()

    def steep_areas(self, dem, threshold, output_prefix, delete_temp_outputs=True):
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

        self.reset_directories()
        
        self.wbt.slope(dem, slope_output) # calculates slope gradient of input raster
        self.reset_directories()

        self.wbt.conditional_evaluation(i=slope_output,
                                output=raster_output,
                                statement=f'value > {threshold}', # creates new raster based on slope output under certain conditions
                                true=1,
                                false='null',
                                )
        self.reset_directories()

        # temp_polygon_output = 'temp_polygon_output.shp'
        self.wbt.raster_to_vector_polygons(i=raster_output, output=polygon_output) # converts raster to vector polygons
        self.reset_directories()
        
        # wbt.dissolve(temp_polygon_output, polygon_output)         
        
        if delete_temp_outputs:
            # os.remove(os.path.join(working_dir,temp_polygon_output))
            os.remove(os.path.join(self.wbt.work_dir, slope_output)) # removes temporary slope output raster file