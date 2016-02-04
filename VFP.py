from PyQt4 import QtCore as core, QtGui as gui
import sys,math,time

from devices.ad5764_dcbox_VFP import ad5764_dcbox_VFP_widget
from devices.ad5764_acbox_VFP import ad5764_acbox_VFP_widget

global serverNameAD5764_DCBOX; serverNameAD5764_DCBOX = "ad5764_dcbox"
global serverNameAD5764_ACBOX; serverNameAD5764_ACBOX = "ad5764_acbox"

class interface(gui.QMainWindow):
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
        self.tab_changed()

    def connect(self):
        import labrad
        self.connection = labrad.connect()        
        self.password = None
        self.doUI()
        #gui.qApp.quit()

    def timer_event(self):
        if self.ad5764_dcbox:
            for device in self.ad5764_dcbox_devices:
                device.update_readouts()
            #dc_voltages = self.connection.ad5764_dcbox.get_voltages()
            #for device in self.ad5764_dcbox_devices:
            #    device.update_readouts(dc_voltages)

        if self.ad5764_acbox:
            ac_voltages = self.connection.ad5764_acbox.get_settings()
            for device in self.ad5764_acbox_devices:
                device.update_readouts(ac_voltages)

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

    def doUI(self):
        self.tabs=gui.QTabWidget(self)
        self.setCentralWidget(self.tabs)
        col = gui.QColor(223,242,243)
        self.tabs.setStyleSheet('QWidget { background-color: %s }'%col.name())
        self.tabs.currentChanged.connect(self.tab_changed)

        servers = str(self.connection.servers).splitlines()
        #print(servers)

        self.ad5764_dcbox_devices = []
        if serverNameAD5764_DCBOX in servers:
            self.ad5764_dcbox = True
            devices = self.fetch_devices(serverNameAD5764_DCBOX)
            for device in devices:
                port = device[1][1]
                name = device[0]
                self.ad5764_dcbox_devices.append(ad5764_dcbox_VFP_widget(self,self.connection,port))
                self.tabs.addTab(self.ad5764_dcbox_devices[-1],name)
        else:self.ad5764_dcbox=False


        self.ad5764_acbox_devices = []
        if serverNameAD5764_ACBOX in servers:
            self.ad5764_acbox=True
            devices = self.fetch_devices(serverNameAD5764_ACBOX)
            for device in devices:
                port = device[1][1]
                name = device[0]
                self.ad5764_acbox_devices.append(ad5764_acbox_VFP_widget(self,self.connection,port))
                self.tabs.addTab(self.ad5764_acbox_devices[-1],name)
        else:self.ad5764_acbox=False

        self.setFixedSize((self.ll+self.bl)*4 + self.iw*3 + 6, (self.iw+self.ls)*2 + self.iw + 27)
        self.move(2,2)
        self.show()

    def tab_changed(self):
        size = self.tabs.currentWidget().size
        self.setFixedSize(size[0],size[1])


if __name__=='__main__':
    app = gui.QApplication(sys.argv)
    i = interface()
    sys.exit(app.exec_())
