from PyQt4 import QtCore as core, QtGui as gui
import sys,math,time

from devices.ad5764_dcbox_VFP import ad5764_dcbox_VFP_widget

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

        voltages = self.connection.ad5764_dcbox.get_voltages()
        for device in self.ad5764_dcbox_devices:
            device.update_readouts(voltages)

    def doUI(self):
        self.tabs=gui.QTabWidget(self)
        self.setCentralWidget(self.tabs)
        col = gui.QColor(223,242,243)
        self.tabs.setStyleSheet('QWidget { background-color: %s }'%col.name())

        servers = str(self.connection.servers).splitlines()
        print(servers)

        self.ad5764_dcbox_devices = []
        if 'ad5764_dcbox' in servers:
            devices = self.connection.ad5764_dcbox.list_devices()
            for device in devices:
                if '4' in device[1]:
                    com = device[1].partition('(')[2][:-1]
                    self.ad5764_dcbox_devices.append(ad5764_dcbox_VFP_widget(self,self.connection,device,com))
                    self.tabs.addTab(self.ad5764_dcbox_devices[-1],device[1])

        self.setFixedSize((self.ll+self.bl)*4 + self.iw*3 + 6, (self.iw+self.ls)*2 + self.iw + 27)
        self.move(2,2)
        self.show()




if __name__=='__main__':
    app = gui.QApplication(sys.argv)
    i = interface()
    sys.exit(app.exec_())