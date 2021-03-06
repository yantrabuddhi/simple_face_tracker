#!/usr/bin/python
 
#----------------------------------------------------------------------------
# Face Detection Test (OpenCV)
#
# thanks to:
# http://japskua.wordpress.com/2010/08/04/detecting-eyes-with-python-opencv
#----------------------------------------------------------------------------

import cv
import rospy
import sys
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from simple_face_tracker.msg import targets

from cv_bridge import CvBridge, CvBridgeError

class FaceDetect:
    NODE_NAME = 'face_detect'

    def __init__(self):
        self.haarbase = '/opt/ros/hydro/share/OpenCV/' #'/usr/share/opencv/'
        self.faceCascade = cv.Load(self.haarbase + "haarcascades/haarcascade_frontalface_alt.xml")
        self.pub = rospy.Publisher('facedetect', targets, queue_size=10)
        cv.NamedWindow("ImageShow", 1)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/cv_camera/image_raw",Image,self.callback)
        
    def callback(self,data):
        try:
            cv_image = self.bridge.imgmsg_to_cv(data,"bgr8")#imgmsg_to_cv2
        except CvBridgeError, e:
            print e
            
        (cols,rows) = cv.GetSize(cv_image)
        img = self.DetectFace(cv_image,self.faceCascade)
        cv.ShowImage("ImageShow", img)    
        cv.WaitKey(10)

#rospy.init_node('face_locations', anonymous=True)
#r = rospy.Rate(10) # 10hz

    def DetectFace(self,image, faceCascade):
     
        min_size = (20,20)
        image_scale = 2
        haar_scale = 1.1
        min_neighbors = 3
        haar_flags = 0
     
        # Allocate the temporary images
        grayscale = cv.CreateImage((image.width, image.height), 8, 1)
        smallImage = cv.CreateImage(
                (
                    cv.Round(image.width / image_scale),
                    cv.Round(image.height / image_scale)
                ), 8 ,1)
     
        # Convert color input image to grayscale
        cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)
     
        # Scale input image for faster processing
        cv.Resize(grayscale, smallImage, cv.CV_INTER_LINEAR)
     
        # Equalize the histogram
        cv.EqualizeHist(smallImage, smallImage)
     
        # Detect the faces
        faces = cv.HaarDetectObjects(
                smallImage, faceCascade, cv.CreateMemStorage(0),
                haar_scale, min_neighbors, haar_flags, min_size
            )
     
        # If faces are found
        if faces:
            payload=targets()
            for ((x, y, w, h), n) in faces:
                # the input to cv.HaarDetectObjects was resized, so scale the
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                cv.Rectangle(image, pt1, pt2, cv.RGB(255, 0, 0), 5, 8, 0)
                fpt=Point()
                fpt.x=(float(x) + float(w)/2.0)/float(smallImage.width)
                fpt.y=(float(y) + float(h)/2.0)/float(smallImage.height)
                payload.positions.append(fpt)

            msg = payload

            rospy.loginfo(msg)
            self.pub.publish(msg)
     
        return image
 
#----------
# M A I N
#----------
def main(args):
    rospy.loginfo("Starting {0}...".format(FaceDetect.NODE_NAME))

    ic = FaceDetect()

    rospy.init_node('face_detect', anonymous=True)

    rospy.loginfo("{0} started, listening for image input on topic /cv_camera/image_raw, publishing on topic facedetect".format(FaceDetect.NODE_NAME))
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print "shutting down"
        rospy.loginfo("Stopping {0}...".format(FaceDetect.NODE_NAME))
        rospy.loginfo("{0} stopped.".format(FaceDetect.NODE_NAME))

    cv.DestroyAllWindows()
     
if __name__=='__main__':
    main(sys.argv)
