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
import glob

sys.path.append('./backend/')
# Optimally but both functions into one file
# Allow manual face alignment
from FaceAlignmentv2 import FaceAlignmentManual
# Allow algorithm to do it automatically
from FaceAlignment import FaceAlignmentAuto

results = "None"
saveImage = 0
path = "None"
images = 0

# used to prevent multiple feature list display on restart
outputListLayout = None
# used to prevent multiple button display on restart
featuresBtnLayout = None



class UI(QWidget):
    """This class holds all of the logic behind running the front end.

    Args: 
        QWidget: QWidget is passed to allow this class to utilize
        QWidget functions

    Attributes:
        Most of the front end attributes are declared here
        for the program to work.

    """


    def setup(self, Controller):
        """Setup holds all of the QWidgets and the order of the pages

        This function sets up the skeleton of the program, meaning it declares
        all the pages the program has and calls each page in order.

        Args:
            Controller: The Controller class which handles which pages
            the program should go to.

        """

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
        # Optimally should only be one button
        self.menuButton = QPushButton("Back to main menu")
        self.menuButton2 = QPushButton("Back to main menu")

        # Hold the widgets
        self.menu = QStackedLayout()
        
        # Setting up the necessary QWidgets
        # order matters
        self.menuSelection = QWidget()
        self.webcamSelection = QWidget()
        self.pictureSelection = QWidget()
        self.resizeSelectedPicture = QWidget()
        self.faceAlignmentPickScreen = QWidget()
        self.faceAlignmentManualHelpScreen = QWidget()
        self.photoProcessedScreen = QWidget()
        self.featuresListScreen = QWidget()
        self.finalScreen = QWidget()

        # Call the functions here
        self.beginningMenu()
        self.webcamConfiguration()
        self.photoSelection()
        self.resizingPicture()
        self.faceAlignmentPick()
        self.faceAlignmentManualHelper()
        self.photoProcessed()
        self.featuresList()
        self.endScreen()

        # order matters!
        self.menu.addWidget(self.menuSelection)
        self.menu.addWidget(self.webcamSelection)
        self.menu.addWidget(self.pictureSelection)
        self.menu.addWidget(self.resizeSelectedPicture)
        self.menu.addWidget(self.faceAlignmentPickScreen)
        self.menu.addWidget(self.faceAlignmentManualHelpScreen)
        self.menu.addWidget(self.photoProcessedScreen)
        self.menu.addWidget(self.featuresListScreen)
        self.menu.addWidget(self.finalScreen)

    # menu selection
    def beginningMenu(self):
        """This page holds the main menu (Select a photo, Webcam, Quit)


        """

        self.menuSelection.resize(675, 400)
        
        # Setting up layout
        mainLayout = QVBoxLayout()

        # Main menu title and styling
        mainMenuTitle = QLabel(self.menuSelection)
        mainMenuTitle.setAlignment(Qt.AlignCenter)
        mainMenuTitle.setFont(QFont("Century Gothic", 14, weight=QFont.Bold))
        mainMenuTitle.move(50, 50)
        mainMenuTitle.setText("Identifying Distinctive Features for Explainable Face Verification")
        mainMenuTitle.adjustSize()
        self.menuSelection.setWindowTitle("Unique Facial Feature Detection")
       
        # Choose a webcam button
        CameraSettings = QPushButton('Use a camera', self)
        CameraSettings.setToolTip('Choose a webcam')
        
        # Choose from files button
        ChoosePicture = QPushButton("Choose from files", self)
        ChoosePicture.setToolTip('Choose picture')

        # Menu buttons
        CameraSettings.clicked.connect(self.configureWebcamWindow)
        ChoosePicture.clicked.connect(self.choosePictureWindow)
        
        # Button layouts
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(CameraSettings)
        buttonLayout.addWidget(ChoosePicture)

        # Quit button
        quitButton = QPushButton('Quit', self)
        quitButton.clicked.connect(QApplication.instance().quit)
        buttonLayout.addWidget(quitButton)

        # Setting layout
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

        # Delete previous photo (deleting all photos function)
        files = glob.glob("backend/webcam_photos/*.jpg")
        for f in files:
            os.remove(f)




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
        """Allows user to choose from files

        Note:
            This is also where we set the picture location that we send to
            the backend.

        """

        
        global saveImage
        saveImage = 1

        self.pictureSelection.setWindowTitle("Unique Facial Feature Detection")
        self.pictureSelection.resize(575, 400)
        
        # Layouts
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
        self.selectedPhotoContinue.clicked.connect(self.faceAlignmentPickWindow)

        selectedPhotoHelper = QLabel(self.pictureSelection)
        self.selectedPictureName = QLabel(self.pictureSelection)

        selectedPhotoHelper.setGeometry(QRect(160, -60, 300, 200))
        selectedPhotoHelper.setStyleSheet("font: 14pt Century Gothic; font-weight: bold")
        selectedPhotoHelper.setText("Selected photo is: ")
        
        # Declaring location for the chosen file
        self.selectedPictureLocation = ""

        # Picture Preview Layout
        pictureDisplayLayout = QVBoxLayout()
        pictureDisplayLayout.addWidget(selectedPhotoHelper)
        pictureDisplayLayout.addWidget(self.selectedPictureName)


        pictureSelectionLayout.addLayout(pictureDisplayLayout)
        pictureSelectionLayout.addLayout(pictureSelectionMainMenu)

        self.pictureSelection.setLayout(pictureSelectionLayout)


 # Run photo through backend
    def startPhotoProcessing(self):
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
        # print ("LIST:", self.uniqueFeatureList)
        outputTextFileName = './static/features.txt'
        outputTextFile = open(outputTextFileName, "w")
        outputTextFile.write(self.uniqueFeatureList)
        outputTextFile.close()

    def faceAlignmentPick(self):
        """The menu to choose manual or auto alignment

        """

        self.faceAlignmentPickScreen = QWidget()
        self.faceAlignmentPickScreen.setWindowTitle("Unique Facial Feature Detection")
        self.faceAlignmentPickScreen.resize(575, 400)
        
        # Layouts
        faceAlignmentLayout = QVBoxLayout()
        faceAlignmentButtonLayout = QHBoxLayout()
        faceAlignmentTitleLayout = QVBoxLayout()
        faceAlignmentTitleLayout.setContentsMargins(50,0,50,100)

        # Title styling
        facePickerTitle = QLabel(self.faceAlignmentPickScreen)
        facePickerTitle.setAlignment(Qt.AlignCenter)
        facePickerTitle.setStyleSheet("font: 14pt Century Gothic; font-weight: bold")
        facePickerTitle.setText("Face Alignment")
        
        # Instructions styling
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
        
        # Send to desired alignment function
        faceAlignmentAutoButton.clicked.connect(self.startFaceAlignmentAuto)
        faceAlignmentManualButton.clicked.connect(self.faceAlignmentManualHelpWindow)
        
        # Final layout configuration
        faceAlignmentLayout.addLayout(faceAlignmentTitleLayout)
        faceAlignmentLayout.addLayout(faceAlignmentButtonLayout)
        self.faceAlignmentPickScreen.setLayout(faceAlignmentLayout)

    def faceAlignmentManualHelper(self):
        """This screen gives instructions on how to manually align

        The user is able to manually adjust as many times as they want

        """
        
        # Ensure webcam has stopped
        self.camera.stop()

        # 
        self.faceAlignmentManualHelpScreen.setWindowTitle("Unique Facial Feature Detection")
        self.faceAlignmentManualHelpScreen.resize(575, 400)

        # Layouts
        faceAlignmentManualHelpLayout = QVBoxLayout()
        faceAlignmentManualButtonLayout = QHBoxLayout()
        
        # This is the display of the picture after alignment
        self.faceManualHelper = QLabel(self.faceAlignmentManualHelpScreen)
        self.faceManualHelper.setAlignment(Qt.AlignCenter)

        # Button to start manual face alignment function
        faceAlignmentManualButton = QPushButton("Manually align face", self)
        faceAlignmentManualButton.clicked.connect(self.startFaceAlignmentManual)

        # Title styling
        manualInstructionsTitle = QLabel(self.faceAlignmentManualHelpScreen)
        manualInstructionsTitle.setAlignment(Qt.AlignCenter)
        manualInstructionsTitle.setStyleSheet("font: 14pt Century Gothic; font-weight: bold")
        manualInstructionsTitle.setText("Instructions:")
        
        # Instructions styling
        manualInstructions = QLabel(self.faceAlignmentManualHelpScreen)
        manualInstructions.setAlignment(Qt.AlignCenter)
        manualInstructions.setStyleSheet("font: 14pt Century Gothic")
        manualInstructions.setText("A screen will appear showing the image. With the selector tool, draw a box around the face in the image.\n When satisfied, press ENTER. Once completed, exit the newly opened ROI window and the ROI selector window.")
        manualInstructions.setWordWrap(True)

        # Layout configuration
        faceAlignmentManualHelpLayout.addWidget(manualInstructionsTitle)
        faceAlignmentManualHelpLayout.addWidget(manualInstructions)
        faceAlignmentManualHelpLayout.addWidget(self.faceManualHelper)
        faceAlignmentManualHelpLayout.addWidget(faceAlignmentManualButton)

        # Continue when done alignment button
        faceAlignmentManualContinue = QPushButton("Continue", self)
        faceAlignmentManualButtonLayout.addWidget(faceAlignmentManualContinue)
        faceAlignmentManualContinue.clicked.connect(self.startPhotoProcessing)
        
        # Final layout configuration
        faceAlignmentManualHelpLayout.addLayout(faceAlignmentManualButtonLayout)
        self.faceAlignmentManualHelpScreen.setLayout(faceAlignmentManualHelpLayout)



    def startFaceAlignmentAuto(self):
        """Starts the auto alignment
           
        Note:
            User must have CUDA enabled GPU for this to work

        """
        # goes to line 600, resizingPicture()
        self.resizingProcessedWindow()

        # Calls the auto face alignment algorithm in the backend
        FaceAlignmentAuto(self.selectedPictureLocation)

        # Setting the cropped img once FaceAlignment is done
        self.croppedImg = QPixmap("./backend/ResizedImages/newCropped.jpeg")

        # Setting the display labels to the cropped image
        self.resizingPictureDisplayLabel.setPixmap(self.croppedImg)
        self.faceManualHelper.setPixmap(self.croppedImg)

    def startFaceAlignmentManual(self):
        """Starts the manual alignment

        """

        # Calls the manual face alignment given the selected picture location
        FaceAlignmentManual(self.selectedPictureLocation)

        # Resetting the photo on screen
        self.croppedImg = QPixmap("./backend/ResizedImages/newCropped.jpeg")

        # Setting the display labels to the cropped image
        self.resizingPictureDisplayLabel.setPixmap(self.croppedImg)
        self.faceManualHelper.setPixmap(self.croppedImg)


    # Choose a file
    def openPhoto(self):
        """Allows user to choose file from their own documents

        """
        # Open file dialog for user to pick their image
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Image files (*.jpg *.png)")

        # If valid file
        if files:

            # Picture display styling
            self.selectedPictureName.setGeometry(QRect(70, -30, 500, 200))
            self.selectedPictureName.setAlignment(Qt.AlignCenter)
            self.selectedPictureName.setStyleSheet("font: 10pt Century Gothic")
            
            # Picture preview display
            picturePreview = QPixmap(files[0])
            self.selectedPictureName.setPixmap(picturePreview.scaled(self.selectedPictureName.width() * 2, self.selectedPictureName.height() * 2, Qt.KeepAspectRatio))
            
            # Saving the chosen picture location
            self.selectedPictureLocation = files[0]

            # Enable continue button (this is greyed out if image has not been selected yet)
            self.selectedPhotoContinue.setEnabled(True)



    # This screen will show after, giving the option to the user to manually align
    def resizingPicture(self):
        """This page shows after auto alignment

        This page also gives user to manually adjust if needed

        """
        self.resizeSelectedPicture.setWindowTitle("Unique Facial Feature Detection")
        self.resizeSelectedPicture.resize(575, 400)

        # Outer layout
        resizingPictureLayout = QVBoxLayout()

        # Photo picked from user
        self.croppedImg = QPixmap("")

        # Resized photo display preview
        self.resizingPictureDisplayLabel = QLabel(self.resizeSelectedPicture)
        self.resizingPictureDisplayLabel.setAlignment(Qt.AlignCenter)
        self.resizingPictureDisplayLabel.setStyleSheet("padding: 30px")

        resizingPictureDisplayLayout = QVBoxLayout()

        # Title styling
        croppedTitle = QLabel(self.resizeSelectedPicture)
        croppedTitle.setAlignment(Qt.AlignCenter)
        croppedTitle.setStyleSheet("font: 14pt Century Gothic")
        croppedTitle.setText("Your Cropped Photo:")
        
        # Note that the photo is readjusted to 178x218
        # Would add more warnings if we added more adjustments in the face alignment
        croppedWarning = QLabel(self.resizeSelectedPicture)
        croppedWarning.setAlignment(Qt.AlignCenter)
        croppedWarning.setStyleSheet("font: 10pt Century Gothic")
        croppedWarning.setText("Note: Your photo will automatically adjust to 178x218")

        # Layout configuration
        resizingPictureDisplayLayout.addWidget(croppedTitle)
        resizingPictureDisplayLayout.addWidget(croppedWarning)
        resizingPictureDisplayLayout.addWidget(self.resizingPictureDisplayLabel)


        # Restart buttons
        resizingPictureBtnLayout = QHBoxLayout()
        repeatResizingPicture = QPushButton("Manually Crop Photo", self)
        finishedResizingPhotoButton = QPushButton("Continue", self)
        
        # Layout configuration 
        resizingPictureBtnLayout.addWidget(repeatResizingPicture)
        resizingPictureBtnLayout.addWidget(finishedResizingPhotoButton)
        resizingPictureLayout.addLayout(resizingPictureDisplayLayout)
        resizingPictureLayout.addLayout(resizingPictureBtnLayout)

        
        self.resizeSelectedPicture.setLayout(resizingPictureLayout)
        
        # This goes to the manual alignment window if user wants to manually align
        repeatResizingPicture.clicked.connect(self.faceAlignmentManualHelpWindow)
        # Go to backend to get unique features
        finishedResizingPhotoButton.clicked.connect(self.startPhotoProcessing)


    def endScreen(self):
        """Final screen, allowing user to restart or quit

        """
        self.finalScreen.setWindowTitle("Unique Facial Feature Detection")
        self.finalScreen.resize(575, 400)

        finalScreenBtnLayout = QHBoxLayout()
        menuButtonFinal = QPushButton("Restart")
        exitBtn = QPushButton("Quit")

        finalScreenBtnLayout.addWidget(menuButtonFinal)
        finalScreenBtnLayout.addWidget(exitBtn)

        # Final screen text styling
        finalScreenText = QLabel(self.finalScreen)
        finalScreenText.setStyleSheet("font: 14pt Century Gothic")
        finalScreenText.setText("Would you like to try again?")
        finalScreenText.setGeometry(QRect(30, -10, 500, 200))
        finalScreenText.setAlignment(Qt.AlignCenter)

        # Final screen buttons
        menuButtonFinal.clicked.connect(self.menuWindow)
        exitBtn.clicked.connect(self.exitProgram)

        self.finalScreen.setLayout(finalScreenBtnLayout)

    
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

