import sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import math

from scipy import signal


import struct
import serial
import numpy

import os
import re
import pickle
import random
import binascii
import csv



def smooth(x,window_len=11,window='hanning'):

  if x.ndim != 1:
    raise ValueError('smooth only accepts 1 dimension arrays.')

  if x.size < window_len:
    raise ValueError('Input vector needs to be bigger than window size.')


  if window_len<3:
    return x


  if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
    raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


  s=numpy.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
  #print(len(s))
  if window == 'flat': #moving average
    w=numpy.ones(window_len,'d')
  else:
    w=eval('numpy.'+window+'(window_len)')

  y=numpy.convolve(w/w.sum(),s,mode='valid')
  return y


CMD_CONNECT = 0xAA
CMD_BUFFER = 0xAB
CMD_DECODER = 0xAC
CMD_IMPEDANCE = 0xAD
CMD_RESET = 0xDE
RESET2 = 0xAD
CMD_UPLOAD_FILTER_BAND = 0xBC
CMD_UPLOAD_FILTER_NOTCH = 0xBD
CMD_UPLOAD_FILTER_IMP = 0xBE

CMD_USER_FILTER_BAND = 0xCA
CMD_USER_FILTER_NOTCH = 0xCB
CMD_USER_FILTER_IMP  = 0xCC

