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


def main(root, fname_base, outfname):
    searchterm = root + '/' + fname_base + '*.fits'
    print(searchterm)
    fitsfiles = glob.glob(searchterm)
    fitsfiles.sort()
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='IRTF Scan 1', artist='Matplotlib',
                    comment='Scan 1, rows 248:394')
    writer = FFMpegWriter(fps=5, metadata=metadata)

    fig = plt.figure(figsize=(10, 8))
    handle = plt.imshow(np.zeros((146, 1024)), cmap='hot',
                        interpolation='nearest', aspect='auto')

    tomovie = fitsfiles
    with writer.saving(fig, outfname+".mp4", 100):
        for fitsfile in tomovie:
            print(fitsfile)
            no = fitsfile.split('-')[1][:5]
            handle.get_axes().set_title(no)
            data = read_scan1(fitsfile)
            filtered = median_filter(data, 2)
            handle.set_data(filtered)
            handle.autoscale()
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
