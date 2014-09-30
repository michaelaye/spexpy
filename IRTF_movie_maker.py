import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
import pyfits
import glob
from scipy.ndimage import median_filter
import argparse


def read_scan1(fname):
    data = pyfits.getdata(fname, 0)
    return data[248:394, :]


def read_guide(fname):
    return pyfits.getdata(fname, 0)


def determine_data_type(fitsfiles):
    xsize = pyfits.getheader(fitsfiles[0])['NAXIS1']
    if xsize == 512:
        return 'guide'
    elif xsize == 1024:
        return 'spex'
    else:
        return 'unknown'


class TypeSettings(object):
    def __init__(self, typestring):
        if typestring == 'guide':
            self.figsize = (10, 10)
            self.aspect = 'equal'
            self.zeroshape = (512, 512)
            self.cmap = 'gray'
            self.vmax = 2000
        elif typestring == 'spex':
            self.figsize = (10, 8)
            self.aspect = 'auto'
            self.zeroshape = (146, 1024)
            self.cmap = 'hot'
            self.vmax = None


def main(root, fname_base, outfname):
    searchterm = root + '/' + fname_base + '*.fits'
    print(searchterm)
    fitsfiles = glob.glob(searchterm)
    fitsfiles.sort()
    datatype = determine_data_type(fitsfiles)
    settings = TypeSettings(datatype)

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='IRTF ' + outfname, artist='Matplotlib',
                    comment='IRTF' + str(settings.zeroshape))
    writer = FFMpegWriter(fps=5, metadata=metadata)

    fig = plt.figure(figsize=settings.figsize)
    handle = plt.imshow(np.zeros(settings.zeroshape), cmap=settings.cmap,
                        interpolation='nearest', aspect=settings.aspect,
                        vmax=2000)

    tomovie = fitsfiles
    with writer.saving(fig, outfname+".mp4", 100):
        for fitsfile in tomovie:
            print(fitsfile)
            no = fitsfile.split('-')[1][:5]
            time = pyfits.getheader(fitsfile)['TIME_OBS']
            handle.get_axes().set_title(no + ' ' + time)
            data = read_scan1(fitsfile)
            filtered = median_filter(data, 2)
            handle.set_data(filtered)
            writer.grab_frame()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("root",
                        help='Root folder where data to process is in.')
    parser.add_argument("fname_base",
                        help='base fname to scan for')
    parser.add_argument('movie_name',
                        help='Output filename for the movie.')
    args = parser.parse_args()
    main(args.root, args.fname_base, args.movie_name)
