import cv2
import numpy as np
import time
##from adafruit_servokit import ServoKit


#Global Variables
##kit = ServoKit(channels=16)
triggerbusy = False



#Normalize opencv coordinates for servos
def normalizecoordinates(value):
    old_min = 0
    old_max = 1300
    new_min = 0
    new_max = 360
    return round(((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min)

#Pan and Tilt Servo
def servoaction(x,y):
    kit.servo[1].angle = normalizecoordinates(x)
    kit.servo[4].angle = normalizecoordinates(y)
    if not triggerbusy:
        trigger()

#Pan and Tilt Servo
def startposition():
    kit.servo[1].angle = 90
    kit.servo[4].angle = 90

#Bang Bang!
def trigger():
    triggerbusy = True
    kit.servo[0].angle = 0
    time.sleep(.1)
    kit.servo[0].angle = 60
    time.sleep(.1)
    kit.servo[0].angle = 0
    triggerbusy = False

#Start Turret Def
def startturret():

    ##startposition()

    cap = cv2.VideoCapture(0)
    frame_width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height =int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))
    timer = 0

    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')

    out = cv2.VideoWriter("output.avi", fourcc, 5.0, (1280,720))

    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    print(frame1.shape)
    while cap.isOpened():
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        maxSize = 0


        if timer < 50:
            timer += 1
        else:
            print("test")
            ##startposition()

        for contour in contours:

            (x, y, w, h) = cv2.boundingRect(contour)
            if (x * y) > maxSize:
                maxSize = (x * y)
            else:
                break
            timer = 0

            print("BANG! BANG! BANG! at ", (normalizecoordinates(x), normalizecoordinates(y)))
            ##servoaction(x, y)

            if cv2.contourArea(contour) < 900:
                continue

            cv2.circle(frame1,(x,y),20,(0,255,0))
            #cv2.putText(frame1, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
            #           1, (0, 0, 255), 3)
        cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2)
        image = cv2.resize(frame1, (1280,720))
        out.write(image)

        frame1 = frame2
        ret, frame2 = cap.read()

        if cv2.waitKey(40) == 27:
            break

    cv2.destroyAllWindows()
    cap.release()
    out.release()



#Start Turret
time.sleep(1)
print("Ready?")
time.sleep(2)
print("Aim")
time.sleep(2)
print("Fire!")
startturret()