from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel 
from PyQt5.QtGui import QPixmap
from imagine_dl import Imagine

download = Imagine("config.json")
download.createSubredditInstance()
download.generateSubmissionIter()

class ImagineGui(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Imagine Image Downloader'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        
        # create save and next buttons
        self.save_btn = QPushButton('Save')
        self.next_btn = QPushButton('Next')

        self.save_btn.clicked.connect(lambda x: self.updateImage('save'))
        self.next_btn.clicked.connect(lambda x: self.updateImage('next'))

        # create button container and add buttons to it
        button_stack = QHBoxLayout() 
        button_stack.addWidget(self.save_btn)
        button_stack.addWidget(self.next_btn)
        
        # create image label
        self.labelImage = QLabel()
        self.updateImage('pass')

        # create main gui containers
        v_stack = QVBoxLayout()
        v_stack.addWidget(self.labelImage)
        v_stack.addLayout(button_stack)
        self.setLayout(v_stack)
        self.show()

        #run application until the user closes it

    def updateImage(self, opt):
        download.imageOption(opt)
        path = None
        while (path is None):
            path = download.imageSelection()
        pixmap = QPixmap(path)
        self.labelImage.setPixmap(pixmap.scaledToWidth(640))

app = QApplication([]) # application init
w = ImagineGui()
app.exec_()