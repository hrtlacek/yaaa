import numpy as np
from scipy.interpolate import interp2d, interp1d
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


# /*================================
# =  MATLAB TRanslation Helpers    =
# ==================================*/


def isempty(x):
    if len(x) == 0:
        return True
    else:
        return False


def mlFind(func, n, direction):
    if direction != 'last':
        if n != 0:
            return np.where(func)[0][0:n]
        else:
            return np.where(func)[0]
    else:
        if n != 0:
            return np.flip(np.flip(np.where(func), axis=1)[0][0:n], axis=0)
        else:
            return np.flip(np.flip(np.where(func), axis=1)[0], axis=0)

# ======================================================================


def octaveSmooth(spectrum, Noct, sr):
    """Spectrum Octave Smoother

    1/N octave smoother. Very efficient. Original Source unkown.
    Translation of old matlab FFT eqtool spec smoother.

    Arguments:
        spectrum {np.array} -- Input Magnitude spectrum (linear)
        Noct {float} -- smoothing amount. Lower numbers produce more smoothing.
        sr {float/int} -- input spectrum sample rate

    Returns:
        np.array -- smoothed spectrum
    """

    Nfft = len(spectrum)
    Px = aToDb(spectrum)
    nyq = sr / 2
    freq = np.linspace(0, nyq, Nfft)

    if Noct > 0:
        Noct = 2 * Noct
        # octave center frequencies
        f1 = 1
        i = 0
        fc = np.array([])
        while f1 < nyq:
            f1 = f1 * 10**(3 / (10 * Noct))
            i = i + 1
            fc = np.append(fc, f1)

    # octave edge frequencies
        fe = np.array([])
        for i in range(len(fc)):
            f1 = 10**(3 / (20 * Noct)) * fc[i]
            fe = np.append(fe, f1)

    # find nearest frequency edges
        for i in range(len(fe)):
            fe_p = mlFind(freq > fe[i], 1, 'first')
            fe_m = mlFind(freq < fe[i], 1, 'last')
            fe_0 = mlFind(freq == fe[i], 0, 'first')
            if isempty(fe_0) == False:
                fe[i] = fe_0
            else:
                p = fe_p - fe[i]
                m = fe[i] - fe_m
                if p < m:
                    fe[i] = fe_p
                else:
                    fe[i] = fe_m

        Px_oct = np.zeros(len(fe) - 1)

        for i in range(len(fe) - 1):

            Px_i = Px[int(fe[i]):1 + int(fe[i + 1])]
            Px_oct[i] = np.mean(Px_i, axis=0)


#         print(min(fc))
        fc = fc[1:]

        #         print(min(freq))
        fc = np.insert(fc, 0, 0)
        Px_oct = np.insert(Px_oct, 0, Px[1])
        interpolator = interp1d(fc, Px_oct, kind='cubic', bounds_error=True)

        Px_oct = interpolator(freq)

    smoothSpectrum = Px_oct
    return smoothSpectrum


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
