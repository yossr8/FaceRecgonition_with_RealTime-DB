import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facerecognition-12-default-rtdb.firebaseio.com/"
})

#the refrence path to studentsID
ref = db.reference('StudentsId')

data = {
    "852741":
        {
            "name": "Emly Blunt",
            "major": "Economics",
            "starting Year": 2021,
            "total_attendance": 12,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting Year": 2020,
            "total_attendance": 7,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "123456":
        {
            "name": "Yossr Yasser",
            "major": "Computer Science",
            "starting Year": 2020,
            "total_attendance": 3,
            "standing": "A",
            "year": 3,
            "last_attendance_time": "2023-4-25  00:54:34"
        },
    "111111":
        {
            "name": "mohamed fathalla",
            "major": "Computer Science",
            "starting Year": 2018,
            "total_attendance": 10,
            "standing": "A",
            "year": 4,
            "last_attendance_time": "2023-4-25  00:54:34"
    }
}

#to send data to firebase
for key,value in data.items():
    ref.child(key).set(value)
