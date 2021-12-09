import os 
from wbt_utils import *
import geopandas as gpd

# import whitebox
# wbt = whitebox.WhiteboxTools()

wbt = wbt_setup(verbose=True) 

__all__ = ['intersect', # NOT TESTED
           'zonal_statistics', # NOT TESTED
           'distance_from_points', # TESTED
           'distance_from_lines', # TESTED
           'distance_from_polygons', # TESTED
           'distance_from_raster', # TESTED
           'hotspots_from_points', # TESTED
           'hotspots_from_lines', # TESTED
           'hotspots_from_polygons', # TESTED
           'hotspots_from_raster', # TESTED
           'interpolate_points', # NOT TESTED 
           'SummarizeWithin', # NOT TESTED
          ]

def intersect(input_vector_file, overlay, output_vector_file):
    """
    Function to return all feature parts that occur in both input layers

    Inputs:
        input_vector_file: str <-- path to vector(.shp) file
        overlay: str <-- path to overlay vector(.shp) file
        output_vector_file: str <-- name of output vector(.shp) file

    Outputs:
        output_vector_file: shapefile  <-- output vector shapefile
    """
    wbt.intersect(input_vector_file, overlay, output_vector_file)
    os.chdir(wbt.work_dir)

def zonal_statistics(input_raster, input_zones, output_raster, field='FID', stat='mean', input_zones_is_raster=True):
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
        wbt.vector_polygons_to_raster(temp_input_zones, input_zones_raster, field=field, nodata=False) # transforming polygon to raster if input_zones is a polygon
    
    wbt.zonal_statistics(i=input_raster, features=input_zones_raster, output=output_raster, stat=stat)

    if not input_zones_is_raster:
        os.remove(os.path.join(wbt.work_dir,input_zones_raster)) # removing temporary raster file if one had to be created
    os.chdir(wbt.work_dir)
    
def distance_from_points(input_points, output_raster):
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

    temp_input_points = 'temp_input_points.shp'

    gdf = gpd.read_file(input_points)
    gdf['FID_wbt'] = 1
    gdf.to_file(temp_input_points)

    input_raster = 'temp_input_raster.tif' # assigning file name
    input_raster_zeros = 'temp_input_raster_zeros.tif'
    wbt.vector_points_to_raster(temp_input_points,input_raster,field='FID_wbt', cell_size=100) # points to raster transformation
    wbt.convert_nodata_to_zero(input_raster, input_raster_zeros)
    wbt.euclidean_distance(input_raster_zeros, output_raster) # euclidean distance calculated on created raster
    os.remove(os.path.join(wbt.work_dir, input_raster)) # removes temporary raster file
    os.remove(os.path.join(wbt.work_dir, input_raster_zeros))
    os.remove(os.path.join(wbt.work_dir, temp_input_points))
    os.chdir(wbt.work_dir)

def distance_from_lines(input_lines, output_raster):
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
    temp_input_lines = 'temp_input_lines.shp'

    gdf = gpd.read_file(input_lines)
    gdf['FID_wbt'] = 1
    gdf.to_file(temp_input_lines)

    input_raster = 'temp_input_raster.tif'  # assigning file name
    temp_input_raster_zeros = 'temp_input_raster_zeros.tif'
    wbt.vector_lines_to_raster(temp_input_lines, input_raster,field='FID_wbt', cell_size=100) # lines to raster transformation
    wbt.convert_nodata_to_zero(input_raster,temp_input_raster_zeros)
    wbt.euclidean_distance(temp_input_raster_zeros, output_raster) # euclidean distance calculated on created raster
    os.remove(os.path.join(wbt.work_dir,input_raster)) # removes temporary raster file
    os.remove(os.path.join(wbt.work_dir,temp_input_lines))
    os.remove(os.path.join(wbt.work_dir,temp_input_raster_zeros))
    os.chdir(wbt.work_dir)

def distance_from_polygons(input_polygons, output_raster):
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
    temp_input_polygons = 'temp_input_polygons.shp'
    temp_input_raster_zeros = 'temp_input_raster_zeros.tif'
    gdf = gpd.read_file(input_polygons)
    gdf['FID_wbt'] = 1
    gdf.to_file(temp_input_polygons)

    input_raster = 'temp_input_raster.tif' # assigning file name
    wbt.vector_polygons_to_raster(temp_input_polygons ,input_raster, field='FID_wbt', cell_size = 100) # polygons to raster transformation
    wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
    wbt.euclidean_distance(temp_input_raster_zeros, output_raster) # euclidean distance calculated on created raster
    os.remove(os.path.join(wbt.work_dir,input_raster)) # removes temporary raster file
    os.remove(os.path.join(wbt.work_dir,temp_input_polygons))
    os.remove(os.path.join(wbt.work_dir,temp_input_raster_zeros))
    os.chdir(wbt.work_dir)


