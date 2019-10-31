"""
-----Load Configuration Test File-----

Written by: Edward Small
When: 31/10/2019

Contains unit tests to check the functionality of the `find_besthist` function

To run this test specifically, look at the documentation at:
https://gitlab.noc.soton.ac.uk/edsmall/bodc-dmqc-python

"""

import unittest
import numpy as np
from .find_besthist import barotropic_potential_vorticity, spatial_correlation


class FindBestHistTestCase(unittest.TestCase):
    """
    Test cases for find_besthist function, and associated functions
    """

    def test_bpv_returns_float(self):
        """
        Checks that barotropic_potential_vorticity returns a float if
        inputs are just floats.
        :return: Nothing
        """

        pv_result = barotropic_potential_vorticity(1, 1)
        self.assertTrue(isinstance(pv_result, float), "potential vorticity is not float")

    def test_bpv_vectorised_returns_array(self):
        """
        Check that barotropic_potential_vorticity returns an array if the function
        is vectorised and given lists as inputs
        :return: Nothing
        """

        lat = [1, 2, 3, 4]
        z_value = [4, 3, 2, 1]
        barotropic_potential_vorticity_vec = np.vectorize(barotropic_potential_vorticity)
        pv_result = barotropic_potential_vorticity_vec(lat, z_value)
        self.assertTrue(isinstance(pv_result, np.ndarray), "potential vorticity vec is not list")


if __name__ == '__main__':
    unittest.main()

"""barotropic_potential_vorticity_vec = np.vectorize(barotropic_potential_vorticity)

grid_lat = [-57.996, -56.375, -54.496]
grid_z = [523, 522.31, 444.71]

ans = barotropic_potential_vorticity(-59.1868, 5108.3)
ans_vec = barotropic_potential_vorticity_vec(grid_lat, grid_z)
print(ans)
print(ans_vec)

remain_hist_long = [53.195, 51.954, 53.107]
LONG = 57.1794
longitude_large = 8
remain_hist_lat = [-57.996, -56.375, -54.496]
LAT = -59.1868
latitude_large = 4
remain_hist_dates = [1.9741 * 10 ** 3, 1.9471 * 10 ** 3, 1.9472 * 10 ** 3]
DATES = 2.018 * 10 ** 3
age_large = 20
PV_float = -2.452
PV_hist = [-0.0236 * 10 ** -6, -0.0233 * 10 ** -6, -0.0267 * 10 ** -6]
phi_large = 0.5

ans = spatial_correlation(remain_hist_long[0], LONG, longitude_large,
                          remain_hist_lat[0], LAT, latitude_large,
                          remain_hist_dates[0], DATES, age_large,
                          phi_large, PV_hist[0], PV_float)

print(ans)"""
