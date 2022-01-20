import os
from datetime import datetime, date

import cv2
import dlib
import face_recognition
import numpy as np
import pymysql
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, Response, send_from_directory
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from keras.models import load_model
from sqlalchemy import exc

from flask_session import Session

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

pymysql.install_as_MySQLdb()
# Database

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/mcaprj'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# INIT DB
db = SQLAlchemy(app)
# ma
ma = Marshmallow(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
emotion_model_path = 'models/model.h5'
emotion_classifier = load_model(emotion_model_path, compile=False)
input_shape = 64
EMOTIONS = ["angry", "disgust", "scared",
            "happy", "sad", "surprised", "neutral"]

sess = Session(app)


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))

    def __init__(self, name, roll_no):
        self.name = name
        self.roll_no = roll_no


class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __init__(self, image, user_id):
        self.image = image
        self.user_id = user_id


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    is_present = db.Column(db.Boolean, default=False)
    emotion = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today())
    datetime = db.Column(db.DateTime, default=datetime.today())

    def __init__(self, user_id, is_present, emotion, date, datetime):
        self.user_id = user_id
        self.is_present = is_present
        self.emotion = emotion
        self.date = date
        self.datetime = datetime


class StudentSchema(ma.Schema):
    class Meta:
        fields = ['id', 'name', 'roll_no']


class ImageSchema(ma.Schema):
    class Meta:
        fields = ['id', 'image', 'user_id']


class AttendanceSchema(ma.Schema):
    class Meta:
        fields = ['id', 'user_id', 'is_present', 'emotion', 'date', 'datetime']


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

image_schema = ImageSchema()
images_schema = ImageSchema(many=True)

attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)


def getEmotionText(param):
    return EMOTIONS[int(param)]


@app.route('/', methods=['GET'])
def get_all_attendance():
    dataset = db.session.query(Attendance, Student).filter(Attendance.user_id == Student.id,
                                                           Attendance.date == date.today(),
                                                           Attendance.is_present != 0).all()
    resp_data = []
    for attns, stns in dataset:

        resp_data.append({"id": attns.id, "datetime": attns.datetime, "emotion": getEmotionText(attns.emotion),
                          "name": stns.name,
                          "roll_no": stns.roll_no, "is_present": attns.is_present})
    return render_template("index.html", data=resp_data, now=date.today())


def getframe():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            return frame


def gen():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/del_attendance', methods=['POST'])
def del_attendance():
    id = request.form['id']
    print(id)
    atn = Attendance.query.get(id)
    db.session.delete(atn)
    if db.session.commit():
        print("Deleted")
    else:
        print("Not Deleted")
    return redirect(url_for("get_all_attendance"))


@app.route('/image', methods=['GET'])
def get_all_image():
    images = Images.query.all()
    result = images_schema.dump(images)
    return jsonify(result)


@app.route('/image/<id>', methods=['GET'])
def get_one_student(id):
    student = Student.query.get(id)
    return student_schema.jsonify(student)


@app.route('/image/<id>', methods=['DELETE'])
def delete_image(id):
    image = Images.query.get(id)
    if image is not None:
        try:
            db.session.delete(image)
            db.session.commit()
            os.remove(os.path.join("images", image.image))
        except:
            pass
    return student_schema.jsonify(image)


@app.route('/<id>', methods=['GET'])
def get_one_image(id):
    image = Images.query.get(id)
    return image_schema.jsonify(image)


