# YAAA

## About
YAAA (Yet Another Audio Analyzer) is a simple program written in python. It is still under development.
![interface screen shot](./img/main.png)

The idea is having a very simple powerful program to look at an audio singnal's time and frequency domain data interactively.\\
Using pyo, yaaa is able to play back sound, but also provides a granular sampling engine, so one can scrub through the sound. pyqtgraph provides a powerful interface that supports rapid updates.

## Usage
This is still in a very early stage of development, and has just been tested under linux. Since it is based on python, it should work under other platforms too.
Loading long soundfiles might take a while.


### Dependencies
- python 3.6
- pyqtgraph
- pyo
- numpy
- scipy
- librosa

The peak finding algorithm used here was created by Marcos Duarte, https://github.com/demotu/BMC.

## Future ideas
- Command line mode: Open yaaa with command line flags, such as a startup file and cropping that file etc.
- Adjustment of peak finding algorithm via GUI
