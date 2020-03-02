##############################################################
# Use python 2.7
##############################################################

import sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import math

from scipy import signal


import struct
import serial

# self.PROGRAM_VER = 4.0

# s = struct.Struct('f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f')
# s2 = struct.Struct('f')

# sAccel = struct.Struct('f f f')

# dataBuffer1 = 0
# dataBuffer2 = 0

# #dataBufferChannel1 = 0
# #dataBufferChannel2 = 0
# #dataBufferChannel3 = 0
# #dataBufferChannel4 = 0
# #dataBufferChannel5 = 0

# accelBufferX = 0
# accelBufferY = 0
# accelBufferZ = 0

# writeVal = 1
# serialEnabled = False

# DOWNSAMPLE_WIND = 1
# self.FFT_WINDOW = 5000
# SPECT_WINDOW = 5000
# spectBin = 500
# SAMPLES = 5000
# FS = 500


# BGCOLOR = pg.mkColor(220,220,220)
# FGCOLOR = pg.mkColor(100,100,100)
# plotcolor = QtGui.QColor(76,100,230)
# PLTWIDTH = 2




import numpy

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

class serialReceiver(QtCore.QThread):
  
  
  newSample = QtCore.pyqtSignal(int,int, tuple, tuple)
  serialConn = QtCore.pyqtSignal(bool)
  
  def __init__(self, baud, port, serialEnabled, dataBuffer1, dataBuffer2, writeVal,
              accelBufferX, accelBufferY, accelBufferZ):
    QtCore.QThread.__init__(self)
    self.serialEnabled = serialEnabled
    self.dataBuffer1 = dataBuffer1
    self.dataBuffer2 = dataBuffer2
    self.writeVal = writeVal
    self.accelBufferX = accelBufferX
    self.accelBufferY = accelBufferY
    self.accelBufferZ = accelBufferZ



    self.ser = serial.Serial()

    self.ser.baudrate = baud
    self.ser.port = port
    self.ser.open()
    #self.ser.write("wb")
    self.ser.write(str.encode("wb"))
    
  def run(self):

    s = struct.Struct('f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f')
    s2 = struct.Struct('f')

    sAccel = struct.Struct('f f f')

    while True:
      data = self.ser.read(1)
      #if(data == 255):
      if(ord(data) == 255):
        data = self.ser.read(3)
        #if(data[0] == 255 and data[1] == 0):
        if(data[0] == 255 and data[1] == 0):
          #channel = data[2]
          channel = data[2]
          if(channel == 6):
            print("")
            data = self.ser.read(4)
            log = s2.unpack(data)
            print("log:"+str(log))
            print("")
          elif(channel == 7):
            data = self.ser.read(12)
            self.accelBufferX = sAccel.unpack(data)
            self.newSample.emit(7,7, self.dataBuffer1, self.dataBuffer2)
          elif(channel > 0) and (channel < 6):
            data = self.ser.read(500)
            if(self.writeVal == 1):
              self.dataBuffer1 = s.unpack(data)
              self.writeVal = 2
            else:
              self.dataBuffer2 = s.unpack(data)
              self.writeVal = 1
            #unpacked_data = s.unpack(data)
            chanCounter = channel
            self.newSample.emit(channel,self.writeVal, self.dataBuffer1, self.dataBuffer2)
        else:
          self.ser.flush()
      elif(data[0] == 5):
      #elif(data[0] == 5):
        if not self.serialEnabled : 
          self.serialConn.emit(self.serialEnabled)
        self.enabled = 1
        print("Raw signals enabled!")
        
      else:
        self.ser.flush()


          
  def setRawAcquisition(self):
    #self.ser.write("wb")
    self.ser.write(str.encode("wb"))
    
  def setDecoderAcquisition(self):
    #self.ser.write("wa")
    self.ser.write(str.encode("wa"))

