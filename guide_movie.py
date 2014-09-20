import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
import pyfits
import glob
import os
from scipy.ndimage import median_filter

os.chdir('/raid1/maye/irtf/140918/guidedog/scan1')

def read_scan1(fname):
    data = pyfits.getdata(fname, 0)
    return data[248:394, :]

def read_guide(fname):
    return pyfits.getdata(fname, 0)

fitsfiles = glob.glob('sylvester*.fits')
fitsfiles.sort()
FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='IRTF Scan 1', artist='Matplotlib',
                comment='Scan 1, rows 248:394')
writer = FFMpegWriter(fps=5, metadata=metadata)

fig = plt.figure(figsize=(10,10))
handle = plt.imshow(np.zeros((512, 512)),cmap='gray',
            interpolation='nearest')
plt.axis('off')

#plt.xlim(-5, 5)
#plt.ylim(-5, 5)

tomovie = fitsfiles
with writer.saving(fig, "/u/paige/maye/guide_movie.mp4", 100):
    for fitsfile in tomovie:
        print fitsfile
        nr = fitsfile.split('-')[1][:5]
        handle.get_axes().set_title(nr)
        data = read_guide(fitsfile)
        cleaned = median_filter(data, size=3)
        handle.set_data(cleaned)
        handle.autoscale()
        writer.grab_frame()
