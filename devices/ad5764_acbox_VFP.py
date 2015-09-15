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
        self.input_frq  = intInput(self,  [0,1e8],  '',[sp_x * 2 + ll, ls*1, ll, ls],"set frequency")
        self.input_phs  = floatInput(self,[0,360],4,'',[sp_x * 2 + ll, ls*4, ll, ls],"set phase")
        self.button_frq = queryButton("set",self,'',[sp_x * 2, ls*1, ll, ls],self.write_frq)
        self.button_phs = queryButton("set",self,'',[sp_x * 2, ls*4, ll, ls],self.write_phs)

        self.label_clockmult = simpleText(self,"Clock multiplier",[sp_x*2 + ll*2 + ls, ls*0, ll, ls])
        self.input_clockmult = intInput(self,[3,6],''     ,[sp_x*2 + ll*3 + ls, ls*0, int(ll//2), ls])
        
        self.button_init     = queryButton("init",self,'' ,[sp_x*2 + ll*2 + ls, ls*1, ll, ls],self.do_init)
        self.button_reset    = queryButton("reset",self,'',[sp_x*2 + ll*2 + ls, ls*2, ll, ls],self.do_reset)
        

        col = gui.QColor(255,255,255)
        self.setStyleSheet('QWidget { background-color: %s }'%col.name())

        self.connection.ad5764_acbox.select_device(self.device)
        self.connection.ad5764_acbox.read_voltages()

    def write_frq(self):
        value = self.input_frq.getValue()
        if not (str(value) == 'nan'):
            self.connection.ad5764_acbox.select_device(self.device)
            print(self.connection.ad5764_acbox.set_frequency(float(self.input_frq.getValue())))
    
    def write_phs(self):
        value = self.input_phs.getValue()
        if not (str(value) == 'nan'):
            self.connection.ad5764_acbox.select_device(self.device)
            print(self.connection.ad5764_acbox.set_phase(self.input_phs.getValue()))

    def do_init(self):
        clock_mult = self.input_clockmult.getValue()
        if not (str(clock_mult) == 'nan'):
            self.connection.ad5764_acbox.select_device(self.device)
            print(self.connection.ad5764_acbox.initialize(clock_mult))

    def do_reset(self):
        self.connection.ad5764_acbox.select_device(self.device)
        print(self.connection.ad5764_acbox.reset())


    def update_readouts(self,voltages):
        for entry in voltages:
            if entry[0] == self.com:
                for port in range(4):
                    self.ports[port].update_readout(entry[port+1])
                
                # frequency
                self.output_frq.setText(entry[5])

                # phase
                self.output_phs.setText(entry[6]+'\xb0')


                
                return True
        print("Error: device com not found in voltage list")
        return False
