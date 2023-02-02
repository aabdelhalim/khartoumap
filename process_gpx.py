import pandas as pd
import argparse
import os

from gpxplotter import (
    read_gpx_file,
)
import glob
import natsort
import warnings
from Helpers import folium_plot
from DataController.ValhallaController import Valhalla

warnings.filterwarnings("ignore")


def MapPlotDir(data, Args):
    MapPlot(data, Args)


def process_files(directory, Args):
    tracking = 0
    # processed_files = set()
    gpx_files = natsort.natsorted(glob.glob(os.path.join(directory, "*.gpx")))
    for filename in gpx_files:
        Args.gpx = filename
        data = GetDataFromGPXFolder(filename)
        for track in data:
            track_data = CreateDataFrame(track)
            MapPlotDir(track_data, Args)
            ArgsOptions(track_data, Args)
            tracking += 1
            print(f"file {tracking} processed: {filename}")


################ Plotting ################


def MapPlot(data, Args):
    """
    :param data:
    :return:
    """
    the_map = folium_plot(data)
    the_map.save(f"{Args.gpx[:-4]}_plot.html")

    print("\n#####################################################################\n")

    print(f"Stats for GPX File: {Args.gpx}\n")
    print(f"Total distance = {round(data.distance.max() / 1000, 2)} km")
    data["time"] = pd.to_datetime(data["time"], unit="s")
    print(
        f"Total time = {round((data.iloc[-1].time - data.time[0]).seconds / 60, 2)} minutes"
    )
    print(
        f"Elevation change = {round(data.elevation.max() - data.elevation.min(), 2)} m"
    )
    print(f"Average speed = {round(data.speed.mean() * 3.6, 2)} km/hr")
    print(f"Track map saved in script directory as: {Args.gpx[:-4]}_plot.html")


def PlotValhalla(data, Args):
    """
    :param data:
    :return:
    """

    the_map = folium_plot(data)
    the_map.save(f"{Args.gpx[:-4]}_valhalla_plot.html")
    print(f"Map Matching Successful! See: {Args.gpx[:-4]}_valhalla_plot.html")


def GetDataFromGPXFolder(file_path=None):
    tracks = []
    for track in read_gpx_file(file_path):
        tracks.append(track)
    return tracks


def GetDataFromGPX():
    for track in read_gpx_file(Args.gpx):
        data = track
    return data


def CreateDataFrame(GPXdata):
    """
    :param GPXdata:
    :return:
    """

    time = pd.Series(GPXdata["segments"][0]["time"])
    lats = pd.Series(GPXdata["segments"][0]["lat"])
    lons = pd.Series(GPXdata["segments"][0]["lon"])
    distance = pd.Series(GPXdata["segments"][0]["distance"])
    elevation = pd.Series(GPXdata["segments"][0]["elevation"])
    speed = pd.Series(GPXdata["segments"][0]["velocity"])

    data = pd.DataFrame(
        {
            "lat": lats,
            "lon": lons,
            "time": time,
            "distance": distance,
            "elevation": elevation,
            "speed": speed,
        }
    )
    return data


def ArgsOptions(data, Args=None):
    """
    :param data:
    :return:
    """

    if Args.output:
        # data.drop(['time'], axis=1).to_csv(f'{Args.gpx[:-4]}_output.csv', index=False)
        data.to_csv(f"{Args.gpx[:-4]}.csv", index=False)
        print(f"Track data saved in gpx directory as: {Args.gpx[:-4]}.csv")
    print("\n#####################################################################\n")

    if Args.valhalla:
        # print('\n#####################################################################\n')
        print("Running Valhalla Map Matching (Meili)")

        data = data.sort_values(by=["time"], ascending=True)
        valhalla = Valhalla(data)
        data = valhalla.valhalla_df()
        PlotValhalla(data, Args)

        if Args.output:
            valhalla.valhalla_df().drop(["time"], axis=1).to_csv(
                f"{Args.gpx[:-4]}_output.csv", index=False
            )
            # valhalla.valhalla_df().to_csv(f'{Args.gpx[:-4]}.csv', index=False)
            print(f"Track data saved in gpx directory as: {Args.gpx[:-4]}.csv")
            print(
                "\n#####################################################################\n"
            )

        if Args.geojson:
            data.to_json(f"{Args.gpx[:-4]}.json", orient="records")
            print(f"Track GeoJson saved in gpx directory as: {Args.gpx[:-4]}.json")
            print(
                "\n#####################################################################\n"
            )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gpx", help="GPX file.")
    parser.add_argument(
        "-o", "--output", action="store_true", help="Produce output csv files."
    )
    parser.add_argument(
        "-v",
        "--valhalla",
        action="store_true",
        help="Use Valhalla map matching (beta).",
    )
    parser.add_argument(
        "-j", "--geojson", action="store_true", help="Produce A geojson output (beta)."
    )
    parser.add_argument(
        "-d",
        "--directory",
        nargs="?",
        const=None,
        help="GPX files directory (optional).",
    )
    Args = parser.parse_args()

    try:
        if Args.directory is not None:
            process_files(Args.directory, Args)

        elif Args.gpx:
            data = GetDataFromGPX()
            data = CreateDataFrame(data)
            MapPlot(data, Args)
            ArgsOptions(data, Args)
            print("Done!")
            print(
                "\n#####################################################################\n"
            )

        else:
            raise Exception(
                "Please specify either a GPX file or a directory of GPX files using the -g or -d flags respectively"
            )

    except Exception as e:
        print(f"An error occurred: {e}")

