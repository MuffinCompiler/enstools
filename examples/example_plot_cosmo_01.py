#!/usr/bin/env python3
import os
import enstools.io
import enstools.plot
import matplotlib.pyplot as plt
from enstools.misc import download
from datetime import datetime
import argparse
import cartopy.crs as ccrs

if __name__ == "__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", help="if provided, the plot will be saved in the given name.")
    parser.add_argument("--data", default="data", help="storage location for downloaded files.")
    args = parser.parse_args()

    # ensure that the data directory is available
    if not os.path.exists(args.data):
        os.makedirs(args.data)

    # download the 24h forecast from today 00 UTC.
    today = datetime.now().date()
    file_name = "cosmo-d2_germany_rotated-lat-lon_single-level_%s00_024_PMSL.grib2" % today.strftime("%Y%m%d")
    download("https://opendata.dwd.de/weather/nwp/cosmo-d2/grib/00/pmsl/%s.bz2" % file_name,
             "%s/%s.bz2" % (args.data, file_name))

    # read the grib file
    grib = enstools.io.read("%s/%s" % (args.data, file_name))

    # create a basic contour plot and show or save it
    fig, ax = enstools.plot.contour(grib["PMSL"][0, :, :] / 100.0,
                                    coastlines="50m",
                                    borders="50m",
                                    rotated_pole=grib["rotated_pole"],
                                    projection=ccrs.NearsidePerspective(central_latitude=50, central_longitude=10),
                                    subplot_args=(121,))
    ax.set_global()
    fig, ax = enstools.plot.contour(grib["PMSL"][0, :, :] / 100.0,
                                    coastlines="50m",
                                    borders="50m",
                                    rotated_pole=grib["rotated_pole"],
                                    figure=fig,
                                    subplot_args=(122,))
    if args.save is None:
        plt.show()
    else:
        fig.savefig(args.save, bbox_inches="tight", transparent=True)
