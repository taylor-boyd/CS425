import face_alignment

from PIL import Image
# Getting distance between points
from math import hypot

from skimage import io

fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False)

currentImage = "Test3.jpeg"

input = io.imread(currentImage)
preds = fa.get_landmarks(input)

# Store data from preds
data = preds[0]
dataLen = len(data)

# Data[0] is first point
xValues = [x[0] for x in data]
yValues = [y[1] for y in data]

midPoint = (sum(xValues) / dataLen, sum(yValues) / dataLen)
midPointX = midPoint[0]
midPointY = midPoint[1]



# only need these two
bottomRight = []
upperLeft = []


for x in data:
    if (x[0] > midPointX and x[1] > midPointY):
        bottomRight.append(x.tolist())
    elif (x[0] < midPointX and x[1] < midPointY):
        upperLeft.append(x.tolist())

# Getting furthest coords (from midPoint)
def generateMaxCoords(section):
    maxCoords = 0
    maxNum = 0
    for x in section:
        distance = (hypot(midPointX - x[0], midPointY - x[1]))
        if (distance > maxNum):
            maxNum = distance
            maxCoords = x

    return maxCoords


bottomRightMax = generateMaxCoords(bottomRight)
upperLeftMax = generateMaxCoords(upperLeft)

# Adding extra space
bottomRightMax[0] += 100
upperLeftMax[0] -= 100
bottomRightMax[1] += 100
upperLeftMax[1] -= 100


im = Image.open(currentImage)

# The math coordinate system here is weird, research PIL crop to learn more (this part was confusing D:)
img2 = im.crop((upperLeftMax[0], upperLeftMax[1],  bottomRightMax[0], bottomRightMax[1]))
size = 178, 218

# Save thumbnail in required format
# UNCOMMENT WHEN RESIZING THE IMAGE!!!
# img2.thumbnail(size, Image.ANTIALIAS)
# img2.save("Test.jpeg", "JPEG")

img2.show()



# im.show()
