from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import os
import sys
import time

# TODO:
# Only continue if valid webcam or valid picture is selected

class UI(QWidget):
    def setup(self, Controller):
        
        # Need multiple menuButtons for each 
        self.menuButton = QPushButton("Back to main menu")
        self.menuButton2 = QPushButton("Back to main menu")

        # Hold the widgets
        self.menu = QStackedLayout()
        
        # order matters
        self.menuSelection = QWidget()
        self.webcamSelection = QWidget()
        self.pictureSelection = QWidget()
        self.finalScreen = QWidget()

        # Call the functions here
        self.beginningMenu()
        self.webcamConfiguration()
        self.photoSelection()
        self.endScreen()

        # order matters!
        self.menu.addWidget(self.menuSelection)
        self.menu.addWidget(self.webcamSelection)
        self.menu.addWidget(self.pictureSelection)
        self.menu.addWidget(self.finalScreen)

    def beginningMenu(self):
        # This is in menu selection
        # BELOW: originally 550, 400
        self.menuSelection.resize(575, 400)

        self.mainLayout = QVBoxLayout()

        self.mainMenuTitle = QLabel(self.menuSelection)
        #BELOW: x val orig. 130, width val 300
        self.mainMenuTitle.setGeometry(QRect(130, -30, 320, 200))
        self.mainMenuTitle.setAlignment(Qt.AlignCenter)
        self.mainMenuTitle.setStyleSheet("font: 14pt Century Gothic")
        self.mainMenuTitle.setText("Start Menu")
        

        self.menuSelection.setWindowTitle("Unique Facial Feature Detection")
        self.CameraSettings = QPushButton('Camera Settings', self)
        self.CameraSettings.setToolTip('Change camera settings')

        # CameraSettings.clicked.connect(self.buttonClicked)

        self.ChoosePicture = QPushButton("Choose from files", self)
        self.ChoosePicture.setToolTip('Choose picture')

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.CameraSettings)
        self.buttonLayout.addWidget(self.ChoosePicture)
        
        self.quitButton = QPushButton('Quit', self)
        self.quitButton.clicked.connect(QApplication.instance().quit)
        self.buttonLayout.addWidget(self.quitButton)
        self.mainLayout.addLayout(self.buttonLayout)
        self.menuSelection.setLayout(self.mainLayout)

    def webcamConfiguration(self):

        self.webcamSelection.setWindowTitle("Unique Facial Feature Detection")
        # BELOW: originally 550, 400
        self.webcamSelection.resize(575, 400)

        self.webcamLayout = QHBoxLayout()

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            pass #quit

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.save_path = ""

        self.viewfinder = QCameraViewfinder()
        self.viewfinder.show()
        self.setCentralWidget(self.viewfinder)

        # Set the default camera.
        self.select_camera(0)

        # Setup tools
        camera_toolbar = QToolBar("Camera")
        camera_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(camera_toolbar)

        camera_selector = QComboBox()
        camera_selector.addItems([c.description() for c in self.available_cameras])
        camera_selector.currentIndexChanged.connect( self.select_camera )

        camera_toolbar.addWidget(camera_selector)

        self.webcamLayout.addWidget(self.menuButton) # back to main menu button

        self.continueSelectedWebcam = QPushButton("Continue", self)
        self.webcamLayout.addWidget(self.continueSelectedWebcam)

        self.webcamSelection.setLayout(self.webcamLayout)
        #self.show()

    def select_camera(self, i):
        self.camera = QCamera(self.available_cameras[i])
        self.camera.setViewfinder(self.viewfinder)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
        self.camera.start()

        self.capture = QCameraImageCapture(self.camera)
        self.capture.error.connect(lambda i, e, s: self.alert(s))
        self.capture.imageCaptured.connect(lambda d, i: self.status.showMessage("Image %04d captured" % self.save_seq))

        self.current_camera_name = self.available_cameras[i].description()
        self.save_seq = 0

    def photoSelection(self):

        self.pictureSelection.setWindowTitle("Unique Facial Feature Detection")
        # BELOW: originally 550, 400
        self.pictureSelection.resize(575, 400)

        # 320, 220

        self.pictureSelectionLayout = QHBoxLayout()
        self.pictureSelectionMainMenu = QVBoxLayout()
        self.pictureSelectionMainMenu.addWidget(self.menuButton2)

        self.selectPhotoButton = QPushButton("Select a picture", self)
        self.selectedPhotoContinue = QPushButton("Continue: ", self)
        self.pictureSelectionLayout.addWidget(self.selectPhotoButton)
        self.pictureSelectionLayout.addWidget(self.selectedPhotoContinue)


        self.selectedPhotoHelper = QLabel(self.pictureSelection)
        self.selectedPictureName = QLabel(self.pictureSelection)
        self.selectedPhotoHelper.setGeometry(QRect(160, -60, 300, 200))
        self.selectedPhotoHelper.setStyleSheet("font: 14pt Century Gothic")
        self.selectedPhotoHelper.setText("Selected photo is: ")

        # TODO: 
        # Add a gridlayout to separate return menu option

        self.pictureSelectionLayout.addLayout(self.pictureSelectionMainMenu)
        self.pictureSelection.setLayout(self.pictureSelectionLayout)

    # Choose a file
    def openPhoto(self):
        # options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Image files (*.jpg *.png)")
        if files:
            print(files)
            self.selectedPictureName.setGeometry(QRect(70, -30, 500, 200))
            self.selectedPictureName.setAlignment(Qt.AlignCenter)
            self.selectedPictureName.setStyleSheet("font: 10pt Century Gothic")
            self.selectedPictureName.setText(str(files))

            # TODO: Implement picture preview
            # self.picturePreview = QPixmap(str(files))
            # self.selectedPictureName.setPixmap(self.picturePreview)
            # self.setCentralWidget(self.selectedPictureName)
            # self.resize(self.picturePreview.width(), self.picturePreview.height())

    def endScreen(self):
        self.finalScreen.setWindowTitle("Unique Facial Feature Detection")
        # BELOW: originally 550, 400
        self.finalScreen.resize(575, 400)

        self.finalScreenBtnLayout = QHBoxLayout()
        self.menuButtonFinal = QPushButton("Restart")
        self.exitBtn = QPushButton("Quit")

        self.finalScreenBtnLayout.addWidget(self.menuButtonFinal)
        self.finalScreenBtnLayout.addWidget(self.exitBtn)
        

        self.finalScreenText = QLabel(self.finalScreen)
        self.finalScreenText.setStyleSheet("font: 14pt Century Gothic")
        self.finalScreenText.setText("Would you like to try again?")
        self.finalScreenText.setGeometry(QRect(30, -10, 500, 200))
        self.finalScreenText.setAlignment(Qt.AlignCenter)

        self.finalScreen.setLayout(self.finalScreenBtnLayout)



