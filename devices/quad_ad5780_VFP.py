from PyQt4 import QtGui as gui, QtCore as core
from widgets import simpleText,floatInput,queryButton,colorBox
import os

global serverNameQUAD_AD5780;  serverNameQUAD_AD5780  = "ad5780_dcbox"

class portDisplay(gui.QWidget):
    def __init__(self,parent,num,pos,icon,ll=96,ls=23,iw=32):
        super(portDisplay,self).__init__(parent)
        self.parent = parent
        self.port   = num

        sp_x = 171 + 32
        
        self.label_current_value = simpleText(self,"Loading...",[0,0,ll,ls],"Current value")
        self.input_set_value     = floatInput(self,[-10,10],8,
                                              'Enter a value here and press "set" to set the voltage on the selected DCbox.\nBe careful not to use this feature while a sweep is using the selected port.',
                                              [0,iw+2,ll,ls],
                                              'Set value')
        self.button_set_value    = queryButton("set",self,"Set port %i to the enterred value"%num,
                                               [ll,iw+2],self.set_value)
        self.label_port_number   = simpleText(self,str(num),[ll+2+iw+4,int((iw-ls)//2),ls,ls])
        
        self.BNC_port_label      = gui.QLabel(self)
        self.BNC_port_label.setPixmap(icon)
        self.BNC_port_label.setGeometry(ll+2,0,iw,iw)

        button_size = self.button_set_value.sizeHint().width()

        self.move(pos[0],pos[1])
        self.setMinimumSize(ll+max([iw,button_size]),ls+iw)

    def set_value(self):
        value = self.input_set_value.getValue()
        if str(value) in ['nan','inf']:
            print("Error: invalid value.")
            return False
        if (value > 10) or (value < -10):
            print("Error: value too large. Must be between -10.0 and 10.0")
            return False
        try:
            self.parent.connection[serverNameQUAD_AD5780].select_device(self.parent.device)
            response =  self.parent.connection[serverNameQUAD_AD5780].set_voltage(self.port, value)
            print(response)
            value = response.rpartition(' TO ')[2][:-1]
            self.label_current_value.setText(value)
        except:
            print("Error: something went wrong. The device selected might not be a DCbox device.")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))

    


class quad_ad5780_VFP_widget(gui.QWidget):
    def __init__(self,parent,connection,com):
        super(quad_ad5780_VFP_widget,self).__init__(parent)
        self.connection = connection
        self.device     = com
        self.com        = com
        icon = gui.QPixmap(os.getcwd()+'\\devices\\resources\\BNCport.png')
        self.ports = []
        sp_x = 171 + 32
        sp_y = 32 + 23 + 32
        for port in range(4):
            self.ports.append(
                portDisplay(self,port,[sp_x*(port%2),sp_y*int((port//2))],icon)
                )

        col = gui.QColor(255,255,255)
        self.setStyleSheet('QWidget { background-color: %s }'%col.name())

        self.button_initialize   = queryButton("initialize",self,"initialize the device",[sp_x*2,0],self.initialize)

        self.connection[serverNameQUAD_AD5780].select_device(self.device)
        #self.connection[serverNameQUAD_AD5780].read_voltages()

        # size
        self.size = [sp_x*4 - 25, sp_y*2 - 4]

    def update_readouts(self,voltages):
        for entry in voltages:
            if entry[0] == self.com:
                for port in range(4):
                    self.ports[port].update_readout(entry[port+1])
                return True
        print("Error: device com not found in voltage list")
        return False

    def initialize(self):
        self.connection[serverNameQUAD_AD5780].initialize()
        print("QUAD_AD5780_DCBOX INIT SUCCESS <%s>"%self.com)