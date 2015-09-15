from PyQt4 import QtGui as gui, QtCore as core
from widgets import simpleText,intInput,floatInput,queryButton,colorBox
import os


class portDisplay(gui.QWidget):
    def __init__(self,parent,label,pos,icon,ll=96,ls=23,iw=32):
        super(portDisplay,self).__init__(parent)
        self.parent = parent
        self.label  = label
        
        self.label_current_value = simpleText(self,"Loading...",[0,0,ll,ls],"Current value")
        self.input_set_value     = floatInput(self,[0,1],8,
                                              'Enter a value here and press "set" to set the voltage on the selected DCbox.\nBe careful not to use this feature while a sweep is using the selected port.',
                                              [0,iw+2,ll,ls],
                                              'Set value')
        self.button_set_value    = queryButton("set",self,"Set channel %s to the enterred value"%label,
                                               [ll,iw+2],self.set_value)

        self.label_port_number   = simpleText(self,label,[ll+2+iw+4,int((iw-ls)//2),ls,ls])
        
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
        if (value > 1.0) or (value < 0.0):
            print("Error: value must be in range of 0.0 to 1.0")
            return False
        try:
            self.parent.connection.ad5764_acbox.select_device(self.parent.device)
            response =  self.parent.connection.ad5764_acbox.set_channel_voltage(self.label,value)
            print(response)
        except:
            print("Error: something went wrong. The device selected might not be a ACbox device.")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))




class ad5764_acbox_VFP_widget(gui.QWidget):
    def __init__(self,parent,connection,com):
        super(ad5764_acbox_VFP_widget,self).__init__(parent)
        self.connection = connection
        self.device     = "acbox (%s)"%com
        self.com        = com
        icon = gui.QPixmap(os.getcwd()+'\\devices\\resources\\BNCport.png')
        self.ports = []
        sp_x = 171 + 32
        sp_y = 32 + 23 + 32
        ls   = 23
        ll   = 96
        labels = ['X1','Y1','X2','Y2']
        for port in range(4):
            self.ports.append(
                portDisplay(self,labels[port],[sp_x*(port%2),sp_y*int((port//2))],icon)
                )

        self.label_frq  = simpleText(self,"Frequency (Hz)" ,[sp_x * 2, ls*0, ll, ls])
        self.label_phs  = simpleText(self,"Phase (degrees)",[sp_x * 2, ls*3, ll, ls])
        self.output_frq = simpleText(self,"Loading...",[sp_x * 2 + ll, ls*0, ll, ls])
        self.output_phs = simpleText(self,"Loading...",[sp_x * 2 + ll, ls*3, ll, ls])
        self.input_frq  = intInput(self  ,[0,1e8],  '',[sp_x * 2 + ll, ls*1, ll, ls],"set frequency")
        self.input_phs  = floatInput(self,[0,360],4,'',[sp_x * 2 + ll, ls*4, ll, ls],"set phase")

        col = gui.QColor(255,255,255)
        self.setStyleSheet('QWidget { background-color: %s }'%col.name())

        self.connection.ad5764_acbox.select_device(self.device)
        self.connection.ad5764_acbox.read_voltages()

    def update_readouts(self,voltages):
        for entry in voltages:
            if entry[0] == self.com:
                for port in range(4):
                    self.ports[port].update_readout(entry[port+1])
                


                
                return True
        print("Error: device com not found in voltage list")
        return False
