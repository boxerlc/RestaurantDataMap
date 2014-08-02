import sys
from PySide import QtGui, QtCore
#import CoordPlot
import Final
import density
import location
import googlemap

GenreList = ['Chinese', 'French', 'Japanese', 'Mexican', 'Italian', 'Korea']

class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        btn1 = QtGui.QPushButton("Show Basic", self)
        btn1.move(30, 100)
        btn1.clicked.connect(self.buttonClicked)

 	btn2 = QtGui.QPushButton("Show Google", self)
        btn2.move(150, 100)
        btn2.clicked.connect(self.buttonClicked)

	btn3 = QtGui.QPushButton("Show Location", self)
        btn3.move(30, 150)
        btn3.clicked.connect(self.buttonClicked)

	btn4 = QtGui.QPushButton("Show Density", self)
        btn4.move(150, 150)
        btn4.clicked.connect(self.buttonClicked)

        cb1 = QtGui.QCheckBox('Chinese', self)
        cb1.move(20, 20)
        cb1.toggle()
        cb1.stateChanged.connect(self.changeGenre)

        cb2 = QtGui.QCheckBox('French', self)
        cb2.move(100, 20)
        cb2.toggle()
        cb2.stateChanged.connect(self.changeGenre)

        cb3 = QtGui.QCheckBox('Japanese', self)
        cb3.move(180, 20)
        cb3.toggle()
        cb3.stateChanged.connect(self.changeGenre)

        cb4 = QtGui.QCheckBox('Mexican', self)
        cb4.move(20, 50)
        cb4.toggle()
        cb4.stateChanged.connect(self.changeGenre)

        cb5 = QtGui.QCheckBox('Italian', self)
        cb5.move(100, 50)
        cb5.toggle()
        cb5.stateChanged.connect(self.changeGenre)

        cb5 = QtGui.QCheckBox('Korea', self)
        cb5.move(180, 50)
        cb5.toggle()
        cb5.stateChanged.connect(self.changeGenre)

        self.statusBar()
        
        self.setGeometry(300, 300, 360, 300)
        self.setWindowTitle('NY Resaurant Data Visualizer V1.1')
        self.show()
        
    def buttonClicked(self):
      
        sender = self.sender()
        if sender.text() == "Show Basic":
            Final.show_regular(GenreList)
	if sender.text() == "Show Google":
            googlemap.show_google(GenreList)
	if sender.text() == "Show Location":
            if len(GenreList) == 1:
		self.statusBar().showMessage('')            	
		location.show_location(GenreList[0])
	    else:
		self.statusBar().showMessage('Only Accept One Input!')	
	if sender.text() == "Show Density":
            if len(GenreList) == 1:
		self.statusBar().showMessage('')
            	density.show_density(GenreList[0])
	    else:
		self.statusBar().showMessage('Only Accept One Input!')
    def changeGenre(self,state):
        item = self.sender().text()
        if state == QtCore.Qt.Checked:
            GenreList.append(item)
        else:
            GenreList.remove(item)
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
