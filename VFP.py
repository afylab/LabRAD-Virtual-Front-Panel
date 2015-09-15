from PyQt4 import QtCore as core, QtGui as gui
import sys,math,time

from devices.ad5764_dcbox_VFP import ad5764_dcbox_VFP_widget
from devices.ad5764_acbox_VFP import ad5764_acbox_VFP_widget

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

    def connect(self):
        import labrad
        firstAttempt=True
        success=connect=False
        while not success:
            if firstAttempt:pwd,ok=gui.QInputDialog.getText(self,"Password","Enter LabRAD password")
            else:pwd,ok=gui.QInputDialog.getText(self,"Password","Something went wrong. Either thepassword\nwas incorrect or LabRAD isn't running.")
            try:
                self.connection = labrad.connect(password = str(pwd))
                success=True;connect=True
            except:
                if pwd=='exit':success=True
            firstAttempt=False
        if connect:
            self.password = str(pwd)
            self.doUI()
        else:
            gui.qApp.quit()

    def timer_event(self):
        if self.ad5764_dcbox:
            dc_voltages = self.connection.ad5764_dcbox.get_voltages()
            for device in self.ad5764_dcbox_devices:
                device.update_readouts(dc_voltages)

        if self.ad5764_acbox:
            ac_voltages = self.connection.ad5764_acbox.get_voltages()
            for device in self.ad5764_acbox_devices:
                device.update_readouts(ac_voltages)

        

    def doUI(self):
        self.tabs=gui.QTabWidget(self)
        self.setCentralWidget(self.tabs)
        col = gui.QColor(223,242,243)
        self.tabs.setStyleSheet('QWidget { background-color: %s }'%col.name())

        servers = str(self.connection.servers).splitlines()
        #print(servers)

        self.ad5764_dcbox_devices = []
        if 'ad5764_dcbox' in servers:
            self.ad5764_dcbox = True
            devices = self.connection.serial_device_manager.list_ad5764_dcbox_devices()
            for device in devices:
                port = device[0]
                name = device[1][:-2]
                self.ad5764_dcbox_devices.append(ad5764_dcbox_VFP_widget(self,self.connection,port))
                self.tabs.addTab(self.ad5764_dcbox_devices[-1],name)
        else:self.ad5764_dcbox=False


        self.ad5764_acbox_devices = []
        if 'ad5764_acbox' in servers:
            self.ad5764_acbox=True
            devices = self.connection.serial_device_manager.list_ad5764_acbox_devices()
            for device in devices:
                port = device[0]
                name = device[1][:-2]
                self.ad5764_acbox_devices.append(ad5764_acbox_VFP_widget(self,self.connection,port))
                self.tabs.addTab(self.ad5764_acbox_devices[-1],name)
        else:self.ad5764_acbox=False

        self.setFixedSize((self.ll+self.bl)*4 + self.iw*3 + 6, (self.iw+self.ls)*2 + self.iw + 27)
        self.move(2,2)
        self.show()




if __name__=='__main__':
    app = gui.QApplication(sys.argv)
    i = interface()
    sys.exit(app.exec_())