class Controller(QMainWindow, UI):
    def __init__(self):

        super().__init__()
        
        self.setup(self)
        
        
        # Sends back to main menu
        # Need separate widget for each window
        self.menuButton.clicked.connect(self.menuWindow)
        self.menuButton2.clicked.connect(self.menuWindow)

        # Menu buttons
        self.CameraSettings.clicked.connect(self.configureWebcamWindow)
        self.ChoosePicture.clicked.connect(self.choosePictureWindow)

        # Select photo button
        self.selectPhotoButton.clicked.connect(self.openPhoto)

        # Continue with selected photo 
        # TODO: CHANGE ENDSCREEN TO PHOTO PROCESSESSING
        self.continueSelectedWebcam.clicked.connect(self.goToEndScreen)
        self.selectedPhotoContinue.clicked.connect(self.goToEndScreen)

        # Final screen buttons
        self.menuButtonFinal.clicked.connect(self.menuWindow)
        self.exitBtn.clicked.connect(self.exitProgram)
        
        
    def menuWindow(self):
        self.menu.setCurrentIndex(0)

    def configureWebcamWindow(self):
        self.menu.setCurrentIndex(1)
        self.show()

    def choosePictureWindow(self):
        self.menu.setCurrentIndex(2)

    def goToEndScreen(self):
        self.menu.setCurrentIndex(3)

    def exitProgram(self):
        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Controller()
    sys.exit(app.exec_())
