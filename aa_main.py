# -*- coding: utf-8 -*-
"""

"""


audioOn = True
global playStop
playStop = 0


import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
import numpy as np
import logging
import audio as au

import audioHelpers as auh

from pyqtgraph.dockarea import *

logging.basicConfig(level=logging.DEBUG)


class KeyPressWindow(QtGui.QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, ev):
        # print(ev)
        # self.scene().keyPressEvent(ev)
        self.sigKeyPress.emit(ev)

def keyPressed(evt):
    global playStop, mainPlayerAmp, phase, trig, playpos,pp
    keyCode = evt.key()
    logging.debug(keyCode)
    if keyCode==32: #space bar
        logging.debug('play/stop key press')
        playStop = (playStop+1)%2
        print (playStop)
        if playStop==1:
            # mainPlayer.setSpeed = 1.
            mainPlayer.setPhase(playpos.get()/numSamps)
            gMul.setValue(0)
            pp.setValue(playpos.get()/numSamps)
            phase.reset()
            trig.play()
            mainPlayerAmp.setValue(1.)

            # while playStop == 1:
            #     time.sleep(0.2)


        else:
            print('stopping')
            # mainPlayer.setSpeed = 0.
            mainPlayerAmp.setValue(0.)
            gMul.setValue(1)



QtGui.QApplication.setGraphicsSystem('raster')
pg.setConfigOptions(antialias=True)

app = QtGui.QApplication([])
# win = QtGui.QMainWindow()
win = KeyPressWindow()
win.sigKeyPress.connect(keyPressed)
area = DockArea()
win.setCentralWidget(area)
win.resize(1000, 500)
win.setWindowTitle('pyqtgraph example: dockarea')


f = '/root/Documents/MATLAB/data/drumLoopMono.flac'
# f = '/root/Documents/MATLAB/data/pereUbu.wav'

def loadAndAnalyze(f):
    global x,sr,nyq,numSamps,absSpec,numFrames, numFreqs, scale, drawSpec
    x,sr = au.simpleLoad(f, mono=True)
    nyq = sr/2
    numSamps = len(x)
    fs = 2**14
    overlap = int(fs*0.98)
    absSpec = np.clip(au.aToDb(abs(au.stft(x, frameSize=fs , overlap=overlap))),-100,100)
    # absSpecLin = au.dBToA(absSpec)
    # smooSpec = np.zeros_like(absSpec)
    # smooSpec = au.octaveSmooth(absSpec,3,sr)
    numFrames=absSpec.shape[1]
    numFreqs = absSpec.shape[0]
    scale = numFreqs/numFrames
    drawSpec = absSpec
    return
# for i in range(numFrames):
#     smooSpec[:,i] = au.octaveSmooth(absSpecLin[:,i],5,sr)
# smooSpec = np.clip(au.aToDb(smooSpec),-100,100)

loadAndAnalyze(f)



## Create docks, place them into the window one at a time.
## Note that size arguments are only a suggestion; docks will still have to
## fill the entire dock area and obey the limits of their internal widgets.
d1 = Dock("Dock1", size=(100, 10))  # give this dock the minimum possible size
d1.hideTitleBar()
# d2 = Dock("Dock2 - Console", size=(500, 300), closable=True)
d3 = Dock("Dock3", size=(500, 200)) #Time domain
d3.hideTitleBar()
d4 = Dock("Spectrum", size=(200, 200))
d7 = Dock("Spec Peaks", size=(200, 200))
# d4.hideTitleBar()
d5 = Dock("Dock5 - Image", size=(500, 500)) #Spectrogram
d5.hideTitleBar()
d6 = Dock("Dock6 (tabbed) - Plot", size=(200, 200))
d6.hideTitleBar()
# place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
area.addDock(d1, 'left')
# area.addDock(d2, 'right')  # place d2 at right edge of dock area
area.addDock(d3, 'bottom', d1)  # place d3 at bottom edge of d1
area.addDock(d5, 'bottom', d3)  # place d5 at left edge of d1
area.addDock(d4, 'right', d5)  # place d4 at right edge of dock area
area.addDock(d6, 'right', d3)  # place d5 at top edge of d4
area.addDock(d7, 'above', d4)


## Add widgets into each dock

## first dock gets save/restore buttons
w1 = pg.LayoutWidget()
# label = QtGui.QLabel(""" Test.
# """)
saveBtn = QtGui.QPushButton('Save dock state')
loadFileBtn = QtGui.QPushButton('Load File')
# loadFileBtn.setEnabled(False)
# w1.addWidget(label, row=0, col=0)
# w1.addWidget(saveBtn, row=1, col=0)
w1.addWidget(loadFileBtn, row=2, col=0)
d1.addWidget(w1)
d1.hideTitleBar()
state = None


