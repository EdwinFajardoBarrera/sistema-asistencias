from MySQLdb import DATETIME
import cv2 as cv
from flask import Flask, render_template, Response, redirect, url_for
from flask import request
from markupsafe import escape
import imutils
import os
import numpy as np
from flask_mysqldb import MySQL
from flask import jsonify
from datetime import datetime
import requests
import json

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'assistances_system'

mysql = MySQL(app)
# === RUTAS === #


@app.route('/assists')
def assists():
    return render_template("assistances.html")


@app.route('/hey')
def hey():
    query = "SELECT u.name, u.id FROM users as u, assistances as a WHERE a.user_id = u.id AND Date(date) = CURDATE();"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    users = cursor.fetchall()
    # print(str(users))

    res = ''
    for i in users:
        only_name = ((str(i[0])).split())[0]
        # print("MNnombre " + only_name)
        name = only_name + "_" + str(i[1])
        # print("USUARIO: " + name)
        res = res + name + ","

    res = res[:-1]
    print("RES: " + res)

    return res


@app.route('/assistances')
def assistances():
    query = "SELECT u.name, u.id, a.date FROM users as u, assistances as a WHERE a.user_id = u.id AND Date(date) = CURDATE();"
    cur = mysql.connection.cursor()
    cur.execute(query)
    row_headers = [x[0]
                   for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json.dumps(json_data)


@app.route('/users')
def users():
    query = "SELECT u.name, u.id, u.birthday FROM users as u"
    cur = mysql.connection.cursor()
    cur.execute(query)
    row_headers = [x[0]
                   for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json.dumps(json_data)


@app.route('/users-view')
def users_view():
    return render_template("users.html")

# @app.route('/users', methods=["GET", "POST"])
# @app.route('/users/<id>', methods=["GET", "DELETE"])
# def user():
#     # if (request.method == "GET"):
#     print("USUARIOS")
#     return "usuarios"


@app.route('/asist/<id>')
def assist(id):
    query = "INSERT INTO assistances(user_id, date) VALUES (%s, %s)"
    cur = mysql.connection.cursor()
    cur.execute(query, (id, datetime.now()))
    mysql.connection.commit()
    cur.close()
    print("REGISTRADO!")
    return ":)"


@app.route('/')  # Menú principal
def index():
    return render_template('index.html')


@app.route('/register_face/<name>')  # Registro de caras
def register_face(name):
    return render_template('capture.html', name=name)


@app.route('/detect_face')  # Sistema de reconocimiento (lista)
def detect_face():
    return render_template('recognice.html')


@app.route('/train')  # Sistema de entrenamiento
def train():
    return train_system()


@app.route('/recognice_feed')  # Genera las imagenes de reconocimiento
def recognice_feed():
    return Response(detect_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed/<name>')  # Genera las imagenes de guardado de caras
def video_feed(name):
    return Response(capture_faces(name), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/register_user', methods=["POST"])
def register():
    if request.method == "POST":
        print("request")
        print(request.is_json)
        content = request.get_json()
        print(content)
        # details = request.form
        name = content['name']
        birthday = content['birthday']
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users(name, birthday, address) VALUES (%s, %s, %s)", (name, birthday, "Calle 53 #321 x 14a"))
        mysql.connection.commit()
        query = "SELECT * FROM users ORDER BY id DESC LIMIT 1;"
        cur.execute(query)
        user = cur.fetchone()
        cur.close()

        user = str(user).replace("'", "")
        user = user.replace("(", "")
        print(user)

        parts = user.split(",")
        id = parts[0]
        name = parts[1].split()[0]

        user_id = name + '_' + id
        return jsonify(
            userName=user_id
        )
    return "user"


# === METODOS === #

# Método que detecta que persona se reconoce

def detect_faces():  # generate frame by frame from camera
    camera = cv.VideoCapture(0)
    assistance = False
    usersList = []
    dataPath = os.getcwd() + '/Data'
    imagePaths = os.listdir(dataPath)
    print('imagePaths=', imagePaths)

    face_recognizer = cv.face.EigenFaceRecognizer_create()
    face_recognizer.read('modeloEigenFace.xml')
    faceClassif = cv.CascadeClassifier(
        cv.data.haarcascades+'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = camera.read()
        if ret == False:
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        auxFrame = gray.copy()

        faces = faceClassif.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            rostro = auxFrame[y:y+h, x:x+w]
            rostro = cv.resize(rostro, (150, 150),
                               interpolation=cv.INTER_CUBIC)

            result = face_recognizer.predict(rostro)

            if result[1] < 5500:
                completeId = imagePaths[result[0]]  # Edwin_12
                parts = imagePaths[result[0]].split("_")  # ["Edwin", "12"]
                userName = parts[0]  # Edwin
                userId = parts[1]  # 12

                if (completeId not in usersList):
                    cv.putText(frame, '{}'.format(
                        userName), (x, y-25), 2, 1.1, (0, 255, 0), 1, cv.LINE_AA)
                else:
                    cv.putText(frame, '{}'.format(
                        userName + " - Registrado"), (x, y-25), 2, 1.1, (0, 255, 0), 1, cv.LINE_AA)

                # imagePaths[result[0]]), (x, y-25), 2, 1.1, (0, 255, 0), 1, cv.LINE_AA)
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Se obtienen los que tienen asistencia hoy
                if (not assistance):
                    r = requests.get('http://localhost:5000/hey')
                    usersList = (r.text).split(",")
                    assistance = True

                # Si no está en la lista se guarda su asistencia
                if (completeId not in usersList):
                    r = requests.get('http://localhost:5000/asist/' + userId)
                    usersList.append(completeId)

            else:
                cv.putText(frame, 'Desconocido', (x, y-20), 2,
                           0.8, (0, 0, 255), 1, cv.LINE_AA)
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

        ret, buffer = cv.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


# Método que captura las imagenes
def capture_faces(name):  # generate frame by frame from camera
    camera = cv.VideoCapture(0)
    count = 0

    # Se obtiene el path de datos
    dataPath = os.getcwd() + '/Data'
    personPath = dataPath + '/' + name

    # Se crea la carpeta para los datos del usuario
    if not os.path.exists(personPath):
        print('Carpeta creada: ', personPath)
        os.makedirs(personPath)

    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            faceClassif = cv.CascadeClassifier(
                cv.data.haarcascades+'haarcascade_frontalface_default.xml')

            frame = imutils.resize(frame, width=640)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            auxFrame = frame.copy()

            faces = faceClassif.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                rostro = auxFrame[y:y+h, x:x+w]
                rostro = cv.resize(rostro, (150, 150),
                                   interpolation=cv.INTER_CUBIC)
                cv.imwrite(personPath + '/rostro_{}.jpg'.format(count), rostro)
                count = count + 1

        success, buffer = cv.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


# Método para entrenamiento del sistema
def train_system():
    dataPath = os.getcwd() + '/Data'
    peopleList = os.listdir(dataPath)

    labels = []
    facesData = []
    label = 0

    for nameDir in peopleList:
        personPath = dataPath + '/' + nameDir
        print('Leyendo las imágenes')

        for fileName in os.listdir(personPath):
            # print('Rostros: ', nameDir + '/' + fileName)
            labels.append(label)
            facesData.append(cv.imread(personPath+'/'+fileName, 0))
        label = label + 1

    # Métodos para entrenar el reconocedor
    face_recognizer = cv.face.EigenFaceRecognizer_create()

    # Entrenando el reconocedor de rostros
    print("Entrenando...")
    face_recognizer.train(facesData, np.array(labels))

    # Almacenando el modelo obtenido
    face_recognizer.write('modeloEigenFace.xml')
    print("Modelo almacenado...")

    return redirect('/')
