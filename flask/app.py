from flask import Flask, jsonify, request
import sqlite3
import base64
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('DB_workhour.db')
    conn.row_factory = sqlite3.Row
    return conn

# Маршрут для получения данных из таблицы Employees
@app.route('/employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Employees')
    employees = cursor.fetchall()
    conn.close()
    return jsonify({'employees': [dict(emp) for emp in employees]})

# Маршрут для получения данных из таблицы QRCode
# Маршрут для добавления данных о QR коде в базу данных
@app.route('/qrcodes/add', methods=['POST'])
def add_qr_code():
    data = request.json.get('data')
    image_base64 = request.json.get('image')

    # Convert base64 back to image
    im = Image.open(BytesIO(base64.b64decode(image_base64)))

    # Соединяемся с базой данных
    conn = sqlite3.connect('DB_workhour.db')
    cursor = conn.cursor()

    # Вставляем данные в таблицу QRCode
    cursor.execute('INSERT INTO QRCode (qr_code, last_updated) VALUES (?, current_timestamp)', (data,))
    conn.commit()
    conn.close()

    return 'QR code successfully added to the database!'


@app.route('/employees/', methods=['POST'])
def check_login():
    login = request.json.get('login')
    password = request.json.get("password")

    conn = sqlite3.connect('DB_workhour.db')
    cursor = conn.cursor()

    cursor.execute("SELECT full_name FROM employees WHERE Username=? AND password=?", (login, password))
    user = cursor.fetchone()

    if user:
        return jsonify(user)
    else:
        return jsonify(0)

# Маршрут для получения данных из таблицы WorkHours
@app.route('/workhours', methods=['GET'])
def get_workhours():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM WorkHours')
    workhours = cursor.fetchall()
    conn.close()
    return jsonify({'workhours': [dict(wh) for wh in workhours]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
