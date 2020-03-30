from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel 
from PyQt5.QtGui import QPixmap
from imagine_dl import Imagine

download = Imagine("config.json")
download.createSubredditInstance()
download.generateSubmissionIter()
img = None
while img is None:
    img = download.imageSelection()

def saveImage():
    download.imageOption('s')
    global img
    img = download.imageSelection()



# QT Stuff Below
app = QApplication([]) # application init
window = QWidget() # base widget

# buttons
save_btn = QPushButton('Save')
next_btn = QPushButton('Next')
save_btn.clicked.connect(saveImage)

button_stack = QHBoxLayout() 
button_stack.addWidget(save_btn)
button_stack.addWidget(QPushButton('Set'))
button_stack.addWidget(next_btn)

labelImage = QLabel()
pixmap = QPixmap(img)
labelImage.setPixmap(pixmap)

v_stack = QVBoxLayout()
v_stack.addWidget(labelImage)
v_stack.addLayout(button_stack)

window.setLayout(v_stack)
window.show()
app.exec_() #run application until the user closes it
