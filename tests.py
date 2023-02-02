import unittest
import pandas as pd
import argparse
import os
from gpxplotter import read_gpx_file
import glob
import natsort
import warnings
import process_gpx
from Helpers import folium_plot
from DataController.ValhallaController import Valhalla
import requests_mock

import datetime

from process_gpx import *


class TestMapPlotting(unittest.TestCase):
    def setUp(self):
        # Set up test data
        self.time = pd.Series([1, 2, 3, 4, 5])
        self.lats = pd.Series([1, 2, 3, 4, 5])
        self.lons = pd.Series([1, 2, 3, 4, 5])
        self.distance = pd.Series([1, 2, 3, 4, 5])
        self.elevation = pd.Series([1, 2, 3, 4, 5])
        self.speed = pd.Series([1, 2, 3, 4, 5])
        self.data = pd.DataFrame(
            {
                "lat": self.lats,
                "lon": self.lons,
                "time": self.time,
                "distance": self.distance,
                "elevation": self.elevation,
                "speed": self.speed,
            }
        )
        self.Args = argparse.Namespace(gpx="test.gpx")

        GPXdata = {
            "segments": [
                {
                    "time": self.time,
                    "lat": self.lats,
                    "lon": self.lons,
                    "distance": self.distance,
                    "elevation": self.elevation,
                    "velocity": self.speed,
                }
            ]
        }
        self.data = pd.DataFrame(
            {
                "lat": self.lats,
                "lon": self.lons,
                "time": self.time,
                "distance": self.distance,
                "elevation": self.elevation,
                "speed": self.speed,
            }
        )

    def test_PlotValhalla(self):
        PlotValhalla(self.data, self.Args)
        # Check if plot is saved
        self.assertTrue(os.path.isfile("test_valhalla_plot.html"))

    def test_MapPlot(self):
        MapPlot(self.data, self.Args)
        # Check if plot is saved
        self.assertTrue(os.path.isfile("test_plot.html"))

    def test_CreateDataFrame(self):

        GPXdata = {
            "segments": [
                {
                    "time": self.time,
                    "lat": self.lats,
                    "lon": self.lons,
                    "distance": self.distance,
                    "elevation": self.elevation,
                    "velocity": self.speed,
                }
            ]
        }
        result = CreateDataFrame(GPXdata)
        pd.testing.assert_frame_equal(result, self.data)

    def tearDown(self):
        # Remove plot files
        if os.path.isfile("test_plot.html"):
            os.remove("test_plot.html")
        if os.path.isfile("test_valhalla_plot.html"):
            os.remove("test_valhalla_plot.html")


class TestValhalla:
    pass


if __name__ == "__main__":

    unittest.main()

