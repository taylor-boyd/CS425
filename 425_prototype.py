from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PIL import Image

import os
import sys
import time
import cv2
import subprocess
import json

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
# Throw error for the above ^
# When selecting "Back to menu" reset current image to ""
# Add detailed screens to illustrate the flow and what is happening to the photos
# Add guide for how to manually crop

# TODO:
# IMPLEMENT MULTITHREADING SO PROGRAM WON'T FREEZE WHEN GETTING FACE ALIGNMENT
# https://www.learnpyqt.com/tutorials/multithreading-pyqt-applications-qthreadpool/
# class Worker(QRunnable):


#    @pyqtSlot()
#        def run(self):
#        print ("hi")
#        time.sleep(5)
#        print ("complete")

results = "None"
saveImage = 0
path = "None"
images = 0

# used to prevent multiple feature list display on restart
outputListLayout = None
# used to prevent multiple button display on restart
featuresBtnLayout = None

class UI(QWidget):
    def setup(self, Controller):

        # Creates webcam_photos if it doesn't exist
        if not os.path.exists("backend/webcam_photos"):
            os.makedirs("backend/webcam_photos")
        else:
            print("webcam_photos exists")

        # Create ResizedImages if it doesn't exist
        if not os.path.exists("backend/ResizedImages"):
            os.makedirs("backend/ResizedImages")
        else:
            print ("ResizedImages exists")

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

        self.faceAlignmentPickScreen = QWidget()
        self.faceAlignmentManualHelpScreen = QWidget()

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
        self.faceAlignmentPick()
        self.faceAlignmentManualHelper()
        # self.photoProcessing()
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
        self.menu.addWidget(self.faceAlignmentPickScreen)
        self.menu.addWidget(self.faceAlignmentManualHelpScreen)
        # self.menu.addWidget(self.photoProcessingScreen)
        self.menu.addWidget(self.photoProcessedScreen)
        self.menu.addWidget(self.featuresListScreen)
        self.menu.addWidget(self.caricatureCreationScreen)
        self.menu.addWidget(self.finalScreen)

    # menu selection
    def beginningMenu(self):

        self.menuSelection.resize(675, 400)

        mainLayout = QVBoxLayout()

        mainMenuTitle = QLabel(self.menuSelection)
        mainMenuTitle.setAlignment(Qt.AlignCenter)
        mainMenuTitle.setFont(QFont("Century Gothic", 14, weight=QFont.Bold))
        mainMenuTitle.move(50, 50)
        mainMenuTitle.setText("Identifying Distinctive Features for Explainable Face Verification")
        mainMenuTitle.adjustSize()


        self.menuSelection.setWindowTitle("Unique Facial Feature Detection")
        CameraSettings = QPushButton('Use a camera', self)
        CameraSettings.setToolTip('Choose a webcam')

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
        global saveImage
        saveImage = 0

        self.webcamSelection.setWindowTitle("Unique Facial Feature Detection")
        self.webcamSelection.resize(575, 400)

        # create stacked layout
        self.stackedLayout = QStackedLayout()

        # create first page
        self.p1 = QWidget()
        self.p1Layout = QVBoxLayout()

        # create a second page
        self.p2 = QWidget()
        self.p2Layout = QVBoxLayout()

        # getting available cameras
        self.available_cameras = QCameraInfo.availableCameras()

        # if no camera found
        if not self.available_cameras:
            # exit the code
            pass

        # path to save
        self.save_path = "/backend/webcam_photos/"

        # creating a QCameraViewfinder object
        self.viewfinder = QCameraViewfinder()

        # Set the default camera.
        self.select_camera(0)

        # creating a tool bar
        toolbar = QToolBar("Camera Tool Bar")
        toolbar2 = QToolBar("Camera Tool Bar")

        # adding tool bar to main window
        self.p1Layout.addWidget(toolbar)

        self.p2Layout.addWidget(toolbar2)

        show_photo = QAction("Show photo taken", self)
        show_photo.triggered.connect(self.showWebcamPic)
        toolbar2.addAction(show_photo)

        # creating a show viewfinder action
        show_viewfinder = QAction("Show", self)

        # add action to it
        show_viewfinder.triggered.connect(self.show_cam)

        # adding it to tool bar
        toolbar.addAction(show_viewfinder)

        # creating a photo action to take photo
        click_action = QAction("Take photo", self)

        # adding status tip to the photo action
        click_action.setStatusTip("This will capture picture")

        # adding tool tip
        click_action.setToolTip("Capture picture")

        # adding action to it
        # calling take_photo method
        click_action.triggered.connect(self.click_photo)
        #click_action.triggered.connect(self.showWebcamPic)

        # adding this to the tool bar
        toolbar.addAction(click_action)

        # setting tool bar stylesheet
        toolbar.setStyleSheet("background : white; color : black;")

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

        # adding this to layout
        toolbar.addWidget(camera_selector)

        self.p1Layout.addWidget(self.viewfinder)

        self.webcampic = QLabel(self.p2)
        self.p2Layout.addWidget(self.webcampic)

        #webcamPreview = QPushButton("Show photo taken", self)
        #webcamPreview.clicked.connect(self.showWebcamPic)
        #self.p2Layout.addWidget(webcamPreview)
        retakePhoto = QPushButton("Retake Photo", self)
        retakePhoto.clicked.connect(self.changeIndex)
        retakePhoto.clicked.connect(self.clearLabel)
        self.p2Layout.addWidget(retakePhoto)
        continueSelectedWebcam = QPushButton("Use this photo", self)
        continueSelectedWebcam.clicked.connect(self.faceAlignmentPickWindow)
        continueSelectedWebcam.clicked.connect(self.stopCam)
        self.p2Layout.addWidget(continueSelectedWebcam)
        self.menuButton.clicked.connect(self.stopCam)
        self.p2Layout.addWidget(self.menuButton) # back to main menu button

        self.p1.setLayout(self.p1Layout)
        self.p2.setLayout(self.p2Layout)


        self.stackedLayout.addWidget(self.p1)
        self.stackedLayout.addWidget(self.p2)

        # setting final layout
        self.webcamSelection.setLayout(self.stackedLayout)

        self.stackedLayout.setCurrentIndex(0)

    def changeIndex(self):
        self.stackedLayout.setCurrentIndex(0)

    def clearLabel(self):
        self.webcampic.clear()

    # method to show viewfinder
    def show_cam(self):

        # start the camera
        self.camera.start()


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

        # creating a QCameraImageCapture object
        self.capture = QCameraImageCapture(self.camera)


        # showing alert if error occur
        self.capture.error.connect(lambda error_msg, error,
                                   msg: self.alert(msg))

        # when image captured showing message
        # self.capture.imageCaptured.connect(lambda d,
         #                                  i: self.status.showMessage("Image captured : "
                                                                     # + str(self.save_seq)))

        # getting current camera name
        self.current_camera_name = self.available_cameras[i].description()

        # inital save sequence
        self.save_seq = 0

    # method to take photo
    def click_photo(self):

        # time stamp
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")


        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path += self.save_path

        self.capture.capture(os.path.join(dir_path, "%s-%04d-%s.jpg" % (
            self.current_camera_name,
            self.save_seq,
            timestamp)))
        # increment the sequence

        self.selectedPictureLocation = os.path.join(dir_path,
                                                    "%s-%04d-%s.jpg" % (
            self.current_camera_name,
            self.save_seq,
            timestamp
                                                    ))

        self.save_seq += 1

        self.stackedLayout.setCurrentIndex(1)

    def showWebcamPic(self):
        webcampicPreview = QPixmap(self.selectedPictureLocation)
        self.webcampic.setPixmap(webcampicPreview.scaled(self.webcampic.width(), self.webcampic.height(), Qt.KeepAspectRatio))

    def stopCam(self):
        self.camera.stop()

    # method for alerts
    def alert(self, msg):

        # error message
        error = QErrorMessage(self)

        # setting text to the error message
        error.showMessage(msg)

    def photoSelection(self):
        global saveImage
        saveImage = 1

        self.pictureSelection.setWindowTitle("Unique Facial Feature Detection")

        self.pictureSelection.resize(575, 400)

        pictureSelectionLayout = QVBoxLayout()
        pictureSelectionMainMenu = QHBoxLayout()
        pictureSelectionMainMenu.addWidget(self.menuButton2)

        selectPhotoButton = QPushButton("Select a picture", self)
        self.selectedPhotoContinue = QPushButton("Continue: ", self)

        # Disable continue button until photo is chosen
        self.selectedPhotoContinue.setEnabled(False)
        pictureSelectionMainMenu.addWidget(selectPhotoButton)
        pictureSelectionMainMenu.addWidget(self.selectedPhotoContinue)

        # Select photo button
        selectPhotoButton.clicked.connect(self.openPhoto)

        # Go to resizing window
        # TODO:
        self.selectedPhotoContinue.clicked.connect(self.faceAlignmentPickWindow)

        selectedPhotoHelper = QLabel(self.pictureSelection)
        self.selectedPictureName = QLabel(self.pictureSelection)

        selectedPhotoHelper.setGeometry(QRect(160, -60, 300, 200))
        selectedPhotoHelper.setStyleSheet("font: 14pt Century Gothic; font-weight: bold")
        selectedPhotoHelper.setText("Selected photo is: ")

        self.selectedPictureLocation = ""

        pictureDisplayLayout = QVBoxLayout()
        pictureDisplayLayout.addWidget(selectedPhotoHelper)
        pictureDisplayLayout.addWidget(self.selectedPictureName)


        pictureSelectionLayout.addLayout(pictureDisplayLayout)
        pictureSelectionLayout.addLayout(pictureSelectionMainMenu)

        self.pictureSelection.setLayout(pictureSelectionLayout)


 # Run photo through backend
    def startPhotoProcessing(self):
        print ("BACKEND NOW")
        self.photoProcessedWindow()
        filename = QTextDocument(self.selectedPictureName.text())
        textFileName = filename.toPlainText()

        # get actual photo file name without end punctuation
        afterFirstApost = textFileName.find('\'') + 1
        lastApost = len(textFileName) - 2
        actualFileName = textFileName[afterFirstApost:lastApost]

        # old way of calling shape_predict.py, can probably delete; returns 0 on success
        # self.uniqueFeatureList = os.system('python backend/shape_predict.py ' + actualFileName)

        # run shape_predict.py with actualFileName
        proc = subprocess.Popen(["python", "backend/shape_predict.py", self.selectedPictureLocation], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        self.uniqueFeatureList = out.decode("utf-8")
        # print ("UNIQUE FEATURES:", self.uniqueFeatureList)

        # write feature list to a .txt file - currently creates and overwrites the same file
        # TODO: consider how it'll work with different files
        print ("LIST:", self.uniqueFeatureList)
        outputTextFileName = './static/features.txt'
        outputTextFile = open(outputTextFileName, "w")
        outputTextFile.write(self.uniqueFeatureList)
        outputTextFile.close()



    def faceAlignmentPick(self):
        self.faceAlignmentPickScreen = QWidget()
        self.faceAlignmentPickScreen.setWindowTitle("Unique Facial Feature Detection")
        self.faceAlignmentPickScreen.resize(575, 400)

        faceAlignmentLayout = QVBoxLayout()
        faceAlignmentButtonLayout = QHBoxLayout()

        faceAlignmentTitleLayout = QVBoxLayout()

        faceAlignmentTitleLayout.setContentsMargins(50,0,50,100)

        facePickerTitle = QLabel(self.faceAlignmentPickScreen)
        facePickerTitle.setAlignment(Qt.AlignCenter)
        facePickerTitle.setStyleSheet("font: 14pt Century Gothic; font-weight: bold")
        facePickerTitle.setText("Face Alignment")

        facePickerInstructions = QLabel(self.faceAlignmentPickScreen)
        facePickerInstructions.setAlignment(Qt.AlignCenter)
        facePickerInstructions.setStyleSheet("font: 14pt Century Gothic")
        facePickerInstructions.setText("If you do not have a NVIDIA CUDA enabled GPU, please pick 'Manual Face Alignment'. If you do, please use 'Auto Face Alignment'")
        facePickerInstructions.setWordWrap(True)

        faceAlignmentTitleLayout.addWidget(facePickerTitle)
        faceAlignmentTitleLayout.addWidget(facePickerInstructions)



        faceAlignmentAutoButton = QPushButton("Auto Face Alignment", self)
        faceAlignmentManualButton = QPushButton("Manual Face Alignment", self)

        faceAlignmentButtonLayout.addWidget(faceAlignmentAutoButton)
        faceAlignmentButtonLayout.addWidget(faceAlignmentManualButton)

        faceAlignmentAutoButton.clicked.connect(self.startFaceAlignmentAuto)
        faceAlignmentManualButton.clicked.connect(self.faceAlignmentManualHelpWindow)

        faceAlignmentLayout.addLayout(faceAlignmentTitleLayout)
        faceAlignmentLayout.addLayout(faceAlignmentButtonLayout)
        self.faceAlignmentPickScreen.setLayout(faceAlignmentLayout)

    def faceAlignmentManualHelper(self):
        self.camera.stop()
        self.faceAlignmentManualHelpScreen = QWidget()
        self.faceAlignmentManualHelpScreen.setWindowTitle("Unique Facial Feature Detection")
        self.faceAlignmentManualHelpScreen.resize(575, 400)

        # Layouts
        faceAlignmentManualHelpLayout = QVBoxLayout()
        faceAlignmentManualButtonLayout = QHBoxLayout()

        self.faceManualHelper = QLabel(self.faceAlignmentManualHelpScreen)
        self.faceManualHelper.setAlignment(Qt.AlignCenter)

        faceAlignmentManualButton = QPushButton("Manually align face", self)
        faceAlignmentManualButton.clicked.connect(self.startFaceAlignmentManual)

        manualInstructionsTitle = QLabel(self.faceAlignmentManualHelpScreen)
        manualInstructionsTitle.setAlignment(Qt.AlignCenter)
        manualInstructionsTitle.setStyleSheet("font: 14pt Century Gothic; font-weight: bold")
        manualInstructionsTitle.setText("Instructions:")

        manualInstructions = QLabel(self.faceAlignmentManualHelpScreen)
        manualInstructions.setAlignment(Qt.AlignCenter)
        manualInstructions.setStyleSheet("font: 14pt Century Gothic")
        manualInstructions.setText("A screen will appear showing the image. With the selector tool, draw a box around the face in the image.\n When satisfied, press ENTER. Once completed, exit the newly opened ROI window and the ROI selector window.")
        manualInstructions.setWordWrap(True)





        faceAlignmentManualHelpLayout.addWidget(manualInstructionsTitle)
        faceAlignmentManualHelpLayout.addWidget(manualInstructions)
        faceAlignmentManualHelpLayout.addWidget(self.faceManualHelper)
        faceAlignmentManualHelpLayout.addWidget(faceAlignmentManualButton)
        # faceAlignmentManualHelpLayout.addWidget(self.resizingPictureDisplayLabel)

        faceAlignmentManualContinue = QPushButton("Continue", self)
        faceAlignmentManualButtonLayout.addWidget(faceAlignmentManualContinue)

        # faceAlignmentManualContinue.clicked.connect(self.photoProcessingWindow)
        faceAlignmentManualContinue.clicked.connect(self.startPhotoProcessing)

        faceAlignmentManualHelpLayout.addLayout(faceAlignmentManualButtonLayout)
        self.faceAlignmentManualHelpScreen.setLayout(faceAlignmentManualHelpLayout)



    def startFaceAlignmentAuto(self):
        # goes to line 600, resizingPicture()
        self.resizingProcessedWindow()
        FaceAlignmentAuto(self.selectedPictureLocation)

        # Setting the cropped img once FaceAlignment is done
        # Need to think of this when we use multiple photos
        self.croppedImg = QPixmap("./backend/ResizedImages/newCropped.jpeg")
        self.resizingPictureDisplayLabel.setPixmap(self.croppedImg)
        self.faceManualHelper.setPixmap(self.croppedImg)

    def startFaceAlignmentManual(self):
        FaceAlignmentManual(self.selectedPictureLocation)
        # Resetting the photo on screen
        self.croppedImg = QPixmap("./backend/ResizedImages/newCropped.jpeg")
        self.resizingPictureDisplayLabel.setPixmap(self.croppedImg)
        self.faceManualHelper.setPixmap(self.croppedImg)


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

            # Enable continue button
            self.selectedPhotoContinue.setEnabled(True)



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

        repeatResizingPicture.clicked.connect(self.faceAlignmentManualHelpWindow)
        finishedResizingPhotoButton.clicked.connect(self.startPhotoProcessing)



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

        # from Jeron
        # predictor = ShapePredictor("model/shape_model", "shape-labels.txt")
        global results
        global images
        if saveImage == 1:
            # if file exists
            if (str(os.path.isfile("./backend/ResizedImages/newCropped.jpeg")) == True):
                images = Image.open("./backend/ResizedImages/newCropped.jpeg")
        else:
            images = Image.open(path)
        # results = predictor.process_image(images)

        # Two buttons here for Feature List or Caricature
        photoProcessedBtnLayout = QHBoxLayout()
        getFeaturesListBtn = QPushButton("Get unique feature's list!")
        # createCaricatureBtn = QPushButton("Create a caricature!")

        photoProcessedBtnLayout.addWidget(getFeaturesListBtn)
        # photoProcessedBtnLayout.addWidget(createCaricatureBtn)

        getFeaturesListBtn.clicked.connect(self.outputtingList) # orig. featuresListWindow
        # createCaricatureBtn.clicked.connect(self.caricatureCreationWindow)

        self.photoProcessedScreen.setLayout(photoProcessedBtnLayout)

    # outputs list of unique features
    def outputtingList(self):
        self.featuresListWindow()
        global outputListLayout
        if outputListLayout is None:
            # set up initial layout
            outputListLayout = self.featuresListScreen.layout()
        else:
            # reset layout (assumed restart)

            # delete widgets
            while outputListLayout.count():
                child = outputListLayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # re-add header layout - part of featuresList
            obtainedFeaturesList = QLabel(self.photoProcessedScreen)
            obtainedFeaturesList.setStyleSheet("font: 14pt Century Gothic")
            obtainedFeaturesList.setText("Your unique features!")
            obtainedFeaturesList.setAlignment(Qt.AlignCenter)
            outputListLayout.addWidget(obtainedFeaturesList)

        global featuresBtnLayout
        if featuresBtnLayout is None:
            # set up initial layout
            featuresBtnLayout = QHBoxLayout()
        else:
            # reset layout (assumed restart)

            # delete widgets
            while featuresBtnLayout.count():
                child = featuresBtnLayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # open .txt file with features
        inputTextFileName = './static/features.txt'

        # was originally "r", might change back (change by Josh)
        inputTextFile = open(inputTextFileName, "r")
        '''
        # read features from .txt file
        listOfFeatures = inputTextFile.read()
        results = str(listOfFeatures)    # save list into results for Jeron's saveList
        '''
        # display list of unique features
        actualFeaturesList = QLabel(self.photoProcessedScreen)
        actualFeaturesList.setStyleSheet("font: 10pt Century Gothic")

        # convert features.txt contents into dictionary <string, float>
        uniqueFeatureDict = eval(inputTextFile.read())
        # sort dictionary in descending order
        uniqueFeatureDict = dict(sorted(uniqueFeatureDict.items(), key=lambda item: item[1], reverse=True))
        # add dictionary items to QLabel text
        for x, y in uniqueFeatureDict.items():
            actualFeaturesList.setText(actualFeaturesList.text() + "\n" + x + ": " + str(y))

        # actualFeaturesList.setText(listOfFeatures)
        actualFeaturesList.setWordWrap(True)
        actualFeaturesList.setAlignment(Qt.AlignCenter)
        outputListLayout.addWidget(actualFeaturesList)

        # close .txt file
        inputTextFile.close()

        # Allow save option
        # Save in .txt format is probably preferable
        # saveListBtn does nothing for now, will implement when we tie in unique algorithm
        saveListBtn = QPushButton("Save unique features list")

        # if from Jeron
        global images

        savePhotoBtn = QPushButton("Save Photo")

        if saveImage == 0 or self.selectedPictureLocation.find('webcam_photos') != -1:
            # savePhotoBtn = QPushButton("Save Photo")
            featuresBtnLayout.addWidget(savePhotoBtn)
            # savePhotoBtn.clicked.connect(self.savePhoto(images))

        continueBtn = QPushButton("Continue")

        featuresBtnLayout.addWidget(saveListBtn)
        '''
        # if from Jeron
        if saveImage == 0:
            featuresBtnLayout.addWidget(savePhotoBtn)
        '''
        featuresBtnLayout.addWidget(continueBtn)

        # Save Features List - from Jeron
        saveListBtn.clicked.connect(self.saveList)

        # Save Photo
        savePhotoBtn.clicked.connect(self.savePhoto)

        # Delete features.txt then go to end screen
        continueBtn.clicked.connect(self.deleteFeaturesTxt)
        continueBtn.clicked.connect(self.fileDelete)

        # Go to end screen
        #continueBtn.clicked.connect(self.goToEndWindow)

        outputListLayout.addLayout(featuresBtnLayout)
        # self.featuresListScreen.setLayout(outputListLayout)   # necessary???

    def deleteFeaturesTxt(self):
        file_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.exists(file_path + '\\static\\features.txt'):
            os.remove(file_path + '\\static\\features.txt')
        self.goToEndWindow()

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

        # obtainedFeaturesList.setText(str(results))    # from Jeron?

        featuresLayout.addWidget(obtainedFeaturesList)

        # Features are displayed in outputtingList
        # Buttons are added in outputtingList to maintain order of widgets

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

    def saveList(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', "features.txt")
        listFile = open("./static/features.txt", 'r')
        listFromListFile = listFile.read()

        # only write to file if save file name was created
        if name:
            file = open(name, 'w')
            # global results

            # writing contents of static/features.txt into new file
            # orig. write(str(results))
            file.write(listFromListFile)

            # close output file
            file.close()

        # close input file
        listFile.close()

        # delete features.txt on program end
        file_path = os.path.dirname(os.path.realpath(__file__))
        os.remove(file_path + '\\static\\features.txt')

    # orig. parameters: self, input
    def savePhoto(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', "image.png")
        # only save photo file if file name was decided
        if name:
            # this file should exist if it has been cropped
            img = Image.open("./backend/ResizedImages/newCropped.jpeg")
            global images
            img.save(name + '.jpeg', 'jpeg')
            # file.close()

    def fileDelete(self):
        # os.remove("static/temp.txt")
        if os.path.exists("backend/ResizedImages/newCropped.jpeg"):
            os.remove("backend/ResizedImages/newCropped.jpeg")
        global saveImage
        if os.path.exists(self.selectedPictureLocation) and self.selectedPictureLocation.find('webcam_photos') != -1:
            os.remove(self.selectedPictureLocation)
        self.exitProgram()

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

        # Reset the QLabel for current picture
        self.selectedPictureName.clear()

        # Turn continue button off in photo selection
        self.selectedPhotoContinue.setEnabled(False)

        self.faceManualHelper.clear()
        self.resizingPictureDisplayLabel.clear()
        self.webcampic.clear()

        # Need to do same stuff for webcam stuff

    def configureWebcamWindow(self):
        self.menu.setCurrentIndex(1)
        self.stackedLayout.setCurrentIndex(0)

    def choosePictureWindow(self):
        self.menu.setCurrentIndex(2)

    # REFER TO ABOVE ABOUT MULTITHREADING
    # def resizingPhotoProcessingWindow(self):
        # self.menu.setCurrentIndex(3)

    def resizingProcessedWindow(self):
        self.menu.setCurrentIndex(3)

    def faceAlignmentPickWindow(self):
        self.menu.setCurrentIndex(4)

    def faceAlignmentManualHelpWindow(self):
        self.menu.setCurrentIndex(5)

    # Choose for caricature or just a list
    # def photoProcessingWindow(self):
        # self.menu.setCurrentIndex(6)

    def photoProcessedWindow(self):
        self.menu.setCurrentIndex(6)

    def featuresListWindow(self):
        self.menu.setCurrentIndex(7)

    def caricatureCreationWindow(self):
        self.menu.setCurrentIndex(8)

    def goToEndWindow(self):
        self.menu.setCurrentIndex(9)

    def exitProgram(self):
        sys.exit()

if __name__ == '__main__':

    # create pyqt app
    app = QApplication(sys.argv)

    # create instance of controller() window
    ex = Controller()

    # start the app
    sys.exit(app.exec_())
