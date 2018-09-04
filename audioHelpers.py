import numpy as np
from scipy.interpolate import interp2d
import peakdetect as pd
import librosa
from numba import jit


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


def stft(X, frameSize=4096, windowFunction='hann', overlap=0, absVal=True):
    Y = librosa.stft(X, n_fft=frameSize, hop_length=frameSize -
                     overlap, window=windowFunction)
    if abs:
        return np.abs(Y)
    else:
        return Y


def simpleLoad(path, mono=False, resample=False, sr=None, normalize=None, normalizeVal=None):
    if not resample:
        data, sro = librosa.load(path, mono=mono, sr=None)
    else:
        data, sro = librosa.load(path, mono=mono, sr=sr)

    if normalize != None:
        linPeak = np.max(np.abs(data))
    if normalize == 'peak':
        if normalizeVal == None:
            normalizeVal = 0
            print('no normalize value provided')
        data = (data/linPeak)*dBToA(normalizeVal)
    elif normalize == 'rms':
        if normalizeVal == None:
            normalizeVal = -23
            print('waring, no explicit normalize Value given. Normalizing to -23 dB RMS.')
        rms = np.mean(aToDb(getRms(data.T)))
        rmsDiff = normalizeVal - rms
        clipDistance = -1*aToDb(linPeak)
        amp = np.min(rmsDiff, clipDistance)
        data = data*dBToA(amp)

    elif normalize == 'lufs':
        raise NotImplementedError(
            'LUFS normalization is not implemented yet. Do it.')

    return data.T, sro


@jit
def aToDb(linArray, accuracy=10):
    # A = 20*log10(V2/V1)
    dbArray = 20.*np.log10(np.clip(linArray, 10**-accuracy, 10**accuracy))
    return dbArray


@jit
def dBToA(X):
    """Given a np.array calculates linear from dB values"""
    P1 = 10.**(X/20.)
    return P1

def getRms(x):
    """check this for stereo"""
    return np.sqrt(np.mean(x**2., axis=0))
