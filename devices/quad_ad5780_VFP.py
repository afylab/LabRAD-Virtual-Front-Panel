from PyQt4 import QtGui as gui, QtCore as core
import os

global serverNameQuadAD5780; serverNameQuadAD5780 = "dcbox_quad_ad5780"


class portDisplay(gui.QWidget):
    def __init__(self,parent,num):
        super(portDisplay,self).__init__(parent)
        self.parent = parent
        self.port   = num
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
        self.label_port_number   = gui.QLineEdit(); self.label_port_number.setText("Port %i"%self.port)
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
        if (value > 10) or (value < -10):
            print("Error: value too large. Must be between -10.0 and 10.0")
            return False
        #try:
        self.parent.connection.dcbox_quad_ad5780.select_device(self.parent.devID)
        response =  self.parent.connection.dcbox_quad_ad5780.set_voltage(self.port, value)
        print(response)
        #except:
        #    print("Error: something went wrong. The device selected might not be a DCbox device.")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))



class quad_ad5780_VFP_widget(gui.QWidget):
    def __init__(self,parent,connection,com,devID,IDGen):
        super(quad_ad5780_VFP_widget,self).__init__(parent)
        self.connection = connection
        self.listenerID = IDGen.next()
        self.device     = "%s - %s"%(serverNameQuadAD5780,com)
        self.com        = com
        self.devID      = devID

        self.ports = []
        for port in range(4):
            self.ports.append(portDisplay(self,port))

        self.hBoxTopRow   = gui.QHBoxLayout()
        self.hBoxTopRow.addWidget(self.ports[0])
        self.hBoxTopRow.addWidget(self.ports[1])
        self.hBoxTopRow.addWidget(self.ports[2])
        self.hBoxTopRow.addWidget(self.ports[3])

        self.hBoxBotRow = gui.QHBoxLayout()
        self.buttonInit = gui.QPushButton("Initialize")
        self.buttonInit.clicked.connect(self.do_init)
        self.hBoxBotRow.addWidget(self.buttonInit)

        self.vBoxMainLayout = gui.QVBoxLayout()
        self.vBoxMainLayout.addLayout(self.hBoxTopRow)
        self.vBoxMainLayout.addLayout(self.hBoxBotRow)

        self.setLayout(self.vBoxMainLayout)

        self.connection.dcbox_quad_ad5780.signal__channel_voltage_changed(self.listenerID)
        self.connection._backend.cxn.addListener(self.port_update,self.connection.dcbox_quad_ad5780.ID,context=None,ID=self.listenerID)

        self.connection.dcbox_quad_ad5780.select_device(self.devID)
        self.connection.dcbox_quad_ad5780.send_voltage_signals()

    def do_init(self,event):
        self.connection.dcbox_quad_ad5780.select_device(self.devID)
        self.connection.dcbox_quad_ad5780.initialize()

    def port_update(self,ctx,data):
        self.ports[int(data[0])].label_current_value.setText(data[1])

    def setEditingPermission(self,canEdit):
        for port in self.ports:port.label_custom_name.setReadOnly(not canEdit)
