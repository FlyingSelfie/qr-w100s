#!/usr/bin/env python

from PySide import QtGui, QtCore

from input.video import VideoTestWidget, WalkeraVideoProcess

import socket
import binascii
import time
import sys

class WalkeraCommand():
   def __init__(self):
      self.data  = bytearray(18)
      self.zero()
   def zero(self):
      self.switch   = 0x61
      self.thrust   = 0x02bf #min value
      self.yaw      = 0x044a
      self.pitch    = 0x044a
      self.roll     = 0x044a
      self.update()
   def update(self):
      self.data[0] = self.switch #enable code
      self.data[1] = self.thrust >> 8
      self.data[2] = self.thrust & 0xff
      self.data[3] = self.yaw >> 8
      self.data[4] = self.yaw & 0xff
      self.data[5] = self.pitch >> 8
      self.data[6] = self.pitch & 0xff
      self.data[7] = self.roll >> 8
      self.data[8] = self.roll & 0xff
      self.data[9] = self.roll >> 8
      self.data[10] = self.roll & 0xff
      self.data[11] = self.thrust >> 8
      self.data[12] = self.thrust & 0xff
      self.data[13] = self.yaw >> 8
      self.data[14] = self.yaw & 0xff
      self.data[15] = self.pitch >> 8
      self.data[16] = self.pitch & 0xff
      self.data[17] = sum(self.data[0:17]) & 0xFF
   def getString(self):
      return binascii.hexlify(self.data)

def pulse():
   w = WalkeraCommand()
   
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) #disable Nagle          
   #s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0) #disable kernel buffer
   s.connect(("192.168.10.1", 2001))
   s.setblocking(0)
   
   w.zero()
   s.send(w.data)
   print "zero: ", w.getString()
   sys.stdout.flush()
   
   data = [0, 1, 0, 0]
   w.thrust = (int(data[1])*(0x05dc-0x02bf) + 0x02bf)
   w.pitch = (int((1 - data[3])*((0x0640-0x025b)>>1)) + 0x025b)
   w.roll = (int((1 - data[2])*((0x0640-0x025b)>>1)) + 0x025b)
   w.yaw = (int((1 - data[0])*((0x0640-0x025b)>>1)) + 0x025b)
   w.update()
   s.send(w.data)
   print "full: ", w.getString()
   sys.stdout.flush()
   
   data = [0, 0, 0, 0]
   w.thrust = (int(data[1]*((0x05dc-0x02bf))) + 0x02bf)
   w.pitch = (int((1 - data[3])*((0x0640-0x025b)>>1)) + 0x025b)
   w.roll = (int((1 - data[2])*((0x0640-0x025b)>>1)) + 0x025b)
   w.yaw = (int((1 - data[0])*((0x0640-0x025b)>>1)) + 0x025b)
   w.update()
   s.send(w.data)
   print "zero: ", w.getString()
   sys.stdout.flush()
   
   s.close()

if __name__ == '__main__':
   
   app = QtGui.QApplication(sys.argv)
   widget = VideoTestWidget(WalkeraVideoProcess)
   app.aboutToQuit.connect(widget.shutdown)
   widget.show()

   FPS = 0.5
   t = QtCore.QTimer()
   t.timeout.connect(pulse)
   t.start(1000.0/FPS)
   
   sys.exit(app.exec_())
   
   
   

   