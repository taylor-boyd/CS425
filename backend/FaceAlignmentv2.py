import cv2
import numpy as np

def CropAndResize(img_path):

    img_raw = cv2.imread(img_path)

    roi = cv2.selectROI(img_raw)

    print (roi)
    
    # This line from tutorial here -> 
    # https://blog.electroica.com/select-roi-or-multiple-rois-bounding-box-in-opencv-python/ 
    roi_cropped = img_raw[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

    cv2.imshow("ROI", roi_cropped)

    # STILL NEED TO DO THE 40 INCHES MODIFICATIONS
    resize = (178, 218)

    finalCropped = cv2.resize(roi_cropped, resize)
    cv2.imwrite("./ResizedImages/newCropped.jpeg", finalCropped)



    cv2.waitKey(0)
    
    # Resize FIRST
    # Return path of new photo (roi_cropped)


# This will be passed through front end
# img_path = "./FaceAlignTests/Test3.jpg"

# CropAndResize(img_path)
