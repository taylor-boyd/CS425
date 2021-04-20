import cv2
import numpy as np

def FaceAlignmentManual(path):
    
    img = cv2.imread(path)

    roi = cv2.selectROI(img)
    
    # TODO:
    # PUT THIS "ROI" IN FRONT END
    # PUT ROI SCREEN ON PYQT SCREEN!
    # print (roi)
    
    # This line from tutorial here -> 
    # https://blog.electroica.com/select-roi-or-multiple-rois-bounding-box-in-opencv-python/ 
    roi_cropped = img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

    cv2.imshow("ROI", roi_cropped)

    # STILL NEED TO DO THE 40 INCHES MODIFICATIONS
    resize = (178, 218)

    finalCropped = cv2.resize(roi_cropped, resize)
    cv2.imwrite("./backend/ResizedImages/newCropped.jpeg", finalCropped)



    cv2.waitKey(0)
    