class tabdemo(QtGui.QTabWidget):
  
  def __init__(self, parent = None):

    self.PROGRAM_VER = 4.0



    self.dataBuffer1 = (0,0)
    self.dataBuffer2 = (0,0)

    #dataBufferChannel1 = 0
    #dataBufferChannel2 = 0
    #dataBufferChannel3 = 0
    #dataBufferChannel4 = 0
    #dataBufferChannel5 = 0

    self.accelBufferX = 0
    self.accelBufferY = 0
    self.accelBufferZ = 0

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
    #self.tabEEG = QtGui.QWidget()
    #self.tabSpect = QtGui.QWidget()
    #self.tabGame = QtGui.QWidget()
    #self.tabConnect = QtGui.QWidget()	#connect
    #self.tabAccel = QtGui.QWidget() #accel
    
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
    self.serialPort = str('/dev/tty.mindreachBTv4-Bluetooth')

    self.disableYAutorange = False
    self.yLimitSpinbox_value = 00100.0 #uV 
    self.yLimit_value = self.yLimitSpinbox_value / 1000000
 
    
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
    #self.graph1.setYRange(0,200,padding=0)
    self.graph2.setLabel('left', "Amplitude", "V")
    self.graph2.setLabel('bottom', "Number of points")
    self.graph2.setTitle("Channel 2")
    #self.graph2.setYRange(0,200,padding=0)
    self.graph3.setLabel('left', "Amplitude", "V")
    self.graph3.setLabel('bottom', "Number of points")
    self.graph3.setTitle("Channel 3")
    #self.graph3.setYRange(0,200,padding=0)
    self.graph4.setLabel('left', "Amplitude", "V")
    self.graph4.setLabel('bottom', "Number of points")
    self.graph4.setTitle("Channel 4")
    #self.graph4.setYRange(0,200,padding=0)
    self.graph5.setLabel('left', "Amplitude", "V")
    self.graph5.setLabel('bottom', "Number of points")
    self.graph5.setTitle("Channel 5")
    #self.graph5.setYRange(0,200,padding=0)

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
    
    #self.graph1.setYLink(self.graph2)
    #self.graph2.setYLink(self.graph1)
    
    #self.graph2.setYLink(self.graph3)
    #self.graph3.setYLink(self.graph2)
    
    #self.graph3.setYLink(self.graph4)
    #self.graph4.setYLink(self.graph5)
    
    #self.graph4.setYLink(self.graph5)
    #self.graph5.setYLink(self.graph1)
    
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
    #self.fftData = pg.PlotCurveItem()
    #self.fft.addItem(self.fftData)
    #self.spectogram.setLabel('left', "Amplitude", "V")
    #self.spectogram.setLabel('bottom', "Number of points")
    self.spectrogram = pg.ImageItem()
    self.spectrogramImage.addItem(self.spectrogram)
    self.spectrogramImage.setLabel('left', 'Frequency', units='Hz')
    self.spectrogramImage.setLabel('bottom', 'Time', units='s')
    
    
    self.tabConnect = QtGui.QWidget()	#connect
    self.tabEEG = QtGui.QWidget()
    self.tabSpect = QtGui.QWidget()
    self.tabGame = QtGui.QWidget()
    self.tabAccel = QtGui.QWidget() #accel
    self.connectTabIndex = self.addTab(self.tabConnect,"Connect") + 1
    self.eegTabIndex = self.addTab(self.tabEEG,"EEG Data") + 1
    self.spectTabIndex = self.addTab(self.tabSpect,"Spectogram") + 1 
    self.accelTabIndex = self.addTab(self.tabAccel,"Accel Data") + 1
    self.gameTabIndex = self.addTab(self.tabGame,"Game") + 1
    print("connectIndex",self.connectTabIndex)
    print("eegIndex",self.eegTabIndex)

    
    self.connectTabUI()
    self.graphTabUI()
    self.spectTabUI()
    self.gameTabUI()
    self.accelTabUI()
    self.connectTabs()
    
    #self.setCurrentIndex(self.gameTabIndex -1)
    
    #serial = serialReceiver(1, 1)
    #serial.newSample.connect(self.updateGraphs)
    #self.thread = serial
    #serial.start()
    self.setWindowTitle("VisionVolt - Mindreach EEG Headset GUI, version: " + str(self.PROGRAM_VER))
  
  def setAutoRange(self,graph, enable):
    axY = graph.getAxis('left')
    if(enable == True):
      graph.enableAutoRange(axY,True,None, 'y')
      #graph.updateAutoRange()
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
          self.thread.setRawAcquisition()
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
          self.thread.setRawAcquisition()
        except:
          print("No Serial connection")

    elif(self.activeTab == self.gameTabIndex):
      print("tab game")
      try:
        self.thread.setDecoderAcquisition()
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
          self.thread.setRawAcquisition()
        except:
          print("No Serial connection")
    else:
      self.counter = 0

      
      
    #print("New active tab: " + str(self.activeTab))
    
  def connectTabs(self):
    self.currentChanged.connect(self.tabChanged)
    self.portedit.editingFinished.connect(self.port_change)
    self.baudedit.editingFinished.connect(self.baud_change)
    self.connectbutton.clicked.connect(self.start_serial)
    
  def updateGraphs(self,channel,buffer, dataBuffer1, dataBuffer2):
    # dataBuffer1 = self.dataBuffer1
    # dataBuffer2 = self.dataBuffer2

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
            #print(self.img_array)
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
        self.channelAccelX[self.counterAccel] = self.accelBufferX[0]
        self.channelAccelY[self.counterAccel] = self.accelBufferX[1]
        self.channelAccelZ[self.counterAccel] = self.accelBufferX[2]
        #print(accelBufferX[2])
        self.counterAccel += 1
        if(self.counterAccel == 1000):
          self.counterAccel = 0
        self.accelDataX.setData(self.channelAccelX,pen=plotcolor)
        self.accelDataY.setData(self.channelAccelY,pen=plotcolor)
        self.accelDataZ.setData(self.channelAccelZ,pen=plotcolor)
        
        #for i in range(0,1):
        #  sample =  accelBufferX[i]
        #  print(sample)
        #  self.channelAccelX[self.counterAccel] = sample
        #  self.counterAccel += 1
        #  if(self.counterAccel == 5000):
        #    self.counterAccel = 0
        #self.accelDataX.setData(self.channelAccelX,pen='y')
    else: # game
      channel = self.activeChannel

  def accelTabUI(self):
    layoutAccel = QtGui.QVBoxLayout()
    
    #configLayout = QtGui.QHBoxLayout()
    #configLayout.addWidget(self.limitCheckbox)
    #layout.addLayout(configLayout)
    layoutAccel.addWidget(self.graphAccel_x)
    layoutAccel.addWidget(self.graphAccel_y)
    layoutAccel.addWidget(self.graphAccel_z)

    #self.setTabText(4,"Accel Data")
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
    
    #self.setTabText(0,"EEG Data")
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

  def gameTabUI(self):
    layout = QtGui.QHBoxLayout()
    #self.setTabText(2,"Game")
    QtGui.closeAllWindows();
    self.tabGame.setLayout(layout)

    
  def connectTabUI(self):
    layout = QtGui.QVBoxLayout()
    
    #self.setTabText(3,"Connect")
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
    layout.addWidget(self.baudtext)
    layout.addWidget(self.baudedit)
    layout.addWidget(self.porttext)
    layout.addWidget(self.portedit)
    layout.addWidget(self.connectbutton)
    layout.addSpacing(800)
    self.tabConnect.setLayout(layout)
    
  def onSerialConnect(self,enabled):
    global serialEnabled
    if not enabled:
      self.setCurrentIndex(self.eegTabIndex-1)
      serialEnabled = True
    
  def port_change(self):
    #print("New port is " + self.portedit.text())
    self.serialPort = self.portedit.text()
  
  def baud_change(self):
    self.serialBaud = int(self.baudedit.text())
  
  def start_serial(self):
    serial = serialReceiver(self.serialBaud, str(self.serialPort), self.serialEnabled, self.dataBuffer1,
     self.dataBuffer2, self.writeVal, self.accelBufferX, self.accelBufferY, self.accelBufferZ)
    serial.newSample.connect(self.updateGraphs)
    serial.serialConn.connect(self.onSerialConnect)
    self.thread = serial
    serial.start()
    
def main():
  app = QtGui.QApplication(sys.argv)
  ex = tabdemo()
  ex.show()
  sys.exit(app.exec_())
  
if __name__ == '__main__':
  main()
