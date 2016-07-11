from PyQt4 import QtCore as core, QtGui as gui
import sys,math,time

from devices.ad5764_dcbox_VFP import ad5764_dcbox_VFP_widget
from devices.ad5764_acbox_VFP import ad5764_acbox_VFP_widget
from devices.quad_ad5780_VFP  import quad_ad5780_VFP_widget
from devices.widgets          import panelShell

global serverNameAD5764_DCBOX; serverNameAD5764_DCBOX = "ad5764_dcbox"
global serverNameAD5764_ACBOX; serverNameAD5764_ACBOX = "ad5764_acbox"
global serverNameQuadAD5780  ; serverNameQuadAD5780   = "dcbox_quad_ad5780"

def listenerIDGen():
    ID = 10000
    while True:
        yield ID
        ID += 1

class interface(gui.QWidget):
    def __init__(self,ll=96,ls=23,iw=32,bl=75):
        super(interface,self).__init__()
        self.ID = listenerIDGen()
        self.connect()

    def connect(self):
        import labrad
        self.connection = labrad.connect()        
        self.password = None
        self.doUI()
        #gui.qApp.quit()

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
            for dev in self.ad5764_dcbox_devices+self.ad5764_acbox_devices+self.quad_ad5780_devices:
                dev.setEditingEnabled(True)
                dev.childWidget.setEditingPermission(True)

        else:
            for dev in self.ad5764_dcbox_devices+self.ad5764_acbox_devices+self.quad_ad5780_devices:
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
                port  = device[1][1]
                name  = device[0]
                devID = [dev[0] for dev in self.connection[serverNameAD5764_DCBOX].list_devices() if port in dev[1]][0]
                #print(devID)

                ad5764_dcbox_device = ad5764_dcbox_VFP_widget(self,self.connection,port,devID,self.ID)
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
                port  = device[1][1]
                name  = device[0]
                devID = [dev[0] for dev in self.connection[serverNameAD5764_ACBOX].list_devices() if port in dev[1]][0]
                #print(devID)

                ad5764_acbox_device = ad5764_acbox_VFP_widget(self,self.connection,port,devID,self.ID)
                ad5764_acbox_shell  = panelShell()
                ad5764_acbox_shell.labelTitle.setText(name)
                ad5764_acbox_shell.setChildWidget(ad5764_acbox_device) 

                self.ad5764_acbox_devices.append(ad5764_acbox_shell)
                self.vBoxPanels.addWidget(self.ad5764_acbox_devices[-1])#,name)
        else:self.ad5764_acbox=False

        self.quad_ad5780_devices = []
        if serverNameQuadAD5780 in servers:
            self.quad_ad5780 = True
            devices = self.fetch_devices(serverNameQuadAD5780)
            for device in devices:
                port  = device[1][1]
                name  = device[0]
                #print(device)
                #print(port)
                devID = [dev[0] for dev in self.connection[serverNameQuadAD5780].list_devices() if port in dev[1]][0]
                quad_ad5780_device = quad_ad5780_VFP_widget(self,self.connection,port,devID,self.ID)
                quad_ad5780_shell  = panelShell()
                quad_ad5780_shell.labelTitle.setText(name)
                quad_ad5780_shell.setChildWidget(quad_ad5780_device)

                self.quad_ad5780_devices.append(quad_ad5780_shell)
                self.vBoxPanels.addWidget(self.quad_ad5780_devices[-1])
        else:self.quad_ad5780=False


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
