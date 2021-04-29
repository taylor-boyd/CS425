import face_alignment

# To check if file size is too large (could break computer)
import os
import sys
from PIL import Image
# Getting distance between points
from math import hypot

from skimage import io


# Provide user path to photo here from front end
def FaceAlignmentAuto(currentImage):
    """Does the auto face alignment using face_alignment
    
    Note: 
        This requires a CUDA enabled GPU
    """
    
    # Getting image size
    currentImageFileSize = os.stat(currentImage).st_size

    # Check if photo is too large, stops if it does.
    # This is to ensure smaller computers can handle the face alignment algorithm
    # Will adjust probably smaller or larger
    sizeThreshold = 1000000
    if (currentImageFileSize < sizeThreshold):
        fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)
    # If photo is too large
    else:
        print("Error: Filesize too large! Please try an image smaller than 1 MB")
        print ("Current size is:", currentImageFileSize, "bytes")
        sys.exit()

    # Get the image
    input = io.imread(currentImage)
    # Get the facial landmarks using face_alignment library
    preds = fa.get_landmarks(input)

    # Store data from preds
    data = preds[0]
    dataLen = len(data)

    # Data[0] is first point
    xValues = [x[0] for x in data]
    yValues = [y[1] for y in data]
    
    # Getting midpoint of all landmarks
    midPoint = (sum(xValues) / dataLen, sum(yValues) / dataLen)
    midPointX = midPoint[0]
    midPointY = midPoint[1]

    # only need these two
    bottomRight = []
    upperLeft = []

    
    # Storing each point into two containers, bottomRight and upperLeft
    for x in data:
        if (x[0] > midPointX and x[1] > midPointY):
            bottomRight.append(x.tolist())
        elif (x[0] < midPointX and x[1] < midPointY):
            upperLeft.append(x.tolist())

    # Getting the furthest point in both of these containers
    bottomRightMax = generateMaxCoords(bottomRight, midPointX, midPointY)
    upperLeftMax = generateMaxCoords(upperLeft, midPointX, midPointY)

    # Adding extra space
    # Good values for what I tested, can adjust to your liking

    # Moved image right (pos values)
    bottomRightMax[0] += 100

    # Moved image left (pos values)
    upperLeftMax[0] -= 10

    # Moved image down (pos values)
    bottomRightMax[1] += 10

    # Moved image up (pos values)
    upperLeftMax[1] -= 100


    im = Image.open(currentImage)

    # The math coordinate system here is weird, research PIL crop to learn more
    img2 = im.crop((upperLeftMax[0], upperLeftMax[1],  bottomRightMax[0], bottomRightMax[1]))
    size = (178, 218)

    # Save thumbnail in required format
    # Optimally add more adjustments here, like horizontally align eyes
    img2 = img2.resize(size)

    # Now saving the cropped image
    img2.save("./backend/ResizedImages/newCropped.jpeg", "JPEG")

    # img2.show()



def generateMaxCoords(section, midPointX, midPointY):
    """Getting furthest coords from midPoint

    Args:
        section: Which section (bottomRight or upperLeft coords)
        midPointX: Middle point X value
        midPointY: Middle point Y value

    Returns:
        maxCoords: Furthest coords from the midpoint
        These will be used to crop the photo

    """
    maxCoords = 0
    maxNum = 0

    # Looking for farthest
    for x in section:
        distance = (hypot(midPointX - x[0], midPointY - x[1]))
        if (distance > maxNum):
            maxNum = distance
            maxCoords = x

    return maxCoords

