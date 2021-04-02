from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import os
import sys
import time
import cv2

sys.path.append('./backend/')
# Optimally but both functions into one file
# Allow manual face alignment
from FaceAlignmentv2 import FaceAlignmentManual
# Allow algorithm to do it automatically
from FaceAlignment import FaceAlignmentAuto


# TODO:
# Only continue if valid webcam or valid picture is selected
# Fix screen name convention (menuSelection, webcamSelection)..

# Notes:
# Webcam photos save in default "photos" if folder isn't selected
# Should save in folder where facial alignment algorithm would work
# Don't show click button until camera is shown?
# Flow -> Select a photo or webcam, send to facial alignment, finish in Bryson's Algorithm
# Smaller image size than 500 kb? Currently have smaller than 1 MB
# 

# TODO:
# IMPLEMENT MULTITHREADING SO PROGRAM WON'T FREEZE WHEN GETTING FACE ALIGNMENT
# https://www.learnpyqt.com/tutorials/multithreading-pyqt-applications-qthreadpool/
# class Worker(QRunnable):


#    @pyqtSlot()
#        def run(self):
#        print ("hi")
#        time.sleep(5)
#        print ("complete")

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
        self.resizeSelectedPictureProcessing = QWidget()
        self.resizeSelectedPicture = QWidget()

        # Make sure finalScreen ends up as last widget
        self.photoProcessingScreen = QWidget()
        self.photoProcessedScreen = QWidget()
        self.featuresListScreen = QWidget()
        self.caricatureCreationScreen = QWidget()
        self.finalScreen = QWidget()

        # Call the functions here
        self.beginningMenu()
        self.webcamConfiguration()
        self.photoSelection()
