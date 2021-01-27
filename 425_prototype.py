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

        mainLayout = QVBoxLayout()

        mainMenuTitle = QLabel(self.menuSelection)
        #BELOW: x val orig. 130, width val 300
        mainMenuTitle.setGeometry(QRect(130, -30, 320, 200))
        mainMenuTitle.setAlignment(Qt.AlignCenter)
        mainMenuTitle.setStyleSheet("font: 14pt Century Gothic")
        mainMenuTitle.setText("Start Menu")
        

        self.menuSelection.setWindowTitle("Unique Facial Feature Detection")
        CameraSettings = QPushButton('Camera Settings', self)
        CameraSettings.setToolTip('Change camera settings')

        ChoosePicture = QPushButton("Choose from files", self)
        ChoosePicture.setToolTip('Choose picture')

        # Menu buttons
        CameraSettings.clicked.connect(self.configureWebcamWindow)
        ChoosePicture.clicked.connect(self.choosePictureWindow)


        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(CameraSettings)
        buttonLayout.addWidget(ChoosePicture)
        
        quitButton = QPushButton('Quit', self)
        quitButton.clicked.connect(QApplication.instance().quit)
        buttonLayout.addWidget(quitButton)
        mainLayout.addLayout(buttonLayout)
        self.menuSelection.setLayout(mainLayout)

    def webcamConfiguration(self):

        self.webcamSelection.setWindowTitle("Unique Facial Feature Detection")
        # BELOW: originally 550, 400
        self.webcamSelection.resize(575, 400)

        webcamLayout = QHBoxLayout()

        # TODO: Only turn on camera once we configure camera? 

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            pass #quit

        status = QStatusBar()
        self.setStatusBar(status)

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

        webcamLayout.addWidget(self.menuButton) # back to main menu button

        continueSelectedWebcam = QPushButton("Continue", self)

        # TODO: CHANGE ENDSCREEN TO PHOTO PROCESSESSING
        continueSelectedWebcam.clicked.connect(self.goToEndScreen)

        webcamLayout.addWidget(continueSelectedWebcam)
        self.webcamSelection.setLayout(webcamLayout)
        #self.show()

    def select_camera(self, i):
        
        # Not sure which of the "self"s we need so ima keep it :)
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

        pictureSelectionLayout = QHBoxLayout()
        pictureSelectionMainMenu = QVBoxLayout()
        pictureSelectionMainMenu.addWidget(self.menuButton2)

        selectPhotoButton = QPushButton("Select a picture", self)
        selectedPhotoContinue = QPushButton("Continue: ", self)
        pictureSelectionLayout.addWidget(selectPhotoButton)
        pictureSelectionLayout.addWidget(selectedPhotoContinue)

        # Select photo button
        selectPhotoButton.clicked.connect(self.openPhoto)
        selectedPhotoContinue.clicked.connect(self.goToEndScreen)

        selectedPhotoHelper = QLabel(self.pictureSelection)
        self.selectedPictureName = QLabel(self.pictureSelection)
        selectedPhotoHelper.setGeometry(QRect(160, -60, 300, 200))
        selectedPhotoHelper.setStyleSheet("font: 14pt Century Gothic")
        selectedPhotoHelper.setText("Selected photo is: ")

        # TODO: 
        # Add a gridlayout to separate return menu option

        pictureSelectionLayout.addLayout(pictureSelectionMainMenu)
        self.pictureSelection.setLayout(pictureSelectionLayout)

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

        finalScreenBtnLayout = QHBoxLayout()
        menuButtonFinal = QPushButton("Restart")
        exitBtn = QPushButton("Quit")

        finalScreenBtnLayout.addWidget(menuButtonFinal)
        finalScreenBtnLayout.addWidget(exitBtn)
        

        finalScreenText = QLabel(self.finalScreen)
        finalScreenText.setStyleSheet("font: 14pt Century Gothic")
        finalScreenText.setText("Would you like to try again?")
        finalScreenText.setGeometry(QRect(30, -10, 500, 200))
        finalScreenText.setAlignment(Qt.AlignCenter)

        # Final screen buttons
        menuButtonFinal.clicked.connect(self.menuWindow)
        exitBtn.clicked.connect(self.exitProgram)
      

        self.finalScreen.setLayout(finalScreenBtnLayout)



class Controller(QMainWindow, UI):
    def __init__(self):

        super().__init__()
        
        self.setup(self)
        
        
        # Sends back to main menu
        # Need separate widget for each window
        # TODO: Figure out how to only have 1 menu button

        self.menuButton.clicked.connect(self.menuWindow)
        self.menuButton2.clicked.connect(self.menuWindow)

       
        
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
