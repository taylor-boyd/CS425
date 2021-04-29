import cv2
import numpy as np

def FaceAlignmentManual(path):
    """ This function allows the user to select a ROI

    """
    
    # Get the image 
    img = cv2.imread(path)
    
    # Allow user to select region of interest (ROI)
    roi = cv2.selectROI(img)

    # This line from tutorial here ->
    # https://blog.electroica.com/select-roi-or-multiple-rois-bounding-box-in-opencv-python/
    roi_cropped = img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    
    # Show the image
    cv2.imshow("ROI", roi_cropped)
    
    # Resizes image
    # Optimally put other adjustments here
    resize = (178, 218)
    
    # Final cropped photo and saving the photo
    finalCropped = cv2.resize(roi_cropped, resize)
    cv2.imwrite("./backend/ResizedImages/newCropped.jpeg", finalCropped)


    cv2.waitKey(0)