@app.route('/<id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    student.name = request.form['name']
    student.name = request.form['roll_no']
    db.session.commit()
    return student_schema.jsonify(student)


@app.route('/<id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if student is not None:
        db.session.delete(student)
        db.session.commit()
        image = Images.query.filter_by(user_id=student.id)
        print(image)
        try:

            f = os.path.join("images", image.image)
            os.remove(f)
        except:
            pass
        return student_schema.jsonify(student)
    else:
        return None


@app.route('/new_student', methods=['POST'])
def new_student():
    file = request.files['image']
    file.save(os.path.join(BASE_DIR, "images/" + file.filename))
    name = request.form['name']
    roll_no = request.form['roll_no']
    new_student = Student(name, roll_no)
    db.session.add(new_student)
    try:
        db.session.commit()
        get_student = Student.query.filter_by(roll_no=roll_no).first()
        new_image = Images(file.filename, get_student.id)
        db.session.add(new_image)
        db.session.commit()
    except exc.SQLAlchemyError:
        pass

    # return student_schema.jsonify(new_student)
    # session['messages'] = "Student Added"
    session['msg'] = "Student Added"
    return redirect(url_for("new_student"))


@app.route('/new_student', methods=['GET'])
def new_student_page():
    return render_template("new_student_form.html", msg=session.get("msg", None))


def read_roll_no_from_db(file_name):
    img_get = Images.query.filter_by(image=file_name).first()
    if img_get is not None:
        student = Student.query.get(img_get.user_id)
        if student is None:
            print("No Student Found")
            return 0
        else:
            return student.roll_no
    else:
        print("No Image Found")


def get_roll_no(img):
    resp = []
    for filename in os.listdir("images"):
        f = os.path.join("images", filename)
        known_image = face_recognition.load_image_file(f)
        unknown_image = face_recognition.load_image_file(img)
        k_list = face_recognition.face_encodings(known_image)
        u_list = face_recognition.face_encodings(unknown_image)
        if len(k_list) > 0 and len(u_list) > 0:
            known_enc = k_list[0]
            unknown_encoding = u_list[0]
            result = face_recognition.compare_faces(
                [known_enc], unknown_encoding)[0]
            if result:
                resp.append(read_roll_no_from_db(filename))
        else:
            print(00000)
            return None
    return resp


def get_emotion(img):
    print(img)
    img = cv2.imread("temp_image/" + img, 0)
    # print(img)
    # # img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, (48, 48), interpolation=cv2.INTER_AREA)
    img = np.array(img)
    img = img.reshape(1, 48, 48, 1)
    # res = model.predict(img)
    res = emotion_classifier.predict(img)
    label = EMOTIONS[res.argmax()]
    print(label)
    return res.argmax()


def create_faces(faces, frames, new_path):
    for counter, face in enumerate(faces):
        x1, y1 = face.left(), face.top()
        x2, y2 = face.right(), face.bottom()
        imgCrop = frames[y1:y2, x1: x2]
        # we need this line to reshape the images
        imgCrop = cv2.resize(imgCrop, (48, 48))
        cv2.imwrite(new_path + str(counter) + ".jpg", imgCrop)


def ConvertListToDic(list):
    res_dct = {list[i]: list[i + 1] for i in range(0, len(list), 2)}
    return res_dct


def remove(string):
    return string.replace(" ", "")


def save_attendance(roll_nos, emotion=3.2):
    user = Student.query.filter_by(roll_no=roll_nos).first()
    c_attn = Attendance.query.filter_by(user_id=user.id, date=date.today()).first()
    if c_attn is None:
        attn = Attendance(user.id, True, emotion, date.today(), datetime.utcnow())
    else:
        return 0
    try:
        db.session.add(attn)
        db.session.commit()
    except:
        pass


@app.route('/read_video', methods=['GET'])
def read_video_frame():
    # return render_template("attendance_new.html")
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/attendance', methods=['GET'])
def get_attendance():
    return render_template("attendance_new.html")


@app.route('/attendance', methods=['POST'])
def post_attendance():
    detector = dlib.get_frontal_face_detector()
    new_path = "temp_image/new"
    if str(request.form['key']) == '1':
        frame = getframe()
        file_name = "request_image/" + str(datetime.utcnow()).replace(" ", "_") + ".jpg"
        if cv2.imwrite(file_name, frame):
            print(file_name)
        else:
            pass
    else:
        file = request.files['image']
        file.save("request_image/" + file.filename)
        frame = cv2.imread("request_image/" + file.filename)
    faces = detector(frame)
    create_faces(faces, frame, new_path)
    cv_img = []
    roll_nos = []
    students = []

    for file in os.listdir("temp_image"):
        f = os.path.join("temp_image", file)
        rolls = get_roll_no(f)
        if rolls is not None:
            for roll in rolls:
                if roll is not None:
                    roll_nos.append(remove(roll))
                    students.append(Student.query.filter_by(
                        roll_no=remove(roll)).first())
                    emotion = get_emotion(file)
                    save_attendance(roll, emotion)
                else:
                    print("No FIle Found")

            for f in os.listdir("request_image"):
                os.remove(os.path.join("request_image", f))

            for f in os.listdir("temp_image"):
                os.remove(os.path.join("temp_image", f))
        else:
            session['msg'] = "No Student Found"

        return redirect(url_for("get_all_attendance"))


@app.route('/filemanager/<path:filename>')
def download_file(filename):
    return send_from_directory("images", filename, as_attachment=True)


@app.route('/students', methods=['GET'])
def get_all_students():
    student = Student.query.all()
    print(student)
    student_with_image = db.session.query(Student, Images).filter(Student.id == Images.user_id).all()
    records = []
    for st, img in student_with_image:
        records.append({"student_id": st.id, "name": st.name, "roll_no": st.roll_no,
                        "img": img.image})
    return render_template("students.html", data=records)


@app.route('/student/<id>', methods=['GET'])
def up_get_student(id):
    student = db.session.query(Student, Images).filter(Student.id == Images.user_id, Student.id == id).first()
    print(student)
    data = {}
    data = {"name": student[0].name, "roll_no": student[0].roll_no, "image": student[1].image,
            "student_id": student[0].id, "image_id": student[1].id,
            "path": os.path.join(BASE_DIR, "images/" + student[1].image)}
    print(data)
    return render_template("student_edit.html", data=data)


@app.route('/student', methods=['POST'])
def do_on_student():
    action = request.form['action']
    id = request.form['id']
    student = db.session.query(Student, Images).filter(Student.id == Images.user_id, Student.id == id).first()
    print(student)
    data = {}
    data = {"name": student[0].name, "roll_no": student[0].roll_no, "image": student[1].image,
            "student_id": student[0].id, "image_id": student[1].id,
            "path": os.path.join(BASE_DIR, "images/" + student[1].image)}

    if action == "delete":
        st = Student.query.filter_by(id=data['student_id']).first()
        img = Images.query.filter_by(id=data['image_id']).first()
        db.session.delete(st)
        db.session.delete(img)
        if db.session.commit():
            os.remove(os.path.join("images", data['image']))
            session['msg'] = "Deleted"
        else:
            session['msg'] = "Image Delete Error"
        print(session['msg'])
    else:
        if action == "edit":
            file = request.files['image']
            if file:
                img = Images.query.filter_by(id=data['image_id']).first()
                if img is not None:
                    filepath = os.path.join(BASE_DIR + 'images/' + file.filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)

                    file.save(os.path.join(BASE_DIR, "images/" + file.filename))
                    print(file.filename)
                    img.image = file.filename

            st = Student.query.filter_by(id=data['student_id']).first()
            st.name = request.form['name']
            st.roll_no = request.form['roll_no']

        db.session.commit()
    return redirect(url_for("get_all_students"))


if __name__ == '__main__':
    app.run(debug=True)