class Controller(QMainWindow, UI):
    """This controls which page the application should go to

    Args:
        QMainWindow: Provides the main application window
        UI: Handles all front end screens

    Attributes:
        Attributes declared in class UI are handled here.

    """

    def __init__(self):

        super().__init__()

        self.setup(self)

        # Sends back to main menu
        # Need separate widget for each window
        # Optimally only one button should be needed
        self.menuButton.clicked.connect(self.menuWindow)
        self.menuButton2.clicked.connect(self.menuWindow)


    
    """These functions set the index of which page the front end should go to

    """
    def menuWindow(self):
        self.menu.setCurrentIndex(0)

        # Reset the QLabel for current picture
        self.selectedPictureName.clear()

        # Turn continue button off in photo selection
        self.selectedPhotoContinue.setEnabled(False)
        
        # Resetting all display labels to empty when restarting
        self.faceManualHelper.clear()
        self.resizingPictureDisplayLabel.clear()
        self.webcampic.clear()

    def configureWebcamWindow(self):
        self.menu.setCurrentIndex(1)
        self.stackedLayout.setCurrentIndex(0)

    def choosePictureWindow(self):
        self.menu.setCurrentIndex(2)

    def resizingProcessedWindow(self):
        self.menu.setCurrentIndex(3)

    def faceAlignmentPickWindow(self):
        self.menu.setCurrentIndex(4)

    def faceAlignmentManualHelpWindow(self):
        self.menu.setCurrentIndex(5)

    def photoProcessedWindow(self):
        self.menu.setCurrentIndex(6)

    def featuresListWindow(self):
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
