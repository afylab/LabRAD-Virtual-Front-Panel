from PyQt4 import QtGui as gui, QtCore as core

SERVER_NAME = 'dac_adc'





class inputPortDisplay(gui.QWidget):
    def __init__(self,parent,num):
        super(inputPortDisplay,self).__init__(parent)
        self.parent = parent
        self.port   = num

        self.hBoxTop    = gui.QHBoxLayout(); self.hBoxTop.setSpacing(0)   ; self.hBoxTop.setContentsMargins(0,0,0,0)
        self.hBodMid    = gui.QHBoxLayout(); self.hBodMid.setSpacing(0)   ; self.hBodMid.setContentsMargins(0,0,0,0)
        self.mainLayout = gui.QVBoxLayout(); self.mainLayout.setSpacing(0); self.mainLayout.setContentsMargins(0,0,0,0)

        self.label_custom_name   = gui.QLineEdit(); self.label_custom_name.setPlaceholderText("custom name")
        self.label_current_value = gui.QLineEdit(); self.label_current_value.setPlaceholderText("current value"); self.label_current_value.setReadOnly(True)
        self.button_hide_show    = gui.QPushButton("Hide"); self.button_hide_show.clicked.connect(self.toggle_display)
        self.label_port_number   = gui.QLineEdit(); self.label_port_number.setText("Input Port %i"%self.port)
        self.label_port_number.setReadOnly(True)

        self.hBoxTop.addWidget(self.label_custom_name)
        self.hBoxTop.addWidget(self.button_hide_show)
        self.hBodMid.addWidget(self.label_current_value)
        self.hBodMid.addWidget(self.label_port_number)

        self.button_get_value = gui.QPushButton("get value")
        self.button_get_value.clicked.connect(self.getValue)

        self.mainLayout.addLayout(self.hBoxTop)
        self.mainLayout.addLayout(self.hBodMid)
        self.mainLayout.addWidget(self.button_get_value)
        self.setLayout(self.mainLayout)

        self.display_enabled = True

    def getValue(self):
        try:
            self.parent.connection[SERVER_NAME].select_device(self.parent.devID)
            self.parent.connection[SERVER_NAME].read_voltage(self.port)
            # no need to call the update; parent listens to read signals and sends values to ports.
        except:
            print("Error: something went wrong; the device might not be functioning properly, or it might not be a DAC-ADC device.")

    def toggle_display(self):
        if self.display_enabled:
            self.disable_display()
        else:
            self.enable_display()

    def enable_display(self):
        self.display_enabled = True
        self.label_current_value.setVisible(True)
        self.label_port_number.setVisible(True)
        self.button_get_value.setVisible(True)
        self.button_hide_show.setText("Hide")

    def disable_display(self):
        self.display_enabled = False
        self.label_current_value.setVisible(False)
        self.label_port_number.setVisible(False)
        self.button_get_value.setVisible(False)
        self.button_hide_show.setText("Show")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))


class outputPortDisplay(gui.QWidget):
    def __init__(self,parent,num):
        super(outputPortDisplay,self).__init__(parent)
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
        self.label_port_number   = gui.QLineEdit(); self.label_port_number.setText("Output Port %i"%self.port)
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
            self.parent.connection[SERVER_NAME].select_device(self.parent.devID)
            response =  self.parent.connection[SERVER_NAME].set_voltage(self.port, value)
            print(response)
        except:
            print("Error: something went wrong. The device selected might not be a DCbox device.")

    def update_readout(self,value):
        self.label_current_value.setText(str(value))

class dac_adc_VFP_widget(gui.QWidget):
    def __init__(self,parent,connection,com,devID,IDGen):
        super(dac_adc_VFP_widget,self).__init__(parent)
        self.connection  = connection
        self.inListenId  = IDGen.next()
        self.outListenId = IDGen.next()
        self.device      = "%s (%s)"%(SERVER_NAME,com)
        self.com         = com
        self.devID       = devID

        self.inputPorts  = []
        self.outputPorts = []
        for port in range(4):
            self.inputPorts.append(inputPortDisplay(self,port))
            self.outputPorts.append(outputPortDisplay(self,port))

        self.hBoxInTop  = gui.QHBoxLayout(); self.hBoxInTop.setSpacing(0) ; self.hBoxInTop.setContentsMargins(0,0,0,0)
        self.hBoxInBot  = gui.QHBoxLayout(); self.hBoxInBot.setSpacing(0) ; self.hBoxInBot.setContentsMargins(0,0,0,0)
        self.hBoxOutTop = gui.QHBoxLayout(); self.hBoxOutTop.setSpacing(0); self.hBoxOutTop.setContentsMargins(0,0,0,0)
        self.hBoxOutBot = gui.QHBoxLayout(); self.hBoxOutBot.setSpacing(0); self.hBoxOutBot.setContentsMargins(0,0,0,0)

        self.hBoxInTop.addWidget(self.inputPorts[0])
        self.hBoxInTop.addWidget(self.inputPorts[1])
        self.hBoxInBot.addWidget(self.inputPorts[2])
        self.hBoxInBot.addWidget(self.inputPorts[3])
        
        self.hBoxOutTop.addWidget(self.outputPorts[0])
        self.hBoxOutTop.addWidget(self.outputPorts[1])
        self.hBoxOutBot.addWidget(self.outputPorts[2])
        self.hBoxOutBot.addWidget(self.outputPorts[3])

        self.vBoxIn  = gui.QVBoxLayout(); self.vBoxIn.setSpacing(0) ; self.vBoxIn.setContentsMargins(0,0,0,0)
        self.vBoxOut = gui.QVBoxLayout(); self.vBoxOut.setSpacing(0); self.vBoxOut.setContentsMargins(0,0,0,0)

        self.vBoxIn.addLayout(self.hBoxInTop)
        self.vBoxIn.addLayout(self.hBoxInBot)
        self.vBoxOut.addLayout(self.hBoxOutTop)
        self.vBoxOut.addLayout(self.hBoxOutBot)

        self.mainLayout = gui.QHBoxLayout(); self.mainLayout.setSpacing(0); self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.addLayout(self.vBoxIn)
        self.mainLayout.addLayout(self.vBoxOut)

        self.setLayout(self.mainLayout)

        self.connection[SERVER_NAME].signal__output_set(self.outListenId)
        self.connection[SERVER_NAME].signal__input_read(self.inListenId)

        self.connection._backend.cxn.addListener(self.out_update, self.connection[SERVER_NAME].ID, context=None, ID=self.outListenId)
        self.connection._backend.cxn.addListener(self.in_update , self.connection[SERVER_NAME].ID, context=None, ID=self.inListenId )

        self.connection[SERVER_NAME].select_device(self.devID)
        self.connection[SERVER_NAME].send_read_requests()

    def out_update(self,ctx,data):
        if ctx.ID[0] == self.devID:
            port = int(data[0])
            self.outputPorts[port].update_readout(data[1])

    def in_update(self,ctx,data):
        if ctx.ID[0] == self.devID:
            port = int(data[0])
            self.inputPorts[port].update_readout(data[1])

    def setEditingPermission(self,canEdit):
        for port in self.inputPorts+self.outputPorts:
            port.label_custom_name.setReadOnly(not canEdit)

