import os
import pickle
import cv2
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facerecognition-12-default-rtdb.firebaseio.com/",
    'storageBucket':"facerecognition-12.appspot.com"
})
bucket = storage.bucket()


# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Set the video capture dimensions
cap.set(3,640) #width
cap.set(4,480) # height

#set background for webcam
imagebackground = cv2.imread('resources/background.png')

#importing the mode images into list
folderModePath = 'resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
    #print(len(imgModeList))

#load the encoding file
print("loading encode file")
file= open("EncodeFile.p","rb")

#to add all the information in the list
encodeListKnowWithIds= pickle.load(file)

#to extract it into 2 parts
file.close()
encodeListKnown , studentIds = encodeListKnowWithIds
#print(studentIds)
print("encode file loaded")

#to show that it is in active state
ModeType =0
counter =0
id = -1
imgStudent = []


# Loop through the frames from the camera
while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # to resize our image becuase it takes alot of computation so we'll lower down to 1/4
    imgSmall = cv2.resize(frame,(0,0),None,0.25,0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    #encoding in the face current frame
    faceCurFrame = face_recognition.face_locations(imgSmall)
    encodeCurFrame = face_recognition.face_encodings(imgSmall, faceCurFrame)

    # Flip the image horizontally
    frame = cv2.flip(frame, 1)

    #to overlay the webcam over the background image
    imagebackground[162:162+480,55:55+640]= frame

    #to overlay modes on the background image
    imagebackground[44:44+633, 808:808+414] = imgModeList[ModeType]   #number can be changes according to the mode

    # Check if the frame was successfully read
    if not ret:
        print("Error: Failed to capture frame")
        break

    if faceCurFrame:
        #loop through all the encodings to see if they matches or not
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            #print("distance", faceDistance)

            # to find the least index
            matchIndex = np.argmin(faceDistance)
            # print("match index", matchIndex)

        #to find the matched face
        if matches [matchIndex]:
            # print("known face detected")
            # print(studentIds[matchIndex])
            y1, x2, y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4,x1*4 #because we reduced img to 1/4
            if cv2.flip:
                bbox = (frame.shape[1] - x1 - (x2 - x1) + 55, y1 + 162, x2 - x1, y2 - y1)
            else:
                bbox = (x1 + 55, y1 + 162, x2 - x1, y2 - y1)
            imagebackground= cvzone.cornerRect(imagebackground,bbox, rt=0)

        id = studentIds[matchIndex] #whenever ids matches we need to show ids
        #to need face information in the first iteration after detection
        if counter ==0:
                cvzone.putTextRect(imagebackground,"Loading",(275,400))
                cv2.imshow('Face Attendance', imagebackground)
                cv2.waitKey(1)
                counter =1
                ModeType =1 #update mode
        #block of code to update the attendan
        if counter != 0:

            if counter == 1:
                # Get the Data
                studentInfo = db.reference(f'StudentsId/{id}').get()
                print(studentInfo)

                #get the image from the storgae
                blob= bucket.get_blob(f'images/{id}.png')


                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2RGB)

                #update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed>30:
                    ref = db.reference(f'StudentsId/{id}')
                    studentInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    ModeType=3
                    counter =0
                    imagebackground[44:44 + 633, 808:808 + 414] = imgModeList[ModeType]

            if ModeType !=3:
                if 10<counter<20:
                    ModeType=2

                imagebackground[44:44 + 633, 808:808 + 414] = imgModeList[ModeType]

                if counter<=10:
                    cv2.putText(imagebackground,str(studentInfo['total_attendance']),(861,125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imagebackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5 ,(255, 255, 255), 1)
                    cv2.putText(imagebackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imagebackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imagebackground, str(studentInfo['year']), (1025, 625 ),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imagebackground, str(studentInfo['starting Year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)


                    #to center the name
                    (w,h),_ =cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset =(414-w)//2
                    cv2.putText(imagebackground, str(studentInfo['name']), (808+offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    imagebackground[175:175 + 216, 909:909 + 216] = imgStudent


                counter+=1

                if counter>=20:
                    counter=0
                    ModeType=0
                    studentInfo=[]
                    imgStudent = []
                    imagebackground[44:44 + 633, 808:808 + 414] = imgModeList[ModeType]
    else:
        ModeType =0
        counter = 0





    #display background
    cv2.imshow('Face Attendance', imagebackground)

    # Wait for a key press event
    # q is for quiting the webcam
    if cv2.waitKey(1) == ord('q'):
        break

# Release the video capture object and close the window
cap.release()
cv2.destroyAllWindows()