def distance_from_raster(input_raster, output_raster):
    """
    Creates new raster showing distances within raster

    Inputs:
        input_raster: str <-- path to input raster(.tif) file
        output_raster: str <-- raster(.tif) file name

    Outputs:
        output_raster: raster <-- output raster(.tif) file 
    """
    temp_input_raster_zeros = 'temp_input_raster_zeros.tif'
    wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
    wbt.euclidean_distance(temp_input_raster_zeros, output_raster) # euclidean distance calculated on input raster
    os.remove(os.path.join(wbt.work_dir, temp_input_raster_zeros))
    os.chdir(wbt.work_dir)

def hotspots_from_points(input_points, output_raster, sigma = 100):
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
    temp_input_points = 'temp_input_points.shp'

    gdf = gpd.read_file(input_points)
    gdf['FID_wbt'] = 1
    gdf.to_file(temp_input_points)

    
    input_raster = 'temp_hotspots_from_points.tif' # assigning temporary file name
    temp_input_raster_zeros = 'temp_input_raster_zeros.tif'

    wbt.vector_points_to_raster(temp_input_points, input_raster, field='FID_wbt', cell_size=100) # points to raster transformation
    wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
    wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
    os.remove(os.path.join(wbt.work_dir, input_raster)) # remove temporary raster file
    os.remove(os.path.join(wbt.work_dir, temp_input_raster_zeros))
    os.remove(os.path.join(wbt.work_dir, temp_input_points))
    os.chdir(wbt.work_dir)

def hotspots_from_lines(input_lines, output_raster, sigma =10):
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
    temp_input_lines = 'temp_input_lines.shp'

    gdf = gpd.read_file(input_lines)
    gdf['FID_wbt'] = 1
    gdf.to_file(temp_input_lines)

    input_raster = 'temp_hotspots_from_lines.tif' # assigning temporary file name
    temp_input_raster_zeros = 'temp_input_raster_zeros.tif'

    wbt.vector_lines_to_raster(temp_input_lines, input_raster, field = 'FID_wbt', cell_size = 100) # lines to raster transformation
    wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
    wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
    os.remove(os.path.join(wbt.work_dir, input_raster)) # remove temporary raster file
    os.remove(os.path.join(wbt.work_dir, temp_input_raster_zeros))
    os.remove(os.path.join(wbt.work_dir, temp_input_lines)) # remove temporary file
    os.chdir(wbt.work_dir)


def hotspots_from_polygons(input_polygons, output_raster,sigma = 10):
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
    temp_input_polygons = 'temp_input_polygons.shp'

    gdf = gpd.read_file(input_polygons)
    gdf['FID_wbt'] = 1
    gdf.to_file(temp_input_polygons)

    input_raster = 'temp_hotspots_from_polygons.tif' # assigning temporary file name
    temp_input_raster_zeros = 'temp_input_rasters_zeros.tif'
    wbt.vector_polygons_to_raster(temp_input_polygons, input_raster, field='FID_wbt', cell_size=100) # polygons to raster transformation
    wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
    wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
    os.remove(os.path.join(wbt.work_dir, input_raster)) # remove temporary file
    os.remove(os.path.join(wbt.work_dir, temp_input_polygons)) 
    os.remove(os.path.join(wbt.work_dir, temp_input_raster_zeros))
    os.chdir(wbt.work_dir)


def hotspots_from_raster(input_raster, output_raster,sigma = 10):
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
    temp_input_raster_zeros = 'temp_input_raster_zeros.tif'

    wbt.convert_nodata_to_zero(input_raster, temp_input_raster_zeros)
    wbt.gaussian_filter(temp_input_raster_zeros, output_raster, sigma=sigma)
    os.remove(os.path.join(wbt.work_dir,temp_input_raster_zeros))
    os.chdir(wbt.work_dir)

def interpolate_points(input_points, field, output_raster):
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
    wbt.radial_basis_function_interpolation(field, i=input_points, output=output_raster) # interpolation function

def SummarizeWithin(input_vector, feature_polygons, output_polygon, field_to_summarize=None, aggfunc='mean'):
    """
    Summarizies vector data relative to existing polygons

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
    input_vector_join.to_file(os.path.join(wbt.work_dir, output_polygon)) # save as file ouput_polygons