def save():
    global state
    state = area.saveState()
    # restoreBtn.setEnabled(True)

import tkinter as tk
from tkinter import filedialog


def load():
    global f
    root = tk.Tk()
    root.withdraw()
    f = filedialog.askopenfilename()
    loadAndAnalyze(f)
    newFile(f)
    # area.restoreState(state)


saveBtn.clicked.connect(save)
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
playBar.setZValue(1000) # bring iso line above contrast controls

# Non-Draggable line for playpos
playBarPlaying = pg.InfiniteLine(angle=90, movable=False, pen='y')
vb.addItem(playBarPlaying)
# vb.setMouseEnabled(x=False) # makes user interaction a little easier
playBarPlaying.setValue(0.8)
playBarPlaying.setZValue(1000) # bring iso line above contrast controls

w3.showGrid(x=True, y=True)
p3 = w3.plot(x)
d3.addWidget(w3)


# ==============Spec Crurrent=======================
w4 = pg.PlotWidget(title="Spectrum")
pi4 = w4.getPlotItem()
pi4.setLimits(xMin=1, xMax=np.log10(sr/2))
# w4.addItem(label)

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

# s1 = w4.addItem()

# s1 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(
#     None), brush=pg.mkBrush(255, 0, 0, 120))
# # s1.setLo
# w4.addItem(s1)




def mouseMoved(evt):
    # return
    global thisFrame
    # print('bla')
    # print(dir(evt))
    # print(evt)
    pos = evt.toPoint()  ## using signal proxy turns original arguments into a tuple
    # print(evt.x())
    if pi4.sceneBoundingRect().contains(pos):
        mousePoint = vb4.mapSceneToView(pos)
        cursorFreq = 10**mousePoint.x()
        index = int((cursorFreq/nyq)*numFreqs)

        if index > 0 and index < numFreqs:
            curvePoint.setPos(float(index)/(numFreqs-1))
            # label.setText("<span style='font-size: 12pt'>freq=%0.1f Hz,   <span style='color: red'>Amp=%0.1f dB</span>" % (cursorFreq, drawSpec[:,thisFrame][index]))
            label.setText('Freq=%0.1f Hz, Amp=%0.1f dB' %
                          (cursorFreq, drawSpec[:, thisFrame][index]))

        # label.setText("<span style='font-size: 12pt'>x=%0.1f" % (mousePoint.x()))
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())

# proxy = pg.SignalProxy(pi4.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
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
    # print(v)
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
    # s = au.octaveSmooth(absSpec[:,thisFrame],3,sr)
    data = drawSpec[:, thisFrame]
    p4.setData(xAxis,data)
    # p4.setData(xAxis,s)
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
    # frame = drawSpec[:, thisFrame]
    indizes = auh.getPeaks(data)
    # print (indizes)
    # indizes = np.arange(100)
    # for i in range(len(indizes)):
        # n = 300

    clipInds = indizes[np.arange(min(100, len(indizes)))]
    xs = (clipInds/numFreqs)*nyq
    ys = data[clipInds]
    # pos = np.array([xs,data[indizes]])
        # pos = np.random.normal(size=(2, n), scale=1e-5)
    
    s1.setData(xs, ys)
    # s1.clear()
    # s1 = w4.plot(xs, ys, pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(255, 0, 0, 150))
    # td = np.array([xs,ys]).T
    # tableData = np.array([td[0,:], td[1,:]], dtype=[('Freq', float), ('Amp', float)])
    w7.setData(formatForTable([xs,ys]))
    # w7.set

    # spots = [{'pos': pos[:, i], 'data': 1}
    #         for i in range(len(indizes))] + [{'pos': [0, 0], 'data': 1}]
    # s1.clear()
    # s1.addPoints(spots)

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
    # pos = Phasor(freq=snd.getRate()*.25, mul=snd.getSize())
    dur = Noise(mul=.001, add=.2)
    gMul = Sig(1)
    g = Granulator(snd, env, [0.5, 0.501], playpos, dur, 64, mul=gMul/5).out()
    mainPlayerAmp = Sig(0)
    trig = Trig()
    pp = Sig(0)
    phase = Phasor(freq=snd.getRate(), phase=pp)

    # mainPlayer = SfPlayer(f, loop=False, mul=mainPlayerAmp, offset = offset).out()
    mainPlayer = OscTrig(snd,trig, freq=snd.getRate() , phase=phase, mul=mainPlayerAmp, interp=0).out()

    # sf = SfPlayer(f, speed=1, loop=False).out()
    # while True:
    #     pass
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
        # print(mainPlayer.phase)




timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