#        self.resizingPictureProcessing()
        self.resizingPicture()
        self.photoProcessing()
        self.photoProcessed()
        self.featuresList()
        self.caricatureCreation()
        self.endScreen()

        # order matters!
        self.menu.addWidget(self.menuSelection)
        self.menu.addWidget(self.webcamSelection)
        self.menu.addWidget(self.pictureSelection)
        # self.menu.addWidget(self.resizeSelectedPictureProcessing)
        self.menu.addWidget(self.resizeSelectedPicture)
        self.menu.addWidget(self.photoProcessingScreen)
        self.menu.addWidget(self.photoProcessedScreen)
        self.menu.addWidget(self.featuresListScreen)
        self.menu.addWidget(self.caricatureCreationScreen)
        self.menu.addWidget(self.finalScreen)

    # menu selection
    def beginningMenu(self):

        self.menuSelection.resize(575, 400)

        mainLayout = QVBoxLayout()

        mainMenuTitle = QLabel(self.menuSelection)
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
        self.webcamSelection.resize(575, 400)

        # setting style sheet 
        self.setStyleSheet("background : lightgrey;") 
  
        # getting available cameras 
        self.available_cameras = QCameraInfo.availableCameras() 
  
        # if no camera found 
        if not self.available_cameras: 
            # exit the code 
            pass
  
        # creating a status bar 
        self.status = QStatusBar() 
  
        # setting style sheet to the status bar 
        self.status.setStyleSheet("background : white;") 
  
        # adding status bar to the main window 
        self.setStatusBar(self.status) 
  
        # path to save 
        self.save_path = "" 
  
        # creating a QCameraViewfinder object 
        self.viewfinder = QCameraViewfinder() 
  
        # showing this viewfinder 
        #self.viewfinder.show() 
  
        # making it central widget of main window 
        #self.setCentralWidget(self.viewfinder) 
  
        # Set the default camera. 
        self.select_camera(0) 
  
        # creating a tool bar 
        toolbar = QToolBar("Camera Tool Bar") 
  
        # adding tool bar to main window 
        self.addToolBar(toolbar) 

        # creating a show viewfinder action
        show_viewfinder = QAction("Show", self)

        # add action to it
        show_viewfinder.triggered.connect(self.show_cam)

        # adding it to tool bar
        toolbar.addAction(show_viewfinder)
  
        # creating a photo action to take photo 
        click_action = QAction("Click photo", self) 
  
        # adding status tip to the photo action 
        click_action.setStatusTip("This will capture picture") 
  
        # adding tool tip 
        click_action.setToolTip("Capture picture") 
  
  
        # adding action to it 
        # calling take_photo method 
        click_action.triggered.connect(self.click_photo) 
  
        # adding this to the tool bar 
        toolbar.addAction(click_action) 
  
        # similarly creating action for changing save folder 
        change_folder_action = QAction("Change save location", self) 
  
        # adding status tip 
        change_folder_action.setStatusTip("Change folder where picture will be saved saved.") 
  
        # adding tool tip to it 
        change_folder_action.setToolTip("Change save location") 
  
        # setting calling method to the change folder action 
        # when triggered signal is emitted 
        change_folder_action.triggered.connect(self.change_folder) 
  
        # adding this to the tool bar 
        toolbar.addAction(change_folder_action) 
  
  
        # creating a combo box for selecting camera 
        camera_selector = QComboBox() 
  
        # adding status tip to it 
        camera_selector.setStatusTip("Choose camera to take pictures") 
  
        # adding tool tip to it 
        camera_selector.setToolTip("Select Camera") 
        camera_selector.setToolTipDuration(2500) 
  
        # adding items to the combo box 
        camera_selector.addItems([camera.description() 
                                  for camera in self.available_cameras]) 
  
        # adding action to the combo box 
        # calling the select camera method 
        camera_selector.currentIndexChanged.connect(self.select_camera) 
  
        # adding this to tool bar 
        toolbar.addWidget(camera_selector) 
  
        # setting tool bar stylesheet 
        toolbar.setStyleSheet("background : white;") 
  
        webcamLayout = QHBoxLayout()
        webcamLayout.addWidget(self.menuButton) # back to main menu button

        continueSelectedWebcam = QPushButton("Continue", self)
        continueSelectedWebcam.clicked.connect(self.photoProcessingWindow)

        webcamLayout.addWidget(continueSelectedWebcam)
        self.webcamSelection.setLayout(webcamLayout)

    # method to show viewfinder
    def show_cam(self):
        # showing this viewfinder 
        self.viewfinder.show() 
  
        # making it central widget of main window 
        self.setCentralWidget(self.viewfinder) 

    # method to select camera 
    def select_camera(self, i): 
  
        # getting the selected camera 
        self.camera = QCamera(self.available_cameras[i]) 
  
        # setting view finder to the camera 
        self.camera.setViewfinder(self.viewfinder) 
  
        # setting capture mode to the camera 
        self.camera.setCaptureMode(QCamera.CaptureStillImage) 
  
        # if any error occur show the alert 
        self.camera.error.connect(lambda: self.alert(self.camera.errorString())) 
  
        # start the camera 
        # self.camera.start() 
  
        # creating a QCameraImageCapture object 
        self.capture = QCameraImageCapture(self.camera) 
  
        # showing alert if error occur 
        self.capture.error.connect(lambda error_msg, error, 
                                   msg: self.alert(msg)) 
  
        # when image captured showing message 
        self.capture.imageCaptured.connect(lambda d, 
                                           i: self.status.showMessage("Image captured : " 
                                                                      + str(self.save_seq))) 
  
        # getting current camera name 
        self.current_camera_name = self.available_cameras[i].description() 
  
        # inital save sequence 
        self.save_seq = 0
  
    # method to take photo 
    def click_photo(self): 
  
        # time stamp 
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S") 
  
        # capture the image and save it on the save path 
        self.capture.capture(os.path.join(self.save_path,  
                                          "%s-%04d-%s.jpg" % ( 
            self.current_camera_name, 
            self.save_seq, 
            timestamp 
        ))) 
  
        # increment the sequence 
        self.save_seq += 1
  
    # change folder method 
    def change_folder(self): 
  
        # open the dialog to select path 
        path = QFileDialog.getExistingDirectory(self,  
                                                "Picture Location", "") 
  
        # if path is selected 
        if path: 
  
            # update the path 
            self.save_path = path 
  
            # update the sequence 
            self.save_seq = 0
  
    # method for alerts 
    def alert(self, msg): 
  
        # error message 
        error = QErrorMessage(self) 
  
        # setting text to the error message 
        error.showMessage(msg)

    def photoSelection(self):

        self.pictureSelection.setWindowTitle("Unique Facial Feature Detection")

        self.pictureSelection.resize(575, 400)

        pictureSelectionLayout = QVBoxLayout()
        pictureSelectionMainMenu = QHBoxLayout()
        pictureSelectionMainMenu.addWidget(self.menuButton2)

        selectPhotoButton = QPushButton("Select a picture", self)
        selectedPhotoContinue = QPushButton("Continue: ", self)
        pictureSelectionMainMenu.addWidget(selectPhotoButton)
        pictureSelectionMainMenu.addWidget(selectedPhotoContinue)

        # Select photo button
        selectPhotoButton.clicked.connect(self.openPhoto)

        # Go to resizing window
        selectedPhotoContinue.clicked.connect(self.startFaceAlignmentAuto)

        selectedPhotoHelper = QLabel(self.pictureSelection)
        self.selectedPictureName = QLabel(self.pictureSelection)

        selectedPhotoHelper.setGeometry(QRect(160, -60, 300, 200))
        selectedPhotoHelper.setStyleSheet("font: 14pt Century Gothic")
        selectedPhotoHelper.setText("Selected photo is: ")

        self.selectedPictureLocation = ""
        
        pictureDisplayLayout = QVBoxLayout()
        pictureDisplayLayout.addWidget(selectedPhotoHelper)
        pictureDisplayLayout.addWidget(self.selectedPictureName)

        
        pictureSelectionLayout.addLayout(pictureDisplayLayout)
        pictureSelectionLayout.addLayout(pictureSelectionMainMenu)

        self.pictureSelection.setLayout(pictureSelectionLayout)

    def startFaceAlignmentAuto(self):
        self.resizingProcessedWindow()
        FaceAlignmentAuto(self.selectedPictureLocation)

        # Setting the cropped img once FaceAlignment is done
        # Need to think of this when we use multiple photos
        self.croppedImg = QPixmap("./backend/ResizedImages/newCropped.jpeg")
        self.resizingPictureDisplayLabel.setPixmap(self.croppedImg)
        print(self.selectedPictureLocation)

    def startFaceAlignmentManual(self):
        FaceAlignmentManual(self.selectedPictureLocation)
        # Resetting the photo on screen
        self.croppedImg = QPixmap("./backend/ResizedImages/newCropped.jpeg")
        self.resizingPictureDisplayLabel.setPixmap(self.croppedImg)
        
       
    # Choose a file
    def openPhoto(self):
        # options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Image files (*.jpg *.png)")
        if files:
            self.selectedPictureName.setGeometry(QRect(70, -30, 500, 200))
            self.selectedPictureName.setAlignment(Qt.AlignCenter)
            self.selectedPictureName.setStyleSheet("font: 10pt Century Gothic")
            
            picturePreview = QPixmap(files[0])
            self.selectedPictureName.setPixmap(picturePreview.scaled(self.selectedPictureName.width() * 2, self.selectedPictureName.height() * 2, Qt.KeepAspectRatio))

            self.selectedPictureLocation = files[0]


            
            # Incorporate/mix Jazel's code here
            # We send cropped photo through Jazel's code to send to Bryson's Algorithm


    # This screen will have a loading screen when the face alignment algorithm is happening
    # THIS NEEDS TO RUN WITH MULTITHREADING(?)
    def resizingPictureProcessing(self):
        self.resizeSelectedPictureProcessing.setWindowTitle("Unique Facial Feature Detection")
        self.resizeSelectedPictureProcessing.resize(575, 400)


        # Add label to say what is happening
        spinnerLabel = QLabel(self.resizeSelectedPictureProcessing)
        spinnerLabel.setGeometry(QRect(270, 120, 30, 30))
        spinnerLabel.setScaledContents(True)
        spinner = QMovie("static/spinner.gif")
        spinnerLabel.setMovie(spinner)
        spinner.start()
        


    # This screen will show after, giving the option to the user to manually align
    def resizingPicture(self):
        self.resizeSelectedPicture.setWindowTitle("Unique Facial Feature Detection")
        self.resizeSelectedPicture.resize(575, 400)
       
        # Outer layout
        resizingPictureLayout = QVBoxLayout()

        # Photo picked from user
        self.croppedImg = QPixmap("")
        self.resizingPictureDisplayLabel = QLabel(self.resizeSelectedPicture)
        self.resizingPictureDisplayLabel.setAlignment(Qt.AlignCenter)
        self.resizingPictureDisplayLabel.setStyleSheet("padding: 30px")
        resizingPictureDisplayLayout = QVBoxLayout()
        croppedTitle = QLabel(self.resizeSelectedPicture)
        croppedTitle.setAlignment(Qt.AlignCenter)
        croppedTitle.setStyleSheet("font: 14pt Century Gothic")
        croppedTitle.setText("Your Cropped Photo:")

        # SHOULD MAKE THIS WARNING A TOOLTIP WARNING
        croppedWarning = QLabel(self.resizeSelectedPicture)
        croppedWarning.setAlignment(Qt.AlignCenter)
        croppedWarning.setStyleSheet("font: 10pt Century Gothic")
        croppedWarning.setText("Note: Your photo will automatically adjust to 178x218")

        resizingPictureDisplayLayout.addWidget(croppedTitle)
        resizingPictureDisplayLayout.addWidget(croppedWarning)
        resizingPictureDisplayLayout.addWidget(self.resizingPictureDisplayLabel) 


        # Buttons
        resizingPictureBtnLayout = QHBoxLayout()
        repeatResizingPicture = QPushButton("Manually Crop Photo", self) 
        finishedResizingPhotoButton = QPushButton("Continue", self)

        resizingPictureBtnLayout.addWidget(repeatResizingPicture)
        resizingPictureBtnLayout.addWidget(finishedResizingPhotoButton)
       

        resizingPictureLayout.addLayout(resizingPictureDisplayLayout)
        resizingPictureLayout.addLayout(resizingPictureBtnLayout)

        
        self.resizeSelectedPicture.setLayout(resizingPictureLayout)
    
        repeatResizingPicture.clicked.connect(self.startFaceAlignmentManual)
        finishedResizingPhotoButton.clicked.connect(self.photoProcessingWindow)

        

    def endScreen(self):
        self.finalScreen.setWindowTitle("Unique Facial Feature Detection")
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

    # MIGHT NOT EVEN NEED IF PROCESSING IS TOO FAST
    def photoProcessing(self):
        self.photoProcessingScreen.setWindowTitle("Unique Facial Feature Detection")
        self.photoProcessingScreen.resize(575, 400)

        photoProcessingBtnLayout = QHBoxLayout()

        # Spinner animation
        spinnerLabel = QLabel(self.photoProcessingScreen)
        spinnerLabel.setGeometry(QRect(270, 120, 30, 30))
        spinnerLabel.setScaledContents(True)
        spinner = QMovie("static/spinner.gif")
        spinnerLabel.setMovie(spinner)
        spinner.start()

        obtainingFeaturesText = QLabel(self.photoProcessingScreen)
        obtainingFeaturesText.setStyleSheet("font: 14pt Century Gothic")
        obtainingFeaturesText.setText("Obtaining unique features...")
        obtainingFeaturesText.setGeometry(QRect(30, -10, 500, 200))
        obtainingFeaturesText.setAlignment(Qt.AlignCenter)

        photoProcessedBtn = QPushButton("Continue") 
        photoProcessingBtnLayout.addWidget(photoProcessedBtn)

        photoProcessedBtn.clicked.connect(self.photoProcessedWindow)


        self.photoProcessingScreen.setLayout(photoProcessingBtnLayout)
        


        #TODO:
        # Only put continue if features have been extracted
        # Allow back button??

        # spinner.stop()

    # Menu to choose feature list or create a caricature
    def photoProcessed(self):
        self.photoProcessedScreen.setWindowTitle("Unique Facial Feature Detection")
        self.photoProcessedScreen.resize(575, 400)

        obtainedFeaturesText= QLabel(self.photoProcessedScreen)
        obtainedFeaturesText.setStyleSheet("font: 14pt Century Gothic")
        obtainedFeaturesText.setText("Obtained unique features!")
        obtainedFeaturesText.setGeometry(QRect(30, -10, 500, 200))
        obtainedFeaturesText.setAlignment(Qt.AlignCenter)


        # Two buttons here for Feature List or Caricature
        photoProcessedBtnLayout = QHBoxLayout()
        getFeaturesListBtn = QPushButton("Get unique feature's list!")
        createCaricatureBtn = QPushButton("Create a caricature!")

        photoProcessedBtnLayout.addWidget(getFeaturesListBtn)
        photoProcessedBtnLayout.addWidget(createCaricatureBtn)

        getFeaturesListBtn.clicked.connect(self.featuresListWindow)
        createCaricatureBtn.clicked.connect(self.caricatureCreationWindow)

        self.photoProcessedScreen.setLayout(photoProcessedBtnLayout)

    # Display feature list
    def featuresList(self):
        self.featuresListScreen.setWindowTitle("Unique Facial Feature Detection")
        self.featuresListScreen.resize(575, 400)

        featuresLayout = QVBoxLayout()
        # Hold save and continue button
        featuresBtnLayout = QHBoxLayout()

        obtainedFeaturesList = QLabel(self.photoProcessedScreen)
        obtainedFeaturesList.setStyleSheet("font: 14pt Century Gothic")
        obtainedFeaturesList.setText("Your unique features!")
        # obtainedFeaturesList.setGeometry(QRect(30, -10, 500, 200))
        obtainedFeaturesList.setAlignment(Qt.AlignCenter)

        featuresLayout.addWidget(obtainedFeaturesList)


        # Display features

        featuresList = QPixmap("static/SampleFeatures")

        featuresListLabel = QLabel(self.photoProcessedScreen)
        featuresListLabel.setPixmap(featuresList)

        featuresLayout.addWidget(featuresListLabel)


        # Allow save option
        # Save in .txt format is probably preferable
        # saveListBtn does nothing for now, will implement when we tie in unique algorithm
        saveListBtn = QPushButton("Save unique features list")
        continueBtn = QPushButton("Continue")

        featuresBtnLayout.addWidget(saveListBtn)
        featuresBtnLayout.addWidget(continueBtn)

        # Go to end screen
        continueBtn.clicked.connect(self.goToEndWindow)

        featuresLayout.addLayout(featuresBtnLayout)
        self.featuresListScreen.setLayout(featuresLayout)

    def caricatureCreation(self):
        # TODO:
        # Shorten names pleeeeeeeeeeeeeeeeeeeeez

        self.caricatureCreationScreen.setWindowTitle("Unique Facial Feature Detection")
        self.caricatureCreationScreen.resize(575, 400)

        caricatureCreationLayout = QVBoxLayout()
        caricatureCreationBtnLayout = QHBoxLayout()

        createdCaricatureText = QLabel(self.photoProcessedScreen)
        createdCaricatureText.setStyleSheet("font: 14pt Century Gothic")
        createdCaricatureText.setText("Your caricature!")
        # obtainedFeaturesList.setGeometry(QRect(30, -10, 500, 200))
        createdCaricatureText.setAlignment(Qt.AlignCenter)

        caricatureCreationLayout.addWidget(createdCaricatureText)

        createdCaricature = QPixmap("static/SampleCaricature")
        createdCaricatureLabel = QLabel(self.caricatureCreationScreen)
        createdCaricatureLabel.setAlignment(Qt.AlignCenter)
        createdCaricatureLabel.setPixmap(createdCaricature)


        caricatureCreationLayout.addWidget(createdCaricatureLabel)

        saveListBtn = QPushButton("Save caricature")
        continueBtn = QPushButton("Continue")

        caricatureCreationBtnLayout.addWidget(saveListBtn)
        caricatureCreationBtnLayout.addWidget(continueBtn)

        continueBtn.clicked.connect(self.goToEndWindow)
        caricatureCreationLayout.addLayout(caricatureCreationBtnLayout)
        self.caricatureCreationScreen.setLayout(caricatureCreationLayout)

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

    # REFER TO ABOVE ABOUT MULTITHREADING
    # def resizingPhotoProcessingWindow(self):
        # self.menu.setCurrentIndex(3)

    def resizingProcessedWindow(self):
        self.menu.setCurrentIndex(3)

    # Choose for caricature or just a list
    def photoProcessingWindow(self):
        self.menu.setCurrentIndex(4)

    def photoProcessedWindow(self):
        self.menu.setCurrentIndex(5)

    def featuresListWindow(self):
        self.menu.setCurrentIndex(6)

    def caricatureCreationWindow(self):
        self.menu.setCurrentIndex(7)

    def goToEndWindow(self):
        self.menu.setCurrentIndex(8)
     


    def exitProgram(self):
        sys.exit()

if __name__ == '__main__':

    # create pyqt app
    app = QApplication(sys.argv)

    # create instance of controller() window
    ex = Controller()

    # start the app
    sys.exit(app.exec_())
