from PyQt4 import QtGui as gui, QtCore as core
from widgets import simpleText,intInput,floatInput,queryButton,colorBox
import os

global serverNameAD5764_ACBOX; serverNameAD5764_ACBOX = "ad5764_acbox"

from math import pi,sin,cos
global tau; tau = 2*pi

class portDisplay(gui.QWidget):
    def __init__(self,parent,name):
        super(portDisplay,self).__init__(parent)
        self.parent = parent
        self.port   = name
        self.vBoxLeft   = gui.QVBoxLayout(); self.vBoxLeft.setSpacing(0)  ; self.vBoxLeft.setContentsMargins(0,0,0,0)
        self.vBoxRight  = gui.QVBoxLayout(); self.vBoxRight.setSpacing(0) ; self.vBoxRight.setContentsMargins(0,0,0,0)
        self.mainLayout = gui.QHBoxLayout(); self.mainLayout.setSpacing(0); self.mainLayout.setContentsMargins(0,0,0,0)

        self.label_custom_name   = gui.QLineEdit(); self.label_custom_name.setPlaceholderText("custom name")
        self.label_current_value = gui.QLineEdit(); self.label_current_value.setPlaceholderText("current value")
        self.input_set_value     = gui.QLineEdit(); self.input_set_value.setPlaceholderText("enter value")
        self.label_current_value.setReadOnly(True)
        self.vBoxLeft.addWidget(self.label_custom_name)
        self.vBoxLeft.addWidget(self.label_current_value)
        self.vBoxLeft.addWidget(self.input_set_value)

        self.button_hide_show    = gui.QPushButton("Hide"); self.button_hide_show.clicked.connect(self.toggle_display)
        self.label_port_number   = gui.QLineEdit(); self.label_port_number.setText(name)
        self.button_set_value    = gui.QPushButton("set"); self.button_set_value.clicked.connect(self.set_value)
        self.label_port_number.setReadOnly(True)
        self.vBoxRight.addWidget(self.button_hide_show)
        self.vBoxRight.addWidget(self.label_port_number)
        self.vBoxRight.addWidget(self.button_set_value)

        self.mainLayout.addLayout(self.vBoxLeft)
        self.mainLayout.addLayout(self.vBoxRight)
        self.setLayout(self.mainLayout)

        # pressing enter simulates clicking on the button
        self.input_set_value.returnPressed.connect(self.button_set_value.click)

        self.display_enabled = True

    def toggle_display(self):
        if self.display_enabled:
            self.disable_display()
        else:
            self.enable_display()

    def enable_display(self):
        self.display_enabled = True
        self.label_current_value.setVisible(True)
        self.input_set_value.setVisible(True)
        self.label_port_number.setVisible(True)
        self.button_set_value.setVisible(True)
        self.button_hide_show.setText("Hide")

    def disable_display(self):
        self.display_enabled = False
        self.label_current_value.setVisible(False)
        self.input_set_value.setVisible(False)
        self.label_port_number.setVisible(False)
        self.button_set_value.setVisible(False)
        self.button_hide_show.setText("Show")

    def set_value(self):
        try:
            value = float(self.input_set_value.text())
        except:
            value = 'nan'

        if str(value) in ['nan','inf']:
            print("Error: invalid value.")
            return False
        if (value > 1.0) or (value < 0.0):
            print("Error: value must be in range of 0.0 to 1.0")
            return False
        try:
            #print(self.port,value)
            self.parent.connection.ad5764_acbox.select_device(self.parent.device)
            response =  self.parent.connection.ad5764_acbox.set_channel_voltage(self.port,value)
            print(response)
        except:
            print("Error: something went wrong. The device selected might not be a ACbox device.")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))




