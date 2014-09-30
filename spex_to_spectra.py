#!/usr/bin/env python
import pyfits
import glob
import numpy as np
import argparse
from scipy.ndimage import median_filter
import sys

filemarkers = {'sylvester': {'moon': (1, 104), 'sky': (107, None)},
               'limb': {'sky': (1, None)},
               'hermite': {'moon': (1, None)}
               }


def read_subarray(fname):
    data = pyfits.getdata(fname, 0)
    return data[248:394, :]


def get_nr_from_fname(fname):
    return int(fname.split('-')[1][:5])


def filter_data_list(filelist, start, end):
    """filter data for image_numbers, start until end (inclusive)"""
    outlist = []
    if end is None:
        end = get_nr_from_fname(filelist[-1])
    print start, end
    for fname in filelist:
        nr = get_nr_from_fname(fname)
        if nr >= start and nr <= end:
            outlist.append(fname)
    return outlist


def read_data_to_cube(filelist):
    data = []
    for fitsfile in filelist:
        data.append(read_subarray(fitsfile))

    # making a numpy-3D-array out of the slow list container
    return np.array(data)


def process_cube(filelist, target, subtarget):
    print "Processing", target, 'with', subtarget
    cube = read_data_to_cube(filelist)
    master = cube.mean(axis=0)
    filtered = median_filter(master, 2)
    regions = []
    regions.append(filtered[:36, :])
    regions.append(filtered[37:73, :])
    regions.append(filtered[74:110, :])
    regions.append(filtered[110:, :])
    for i, region in enumerate(regions):
        spectrum = region.mean(axis=0)
        outfname = 'output' + '/' + '_'.join([target,
                                             subtarget,
                                             'region'+str(i+1)]) + '.csv'
        spectrum.tofile(outfname, sep=',')


def main(root, fname_base, target):
    searchterm = root + '/' + fname_base + '*.fits'
    print(searchterm)
    fitsfiles = glob.glob(searchterm)
    fitsfiles.sort()
    print "Found {} files.".format(len(fitsfiles))
    filenumbers = filemarkers[target]
    for subtarget in filenumbers:
        start = filenumbers[subtarget][0]
        end = filenumbers[subtarget][1]
        filelist = filter_data_list(fitsfiles, start, end)
        if len(filelist) == 0:
            print 'ohoh'
            sys.exit()
        process_cube(filelist, target, subtarget)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("root",
                        help='Root folder where data to process is in.')
    parser.add_argument("fname_base",
                        help='base fname to scan for')
    parser.add_argument('outfname',
                        help='Output filename prefix.')
    args = parser.parse_args()
    main(args.root, args.fname_base, args.outfname)
