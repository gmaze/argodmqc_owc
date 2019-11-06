"""
-----find best historical casts-----

Written by: Breck Owens and Annie Wong
When: xx/12/2006
Converted to python by: Edward Small
When: 30/10/2019

Find ln_max_casts unique historical points that are most strongly correlated with the float profile

Rewritten in December 2006 to only use latitude, longitude, data, and water depth as arguments
and to return index of the station list

N.B. Change to code on the xx/06/2013: add age_large when computing correlation_large
- C Cabanes

N.B Change during conversion to python on the 31/10/2019: Potential Vorticity, Correlation, and
ellipse are calculated multiple times, so I moved them into their own function.
These functions can be vectorised using the numpy library (numpy.vectorize(function))
to use the functions on arrays.
- Edward Small

For information on how to use this file, check the README at either:

https://github.com/ArgoDMQC/matlab_owc
https://gitlab.noc.soton.ac.uk/edsmall/bodc-dmqc-python
"""

import math
import random
import numpy as np


def barotropic_potential_vorticity(lat, z_value):
    """
    Calculates barotropic potential vorticity (pv)
    :param lat: latitude
    :param z_value: depth
    """
    earth_angular_velocity = 2 * 7.292 * 10 ** -5
    lat_radians = lat * math.pi / 180

    potential_vorticity = (earth_angular_velocity * math.sin(lat_radians)) / z_value

    if potential_vorticity == 0:
        potential_vorticity = 1 * 10 ** -5

    return potential_vorticity


# pylint: disable=too-many-arguments
def spatial_correlation(
        longitude_1, longitude_2, ellipse_longitude, latitude_1, latitude_2,
        ellipse_latitude, dates_1, dates_2, ellipse_age, phi, pv_1=0, pv_2=0
):
    """
    Calculates the spatial correlation between two points.
    Can be done with or without potential vorticity
    :param longitude_1: longitude of point 1
    :param longitude_2: longitude if point 2
    :param ellipse_longitude: longitudinal size of ellipse
    :param latitude_1: latitude of point 1
    :param latitude_2: latitude of point 2
    :param ellipse_latitude: latitudinal size of ellipse
    :param dates_1: dates of data for point 1
    :param dates_2: dates of data for point 2
    :param ellipse_age: age of data wanted in ellipse
    :param phi: potential gradient
    :param pv_1: potential vorticity of point 1
    :param pv_2: potential vorticity of point 2
    :return: spatial correlation between points
    """

    pv_correlation = 0
    correlation = ((longitude_1 - longitude_2) ** 2 / (ellipse_longitude ** 2)) + \
                  ((latitude_1 - latitude_2) ** 2 / (ellipse_latitude ** 2)) + \
                  ((dates_1 - dates_2) ** 2 / (ellipse_age ** 2))

    if pv_1 != 0 and pv_2 != 0:
        pv_correlation = ((pv_2 - pv_1) / (math.sqrt(pv_2 ** 2 + pv_1 ** 2) / phi)) ** 2

    return correlation + pv_correlation


def find_ellipse(data_long, ellipse_long, ellipse_size_long,
                 data_lat, ellipse_lat, ellipse_size_lat,
                 phi, data_pv=0, ellipse_pv=0):
    """
    Finds whether a data point exists inside an ellipse
    :param data_long: longitude of the data point
    :param ellipse_long: longitude of the centre of the ellipse
    :param ellipse_size_long: size of the ellipse in the longitudinal direction
    :param data_lat: latitude of the data point
    :param ellipse_lat: latitude of the centre of the ellipse
    :param ellipse_size_lat: size of the ellipse in the latitudinal direction
    :param phi: cross-isobath scale for ellipse
    :param data_pv: potential vorticity of the data point
    :param ellipse_pv: potential vorticity of the centre of the ellipse
    :return: float. If <1, it exists inside the ellipse
    """

    total_pv = 0
    if data_pv != 0 and ellipse_pv != 0:
        total_pv = (ellipse_pv - data_pv) / math.sqrt(ellipse_pv ** 2 + data_pv ** 2) / phi

    ellipse = math.sqrt((data_long - ellipse_long) ** 2 / (ellipse_size_long * 3) ** 2 + \
                        (data_lat - ellipse_lat) ** 2 / (ellipse_size_lat * 3) ** 2 + \
                        total_pv ** 2)

    return ellipse


# pylint: disable=fixme
# TODO: ARGODEV-155
# Refactor this code to take objects and dictionaries instead of a ludicrous amount of arguments

