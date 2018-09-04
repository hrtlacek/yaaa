import numpy as np
from scipy.interpolate import interp2d
import peakdetect as pd

def makeLogSpec(dbSpec):
    x = np.arange(dbSpec.shape[1])
    y = np.arange(dbSpec.shape[0])
    yLog = np.geomspace(10, dbSpec.shape[0], num=dbSpec.shape[0])
    logSpecInterpolator = interp2d(x, y, dbSpec)

    logSpec = logSpecInterpolator(x, yLog)
    return logSpec

def getPeaks(specFrame):
    indizes = pd.detect_peaks(specFrame, mph=10, mpd=15, threshold=0, edge='rising',
                              kpsh=False, valley=False, show=False, ax=None)
    return indizes