userFilterBand = []
userBandGain = 0.0
userFilterNotch = []
userNotchGain = 0.0
userFilterImp = []
userImpGain = 0.0
class serialReceiver(QtCore.QThread):
  
  
  newSample = QtCore.pyqtSignal(int,int, tuple, tuple, tuple)
  serialConn = QtCore.pyqtSignal(bool)
  ackResult = QtCore.pyqtSignal(bool)
  
  def __init__(self, baud, port, serialEnabled, dataBuffer1, dataBuffer2, writeVal,
              accelBufferX):
    QtCore.QThread.__init__(self)
    self.serialEnabled = serialEnabled
    self.dataBuffer1 = dataBuffer1
    self.dataBuffer2 = dataBuffer2
    self.writeVal = writeVal
    self.accelBufferX = accelBufferX
    self.commandActive = False
    self.loopRun = 1 #variable to stop the loop when entering the game looprun = 0
    self.stopThread = False
    self.ser = serial.Serial()

    self.ser.baudrate = baud
    self.ser.port = port
    #self.ser.open()
    #self.ser.write(str.encode("wb"))
    self.a=0
    #self.serialConnect()

  @staticmethod
  def floatToByteArray(floatNumber):
    floatBytes = bytearray(struct.pack('<f',floatNumber))
    return floatBytes

  @staticmethod
  def formatCmd(commandType,data):
    dataSize = len(data); 
    cmdArray = bytearray([commandType])
    cmdHeaderSize = len(cmdArray)
    cmdArray.extend(data)
    cmdArray += str.encode('\r')
    cmdArray += str.encode('\n')
    #cmdPacket = struct.pack('B' * (cmdHeaderSize+dataSize), cmdArray)
    cmdPacket = cmdArray
    #print(cmdPacket)
    return cmdPacket

  @staticmethod
  def formatDataMsg(commandType,command, value):
    pkt = struct.pack('BBBBf',commandType,command,0,0,value)
    return pkt

  def serialConnect(self):
    print("serial Open")
    try:
      self.ser.open()
      self.serialEnabled = True
      self.serialConn.emit(self.serialEnabled)
    except:
      print("serial open exception")
      self.serialConn.emit(self.serialEnabled)
    #if not self.serialEnabled : 
    #  self.serialEnabled = True
    #  self.serialConn.emit(self.serialEnabled)
    return

  def serialDisconnect(self):
    print("serial close")
    self.ser.close()
    self.serialEnabled = False
    self.serialConn.emit(self.serialEnabled)
    return

  def unpackReceivedData1(self,data,channel):
    try:
      s = struct.Struct('125f')
      self.dataBuffer1 = s.unpack(data)
      self.writeVal = 2
      chanCounter = channel
      self.newSample.emit(channel, self.writeVal, self.dataBuffer1, self.dataBuffer2, self.accelBufferX)
    except:
      print("receive exception1")

  
  def unpackReceivedData2(self,data,channel):
    try:
      s = struct.Struct('125f')
      self.dataBuffer2 = s.unpack(data)
      self.writeVal = 1
      chanCounter = channel
      self.newSample.emit(channel, self.writeVal, self.dataBuffer1, self.dataBuffer2, self.accelBufferX)
    except:
      print("receive exception2")

  def run(self):
    s = struct.Struct('125f')
    #s = struct.Struct('f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f')
    s2 = struct.Struct('f')
    sAccel = struct.Struct('3f')
    #sAccel = struct.Struct('f f f')

    while 1:
      try:
        if self.loopRun:
          data = self.ser.read(1)
          if(ord(data) == 255):
            data = self.ser.read(3)
            #if(data[0] == 255 and data[1] == 0):
            if(data[0] == 255 and data[1] == 0):
              #channel = data[2]
              channel = data[2]
              if(channel == 6):
                #self.loopRun = 0
                print("")
                data = self.ser.read(4)
                log = s2.unpack(data)
                print("log:"+str(log))
                print("")
              elif(channel == 7):
                data = self.ser.read(12)
                self.accelBufferX = sAccel.unpack(data)
                self.newSample.emit(7,7, self.dataBuffer1, self.dataBuffer2, self.accelBufferX)
              elif(channel > 0) and (channel < 6):
                data = self.ser.read(500)
                if(self.writeVal == 1):
                  self.unpackReceivedData1(data,channel)
                  # self.dataBuffer1 = s.unpack(data)
                  # self.writeVal = 2
                  # chanCounter = channel
                  # self.newSample.emit(channel, self.writeVal, self.dataBuffer1, self.dataBuffer2, self.accelBufferX)
                else:
                  self.unpackReceivedData2(data,channel)
                  # self.dataBuffer2 = s.unpack(data)
                  # self.writeVal = 1
                  # chanCounter = channel
                  # self.newSample.emit(channel, self.writeVal, self.dataBuffer1, self.dataBuffer2, self.accelBufferX)
            else:
              pass
              #self.ser.flush()
          #elif(data[0] == 5):
          #  if not self.serialEnabled : 
          #    self.serialConn.emit(self.serialEnabled)
          #  self.enabled = 1
          #  print("Raw signals enabled!")
          #elif(data[0] == 20):
            #if not self.serialEnabled : 
            #  self.serialConn.emit(self.serialEnabled)
            #self.enabled = 1
          else:
            if(self.commandActive):
              self.ackResult.emit(self.waitForAck(data))
              
              print("loop command is active")
              #print(data)
              #ack = self.ser.read()
              #print(ack)

        else:
          self.a +=1
          print(self.a)
      except:
        if self.stopThread:
          print("stopping serial")
          #self.ser.close()
          return
        else:
          continue


  def waitForAck(self,ackHeader):
    print("waitForAck")
    ack = self.ser.read(1)
    #self.printBytes(ackHeader)
    #self.printBytes(ack)
    if(ord(ackHeader) == 0xFA):
      if(ord(ack) == 0x47):
        print("ack")
        self.ser.flush()
        self.commandActive = False
        if(not self.serialEnabled):
          self.serialEnabled = True
          self.serialConn.emit(self.serialEnabled)
        return True
    else:
      print("nack")
      self.ser.flush()
      self.commandActive = False
      return False

  def connect(self):
      print("sending connect")
      self.commandActive = True
      self.ser.cancel_read()
      self.ser.flush()
      firstAck = self.ser.read(1)
      self.ser.write(serialReceiver.formatCmd(CMD_CONNECT,[0x01]))
      return self.waitForAck(firstAck)

  def disconnect(self):
    self.stopThread = True
    self.ser.cancel_read()
    self.ser.flush()
    self.serialDisconnect()
    

  def toggleRawAcquisition(self, enable):
    print("toggle buffer Acquisition: " + str(enable))
    self.commandActive = True
    #self.ser.cancel_read()
    #self.ser.flush()
    self.ser.write(serialReceiver.formatCmd(CMD_BUFFER,[enable]))
    #return self.waitForAck()
        
  def toggleDecoderAcquisition(self, enable):
    print("toggle decoder Acquisition: " + str(enable))
    self.commandActive = True
    #self.ser.cancel_read()
    #self.ser.flush()
    self.ser.write(serialReceiver.formatCmd(CMD_DECODER,[enable]))
    #return self.waitForAck()

  def printBytes(self, bytearrayPrint):
    print(binascii.hexlify(bytearrayPrint).decode('ascii'))

  def sendBandPassParams(self,filterList,gain):
    self.commandActive = True
    #floatlist = [random.random() for _ in range(5*7)]
    #filterParamBytes = struct.pack('%sf' % len(floatlist), *floatlist)
    filterParamBytes = struct.pack('%sf' % len(filterList), *filterList)
    filterGainBytes = struct.pack('f', gain)
    filterArray = bytearray(filterParamBytes)
    gainArray = bytearray(filterGainBytes)
    padArray = bytearray([CMD_UPLOAD_FILTER_BAND,0x00,0x00])
    filterData = padArray + filterArray + gainArray
    msg = serialReceiver.formatCmd(CMD_UPLOAD_FILTER_BAND,filterData)
    self.printBytes(msg)
    print("sending bandpass")
    #self.ser.cancel_read()
    #self.ser.flush()
    self.ser.write(msg)

  def sendNotchParams(self,filterList,gain):
    self.commandActive = True
    filterParamBytes = struct.pack('%sf' % len(filterList), *filterList)
    filterGainBytes = struct.pack('f', gain)
    print("sendgain")
    print(gain)
    filterArray = bytearray(filterParamBytes)
    gainArray = bytearray(filterGainBytes)
    padArray = bytearray([CMD_UPLOAD_FILTER_NOTCH,0x00,0x00])
    filterData = padArray + filterArray + gainArray
    msg = serialReceiver.formatCmd(CMD_UPLOAD_FILTER_NOTCH,filterData)
    self.printBytes(msg)
    print("sending Notch")
    #self.ser.cancel_read()
    #self.ser.flush()
    self.ser.write(msg)



  def sendImpParams(self):
    self.commandActive = True
    floatlist = [random.random() for _ in range(5*6)]
    print(floatlist)
    filterParamBytes = struct.pack('%sf' % len(floatlist), *floatlist)
    filterGainBytes = struct.pack('f', 3.14)
    filterArray = bytearray(filterParamBytes)
    gainArray = bytearray(filterGainBytes)
    padArray = bytearray([CMD_UPLOAD_FILTER_IMP,0x00,0x00])
    filterData = padArray + filterArray + gainArray
    msg = serialReceiver.formatCmd(CMD_UPLOAD_FILTER_IMP,filterData)
    self.printBytes(msg)
    print("sending Impedance")
    #self.ser.cancel_read()
    self.ser.flush()
    self.ser.write(msg)


  def toggleUserBandpass(self,enable):
    self.commandActive = True
    print("toggle user band: " + str(enable))
    #self.ser.cancel_read()
    #self.ser.flush()
    self.ser.write(serialReceiver.formatCmd(CMD_USER_FILTER_BAND,[enable]))


  def toggleUserNotch(self,enable):
    self.commandActive = True
    print("toggle user notch: " + str(enable))
    #self.ser.cancel_read()
    #self.ser.flush()
    self.ser.write(serialReceiver.formatCmd(CMD_USER_FILTER_NOTCH,[enable]))


  def toggleUserImp(self,enable):
    self.commandActive = True
    print("toggle user imp: " + str(enable))
    #self.ser.cancel_read()
    #self.ser.flush()
    self.ser.write(serialReceiver.formatCmd(CMD_USER_FILTER_IMP,[enable]))


  def setRawAcquisition(self):
    self.commandActive = True
    self.loopRun = 1
    self.ser.write(str.encode("wb"))
    
  def setDecoderAcquisition(self):
    self.commandActive = True
    self.loopRun = 10
    self.ser.write(str.encode("wa"))