def find_besthist(
        grid_lat, grid_long, grid_dates, grid_z_value,
        lat, long, date, z_value,
        latitude_large, latitude_small, longitude_large, longitude_small,
        phi_large, phi_small, age_large, age_small, map_pv_use, max_casts
):
    """
    Finds ln_max_casts number of unique historical data points that are most strongly correlated
    with the float profile being processed
    :param grid_lat: array of latitudes of historical data
    :param grid_long: array of longitudes of historical data
    :param grid_dates: array of ages of the historical data
    :param grid_z_value: array of depths of the historical data
    :param lat: latitude of the float profile
    :param long: longitude of the float profile
    :param date: age of the float profile
    :param z_value: depth of the float profile
    :param latitude_large: latitude of large ellipse
    :param latitude_small: latitude of small ellipse
    :param longitude_large: longitude of large ellipse
    :param longitude_small: longitude of small ellipse
    :param phi_large: cross-isobath scale for large ellipse
    :param phi_small: cross-isobath scale for small ellipse
    :param age_large: age of data in large ellipse
    :param age_small: age of data in small ellipse
    :param map_pv_use: flag for whether to use potential vorticity (see load_configuration.py)
    :param max_casts: maximum number of data points wanted
    :return: indices of historical data to use
    """

    #make sure arrays are 1 dimensional
    grid_lat = grid_lat.flatten()
    grid_long = grid_long.flatten()
    grid_z_value = grid_z_value.flatten()
    grid_dates = grid_dates.flatten()

    # set up potential vorticity
    barotropic_potential_vorticity_vec = np.vectorize(barotropic_potential_vorticity)
    pv_float = 0
    pv_hist = 0

    # if we are using potential vorticity, calculate it
    if map_pv_use == 1:
        pv_float = barotropic_potential_vorticity(lat, z_value)

        # need vectorised version of function for operating on array
        barotropic_potential_vorticity_vec = np.vectorize(barotropic_potential_vorticity)
        pv_hist = barotropic_potential_vorticity_vec(grid_lat, grid_z_value)

    # calculate ellipse
    find_ellipse_vec = np.vectorize(find_ellipse)
    ellipse = find_ellipse_vec(grid_long, long, longitude_large, grid_lat, lat, latitude_large,
                               phi_large, pv_hist, pv_float)

    # find points that lie within the ellipse
    hist_long = []
    hist_lat = []
    hist_dates = []
    hist_z_value = []
    index_ellipse = np.argwhere(ellipse < 1)
    for i in index_ellipse:
        hist_long.append(grid_long[i])
        hist_lat.append(grid_lat[i])
        hist_dates.append(grid_dates[i])
        hist_z_value.append(grid_z_value[i])

    # check to see if too many data points were found
    if index_ellipse.__len__() > max_casts:

        # uses pseudo-random numbers so the same random numbers are selected for each run
        np.random.seed(index_ellipse.__len__())

        # pick max_casts/3 random points
        rand_matrix = np.random.rand(math.ceil(max_casts / 3))
        index_rand = np.round(rand_matrix * (index_ellipse.__len__() - 1))

        # make sure the points are all unique
        index_rand = np.unique(index_rand)
        # and sort them into ascending order
        index_rand.sort()

        # create an array containing the indices of the remaining reference data
        # (index_ellipse array without index_rand array)
        # Then create arrays containing the remaining reference lat, long, age, and z_value
        index_remain = index_ellipse.flatten()
        remain_hist_lat = []
        remain_hist_long = []
        remain_hist_z_value = []
        remain_hist_dates = []
        removed = 0
        for i in index_rand:
            index_remain = np.delete(index_remain, int(i) - removed)
            removed += 1

        for i in index_remain:
            remain_hist_lat = np.append(remain_hist_lat, grid_lat[int(i)])
            remain_hist_long = np.append(remain_hist_long, grid_long[int(i)])
            remain_hist_z_value = np.append(remain_hist_z_value, grid_z_value[int(i)])
            remain_hist_dates = np.append(remain_hist_dates, grid_dates[int(i)])

        # sort remaining points by large spatial correlations
        # calculate potential vorticity for remaining data
        if map_pv_use == 1:
            # calculate potential vorticity for remaining data
            """pv_hist = barotropic_potential_vorticity_vec(grid_lat, grid_z_value)"""
            pv_hist = barotropic_potential_vorticity_vec(remain_hist_lat, remain_hist_z_value)

        spatial_correlation_vec = np.vectorize(spatial_correlation)
        correlation_large = spatial_correlation_vec(remain_hist_long, long, longitude_large,
                                                    remain_hist_lat, lat, latitude_large,
                                                    remain_hist_dates, date, age_large,
                                                    pv_hist, pv_float, phi_large)
        """correlation_large = spatial_correlation_vec(grid_lat, long, longitude_large,
                                                    grid_lat, lat, latitude_large,
                                                    grid_dates, date, age_large,
                                                    pv_hist, pv_float, phi_large)"""

        # now sort the correlation into ascending order and keep the index of each correlation
        correlation_large_combined = []
        for i in range(0, index_remain.__len__()):
            correlation_large_combined = np.append(
                correlation_large_combined, [index_remain[i], correlation_large[i]])
            
        print(correlation_large_combined)
        correlation_large_sorted = sorted(correlation_large)
        correlation_large_sorted_index = np.argsort(correlation_large)
        test = correlation_large_sorted_index
        removed = 0


        print(sorted(index_rand))
        print(sorted(test))

        remain_hist_lat_correlation_large = []
        remain_hist_long_correlation_large = []
        remain_hist_z_value_correlation_large = []
        remain_hist_dates_correlation_large = []

        # work out how many large spatial data points needed
        lsegment2 = 2 * math.ceil(max_casts / 3) - index_rand.__len__()

        #select the best large spatial data points, and then remove them from remaining data
        index_large_spatial = []
        print("correlated large sorted index: ", correlation_large_sorted_index.__len__())
        for i in range(0, lsegment2):
            index_large_spatial = np.append(index_large_spatial, correlation_large_sorted_index[i])

        # sort the large spatial correlation indices into order
        index_large_spatial = np.sort(index_large_spatial)
        print(index_large_spatial)
        # find the remaining indices
        removed = 0
        """for i in index_large_spatial:
            index_remain = np.delete(index_remain, int(i) - removed)
            removed += 1"""

        print("index remaining after large spatial: ", index_remain.__len__())

        for i in range(lsegment2, remain_hist_lat.__len__()):
            remain_hist_lat_correlation_large = np.append(
                remain_hist_lat_correlation_large, remain_hist_lat[correlation_large_sorted_index[i]]
            )
            remain_hist_long_correlation_large = np.append(
                remain_hist_long_correlation_large, remain_hist_long[correlation_large_sorted_index[i]]
            )
            remain_hist_z_value_correlation_large = np.append(
                remain_hist_z_value_correlation_large, remain_hist_z_value[correlation_large_sorted_index[i]]
            )
            remain_hist_dates_correlation_large = np.append(
                remain_hist_dates_correlation_large, remain_hist_dates[correlation_large_sorted_index[i]]
            )



        # sort the remaining points by short spatial and temporal correlations
        index_correlation_small = np.arange(start=lsegment2, stop=remain_hist_long.__len__())

        if map_pv_use == 1:
            pv_hist = barotropic_potential_vorticity_vec(
                remain_hist_lat_correlation_large, remain_hist_z_value_correlation_large)

        correlation_small = spatial_correlation_vec(remain_hist_long_correlation_large,
                                                long, longitude_small,
                                                remain_hist_lat_correlation_large,
                                                lat, latitude_small,
                                                remain_hist_dates_correlation_large,
                                                date, age_small,
                                                pv_hist, pv_float, phi_small)

        correlation_small_sorted = sorted(correlation_small)
        correlation_small_sorted_index = np.argsort(correlation_small)

        # select the amount we need for short spatial/temporal correlation
        leftover = max_casts - index_rand.__len__() - lsegment2

        index_small_spatial = []
        for i in range(0, leftover):
            index_small_spatial = np.append(index_small_spatial, correlation_small_sorted_index[i])

        # put together the best random data, large spatial data, and small spatial data
        index = np.concatenate((index_rand, index_large_spatial, index_small_spatial))
        index_1 = np.concatenate((index_rand, index_large_spatial))
        index_2 = np.concatenate((index_rand, index_small_spatial))
        index_3 = np.concatenate((index_small_spatial, index_large_spatial))
        print("size of random points:", np.unique(index_rand).__len__())
        print("size of large spatial points: ", np.unique(index_large_spatial).__len__())
        print("size of small spatial points: ", np.unique(index_small_spatial).__len__())
        print("number of points selected: ", np.unique(index).__len__())
        print("unique points between random and large: ", np.unique(index_1).__len__())
        print("unique points between random and small: ", np.unique(index_2).__len__())
        print("unique points between spatials: ", np.unique(index_3).__len__())


# random.seed(1)
lat_test = np.random.rand(100) * 5 * random.choice([-1, 1]) + -57.996
long_test = np.random.rand(100) * 5 * random.choice([-1, 1]) + 57.1794
z_test = np.random.rand(100) * 5 * random.choice([-1, 1]) + 2.018 * 10 ** 3
age_test = np.random.rand(100) * 5 * random.choice([-1, 1]) + 5.1083 * 10 ** 3

find_besthist(lat_test, long_test, z_test, age_test,
              -59.1868, 57.1794, 2.018 * 10 ** 3, 5.1083 * 10 ** 3,
              4, 2, 8, 4, 0.5, 0.1, 20, 10, 1, 60)

"""find_besthist([-57.996, -56.375], [53.195, 51.954],
              [1.9741 * 10 ** 3, 1.9741 * 10 ** 3], [5.23 * 10 ** 3, 5.2231 * 10 ** 3],
              -59.1868, 57.1794, 2.018 * 10 ** 3, 5.1083 * 10 ** 3,
              4, 2, 8, 4, 0.5, 0.1, 10, 20, 0, 300)"""
