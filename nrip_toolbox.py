import os
from re import L
from tabnanny import verbose
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

    