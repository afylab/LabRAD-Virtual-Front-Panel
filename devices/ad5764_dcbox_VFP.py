from PyQt4 import QtGui as gui, QtCore as core
from widgets import simpleText,floatInput,queryButton,colorBox
import os


class portDisplay(gui.QWidget):
    def __init__(self,parent,num,pos,icon,ll=96,ls=23,iw=32):
        super(portDisplay,self).__init__(parent)
        self.parent = parent
        self.port   = num
        
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
            self.parent.connection.ad5764_dcbox.select_device(self.parent.device)
            response =  self.parent.connection.ad5764_dcbox.set_voltage(self.port, value)
            print(response)
        except:
            print("Error: something went wrong. The device selected might not be a DCbox device.")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))




class ad5764_dcbox_VFP_widget(gui.QWidget):
    def __init__(self,parent,connection,com):
        super(ad5764_dcbox_VFP_widget,self).__init__(parent)
        self.connection = connection
        self.device     = "dcbox (%s)"%com
        self.com        = com
        icon = gui.QPixmap(os.getcwd()+'\\devices\\resources\\BNCport.png')
        self.ports = []
        sp_x = 171 + 32
        sp_y = 32 + 23 + 32
        for port in range(8):
            self.ports.append(
                portDisplay(self,port,[sp_x*(port%4),sp_y*int((port//4))],icon)
                )

        col = gui.QColor(255,255,255)
        self.setStyleSheet('QWidget { background-color: %s }'%col.name())

        self.connection.ad5764_dcbox.select_device(self.device)
        self.connection.ad5764_dcbox.read_voltages()

    def update_readouts(self,voltages):
        for entry in voltages:
            if entry[0] == self.com:
                for port in range(8):
                    self.ports[port].update_readout(entry[port+1])
                return True
        print("Error: device com not found in voltage list")
        return False
