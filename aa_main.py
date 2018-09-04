# -*- coding: utf-8 -*-
"""

"""

__author__ = "Patrik Lechner, https://github.com/hrtlacek"
__version__ = "1.0.0"
__license__ = "MIT"

audioOn = True
global playStop
playStop = 0

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
import numpy as np
import logging
import audioHelpers as auh
from pyqtgraph.dockarea import *
import tkinter as tk
from tkinter import filedialog

logging.basicConfig(level=logging.DEBUG)

class KeyPressWindow(QtGui.QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, ev):
        self.sigKeyPress.emit(ev)

def keyPressed(evt):
    global playStop, mainPlayerAmp, phase, trig, playpos,pp
    keyCode = evt.key()
    logging.debug(keyCode)
    if keyCode==32: #space bar
        logging.debug('play/stop key press')
        playStop = (playStop+1)%2
        if playStop==1:
            mainPlayer.setPhase(playpos.get()/numSamps)
            gMul.setValue(0)
            pp.setValue(playpos.get()/numSamps)
            phase.reset()
            trig.play()
            mainPlayerAmp.setValue(1.)

        else:
            mainPlayerAmp.setValue(0.)
            gMul.setValue(1)

QtGui.QApplication.setGraphicsSystem('raster')
pg.setConfigOptions(antialias=True)

app = QtGui.QApplication([])
win = KeyPressWindow()
win.sigKeyPress.connect(keyPressed)
area = DockArea()
win.setCentralWidget(area)
win.resize(1000, 500)
win.setWindowTitle('pyqtgraph example: dockarea')


f = 'demo.flac'

def loadAndAnalyze(f):
    global x,sr,nyq,numSamps,absSpec,numFrames, numFreqs, scale, drawSpec
    x,sr = auh.simpleLoad(f, mono=True)
    nyq = sr/2
    numSamps = len(x)
    fs = 2**14
    overlap = int(fs*0.98)
    absSpec = np.clip(auh.aToDb(abs(auh.stft(x, frameSize=fs , overlap=overlap))),-100,100)
    numFrames=absSpec.shape[1]
    numFreqs = absSpec.shape[0]
    scale = numFreqs/numFrames
    drawSpec = absSpec
    return

loadAndAnalyze(f)



## Create docks, place them into the window one at a time.
d1 = Dock("Dock1", size=(100, 10))  # give this dock the minimum possible size
d1.hideTitleBar()
d3 = Dock("Dock3", size=(500, 200)) #Time domain
d3.hideTitleBar()
d4 = Dock("Spectrum", size=(200, 200))
d7 = Dock("Spec Peaks", size=(200, 200))
d5 = Dock("Dock5 - Image", size=(500, 500)) #Spectrogram
d5.hideTitleBar()
d6 = Dock("Dock6 (tabbed) - Plot", size=(200, 200))
d6.hideTitleBar()
area.addDock(d1, 'left')
area.addDock(d3, 'bottom', d1)  # place d3 at bottom edge of d1
area.addDock(d5, 'bottom', d3)  # place d5 at left edge of d1
area.addDock(d4, 'right', d5)  # place d4 at right edge of dock area
area.addDock(d6, 'right', d3)  # place d5 at top edge of d4
area.addDock(d7, 'above', d4)


## Add widgets into each dock

## first dock gets save/restore buttons
w1 = pg.LayoutWidget()
saveBtn = QtGui.QPushButton('Save dock state')
loadFileBtn = QtGui.QPushButton('Load File')
w1.addWidget(loadFileBtn, row=2, col=0)
d1.addWidget(w1)
d1.hideTitleBar()
state = None

def load():
    global f
    root = tk.Tk()
    root.withdraw()
    f = filedialog.askopenfilename()
    loadAndAnalyze(f)
    newFile(f)

loadFileBtn.clicked.connect(load)

# ================TIME DOMAIN Complete======================
d3.hideTitleBar()
vb = pg.ViewBox(enableMouse=False)
w3 = pg.PlotWidget(title=f, enableMenu=False, viewBox=vb)
w3.setDownsampling(auto=True, mode='peak')

# Draggable line for playpos
playBar = pg.InfiniteLine(angle=90, movable=True, pen='g')
vb.addItem(playBar)
vb.setMouseEnabled(x=False) # makes user interaction a little easier
playBar.setValue(0.8)
playBar.setZValue(1000) 

# Non-Draggable line for playpos
playBarPlaying = pg.InfiniteLine(angle=90, movable=False, pen='y')
vb.addItem(playBarPlaying)
# vb.setMouseEnabled(x=False) # makes user interaction a little easier
playBarPlaying.setValue(0.8)
playBarPlaying.setZValue(1000)

w3.showGrid(x=True, y=True)
p3 = w3.plot(x)
d3.addWidget(w3)


# ==============Spec Crurrent=======================
w4 = pg.PlotWidget(title="Spectrum")
pi4 = w4.getPlotItem()
pi4.setLimits(xMin=1, xMax=np.log10(sr/2))

w4.showGrid(x=True, y=True)
w4.setLogMode(x=True, y=None)
xAxis = np.linspace(0,sr/2,numFreqs)
p4 = w4.plot(xAxis, drawSpec[:, 0])
d4.addWidget(w4)

#--crosshair
vLine = pg.InfiniteLine(angle=90, movable=False)
hLine = pg.InfiniteLine(angle=0, movable=False)
pi4.addItem(vLine, ignoreBounds=True)
pi4.addItem(hLine, ignoreBounds=True)

label = pg.TextItem('blub', anchor = (0.5,1.))
pi4.addItem(label)
curvePoint = pg.CurvePoint(p4)
label.setParentItem(curvePoint)
w4.addItem(curvePoint)