class ad5764_acbox_VFP_widget(gui.QWidget):
    def __init__(self,parent,connection,com,devID,IDGen):
        super(ad5764_acbox_VFP_widget,self).__init__(parent)
        self.connection = connection
        self.device     = "%s (%s)"%(serverNameAD5764_ACBOX,com)
        self.com        = com
        self.devID      = devID

        self.LIDVoltage = IDGen.next()
        self.LIDFreq    = IDGen.next()
        self.LIDPhase   = IDGen.next()
        self.LIDInit    = IDGen.next()
        self.LIDReset   = IDGen.next()

        self.connection.ad5764_acbox.signal__channel_voltage_changed(self.LIDVoltage)
        self.connection.ad5764_acbox.signal__frequency_changed(self.LIDFreq)
        self.connection.ad5764_acbox.signal__phase_changed(self.LIDPhase)
        self.connection.ad5764_acbox.signal__init_done(self.LIDInit)
        self.connection.ad5764_acbox.signal__reset_done(self.LIDReset)

        self.connection._backend.cxn.addListener(self.port_update ,self.connection.ad5764_acbox.ID,context=None,ID=self.LIDVoltage)
        self.connection._backend.cxn.addListener(self.freq_update ,self.connection.ad5764_acbox.ID,context=None,ID=self.LIDFreq)
        self.connection._backend.cxn.addListener(self.phase_update,self.connection.ad5764_acbox.ID,context=None,ID=self.LIDPhase)
        self.connection._backend.cxn.addListener(self.init_update ,self.connection.ad5764_acbox.ID,context=None,ID=self.LIDInit)
        self.connection._backend.cxn.addListener(self.reset_update,self.connection.ad5764_acbox.ID,context=None,ID=self.LIDReset)

        self.ports = []

        self.labels    = ['X1','Y1','X2','Y2']
        self.fromLabel = {'X1':0,'Y1':1,'X2':2,'Y2':3}
        for port in range(4):
            self.ports.append(
                portDisplay(self,self.labels[port])
                )

        self.vBoxXChannels = gui.QVBoxLayout() # x channel ports
        self.vBoxYChannels = gui.QVBoxLayout() # y channel ports
        self.hBoxXY        = gui.QHBoxLayout() # all 4 ports
        self.vBoxXChannels.addWidget(self.ports[0])
        self.vBoxXChannels.addWidget(self.ports[1])
        self.vBoxYChannels.addWidget(self.ports[2])
        self.vBoxYChannels.addWidget(self.ports[3])
        self.hBoxXY.addLayout(self.vBoxXChannels)
        self.hBoxXY.addLayout(self.vBoxYChannels)


        self.label_frq  = gui.QLineEdit();self.label_frq.setText("Frequency (Hz)");self.label_frq.setReadOnly(True)
        self.label_phs  = gui.QLineEdit();self.label_phs.setText("Phase (degrees)");self.label_phs.setReadOnly(True)
        self.output_frq = gui.QLineEdit();self.output_frq.setReadOnly(True)
        self.output_phs = gui.QLineEdit();self.output_phs.setReadOnly(True)
        self.input_frq  = gui.QLineEdit()
        self.input_phs  = gui.QLineEdit()
        self.button_frq = gui.QPushButton("set")
        self.button_phs = gui.QPushButton("set")

        # pressing enter simulates click on button
        self.input_frq.returnPressed.connect(self.button_frq.click)
        self.input_phs.returnPressed.connect(self.button_phs.click)

        self.vBoxFreqLeft  = gui.QVBoxLayout(); self.vBoxFreqLeft.setContentsMargins(0,0,0,0) ; self.vBoxFreqLeft.setSpacing(0)
        self.vBoxFreqRight = gui.QVBoxLayout(); self.vBoxFreqRight.setContentsMargins(0,0,0,0); self.vBoxFreqRight.setSpacing(0)
        self.hBoxFreq      = gui.QHBoxLayout(); self.hBoxFreq.setContentsMargins(0,0,0,0)     ; self.hBoxFreq.setSpacing(0)
        self.vBoxFreqLeft.addWidget(self.label_frq)
        self.vBoxFreqLeft.addWidget(self.button_frq)
        self.vBoxFreqRight.addWidget(self.output_frq)
        self.vBoxFreqRight.addWidget(self.input_frq)
        self.hBoxFreq.addLayout(self.vBoxFreqLeft)
        self.hBoxFreq.addLayout(self.vBoxFreqRight)

        self.vBoxPhaseLeft  = gui.QVBoxLayout(); self.vBoxPhaseLeft.setContentsMargins(0,0,0,0) ; self.vBoxPhaseLeft.setSpacing(0)
        self.vBoxPhaseRight = gui.QVBoxLayout(); self.vBoxPhaseRight.setContentsMargins(0,0,0,0); self.vBoxPhaseRight.setSpacing(0)
        self.hBoxPhase      = gui.QHBoxLayout(); self.hBoxPhase.setContentsMargins(0,0,0,0)     ; self.hBoxPhase.setSpacing(0)
        self.vBoxPhaseLeft.addWidget(self.label_phs)
        self.vBoxPhaseLeft.addWidget(self.button_phs)
        self.vBoxPhaseRight.addWidget(self.output_phs)
        self.vBoxPhaseRight.addWidget(self.input_phs)
        self.hBoxPhase.addLayout(self.vBoxPhaseLeft)
        self.hBoxPhase.addLayout(self.vBoxPhaseRight)

        self.vBoxPhsFrq = gui.QVBoxLayout() # phase & frequency controls
        self.vBoxPhsFrq.addLayout(self.hBoxFreq)
        self.vBoxPhsFrq.addLayout(self.hBoxPhase)

        # connect set phs,frq buttons to functions
        self.button_phs.clicked.connect(self.write_phs)
        self.button_frq.clicked.connect(self.write_frq)


        self.label_clockmult = gui.QLineEdit();self.label_clockmult.setText("Clock multiplier");self.label_clockmult.setReadOnly(True)
        self.input_clockmult = gui.QLineEdit()
        self.button_init     = gui.QPushButton("Init") ; self.button_init.clicked.connect(self.do_init)
        self.button_reset    = gui.QPushButton("Reset"); self.button_reset.clicked.connect(self.do_reset)

        self.hBoxClockMult = gui.QHBoxLayout(); self.hBoxClockMult.setContentsMargins(0,0,0,0);self.hBoxClockMult.setSpacing(0)
        self.hBoxClockMult.addWidget(self.label_clockmult)
        self.hBoxClockMult.addWidget(self.input_clockmult)

        self.vBoxInitReset = gui.QVBoxLayout(); self.vBoxInitReset.setContentsMargins(0,0,0,0); self.vBoxInitReset.setSpacing(0)
        self.vBoxInitReset.addLayout(self.hBoxClockMult)
        self.vBoxInitReset.addWidget(self.button_init)
        self.vBoxInitReset.addWidget(self.button_reset)

        self.hBoxControlPanel = gui.QHBoxLayout() # top layout, all controls
        self.hBoxControlPanel.setContentsMargins(0,0,0,0)
        self.hBoxControlPanel.addLayout(self.hBoxXY)
        self.hBoxControlPanel.addLayout(self.vBoxPhsFrq)
        self.hBoxControlPanel.addLayout(self.vBoxInitReset)

        x2_perp_tt  = """Portion of X2 perpendicular to X1
(X2 full scale / X1 full scale) * (X2 value / X1 value) * sin(phase)"""
        x2_parr_tt = """Portion of X2 parallel to X1
(X2 full scale / X1 full scale) * (X2 value / X1 value) * cos(phase)""" 

        self.label_x2_parr  = gui.QLineEdit(); self.label_x2_parr.setText("X2 parallel"); self.label_x2_parr.setToolTip(x2_parr_tt)
        self.label_x2_perp  = gui.QLineEdit(); self.label_x2_perp.setText("X2 perpendicular"); self.label_x2_perp.setToolTip(x2_perp_tt)
        self.output_x2_parr = gui.QLineEdit()
        self.output_x2_perp = gui.QLineEdit()

        self.label_x1_scale = gui.QLineEdit();self.label_x1_scale.setText("X1 full scale")
        self.label_x2_scale = gui.QLineEdit();self.label_x2_scale.setText("X2 full scale")
        self.input_x1_scale = gui.QLineEdit()
        self.input_x2_scale = gui.QLineEdit()

        col = gui.QColor(255,255,255)
        self.setStyleSheet('QWidget { background-color: %s }'%col.name())

        self.connection.ad5764_acbox.select_device(self.device)
        self.connection.ad5764_acbox.read_settings()

        self.setLayout(self.hBoxControlPanel)

    def write_frq(self):
        try:
            value = float(self.input_frq.text())
        except:
            value = 'nan'
            print("Error: invalid value.")
        if not (str(value) == 'nan'):
            self.connection.ad5764_acbox.select_device(self.device)
            print(self.connection.ad5764_acbox.set_frequency(value))
    
    def write_phs(self):
        try:
            value = float(self.input_phs.text())
        except:
            value = 'nan'
            print("Error: invalid value.")
        if not (str(value) == 'nan'):
            self.connection.ad5764_acbox.select_device(self.device)
            print(self.connection.ad5764_acbox.set_phase(value))

    def do_init(self):
        try:
            clock_mult = int(self.input_clockmult.text())
        except:
            clock_mult = 'nan'
            print("Error: invalid value for clock multiplier.")
        if not (str(clock_mult) == 'nan'):
            self.connection.ad5764_acbox.select_device(self.device)
            print(self.connection.ad5764_acbox.initialize(clock_mult))

    def do_reset(self):
        self.connection.ad5764_acbox.select_device(self.device)
        print(self.connection.ad5764_acbox.reset())

    def setEditingPermission(self,isEnabled):
        for port in self.ports:port.label_custom_name.setReadOnly(not isEnabled)

    def port_update(self,ctx,data):
        if ctx.ID[0]==self.devID:self.ports[self.fromLabel[data[0]]].update_readout(data[1])
    def freq_update(self,ctx,data):
        if ctx.ID[0]==self.devID:self.output_frq.setText(data[:-3])
    def phase_update(self,ctx,data):
        if ctx.ID[0]==self.devID:self.output_phs.setText(data)
    def init_update(self,ctx,data):
        if ctx.ID[0]==self.devID:pass
    def reset_update(self,ctx,data):
        if ctx.ID[0]==self.devID:pass

    def update_readouts(self,voltages):
        for entry in voltages:
            if entry[0] == self.com:
                for port in range(4):
                    self.ports[port].update_readout(entry[port+1])
                
                # frequency
                self.output_frq.setText(entry[5])

                # phase
                self.output_phs.setText(entry[6]+'\xb0')

                # parallel / perpendicular
                try:
                    x1_fs    = float(self.input_x1_scale.text())
                    x2_fs    = float(self.input_x2_scale.text())
                except:
                    x1_fs=x2_fs=1.0
                x1_value = float(entry[1])
                x2_value = float(entry[3])
                phase    = float(entry[6])
                parr     = cos(tau*float(phase)/360.0)
                perp     = sin(tau*float(phase)/360.0)
                try:
                    x2_parr  = (x2_fs / x1_fs) * (x2_value / x1_value) * parr
                    x2_perp  = (x2_fs / x1_fs) * (x2_value / x1_value) * perp
                    self.output_x2_parr.setText(str(x2_parr))
                    self.output_x2_perp.setText(str(x2_perp))
                except:
                    self.output_x2_parr.setText("NaN")
                    self.output_x2_perp.setText("NaN")


                


                
                return True
        print("Error: device com not found in voltage list")
        return False
