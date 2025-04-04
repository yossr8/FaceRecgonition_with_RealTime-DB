import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognition-12-default-rtdb.firebaseio.com/",
    'storageBucket': "facerecognition-12.appspot.com"
})

# Importing student images
folderPath = 'images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    if img is None:
        print(f"Error: Could not read image {path}")
        continue
    imgList.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    studentIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            encodeList.append(encodings[0])
        else:
            print("Error: Could not find any faces in image")
    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