s1 = w4.plot([0], [0], pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(255, 0, 0, 150))
vb4 = pi4.vb
thisFrame = 0

def mouseMoved(evt):
    global thisFrame
    pos = evt.toPoint()  ## using signal proxy turns original arguments into a tuple
    if pi4.sceneBoundingRect().contains(pos):
        mousePoint = vb4.mapSceneToView(pos)
        cursorFreq = 10**mousePoint.x()
        index = int((cursorFreq/nyq)*numFreqs)

        if index > 0 and index < numFreqs:
            curvePoint.setPos(float(index)/(numFreqs-1))
            label.setText('Freq=%0.1f Hz, Amp=%0.1f dB' %
                          (cursorFreq, drawSpec[:, thisFrame][index]))

        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())

pi4.scene().sigMouseMoved.connect(mouseMoved)

# ==============SPECTRIGRAM-Complete=========================
w5 = pg.ImageView()
ii = w5.getImageItem()
ii.setAutoDownsample(True)
vbS = w5.getView()
scale = numFreqs/numFrames
w5.setImage(np.flip(auh.makeLogSpec(absSpec).T, axis=1),
            scale=[scale, 1])
w5.setPredefinedGradient('flame')
d5.addWidget(w5)
d5.hideTitleBar()

playBarS = pg.InfiniteLine(angle=90, movable=True, pen='g')
vbS.addItem(playBarS)
vbS.setMouseEnabled(x=False) # makes user interaction a little easier
playBarS.setValue(0.8)
playBarS.setZValue(1000) # bring iso line above contrast controls


# ==================Time domain current====================
w6 = pg.PlotWidget(title="Time Domain")
p6 = w6.plot(np.zeros([0]))
pi6 = w6.getPlotItem()
pi6.setLimits(maxXRange=1000, xMin=0, xMax=999, yMin=-1, yMax=1)
d6.addWidget(w6)
w6.showGrid(x=True, y=True)

win.show()

w7 = pg.TableWidget()
d7.addWidget(w7)



# CALLBACKS
def updatePlaybar():
    global playBar,p6,x, playpos,playBarS, thisFrame, scale
    v = playBar.value()
    thisFrame = int((v/numSamps)*numFrames)
    thisFrame = np.clip(thisFrame, 0, numFrames-1)
    if audioOn:
        playpos.setValue(v)
        playBarS.setValue(thisFrame*scale)
    v = max(v,0)
    p6.setData(x[int(v):int(v+1000)])
    xAxis = np.linspace(0,sr/2,numFreqs)
    p4.setData(xAxis, drawSpec[:,thisFrame])
    updatePeaks(drawSpec[:, thisFrame])
    return

def updatePlaybarS():
    global playBar,p6,x, playpos,playBarS, thisFrame, scale
    v = playBarS.value()/scale
    thisFrame = np.clip(int(v), 0, numFrames-1)
    v = (v/numFrames)*numSamps
    v = max(v,0)
    if audioOn:
        playpos.setValue(v)
        playBar.setValue(v) 
    p6.setData(x[int(v):int(v+1000)])
    xAxis = np.linspace(0,sr/2,numFreqs)
    data = drawSpec[:, thisFrame]
    p4.setData(xAxis,data)
    updatePeaks(data)
    return


def formatForTable(cols):
    numCols = len(cols)
    numRows = len(cols[0])
    preList = []
    for i in range(numRows):
        thisRow = (cols[0][i], cols[1][i])
        preList.append(thisRow)
    data = np.array(preList, dtype=[('Freqs', float), ('Amps', float)])
    return preList

def updatePeaks(data):
    global s1, w7
    indizes = auh.getPeaks(data)

    clipInds = indizes[np.arange(min(100, len(indizes)))]
    xs = (clipInds/numFreqs)*nyq
    ys = data[clipInds]
    
    s1.setData(xs, ys)
    w7.setData(formatForTable([xs,ys]))

    return

playBar.sigDragged.connect(updatePlaybar)
playBarS.sigDragged.connect(updatePlaybarS)


# AUDIIO PROCESSING
if audioOn:
    from pyo import *
    s = Server(audio='jack')
    s.boot()
    s.start()
    playpos = Sig(0)
    snd = SndTable(f)
    env = HannTable()
    dur = Noise(mul=.001, add=.2)
    gMul = Sig(1)
    g = Granulator(snd, env, [0.5, 0.501], playpos, dur, 64, mul=gMul/5).out()
    mainPlayerAmp = Sig(0)
    trig = Trig()
    pp = Sig(0)
    phase = Phasor(freq=snd.getRate(), phase=pp)

    mainPlayer = OscTrig(snd,trig, freq=snd.getRate() , phase=phase, mul=mainPlayerAmp, interp=0).out()

else:
    playpos = 0


def newFile(f):
    global snd,phase, mainPlayer,w5,p3,x
    snd.setSound(f)
    phase.setFreq(snd.getRate())
    mainPlayer.setFreq(snd.getRate())
    w5.setImage(np.flip(auh.makeLogSpec(absSpec).T, axis=1), autoRange=True)
    p3.setData(x)

def update():
    global playbar, playBarS,playStop, mainPlayer,phase,scale
    if playStop==1:
        p = phase.get()*numSamps
        playBarPlaying.setValue(p)
        v = p
        thisFrame = int((v/numSamps)*numFrames)
        thisFrame = np.clip(thisFrame, 0, numFrames-1)
        if audioOn:
            playpos.setValue(v)
            playBarS.setValue(thisFrame*scale)
        v = max(v,0)
        p6.setData(x[int(v):int(v+1000)])
        xAxis = np.linspace(0,sr/2,numFreqs)
        p4.setData(xAxis, drawSpec[:,thisFrame])
        updatePeaks(drawSpec[:, thisFrame])

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
