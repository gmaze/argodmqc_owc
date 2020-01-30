"""
-----Get Historical Data Test File-----

Written by: Edward Small
When: 05/12/2019

Contains unit tests to check the functionality of the `get_hist_region_locations` function

To run this test specifically, look at the documentation at:
https://gitlab.noc.soton.ac.uk/edsmall/bodc-dmqc-python
"""

import unittest
import numpy as np
from ow_calibration.get_region.get_region_data import get_region_data


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.wmo_boxes = np.array([[3505, 1, 1, 1],
                        [3506, 1, 1, 1]])
        self.float_name = "3901960"
        self.float_name_removed = "1900479"
        self.index = np.array([0, 4, 5, 11, 13, 15, 20, 21, 42])
        self.pres = np.array([3, 5, 15.1, 25.1, 36, 40, 45, 46, 500000])
        self.config = {'HISTORICAL_DIRECTORY': "data/climatology",
                  'HISTORICAL_CTD_PREFIX': "/historical_ctd/ctd_",
                  'HISTORICAL_BOTTLE_PREFIX': "/historical_bot/bot_",
                  'HISTORICAL_ARGO_PREFIX': "/historical_argo/argo_",
                  'MAP_P_DELTA': 250}

    def test_returns_6(self):
        """
        check that the function returns 6 arrays
        :return: Nothing
        """
        print("Testing that get_region_data returns 6 arrays")
        test = get_region_data(self.wmo_boxes, self.float_name, self.config,
                               self.index, self.pres)

        self.assertTrue(test.__len__() == 6, "Should return 6 arrays")

if __name__ == '__main__':
    unittest.main()
