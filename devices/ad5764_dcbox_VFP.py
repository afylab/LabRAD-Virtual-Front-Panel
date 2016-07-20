from PyQt4 import QtGui as gui, QtCore as core

global serverNameAD5764_DCBOX; serverNameAD5764_DCBOX = "ad5764_dcbox"


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
        try:
            self.parent.connection.ad5764_dcbox.select_device(self.parent.device)
            response =  self.parent.connection.ad5764_dcbox.set_voltage(self.port, value)
            print(response)
        except:
            print("Error: something went wrong. The device selected might not be a DCbox device.")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))




class ad5764_dcbox_VFP_widget(gui.QWidget):
    def __init__(self,parent,connection,com,devID,IDGen):
        super(ad5764_dcbox_VFP_widget,self).__init__(parent)
        self.connection = connection
        self.listenerID = IDGen.next()
        self.device     = "%s (%s)"%(serverNameAD5764_DCBOX,com)
        self.com        = com
        self.devID      = devID
        self.ports = []
        for port in range(8):
            self.ports.append(portDisplay(self,port))

        self.hBoxTopRow = gui.QHBoxLayout()
        self.hBoxBotRow = gui.QHBoxLayout()

        for port in [0,1,2,3]:self.hBoxTopRow.addWidget(self.ports[port])
        for port in [4,5,6,7]:self.hBoxBotRow.addWidget(self.ports[port])

        #self.hBoxTopRow.setContentsMargins(0,0,0,0)#; self.hBoxBotRow.setSpacing(0)
        #self.hBoxBotRow.setContentsMargins(0,0,0,0)#; self.hBoxTopRow.setSpacing(0)

        self.mainLayout = gui.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        #self.mainLayout.setSpacing(0)
        self.mainLayout.addLayout(self.hBoxTopRow)
        self.mainLayout.addLayout(self.hBoxBotRow)
        self.setLayout(self.mainLayout)

        self.connection.ad5764_dcbox.signal__channel_voltage_changed(self.listenerID)
        self.connection._backend.cxn.addListener(self.port_update,self.connection.ad5764_dcbox.ID,context=None,ID=self.listenerID)

        self.connection.ad5764_dcbox.select_device(self.device)
        self.connection.ad5764_dcbox.send_voltage_signals()

    def port_update(self,ctx,data):
        if ctx.ID[0]==self.devID:
            port = int(data[0])
            self.ports[port].update_readout(data[1])

    def update_readouts(self):
        self.connection[serverNameAD5764_DCBOX].select_device(self.device)
        voltages = self.connection[serverNameAD5764_DCBOX].get_voltages()
        for port in range(8):
            self.ports[port].update_readout(float(voltages[port]))
        return True

    def setEditingPermission(self,canEdit):
        for port in self.ports:port.label_custom_name.setReadOnly(not canEdit)
