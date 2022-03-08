import os
# from re import L
# from tabnanny import verbose
import whitebox
import geopandas as gpd

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

    # Set Verbose Mode
    def set_verbose_mode(self, verbose_flag=False):
        self.wbt.verbose = verbose_flag

    # Reset Directories
    def reset_directories(self):
        os.chdir(self.working_dir)
        self.wbt.work_dir = self.working_dir

    ##### INUNDATION ANALYSIS #####

    # Inundation Extents (Inudation Analysis)
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

    # Inundation Extents Between (Inundation Analysis)
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

    ##### HYDROLOGICAL ANALYSIS #####

    # Hydrological Routing (Hydrological Analysis)
    def hydrological_routing(self, dem, output_prefix, facc_threshold=1000, remove_temp_outputs=False):

        """
        Performs complete hydrological routing workflow based on input Digital Elevation Model (DEM), including: 
        fill depressions, flow direction, flow accumulation, flow lines, basins, fill extents. 
        
        Inputs:
            dem : str <-- path to raster(.tif) file
            output_prefix : str <-- site specific name appended to each output file name
            facc_threshold : int or float <-- flow accummulation threshold value
            remove_temp_outputs : boolean <-- defaults to False, removes temporary outputs

        Outputs:
            fill raster [temp] : .tif <-- temporary output generated for analysis
            flow direction raster [temp] : .tif <-- temporary output generated for analysis
            flow accumulation raster [temp] : .tif <-- temporary output generated for analysis
            flow accumulation threshold raster [temp] : .tif <-- temporary output generated for analysis
            flow accumulation threshold lines: .shp <-- output line (.shp) that represents flow accummulation lines
            basins raster [temp] : .tif <-- temporary output generated for analysis
            basins polygon : .shp <-- output polygon(.shp) that represents drainage basins
            fill depth raster : .tif <-- output raster(.tif) that represents sinks
            fill extent raster [temp] : .tif <-- temporary output generated for analysis
            fill extent polygons :  .shp <-- output polygon(.shp) that represents sinks
        
        Returns:
            None 
        
        """

        # Define names for output files
        out_fill = f"{output_prefix}_fill.tif"
        out_fdir = f"{output_prefix}_fdir.tif"
        out_facc = f"{output_prefix}_facc.tif"
        out_facc_setnull = f"{output_prefix}_facc_threshold_{facc_threshold}.tif"
        out_facc_setnull_lines = f"{output_prefix}_facc_threshold_{facc_threshold}_polygons.shp"
        out_basins = f"{output_prefix}_basins.tif"
        out_basins_polygon = f"{output_prefix}_basins_polygons.shp"
        out_calculator = f"{output_prefix}_fill_depth.tif"
        out_conditional = f"{output_prefix}_fill_extent.tif"
        out_conditional_polygon = f"{output_prefix}_fill_extent_polygons.shp"

        self.reset_directories() 

        # Fill depressions
        self.wbt.fill_depressions_planchon_and_darboux(dem, out_fill) # fills depressions of input raster
        self.reset_directories()

        #  Calculate flow direction raster
        self.wbt.d8_pointer(out_fill, out_fdir, esri_pntr=True) # calcualtes flow direction from filled raster
        self.reset_directories()

        # Calculate flow accumulation raster
        self.wbt.d8_flow_accumulation(out_fdir, out_facc, pntr=True, esri_pntr=True) # calculates flow accumulation from flow direction raster
        self.reset_directories()

        # Apply flow accumulation threshold
        self.wbt.conditional_evaluation(i=out_facc, output=out_facc_setnull, statement=f"value >= {facc_threshold}", true=1, false='null') # provides evaluation on raster based on certain condtional statements
        self.reset_directories()

        # Convert thresholded flow accumulation raster to vector lines
        self.wbt.raster_to_vector_lines(i=out_facc_setnull, output=out_facc_setnull_lines) # converts temporary buffered raster to lines
        self.reset_directories()

        # Calculate basins / watersheds
        self.wbt.basins(out_fdir, out_basins, esri_pntr=True) # calculates basins by delineating all of the drainage basins and drainging to the edge of the data
        self.reset_directories()

        # Calculate difference between DEM and filled DEM
        self.wbt.raster_calculator(output=out_calculator, statement=f"'{out_fill}'-'{dem}'") # performs comples mathematical operations on raster based on mathematical expression, or statement
        self.reset_directories()

        # Identify areas where DEM has been filled
        self.wbt.conditional_evaluation(i=out_calculator, output=out_conditional, statement="value>0", true=1, false="null") # provides evaluation on raster based on certain condtional statements
        self.reset_directories()

        # Convert filled areas raster to vector polygons
        self.wbt.raster_to_vector_polygons(i=out_basins, output=out_basins_polygon) # converts temporary buffered raster to polygons
        self.reset_directories()
        
        # Cnvert basins raster to vector polugons
        self.wbt.raster_to_vector_polygons(i=out_conditional, output=out_conditional_polygon) # converts temporary buffered raster to polygons
        self.reset_directories()

        if remove_temp_outputs:
            # Remove temporary outputs
            os.remove(os.path.join(self.wbt.work_dir,out_fill))
            os.remove(os.path.join(self.wbt.work_dir,out_fdir))
            os.remove(os.path.join(self.wbt.work_dir,out_facc))
            os.remove(os.path.join(self.wbt.work_dir,out_facc_setnull))
            os.remove(os.path.join(self.wbt.work_dir,out_basins))
            os.remove(os.path.join(self.wbt.work_dir,out_conditional)) 

        self.reset_directories() 

    ##### GEOMORPHOLOGICAL ANALYSIS #####

    #  Geomorphological Fluvial Flood Hazard Areas (Geomorphological Analysis)
    def geomorphological_fluvial_flood_hazard_areas(self, dem, output_prefix, buffer_distance, facc_threshold = 1000, remove_temp_outputs = True, output_folder = None):
    
        """Calculates Flood hazard areas from raster and outputs these areas as polygons
        
        Inputs:
            dem : str <-- path to raster(.tif) file
            output_prefix : str <-- site specific name appended to each output file name
            buffer_distance : int or float <-- distance used to buffer flow accumulation raster
            facc_threshold : int or float <-- flow accumulation threshold (defaults to 1000)
            remove_temp_areas <-- if True, temporary outputs are removed
        
        Outputs:
            out_facc_setnull_buffer_polygon: str <-- output polygon(.shp) that represents flood hazard areas
        
        Returns:
            None
        """

        if output_folder is not None:
            output_prefix = os.path.join(output_folder,output_prefix)
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)
    
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
            os.remove(out_fill)
            os.remove(out_fdir)
            os.remove(out_facc)
            os.remove(out_facc_setnull)
            os.remove(out_facc_setnull_buffer)
  
        self.reset_directories()

    # Steep Areas (Geomorphological Analysis)
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
    

    ##### GEOMETRIC ANALYSIS #####

    # Intersect (Geometric Analysis)
    def intersect(self, input_vector_file, overlay, output_vector_file):
        """
        Function to return all feature parts that occur in both input layers

        Inputs:
            input_vector_file: str <-- path to vector(.shp) file
            overlay: str <-- path to overlay vector(.shp) file
            output_vector_file: str <-- name of output vector(.shp) file

        Outputs:
            output_vector_file: shapefile  <-- output vector shapefile
        """

        self.reset_directories()

        self.wbt.intersect(input_vector_file, overlay, output_vector_file)
        
        self.reset_directories()

    # Zonal Statistics (Geometric Analysis)
    def zonal_statistics(self, input_raster, input_zones, output_raster, field='FID', stat='mean', input_zones_is_raster=True):
        """Calculates zonal statistics based on an input raster, using raster or polygon zones. 
        
        Inputs:
            input_raster : str <-- path to raster(.tif) file
            input_zones : str <-- input path to raster(.tif) or polygon(.shp)
            output_raster : str <-- output raster(.tif) file name
            field [optional] : str <-- deafult value is 'FID'
            stat [optional] : str <-- default value is 'mean'
            input_zones_is_raster [optional] : boolean <-- default value is 'True'

        Exports:
            output_raster : raster <-- output raster(.tif) file

        Returns:
            None

        """

        if input_zones_is_raster:
            input_zones_raster = input_zones # if statement assigning input_zones to raster variable if already a raster
        else:
            input_zones_raster = 'temp_input_raster.tif' # assigning file name
            temp_input_zones = 'temp_input_zones.shp'
            gdf = gpd.read_file(input_zones)
            gdf['FID'] = gdf.index
            gdf.to_file(temp_input_zones)
            self.wbt.vector_polygons_to_raster(temp_input_zones, input_zones_raster, field=field, nodata=False) # transforming polygon to raster if input_zones is a polygon
        
        self.reset_directories()

        self.wbt.zonal_statistics(i=input_raster, features=input_zones_raster, output=output_raster, stat=stat)
        
        self.reset_directories()

        if not input_zones_is_raster:
            os.remove(os.path.join(self.wbt.work_dir,input_zones_raster)) # removing temporary raster file if one had to be created
        
        self.reset_directories()
    
    # Distance From Points (Geometric Analysis)   
    def distance_from_points(self,input_points, output_raster):
        """
        Creates new raster showing distances between input points

        Inputs:
            input_points: str <-- path to input point (.shp) file
            output_raster: str <-- raster(.tif) file name

        Outputs: 
            output_raster: raster <-- raster(.tif) file

        Returns:
            None
        """

        self.reset_directories()

        temp_input_points = 'temp_input_points.shp'

        gdf = gpd.read_file(input_points)
        gdf['FID_wbt'] = 1
        gdf.to_file(temp_input_points)

        input_raster = 'temp_input_raster.tif' # assigning file name
        input_raster_zeros = 'temp_input_raster_zeros.tif'
        
        self.wbt.vector_points_to_raster(temp_input_points,input_raster,field='FID_wbt', cell_size=100) # points to raster transformation
        self.reset_directories()

        self.wbt.convert_nodata_to_zero(input_raster, input_raster_zeros)
        self.reset_directories()

        self.wbt.euclidean_distance(input_raster_zeros, output_raster) # euclidean distance calculated on created raster
        self.reset_directories()

        os.remove(os.path.join(self.wbt.work_dir, input_raster)) # removes temporary raster file
        os.remove(os.path.join(self.wbt.work_dir, input_raster_zeros))
        os.remove(os.path.join(self.wbt.work_dir, temp_input_points))
        
        self.reset_directories()

    # Distance From Lines
    def distance_from_lines(self,input_lines, output_raster):
        """
        Creates new raster showing distances between lines

        Inputs: 
            input_lines: str <-- path to input point(.shp) file
            output_raster: str <-- raster(.tif) file name

        Outputs:
            output_raster: raster <-- raster(.tif) file

        Returns:
            None
        """

        self.reset_directories()

        temp_input_lines = 'temp_input_lines.shp'

        gdf = gpd.read_file(input_lines)
        gdf['FID_wbt'] = 1
        gdf.to_file(temp_input_lines)

        input_raster = 'temp_input_raster.tif'  # assigning file name
        temp_input_raster_zeros = 'temp_input_raster_zeros.tif'
        
        self.wbt.vector_lines_to_raster(temp_input_lines, input_raster,field='FID_wbt', cell_size=100) # lines to raster transformation
        self.reset_directories()
        
        self.wbt.convert_nodata_to_zero(input_raster,temp_input_raster_zeros)
        self.reset_directories()

        self.wbt.euclidean_distance(temp_input_raster_zeros, output_raster) # euclidean distance calculated on created raster
        self.reset_directories()

        os.remove(os.path.join(self.wbt.work_dir,input_raster)) # removes temporary raster file
        os.remove(os.path.join(self.wbt.work_dir,temp_input_lines))
        os.remove(os.path.join(self.wbt.work_dir,temp_input_raster_zeros))
        self.reset_directories()

    # Distance From Polygons 
    def distance_from_polygons(self, input_polygons, output_raster):
        """
        Creates new raster showing distances between polygons

        Inputs:
            input_polygons: str <-- path to input polygon(.shp) file
            output_raster: str <-- raster(.tif) file name

        Outputs:
            output_raster: raster <-- output raster(.tif) file

        Returns:
            None
        """
        
        self.reset_directories()

        temp_input_polygons = 'temp_input_polygons.shp'
        temp_input_raster_zeros = 'temp_input_raster_zeros.tif'
        
        gdf = gpd.read_file(input_polygons)
        gdf['FID_wbt'] = 1
        gdf.to_file(temp_input_polygons)

        input_raster = 'temp_input_raster.tif' # assigning file name
        self.wbt.vector_polygons_to_raster(temp_input_polygons ,input_raster, field='FID_wbt', cell_size = 100) # polygons to raster transformation
        self.reset_directories()

        self.wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
        self.reset_directories()

        self.wbt.euclidean_distance(temp_input_raster_zeros, output_raster) # euclidean distance calculated on created raster
        self.reset_directories()

        os.remove(os.path.join(self.wbt.work_dir,input_raster)) # removes temporary raster file
        os.remove(os.path.join(self.wbt.work_dir,temp_input_polygons))
        os.remove(os.path.join(self.wbt.work_dir,temp_input_raster_zeros))
        self.reset_directories()

    # Distance From Raster (Geometric Analysis)
    def distance_from_raster(self, input_raster, output_raster):
        """
        Creates new raster showing distances within raster

        Inputs:
            input_raster: str <-- path to input raster(.tif) file
            output_raster: str <-- raster(.tif) file name

        Outputs:
            output_raster: raster <-- output raster(.tif) file 
        """
        
        self.reset_directories()

        temp_input_raster_zeros = 'temp_input_raster_zeros.tif'
        
        self.wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
        self.reset_directories()

        self.wbt.euclidean_distance(temp_input_raster_zeros, output_raster) # euclidean distance calculated on input raster
        self.reset_directories()
        
        os.remove(os.path.join(wbt.work_dir, temp_input_raster_zeros))
        self.reset_directories()

    # Hotspots From Points (Geometric Analysis)
    def hotspots_from_points(self,input_points, output_raster, sigma = 100):
        """
        Creates hotspot raster from input point shapefile

        Inputs:
            input_points: str <-- path to input point(.shp) file
            output_raster: str <-- name of output raster(.tif) file
            sigma [optional]: str <-- represents standard deviation of gaussian filter, default 100

        Outputs:
            output_raster: raster <-- output raster(.tif) file

        Returns:
            None
        """
        
        self.reset_directories()
        
        temp_input_points = 'temp_input_points.shp'

        gdf = gpd.read_file(input_points)
        gdf['FID_wbt'] = 1
        gdf.to_file(temp_input_points)

        
        input_raster = 'temp_hotspots_from_points.tif' # assigning temporary file name
        temp_input_raster_zeros = 'temp_input_raster_zeros.tif'

        self.wbt.vector_points_to_raster(temp_input_points, input_raster, field='FID_wbt', cell_size=100) # points to raster transformation
        self.reset_directories()
        
        self.wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
        self.reset_directories()
        
        self.wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
        self.reset_directories()
        
        os.remove(os.path.join(self.wbt.work_dir, input_raster)) # remove temporary raster file
        os.remove(os.path.join(self.wbt.work_dir, temp_input_raster_zeros))
        os.remove(os.path.join(self.wbt.work_dir, temp_input_points))
        self.reset_directories()

    # Hotspots From Lines (Geometric Analysis)
    def hotspots_from_lines(self, input_lines, output_raster, sigma =10):
        """
        Creates hotspot raster from input line shapefile

        Inputs:
            input lines: str <-- path to input line(.shp) file
            output_raster: str <-- raster(.tif) file name
            sigma [optional]: str <-- represents standard deviation of gaussian filter, default 10

        Outputs:
            output_raster: raster <-- raster(.tif) file 

        Returns:
            None
        """

        self.reset_directories()

        temp_input_lines = 'temp_input_lines.shp'

        gdf = gpd.read_file(input_lines)
        gdf['FID_wbt'] = 1
        gdf.to_file(temp_input_lines)

        input_raster = 'temp_hotspots_from_lines.tif' # assigning temporary file name
        temp_input_raster_zeros = 'temp_input_raster_zeros.tif'

        self.wbt.vector_lines_to_raster(temp_input_lines, input_raster, field = 'FID_wbt', cell_size = 100) # lines to raster transformation
        self.reset_directories()

        self.wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
        self.reset_directories()

        self.wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
        self.reset_directories()

        os.remove(os.path.join(self.wbt.work_dir, temp_input_raster_zeros))
        os.remove(os.path.join(self.wbt.work_dir, temp_input_lines)) # remove temporary file
        self.reset_directories()

    #  Hotspots From Polygons (Geometric Analysis)
    def hotspots_from_polygons(self, input_polygons, output_raster,sigma = 10):
        """
        Creates hotspot raster from input polygon shapefile

        Inputs:
            input polygons: str <-- path to input line(.shp) file
            output_raster: str <-- raster(.tif) file name
            sigma [optional]: str <-- represents standard deviation of gaussian filter, default 10

        Output:
            output_raster: raster <-- raster(.tif) file
        
        Returns:
        None
        """
        
        self.reset_directories()
        
        temp_input_polygons = 'temp_input_polygons.shp'

        gdf = gpd.read_file(input_polygons)
        gdf['FID_wbt'] = 1
        gdf.to_file(temp_input_polygons)

        input_raster = 'temp_hotspots_from_polygons.tif' # assigning temporary file name
        temp_input_raster_zeros = 'temp_input_rasters_zeros.tif'
        
        self.wbt.vector_polygons_to_raster(temp_input_polygons, input_raster, field='FID_wbt', cell_size=100) # polygons to raster transformation
        self.reset_directories()
        
        self.wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
        self.reset_directories()
        
        self.wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
        self.reset_directories()

        os.remove(os.path.join(self.wbt.work_dir, input_raster)) # remove temporary file
        os.remove(os.path.join(self.wbt.work_dir, temp_input_polygons)) 
        os.remove(os.path.join(self.wbt.work_dir, temp_input_raster_zeros))
        
        self.reset_directories()

    # Hotsposts From Raster (Geometric Analysis)
    def hotspots_from_raster(self, input_raster, output_raster,sigma = 10):
        """
        Creates hotspot raster from input raster file

        Inputs:
            input raster: str <-- path to input raster(.tif) file
            output_raster: str <-- raster(.tif) file name
            sigma [optional]: str <-- represents standard deviation of gaussian filter, default 10
        
        Outputs:
            output_raster: raster <-- raster(.tif) file
        
        Returns:
            None
        """

        self.reset_directories()

        temp_input_raster_zeros = 'temp_input_raster_zeros.tif'

        self.wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
        self.reset_directories()

        self.wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
        self.reset_directories()

        os.remove(os.path.join(wbt.work_dir,temp_input_raster_zeros))
        self.reset_directories()

    #  Interpolate Points (Geometric Analysis)
    def interpolate_points(self, input_points, field, output_raster):
        """
        Intepolates points into a raster surface 

        Inputs:
            input_points: str <-- path to input point shapefile
            output_raster : str <-- name of output raster(.tif) file 

        Outputs:
            output_raster: raster <-- output raster(.tif) file

        Returns:
            None
        """

        self.reset_directories()

        self.wbt.radial_basis_function_interpolation(field, i=input_points, output=output_raster) # interpolation function

        self.reset_directories()

    #  Summarise Within (Geometric Analysis)
    def summarize_within(self, input_vector, feature_polygons, output_polygon, field_to_summarize=None, aggfunc='mean'):
        """
        Summarizes vector data relative to existing polygons

        Inputs:
            input_vector: str <-- path to input vector(.shp) file. Can be point/lines/polygons
            feature_polygons: str <-- path to input polygons(.shp)
            output_polygon: str <-- name of output polygon(.shp) file
            field_to_summarize: str <-- name of field to summarize
            aggfunc [optional]: str: aggregation function, default is 'mean'
            
        Outputs:
            output_polygon: shapefile <-- polygon(.shp) file

        Returns:
            None
        """

        self.reset_directories()

        input_vector = gpd.read_file(input_vector) # geopandas read vector
        feature_polygons = gpd.read_file(feature_polygons) # geopandas polygons

        if field_to_summarize == None:
            field_to_summarize == 'Index_WBT'

        input_vector['Index_WBT'] = input_vector.index
        # input_vector_gdf = gpd.GeoDataFrame(input_vector[[field_to_summarize,'geometry']])
        input_vector_gdf = input_vector 
        input_vector_join = input_vector_gdf.join(other=feature_polygons,rsuffix='_P') # attribute join on both inputs
        input_vector_join = input_vector_join.drop(columns=['geometry_P'])
        input_vector_join.dissolve(by=field_to_summarize, aggfunc=aggfunc) # dissolve geometries
        input_vector_join.to_file(os.path.join(self.wbt.work_dir, output_polygon)) # save as file ouput_polygons