class tabdemo(QtGui.QTabWidget):
  
  def __init__(self, parent = None):

    self.PROGRAM_VER = 4.5

    self.after_exit = 0

    self.dataBuffer1 = (0,0)
    self.dataBuffer2 = (0,0)
    self.accelBufferX = (0,0)

    self.writeVal = 1
    self.serialEnabled = False

    self.DOWNSAMPLE_WIND = 1
    self.FFT_WINDOW = 5000
    self.SPECT_WINDOW = 5000
    self.spectBin = 500
    self.SAMPLES = 5000
    self.FS = 500


    self.BGCOLOR = pg.mkColor(220,220,220)
    self.FGCOLOR = pg.mkColor(100,100,100)
    self.plotcolor = QtGui.QColor(76,100,230)
    self.PLTWIDTH = 2

    super(tabdemo, self).__init__(parent)
    
    self.activeTab = 1
    self.activeChannel = 1
    self.counter1 = 0
    self.counter2 = 0
    self.counter3 = 0
    self.counter4 = 0
    self.counter5 = 0
    self.counter = 0
    self.counterAccel = 0
    self.channelone = [0]*5000
    self.channeltwo = [0]*5000
    self.channelthree = [0]*5000
    self.channelfour = [0]*5000
    self.channelfive = [0]*5000
    self.channeldata = [0]*5000
    self.channelAccelX = [0]*1000
    self.channelAccelY = [0]*1000
    self.channelAccelZ = [0]*1000
    self.fftsamples = [0]*5000
    self.bufferSpect = [0]*self.SPECT_WINDOW
    self.spectCounter = 0
    
    self.serialBaud = 115200
    self.serialPort = str('/dev/tty.mindreachBTv4_2-Bluetoo')

    self.username = "nuno"
    self.usernameGame = "nuno"


    self.disableYAutorange = False
    self.yLimitSpinbox_value = 00100.0 #uV 
    self.yLimit_value = self.yLimitSpinbox_value / 1000000
 

    self.stdMultiplier_value = 2.5
    self.stdMultiplierBase_value = 1.0
    self.stateThresholds = 0 
    self.active_file = 0
    self.realthresholds = {}
    
    # -------------------------------
    # RAW DATA GRAPHS
    # -------------------------------
    
    self.limitCheckbox = QtGui.QCheckBox("Disable Y Autorange",self)
    self.limitCheckbox.stateChanged.connect(self.checklimit)

    self.limitLabel1 = QtGui.QLabel("limit peak (uV):")
    self.limitLabel1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)

    self.limitSpinbox = QtGui.QDoubleSpinBox()
    self.limitSpinbox.setMaximum(1000.0)
    self.limitSpinbox.setMinimum(10.0)
    self.limitSpinbox.setAlignment(QtCore.Qt.AlignRight)
    self.limitSpinbox.setMinimumSize(90,20)
    self.limitSpinbox.setMaximumSize(90,20)
    self.limitSpinbox.setValue(self.yLimitSpinbox_value)


    pg.setConfigOption('background', self.BGCOLOR)
    pg.setConfigOption('foreground', self.FGCOLOR)
    pg.setConfigOptions(useOpenGL=True)

   
    pen = pg.mkPen(color = self.plotcolor, width = 3)

    self.graph1 = pg.PlotWidget()
    self.rawData1 = pg.PlotCurveItem(pen=pen)
    self.graph1.addItem(self.rawData1)
    self.graph2 = pg.PlotWidget()
    self.rawData2 = pg.PlotCurveItem(pen=pen)
    self.graph2.addItem(self.rawData2)
    self.graph3 = pg.PlotWidget()
    self.rawData3 = pg.PlotCurveItem(pen=pen)
    self.graph3.addItem(self.rawData3)
    self.graph4 = pg.PlotWidget()
    self.rawData4 = pg.PlotCurveItem(pen=pen)
    self.graph4.addItem(self.rawData4)
    self.graph5 = pg.PlotWidget()
    self.rawData5 = pg.PlotCurveItem(pen=pen)
    self.graph5.addItem(self.rawData5)

    self.graphAccel_x = pg.PlotWidget()
    self.accelDataX = pg.PlotCurveItem()
    self.graphAccel_x.addItem(self.accelDataX)
    self.graphAccel_y = pg.PlotWidget()
    self.accelDataY = pg.PlotCurveItem()
    self.graphAccel_y.addItem(self.accelDataY)
    self.graphAccel_z = pg.PlotWidget()
    self.accelDataZ = pg.PlotCurveItem()
    self.graphAccel_z.addItem(self.accelDataZ)
    #axis_1x = self.graph1.getAxis('left')
    
    self.graph1.setLabel('left', "Amplitude", "V")
    self.graph1.setLabel('bottom', "Number of points")
    self.graph1.setTitle("Channel 1")
    self.graph2.setLabel('left', "Amplitude", "V")
    self.graph2.setLabel('bottom', "Number of points")
    self.graph2.setTitle("Channel 2")
    self.graph3.setLabel('left', "Amplitude", "V")
    self.graph3.setLabel('bottom', "Number of points")
    self.graph3.setTitle("Channel 3")
    self.graph4.setLabel('left', "Amplitude", "V")
    self.graph4.setLabel('bottom', "Number of points")
    self.graph4.setTitle("Channel 4")
    self.graph5.setLabel('left', "Amplitude", "V")
    self.graph5.setLabel('bottom', "Number of points")
    self.graph5.setTitle("Channel 5")

    self.graphAccel_x.setLabel('left', "Acceleration", "ms^-2")
    self.graphAccel_x.setLabel('bottom', "Number of points")
    self.graphAccel_x.setTitle("Acceleration X")

    self.graphAccel_y.setLabel('left', "Acceleration", "ms^-2")
    self.graphAccel_y.setLabel('bottom', "Number of points")
    self.graphAccel_y.setTitle("Acceleration Y")

    self.graphAccel_z.setLabel('left', "Acceleration", "ms^-2")
    self.graphAccel_z.setLabel('bottom', "Number of points")
    self.graphAccel_z.setTitle("Acceleration Z")
    
    self.graph1.setMouseEnabled(x=False, y=True)
    self.graph2.setMouseEnabled(x=False, y=True)
    self.graph3.setMouseEnabled(x=False, y=True)
    self.graph4.setMouseEnabled(x=False, y=True)
    self.graph5.setMouseEnabled(x=False, y=True)

    # -------------------------------
    # SPECTROGRAM GRAPHS
    # -------------------------------
    
    self.ddMenu = QtGui.QComboBox()
    
    self.graph = pg.PlotWidget()
    self.graphData = pg.PlotCurveItem(pen = pen)
    self.graph.addItem(self.graphData)
    self.graph.setLabel('left', "Amplitude", "V")
    self.graph.setLabel('bottom', "Number of points")
    self.graph.setMouseEnabled(x=False, y=True)
    self.fft = pg.PlotWidget()
    self.fftData = pg.PlotCurveItem(pen = pen)
    self.fft.addItem(self.fftData)
    self.fft.setLabel('left', "Amplitude", "V")
    self.fft.setLabel('bottom', "Frequency (Hz)")
    bx = self.fft.getAxis('bottom')
    bx.setScale(0.1)
    
    self.spectrogramImage = pg.PlotWidget()
    self.spectrogram = pg.ImageItem()
    self.spectrogramImage.addItem(self.spectrogram)
    self.spectrogramImage.setLabel('left', 'Frequency', units='Hz')
    self.spectrogramImage.setLabel('bottom', 'Time', units='s')
    
    self.tabConnect = QtGui.QWidget()	#connect
    self.tabEEG = QtGui.QWidget()
    self.tabSpect = QtGui.QWidget()
    self.tabGame = QtGui.QWidget()
    self.tabDist = QtGui.QWidget()
    self.tabAccel = QtGui.QWidget() #accel
    self.connectTabIndex = self.addTab(self.tabConnect,"Connect") + 1
    self.eegTabIndex = self.addTab(self.tabEEG,"EEG Data") + 1
    self.spectTabIndex = self.addTab(self.tabSpect,"Spectogram") + 1 
    self.accelTabIndex = self.addTab(self.tabAccel,"Accel Data") + 1
    self.distTabIndex = self.addTab(self.tabDist,"Distributions") + 1
    self.gameTabIndex = self.addTab(self.tabGame,"Game") + 1
    print("connectIndex",self.connectTabIndex)
    print("eegIndex",self.eegTabIndex)


    # -------------------------------
    # Distribution GRAPHS
    # -------------------------------

    self.positionFileMenu = QtGui.QComboBox()
    
    self.dist_pg = pg.PlotWidget()
    self.plot_pg = pg.PlotWidget()

    # vals = np.hstack([np.random.normal(size=500), np.random.normal(size=260, loc=4)])
    # y,x = np.histogram(vals, bins=np.linspace(-3, 8, 40))
    # self.dist = self.dist_pg.plot(x,y,stepMode=True, fillLevel=0, brush=(0,0,255,150))
    #self.plot = self.plot_pg.plot(vals)

    # mean_pos = np.mean(x)
    # std_pos = np.std(x)
    # vert_line = pg.InfiniteLine(mean_pos, angle = 90)
    # self.dist_pg.addItem(vert_line)

    #self.dist.addItem(self.distData)

    self.plot_pg.setLabel('left', "Counts", "")
    self.plot_pg.setLabel('bottom', "time(s)")
    self.dist_pg.setLabel('bottom', "Position")


    self.showThresholdsCheckbox = QtGui.QCheckBox("Show current thresholds",self)
    self.showThresholdsCheckbox.stateChanged.connect(self.toggleShowThresholds)


    self.stdMultiplierSpinbox = QtGui.QDoubleSpinBox()
    self.stdMultiplierSpinbox.setAlignment(QtCore.Qt.AlignRight)
    self.stdMultiplierSpinbox.setMinimumSize(90,20)
    self.stdMultiplierSpinbox.setMaximumSize(90,20)
    self.stdMultiplierSpinbox.setValue(self.stdMultiplier_value)
    self.stdMultiplierSpinbox.setSingleStep(0.1)

    self.stdMultiplierBaseSpinbox = QtGui.QDoubleSpinBox()
    self.stdMultiplierBaseSpinbox.setAlignment(QtCore.Qt.AlignRight)
    self.stdMultiplierBaseSpinbox.setMinimumSize(90,20)
    self.stdMultiplierBaseSpinbox.setMaximumSize(90,20)
    self.stdMultiplierBaseSpinbox.setValue(self.stdMultiplierBase_value)
    self.stdMultiplierBaseSpinbox.setSingleStep(0.1)

    
    self.connectTabUI()
    self.graphTabUI()
    self.spectTabUI()
    self.distTabUI()
    self.gameTabUI()
    self.accelTabUI()
    self.connectTabs()
    
    self.setWindowTitle("VisionVolt - Mindreach EEG Headset GUI, version: " + str(self.PROGRAM_VER))
  
  def setAutoRange(self,graph, enable):
    axY = graph.getAxis('left')
    if(enable == True):
      graph.enableAutoRange(axY,True,None, 'y')
    else:
      graph.enableAutoRange(axY,False,None, 'y')
  
  def setGraphRange(self,graph,rangeMax,rangeMin):
    graph.setYRange(rangeMax,rangeMin, padding=0)

  def changeLimitValue(self):
    
    self.yLimitSpinbox_value = self.limitSpinbox.value()
    self.yLimit_value = self.yLimitSpinbox_value / 1000000
    print("current value:"+str(self.yLimit_value))
    if(self.disableYAutorange):
      self.setGraphRange(self.graph1, 0-self.yLimit_value, self.yLimit_value) 
      self.setGraphRange(self.graph2, 0-self.yLimit_value, self.yLimit_value)
      self.setGraphRange(self.graph3, 0-self.yLimit_value, self.yLimit_value)
      self.setGraphRange(self.graph4, 0-self.yLimit_value, self.yLimit_value)
      self.setGraphRange(self.graph5, 0-self.yLimit_value, self.yLimit_value)

  def changeStdMultiplier(self):
    self.stdMultiplier_value = self.stdMultiplierSpinbox.value()
    self.changedPositionFile()
    self.showThresholds()

  def changeStdBaseMultiplier(self):
    self.stdMultiplierBase_value = self.stdMultiplierBaseSpinbox.value()
    self.changedPositionFile()
    self.showThresholds()

  def readCSVFilters(self):
    global userFilterBand
    global userBandGain
    global userFilterNotch
    global userNotchGain
    with open('filters.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        #rowS = []
        for row in csv_reader:
            #if any(x.strip() for x in row):
            #  rowS.append(row)
            rowS = row
            if line_count == 0:
                print(f'Column names are {", ".join(rowS)}')
                line_count += 1
            else:
              #iterRow = iter(row)
              #next(iterRow)
              if (int(rowS[0],16) == CMD_UPLOAD_FILTER_BAND):
                print("bandpass")
                #userBandGain = float(next(iterRow))
                userBandGain = float(rowS[1])
                for i in range(2, 2+(5*7)):
                  userFilterBand.append(float(rowS[i]))
                #for val in iterRow:
                #  userFilterBand.append(float(val))
                print(userFilterBand)

              elif (int(rowS[0],16) == CMD_UPLOAD_FILTER_NOTCH):
                print("notch")
                #userNotchGain = float(next(iterRow))
                userNotchGain = float(rowS[1])
                print(userNotchGain)
                for i in range(2, 2+(5*1)):
                  userFilterNotch.append(float(rowS[i]))
                #for val in iterRow:
                #  userFilterNotch.append(float(val))
                print(userFilterNotch)
              elif (int(rowS[0],16) == CMD_UPLOAD_FILTER_IMP):
                print("impedance")
              line_count += 1
        print(f'Processed {line_count} lines.')

    
  def checklimit(self, state):
    if state == QtCore.Qt.Checked:
      print('disable autorange')
      self.disableYAutorange = True
      self.setAutoRange(self.graph1,False)
      self.setAutoRange(self.graph2,False)
      self.setAutoRange(self.graph3,False)
      self.setAutoRange(self.graph4,False)
      self.setAutoRange(self.graph5,False)
      self.setGraphRange(self.graph1, 0-self.yLimit_value, self.yLimit_value)
      self.setGraphRange(self.graph2, 0-self.yLimit_value, self.yLimit_value)
      self.setGraphRange(self.graph3, 0-self.yLimit_value, self.yLimit_value)
      self.setGraphRange(self.graph4, 0-self.yLimit_value, self.yLimit_value)
      self.setGraphRange(self.graph5, 0-self.yLimit_value, self.yLimit_value)
    else:
      print('enable autorange')
      self.disableYAutorange = False
      self.setAutoRange(self.graph1,True)
      self.setAutoRange(self.graph2,True)
      self.setAutoRange(self.graph3,True)
      self.setAutoRange(self.graph4,True)
      self.setAutoRange(self.graph5,True)

  def changeDDMenu(self):
    self.activeChannel = self.ddMenu.currentIndex() + 1
    self.counter = 0
    self.channeldata = [0]*5000
    self.fftsamples = [0]*self.FFT_WINDOW
    self.fftData.setData(self.channeldata)

  def toggleShowThresholds(self, state):
    if state == QtCore.Qt.Checked:
      self.stateThresholds = 1
      self.showThresholds()
      
    elif state != QtCore.Qt.Checked:
      self.stateThresholds = 0
      try:
        self.dist_pg.removeItem(self.mean_vert_current)
        self.dist_pg.removeItem(self.target_up_current)
        self.dist_pg.removeItem(self.target_down_current)
        self.dist_pg.removeItem(self.base_up_current)
        self.dist_pg.removeItem(self.base_down_current)
      except:
        pass


  def showThresholds(self):
    try:
      self.dist_pg.removeItem(self.mean_vert_current)
      self.dist_pg.removeItem(self.target_up_current)
      self.dist_pg.removeItem(self.target_down_current)
      self.dist_pg.removeItem(self.base_up_current)
      self.dist_pg.removeItem(self.base_down_current)
    except:
      pass

    if self.stateThresholds:
      g = open( self.pathUser +'thresholds.txt', 'r')
      thresholds_curr = eval(g.read())
      g.close()

      mean_curr = (thresholds_curr['upReward'] + thresholds_curr['downReward'])/2

      self.mean_vert_current = pg.InfiniteLine(mean_curr, angle = 90,
                                  pen = pg.mkPen(color=(10, 200, 0), width=1, style=QtCore.Qt.DotLine))
      self.target_up_current = pg.InfiniteLine(thresholds_curr['upReward'], angle = 90,
                                  pen = pg.mkPen(color=(10, 200, 0), width=2, style=QtCore.Qt.SolidLine))
      self.target_down_current = pg.InfiniteLine(thresholds_curr['downReward'], angle = 90,
                                  pen = pg.mkPen(color=(10, 200, 0), width=2, style=QtCore.Qt.SolidLine))
      self.base_up_current = pg.InfiniteLine(thresholds_curr['upBase'], angle = 90,
                                  pen = pg.mkPen(color=(10, 200, 0), width=2, style=QtCore.Qt.DashLine))
      self.base_down_current = pg.InfiniteLine(thresholds_curr['downBase'], angle = 90,
                                  pen = pg.mkPen(color=(10, 200, 0), width=2, style=QtCore.Qt.DashLine))


      self.dist_pg.addItem(self.mean_vert_current)
      self.dist_pg.addItem(self.target_up_current)
      self.dist_pg.addItem(self.target_down_current)
      self.dist_pg.addItem(self.base_up_current)
      self.dist_pg.addItem(self.base_down_current)
      

  def changedPositionFile(self):
    self.activeFile = self.positionFileMenu.currentIndex() + 1
    try:
      self.active_file = self.all_pos_files[self.activeFile-1]
    except:
      self.active_file = "No files to show"
      print('no file to show')
    if self.active_file != "No files to show":
      try:
        with open(self.pathUser + self.active_file, 'rb') as filehandle:
            # read the data as binary data stream
            position_array = pickle.load(filehandle)
        y,x = np.histogram(position_array, bins=int(len(position_array)/10))
        self.dist_pg.clear()
        self.dist_pg.plot(x,y,stepMode=True, fillLevel=0, brush=(0,0,255,150))

        mean_pos = np.mean(x)
        std_pos = np.std(x)

        mean_vert = pg.InfiniteLine(mean_pos, angle = 90,
                                    pen = pg.mkPen(color=(200, 0, 0), width=1, style=QtCore.Qt.DotLine))
        
        self.target_up = mean_pos+self.stdMultiplier_value*std_pos
        self.target_down = mean_pos-self.stdMultiplier_value*std_pos
        self.base_up = mean_pos+(self.stdMultiplierBase_value)*std_pos
        self.base_down = mean_pos-(self.stdMultiplierBase_value)*std_pos
        self.range_up = mean_pos-(self.stdMultiplier_value+0.3)*std_pos
        self.range_down = mean_pos+(self.stdMultiplier_value+0.3)*std_pos

        self.realthresholds['upReward'] = self.target_up
        self.realthresholds['downReward'] = self.target_down
        self.realthresholds['upBase'] = self.base_up
        self.realthresholds['downBase'] = self.base_down
        self.realthresholds['upRange'] = self.range_up
        self.realthresholds['downRange'] = self.range_down

        mean_vert = pg.InfiniteLine(mean_pos, angle = 90,
                                    pen = pg.mkPen(color=(200, 0, 0), width=1, style=QtCore.Qt.DotLine))
        target_up = pg.InfiniteLine(self.target_up, angle = 90,
                                    pen = pg.mkPen(color=(200, 0, 0), width=2, style=QtCore.Qt.SolidLine))
        target_down = pg.InfiniteLine(self.target_down, angle = 90,
                                    pen = pg.mkPen(color=(200, 0, 0), width=2, style=QtCore.Qt.SolidLine))
        base_up = pg.InfiniteLine(self.base_up, angle = 90,
                                    pen = pg.mkPen(color=(200, 0, 0), width=2, style=QtCore.Qt.DashLine))
        base_down = pg.InfiniteLine(self.base_down, angle = 90,
                                    pen = pg.mkPen(color=(200, 0, 0), width=2, style=QtCore.Qt.DashLine))
        self.dist_pg.addItem(mean_vert)
        self.dist_pg.addItem(target_up)
        self.dist_pg.addItem(target_down)
        self.dist_pg.addItem(base_up)
        self.dist_pg.addItem(base_down)

        self.showThresholds()
      except:
        self.dist_pg.clear()


  
  def tabChanged(self):
    lastActiveTab = self.activeTab
    print("lastActive:", lastActiveTab)
    self.activeTab = self.currentIndex() + 1
    print("Active:", self.activeTab)
    if(self.activeTab == self.eegTabIndex):
      print("tab eeg")
      self.counter1 = 0
      self.counter2 = 0
      self.counter3 = 0
      self.counter4 = 0
      self.counter5 = 0
      self.channelone = [0]*5000
      self.channeltwo = [0]*5000
      self.channelthree = [0]*5000
      self.channelfour = [0]*5000
      self.channelfive = [0]*5000
      if(lastActiveTab == self.gameTabIndex):
        try:
          self.thread.toggleRawAcquisition(0x01)
        except:
          print("No Serial connection")

    elif(self.activeTab == self.spectTabIndex):
      print("tab spect")
      self.counter = 0
      self.channeldata = [0]*5000
      self.fftsamples = [0]*self.FFT_WINDOW
      self.fftData.setData(self.channeldata)
      if(lastActiveTab == self.gameTabIndex):
        try:
          self.thread.toggleRawAcquisition(0x01)
        except:
          print("No Serial connection")

    elif(self.activeTab == self.gameTabIndex):
      print('Game Tab')
      try:
          self.thread.toggleDecoderAcquisition(0x01)
      except:
        print("No Serial connection")
     

    elif(self.activeTab == self.accelTabIndex):
      print("tab tabAccel")
      self.channelAccelX = [0]*1000
      self.channelAccelY = [0]*1000
      self.channelAccelZ = [0]*1000
      self.counterAccel = 0
      if(lastActiveTab == self.gameTabIndex):
        try:
          self.thread.toggleRawAcquisition(0x01)
        except:
          print("No Serial connection")


    elif(self.activeTab == self.distTabIndex):
      print("tab histogram")

    else:
      self.counter = 0

    
  def connectTabs(self):
    self.currentChanged.connect(self.tabChanged)
    print('here')
    self.portedit.editingFinished.connect(self.port_change)
    self.baudedit.editingFinished.connect(self.baud_change)
    self.connectbutton.clicked.connect(self.start_serial)
    self.disconnectbutton.clicked.connect(self.stop_serial)

    #self.testButton.clicked.connect(self.testFunction)
    self.rawAqButton.clicked.connect(self.toggleRawFunction)
    self.decoderAqButton.clicked.connect(self.toggleDecoderFunction)
    self.uploadBandpassButton.clicked.connect(self.uploadBandpassFunction)
    self.uploadNotchButton.clicked.connect(self.uploadNotchFunction)
    self.enableUserBandpassButton.clicked.connect(self.enableUserBandpassFunction)
    self.enableUserNotchButton.clicked.connect(self.enableUserNotchFunction)
    

  def enableUserBandpassFunction(self):
    if self.thread.isRunning():
      self.thread.toggleUserBandpass(0x01)

  def enableUserNotchFunction(self):
    if self.thread.isRunning():
      self.thread.toggleUserNotch(0x01)

  def uploadBandpassFunction(self):
    global userFilterBand
    global userBandGain
    self.readCSVFilters()
    if self.thread.isRunning():
      self.thread.sendBandPassParams(userFilterBand, userBandGain)
      self.enableUserBandpassButton.setEnabled(True)
    

  def uploadNotchFunction(self):
    global userFilterNotch
    global userNotchGain
    self.readCSVFilters()
    if self.thread.isRunning():
      self.thread.sendNotchParams(userFilterNotch, userNotchGain)
      self.enableUserNotchButton.setEnabled(True)

  def toggleRawFunction(self):
    if self.thread.isRunning():
      self.thread.toggleRawAcquisition(0x01)

  def toggleDecoderFunction(self):
    if self.thread.isRunning():
      self.thread.toggleDecoderAcquisition(0x01)

  def testFunction(self):
    global userFilterBand
    self.readCSVFilters()
    if self.thread.isRunning():
      self.thread.sendBandPassParams(userFilterBand)

  def updateGraphs(self,channel, buffer, dataBuffer1, dataBuffer2, accelBufferX):

    if(self.activeTab == self.eegTabIndex): #raw Data
      if(channel == 1):
        for i in range(0,125):
          if(buffer == 1):
            sample = dataBuffer2[i]/10000
          else:
            sample = dataBuffer1[i]/10000
          self.channelone[self.counter1] = sample
          self.counter1 += 1
          if(self.counter1 == 5000):
            #print(self.channelone)
            self.counter1 = 0
        self.rawData1.setData(self.channelone,pen=self.plotcolor)
      elif(channel == 2):
        for i in range(0,125):
          if(buffer == 1):
            sample = dataBuffer2[i]/10000
          else:
            sample = dataBuffer1[i]/10000
          self.channeltwo[self.counter2] = sample
          self.counter2 += 1
          if(self.counter2 == 5000):
            self.counter2 = 0
        self.rawData2.setData(self.channeltwo,pen=self.plotcolor)
      elif(channel == 3):
        for i in range(0,125):
          if(buffer == 1):
            sample = dataBuffer2[i]/10000
          else:
            sample = dataBuffer1[i]/10000
          self.channelthree[self.counter3] = sample
          self.counter3 += 1
          if(self.counter3 == 5000):
            self.counter3 = 0
        self.rawData3.setData(self.channelthree,pen=self.plotcolor)
      elif(channel == 4):
        for i in range(0,125):
          if(buffer == 1):
            sample = dataBuffer2[i]/10000
          else:
            sample = dataBuffer1[i]/10000
          self.channelfour[self.counter4] = sample
          self.counter4 += 1
          if(self.counter4 == 5000):
            self.counter4 = 0
        self.rawData4.setData(self.channelfour,pen=self.plotcolor)
      elif(channel == 5):
        for i in range(0,125):
          if(buffer == 1):
            sample = dataBuffer2[i]/10000
          else:
            sample = dataBuffer1[i]/10000
          self.channelfive[self.counter5] = sample
          self.counter5 += 1
          if(self.counter5 == 5000):
            self.counter5 = 0
        self.rawData5.setData(self.channelfive,pen=self.plotcolor)
        
    elif(self.activeTab == self.spectTabIndex): #spectogram
      if(channel == self.activeChannel):
        for i in range(0,125):
          if(buffer == 1):
            sample = dataBuffer2[i]/10000
          else:
            sample = dataBuffer1[i]/10000
          self.channeldata[self.counter] = sample
          self.counter += 1
          if(self.counter % self.spectBin == 0 and self.counter != 0):
            self.spectCounter += 1
            self.bufferSpect = np.roll(self.bufferSpect, -self.spectBin, 0)
            self.bufferSpect[-self.spectBin:] = self.channeldata[self.counter-self.spectBin:self.counter]
            ft = np.fft.rfft(self.channeldata,self.FFT_WINDOW)
            f2, Pxx_den2 = signal.welch(self.channeldata, self.FS*10, 'flattop', 1024, scaling='spectrum')
            fftsamples = np.abs(ft[:int(self.FFT_WINDOW/2)])
            fftsamples = fftsamples*10
            fftsamples = fftsamples[::self.DOWNSAMPLE_WIND]
            self.fftData.setData(f2,Pxx_den2)
            self.img_array = np.roll(self.img_array, -1, 0)
            testArray = smooth(fftsamples)
            self.img_array[-1:] = testArray
            self.spectrogram.setImage(self.img_array, autoLevels=False)
          if(self.counter == self.FFT_WINDOW):
            self.counter = 0
        try:
          chn_data_logged = [10*math.log10(y) for y in self.channeldata]
          self.graphData.setData(chn_data_logged)
        except:
          self.graphData.setData(self.channeldata)
    elif(self.activeTab == self.accelTabIndex): #accel
      if(channel == 7):
        self.channelAccelX[self.counterAccel] = accelBufferX[0]
        self.channelAccelY[self.counterAccel] = accelBufferX[1]
        self.channelAccelZ[self.counterAccel] = accelBufferX[2]
        self.counterAccel += 1
        if(self.counterAccel == 1000):
          self.counterAccel = 0
        self.accelDataX.setData(self.channelAccelX,pen= self.plotcolor)
        self.accelDataY.setData(self.channelAccelY,pen= self.plotcolor)
        self.accelDataZ.setData(self.channelAccelZ,pen= self.plotcolor)

    else: # game
      channel = self.activeChannel

  def accelTabUI(self):
    layoutAccel = QtGui.QVBoxLayout()
    layoutAccel.addWidget(self.graphAccel_x)
    layoutAccel.addWidget(self.graphAccel_y)
    layoutAccel.addWidget(self.graphAccel_z)

    self.tabAccel.setLayout(layoutAccel)

  def graphTabUI(self):
    layout = QtGui.QVBoxLayout()
    configLayout = QtGui.QHBoxLayout()
    configLayout.setSpacing(0)
    configLayout.addWidget(self.limitCheckbox)
    configLayout.addWidget(self.limitLabel1)
    configLayout.addWidget(self.limitSpinbox)
    layout.addLayout(configLayout)
    layout.addWidget(self.graph1)
    layout.addWidget(self.graph2)
    layout.addWidget(self.graph3)
    layout.addWidget(self.graph4)
    layout.addWidget(self.graph5)
    
    self.tabEEG.setLayout(layout)
    self.limitSpinbox.valueChanged.connect(self.changeLimitValue)

  def spectTabUI(self):
    layout = QtGui.QGridLayout()
    
    self.ddMenu.addItem("Channel 1")
    self.ddMenu.addItem("Channel 2")
    self.ddMenu.addItem("Channel 3")
    self.ddMenu.addItem("Channel 4")
    self.ddMenu.addItem("Channel 5")
    self.ddMenu.currentIndexChanged.connect(self.changeDDMenu)
    
    # ------------------------
    # SPECTROGRAM ITEMS
    # ------------------------
    
    self.img_array = np.zeros((10, int(2500/self.DOWNSAMPLE_WIND) + 10))
    
    pos = np.array([0., 1.])
    color = np.array([[255,255,255,255],[0,0,0,255]], dtype=np.ubyte)
    cmap = pg.ColorMap(pos,color)
    lut = cmap.getLookupTable(0.0,1.0,256)
    
    self.spectrogram.setLookupTable(lut)
    self.spectrogram.setLevels([0,0.07])
    
    freq = np.arange((self.SAMPLES/2)+1/float(self.SAMPLES)/self.FS)
    #yscale = 1.0/(self.img_array.shape[1]/freq[-1])
    yscale = 0.1
    self.spectrogram.scale((1./self.FS)*self.SAMPLES,yscale)
    
    layout.addWidget(self.ddMenu,0,0,1,2)
    layout.addWidget(self.graph,1,0,1,2)
    layout.addWidget(self.fft,2,0,1,1)
    layout.addWidget(self.spectrogramImage,2,1,1,1)
    
    #self.setTabText(1,"Spectrogram")
    self.tabSpect.setLayout(layout)

  def distTabUI(self):
    layout = QtGui.QGridLayout()

    self.pathData = '/Users/nunoloureiro/mindreach/software_eeg/mindreach_demo/data/'

    self.userText = QtGui.QLabel()
    self.userText.setText("Username:")
    self.userEdit = QtGui.QLineEdit()
    self.userEdit.setText(str(self.username))
    self.StdMultiplierText = QtGui.QLabel()
    self.StdMultiplierText.setText("Set std Multiplier:")
    self.StdMultiplierBaseText = QtGui.QLabel()
    self.StdMultiplierBaseText.setText("Set stdBase Multiplier:")

    
    self.fileText = QtGui.QLabel()
    self.fileText.setText("Choose file to load:")

    self.pathUser = self.pathData + 'subj_' + self.username + "/"

    if os.path.isdir(self.pathUser):
      self.all_pos_files = [f for f in os.listdir(self.pathUser) if f.startswith('positions')]
      self.all_pos_files.sort(key=lambda f: int(re.sub('\D', '', f)))
      for file in self.all_pos_files:
        self.positionFileMenu.addItem(file)
    else:
      self.positionFileMenu.addItem("No files to show")

    self.setNewThresholds = QtGui.QPushButton("Set thresholds as current")

    layout.addWidget(self.userText,0,0,1,1)
    layout.addWidget(self.userEdit,0,1,1,3)
    layout.addWidget(self.positionFileMenu,1,0,1,4)
    layout.addWidget(self.dist_pg,2,0,1,4)
    layout.addWidget(self.StdMultiplierText,6,0,1,1)
    layout.addWidget(self.stdMultiplierSpinbox,6,1,1,1)
    layout.addWidget(self.StdMultiplierBaseText,7,0,1,1)
    layout.addWidget(self.stdMultiplierBaseSpinbox,7,1,1,1)
    layout.addWidget(self.setNewThresholds,6,3,1,1)
    layout.addWidget(self.showThresholdsCheckbox,6,2,1,1)
    self.stdMultiplierSpinbox.valueChanged.connect(self.changeStdMultiplier)
    self.stdMultiplierBaseSpinbox.valueChanged.connect(self.changeStdBaseMultiplier)
    

    self.changedPositionFile()

    self.tabDist.setLayout(layout)
    self.userEdit.textEdited.connect(self.user_change)

    self.positionFileMenu.currentIndexChanged.connect(self.changedPositionFile)
    self.setNewThresholds.clicked.connect(self.setThresholdsInFile)

  def launchGame(self):
    try:
      self.thread.terminate()
      self.app_after_exit = 1
      self.close()

        
    except:
      #self.thread.setDecoderAcquisition()
      print("No Serial connection")

  def toggleAcqEegData(self, state):
    if state == QtCore.Qt.Checked:
      self.stateThresholds = 1
      self.showThresholds()
      
    elif state != QtCore.Qt.Checked:
      self.stateThresholds = 0
      try:
        self.dist_pg.removeItem(self.mean_vert_current)
        self.dist_pg.removeItem(self.target_up_current)
        self.dist_pg.removeItem(self.target_down_current)
        self.dist_pg.removeItem(self.base_up_current)
        self.dist_pg.removeItem(self.base_down_current)
      except:
        pass


  def gameTabUI(self):
    layout = QtGui.QVBoxLayout()

    self.userText = QtGui.QLabel()
    self.userText.setText("Username:")
    self.userEditGame = QtGui.QLineEdit()
    self.userEditGame.setText(str(self.username))

    self.launchGameBtn = QtGui.QPushButton("Launch Game")

    layout.addWidget(self.userText)
    layout.addWidget(self.userEditGame)
    layout.addWidget(self.launchGameBtn)

    layout.addSpacing(800)

    self.tabGame.setLayout(layout)
    self.userEditGame.textEdited.connect(self.user_change_game)
    self.launchGameBtn.clicked.connect(self.launchGame)

    
  def connectTabUI(self):
    layout = QtGui.QVBoxLayout()

    
    self.baudtext = QtGui.QLabel()
    self.baudtext.setText("Baudrate")
    self.baudedit = QtGui.QLineEdit()
    self.baudedit.setText(str(self.serialBaud))
    self.baudedit.setValidator(QtGui.QIntValidator())
    
    self.porttext = QtGui.QLabel()
    self.porttext.setText("COM Port")
    self.portedit = QtGui.QLineEdit()
    self.portedit.setText(self.serialPort)
    self.connectbutton = QtGui.QPushButton("Connect")
    self.disconnectbutton = QtGui.QPushButton("Disconnect")
    #self.testButton = QtGui.QPushButton("test")
    self.rawAqButton = QtGui.QPushButton("raw Acquisition")
    self.decoderAqButton = QtGui.QPushButton("decoder Acquisition")
    self.uploadBandpassButton = QtGui.QPushButton("Upload Bandpass")
    self.enableUserBandpassButton = QtGui.QPushButton("Enable User Bandpass")
    self.uploadNotchButton = QtGui.QPushButton("Upload Notch")
    self.enableUserNotchButton = QtGui.QPushButton("Enable User Notch")

    self.rawAqButton.setEnabled(False)
    self.decoderAqButton.setEnabled(False)
    self.enableUserBandpassButton.setEnabled(False)
    self.enableUserNotchButton.setEnabled(False)
    self.disconnectbutton.setEnabled(False)
    self.uploadBandpassButton.setEnabled(False)
    self.uploadNotchButton.setEnabled(False)
    layout.addWidget(self.baudtext)
    layout.addWidget(self.baudedit)
    layout.addWidget(self.porttext)
    layout.addWidget(self.portedit)
    layout.addWidget(self.connectbutton)
    layout.addWidget(self.disconnectbutton)
    #layout.addWidget(self.testButton)
    layout.addWidget(self.rawAqButton)
    layout.addWidget(self.decoderAqButton)

    layout.addWidget(self.uploadBandpassButton)    
    layout.addWidget(self.enableUserBandpassButton)

    layout.addWidget(self.uploadNotchButton)
    layout.addWidget(self.enableUserNotchButton)
    layout.addSpacing(800)
    self.tabConnect.setLayout(layout)
    
  def onSerialConnect(self,enabled):
    
    self.rawAqButton.setEnabled(enabled)
    self.decoderAqButton.setEnabled(enabled)
    self.disconnectbutton.setEnabled(enabled)
    self.uploadBandpassButton.setEnabled(enabled)
    self.uploadNotchButton.setEnabled(enabled)
    self.serialEnabled = enabled
    #if not enabled:
      #self.setCurrentIndex(self.eegTabIndex-1)
      #self.serialEnabled = True
    
  def port_change(self):
    self.serialPort = self.portedit.text()
  
  def baud_change(self):
    self.serialBaud = int(self.baudedit.text())

  def user_change(self):
    self.username = self.userEdit.text()

    self.positionFileMenu.clear()

    self.pathUser = self.pathData + 'subj_' + self.username + "/"

    if os.path.isdir(self.pathUser):
      self.all_pos_files = [f for f in os.listdir(self.pathUser) if f.startswith('positions')]
      self.all_pos_files.sort(key=lambda f: int(re.sub('\D', '', f)))
      for file in self.all_pos_files:
        self.positionFileMenu.addItem(file)
    else:
      self.positionFileMenu.addItem("No files to show")

  def user_change_game(self):
    self.usernameGame = self.userEditGame.text()

  def setThresholdsInFile(self):

    self.pathUser = self.pathData + 'subj_' + self.username + "/"
    print(self.pathUser)
    if self.realthresholds != {}:
      g = open( self.pathUser +'thresholds.txt', 'r')
      thresholds_old = eval(g.read())
      # print(thresholds_old)
      g.close()


      f = open(self.pathUser + 'thresholds_old.txt', 'w')
      f.write(str(thresholds_old))
      f.close()
      g = open( self.pathUser +'thresholds.txt', 'w')
      g.write(str(self.realthresholds))
      g.close()
      self.showThresholds()
    else:
      print('Cannot write file because there are no thresholds')

  def start_serial(self):
    serial = serialReceiver(self.serialBaud, str(self.serialPort), self.serialEnabled, self.dataBuffer1,
     self.dataBuffer2, self.writeVal, self.accelBufferX)
    serial.newSample.connect(self.updateGraphs)
    serial.serialConn.connect(self.onSerialConnect)
    self.thread = serial
    serial.start()
    self.thread.serialConnect()
    

  def stop_serial(self):
    self.thread.disconnect()
    self.disconnectbutton.setEnabled(False)
    #serial.newSample.connect(self.updateGraphs)
    #serial.serialConn.connect(self.onSerialConnect)
    #serial.start()

  def keyPressEvent(self, event):
    # Did the user press the Escape key?
    if event.key() == QtCore.Qt.Key_Escape: # QtCore.Qt.Key_Escape is a value that equates to what the operating system passes to python from the keyboard when the escape key is pressed.
      # Yes: Close the window
      self.app_after_exit = 0
      self.close()
    
def main():
  app = QtGui.QApplication(sys.argv)
  ex = tabdemo()
  ex.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
