from PyQt4 import QtCore as core, QtGui as gui
import sys,math,time

from devices.ad5764_dcbox_VFP import ad5764_dcbox_VFP_widget
from devices.ad5764_acbox_VFP import ad5764_acbox_VFP_widget
from devices.widgets          import panelShell

global serverNameAD5764_DCBOX; serverNameAD5764_DCBOX = "ad5764_dcbox"
global serverNameAD5764_ACBOX; serverNameAD5764_ACBOX = "ad5764_acbox"

class interface(gui.QWidget):
    def __init__(self,ll=96,ls=23,iw=32,bl=75):
        super(interface,self).__init__()

        self.ll=ll
        self.ls=ls
        self.iw=iw
        self.bl=bl

        self.connect()

        self.timer = core.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timer_event)
        self.timer.start()
        

    def connect(self):
        import labrad
        self.connection = labrad.connect()        
        self.password = None
        self.doUI()
        #gui.qApp.quit()

    def timer_event(self):
        if self.ad5764_dcbox:
            for device in self.ad5764_dcbox_devices:
                device.childWidget.update_readouts()
            #dc_voltages = self.connection.ad5764_dcbox.get_voltages()
            #for device in self.ad5764_dcbox_devices:
            #    device.update_readouts(dc_voltages)

        if self.ad5764_acbox:
            ac_voltages = self.connection.ad5764_acbox.get_settings()
            for device in self.ad5764_acbox_devices:
                device.childWidget.update_readouts(ac_voltages)

    def does_directory_exist(self,directory):
        for end in range(1,len(directory)):
            self.connection.registry.cd(directory[:end])
            if not (directory[end] in self.connection.registry.dir()[0]):
                return False
        return True

    def fetch_devices(self,serverName):
        if not self.does_directory_exist(['','Servers',serverName,'Links']):
            print("The registry has not been set up to handle '%s' devices. Please make sure they are running, then use the Serial Device Manager client."%serverName)
            return []
        self.connection.registry.cd(['','Servers',serverName,'Links'])
        keys = self.connection.registry.dir()[1]
        return [[key,self.connection.registry.get(key)] for key in keys]

    def setEditingPermission(self,permission):
        if permission:
            for dev in self.ad5764_dcbox_devices+self.ad5764_acbox_devices:
                dev.setEditingEnabled(True)
                dev.childWidget.setEditingPermission(True)

        else:
            for dev in self.ad5764_dcbox_devices+self.ad5764_acbox_devices:
                dev.setEditingEnabled(False)
                dev.childWidget.setEditingPermission(False)

    def doUI(self):
        self.vBoxPanels = gui.QVBoxLayout()
        self.vBoxPanels.setSpacing(24)

        self.boxEditingPermission = gui.QCheckBox("Enable label editing",None)
        self.boxEditingPermission.setCheckState(2)
        self.boxEditingPermission.stateChanged.connect(self.setEditingPermission)
        self.vBoxPanels.addWidget(self.boxEditingPermission)

        servers = str(self.connection.servers).splitlines()
        #print(servers)

        self.ad5764_dcbox_devices = []
        if serverNameAD5764_DCBOX in servers:
            self.ad5764_dcbox = True
            devices = self.fetch_devices(serverNameAD5764_DCBOX)
            for device in devices:
                port = device[1][1]
                name = device[0]

                ad5764_dcbox_device = ad5764_dcbox_VFP_widget(self,self.connection,port)
                ad5764_dcbox_shell  = panelShell()
                ad5764_dcbox_shell.labelTitle.setText(name)
                ad5764_dcbox_shell.setChildWidget(ad5764_dcbox_device)
                
                self.ad5764_dcbox_devices.append(ad5764_dcbox_shell)
                self.vBoxPanels.addWidget(self.ad5764_dcbox_devices[-1])#,name)
        else:self.ad5764_dcbox=False


        self.ad5764_acbox_devices = []
        if serverNameAD5764_ACBOX in servers:
            self.ad5764_acbox=True
            devices = self.fetch_devices(serverNameAD5764_ACBOX)
            for device in devices:
                port = device[1][1]
                name = device[0]

                ad5764_acbox_device = ad5764_acbox_VFP_widget(self,self.connection,port)
                ad5764_acbox_shell  = panelShell()
                ad5764_acbox_shell.labelTitle.setText(name)
                ad5764_acbox_shell.setChildWidget(ad5764_acbox_device) 

                self.ad5764_acbox_devices.append(ad5764_acbox_VFP_widget(self,self.connection,port))
                self.vBoxPanels.addWidget(self.ad5764_acbox_devices[-1])#,name)
        else:self.ad5764_acbox=False

        self.layout = gui.QHBoxLayout()
        #self.layout.addWidget(self.)
        self.layout.addLayout(self.vBoxPanels)

        self.setLayout(self.layout)
        self.move(2,2)

        self.show()


if __name__=='__main__':
    app = gui.QApplication(sys.argv)
    i = interface()
    sys.exit(app.exec_())
