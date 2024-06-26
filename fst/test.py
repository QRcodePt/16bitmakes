import re

import requests
from kivy.clock import Clock
from kivy.uix.camera import Camera
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.dialog import MDDialog
from kivy.uix.relativelayout import RelativeLayout
from pyzbar.pyzbar import decode
from kivy.graphics.texture import Texture
import cv2

x = ""
screen_width, screen_height = (400, 100)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = FloatLayout()

        login_label = MDLabel(text='Логин', halign="center")
        login_label_pos_x = screen_width / 9 - login_label.width / 2
        login_label_pos_y = screen_height / 2 + screen_height / 2
        login_label.pos = (login_label_pos_x, login_label_pos_y)

        login_input = MDTextField(hint_text="Введите логин", size_hint=(None, None), width=150, pos_hint={"center_x": 0.5, "center_y": 0.6})

        password_label = MDLabel(text='Пароль', halign="center")
        password_label_pos_x = screen_width / 4 - password_label.width / 1
        password_label_pos_y = screen_height / 10 + screen_height / 24
        password_label.pos = (password_label_pos_x, password_label_pos_y)

        password_input = MDTextField(hint_text="Введите пароль", password=True, size_hint=(None, None), width=150, pos_hint={"center_x": 0.5, "center_y": 0.45})

        layout.add_widget(login_label)
        layout.add_widget(login_input)
        layout.add_widget(password_label)
        layout.add_widget(password_input)

        button = MDRectangleFlatButton(text='Вход', pos_hint={"center_x": 0.5, "center_y": 0.35})
        button.bind(on_press=self.check_login)
        layout.add_widget(button)

        self.add_widget(layout)

    def check_login(self, instance):
        login_input = self.children[0].children[3]
        password_input = self.children[0].children[1]

        login = login_input.text
        print(login)
        password = password_input.text
        print(password)

        url = 'http://127.0.0.1:5000/employees'
        data = {'login': login, 'password': password}

        response = requests.post(url, json=data)

        user = response.json()
        string = str(user)
        string = re.sub(r'\W', ' ', string)
        string = string[2:]

        if user:
            self.open_next_screen(instance, string)
            print('activate')
        else:
            self.show_invalid_password_popup()
            print("dontactivate")

    def show_invalid_password_popup(self):
        dialog = MDDialog(title="Ошибка", text="Неправильный логин/пароль, попробуйте снова.", size_hint=(0.8, 0.3))
        dialog.open()

    def open_next_screen(self, instance, string):
        next_screen = NextScreen(string_value=string)
        self.manager.current = 'NextScreen'


class NextScreen(Screen):
    def __init__(self, string_value="", **kwargs):
        super(NextScreen, self).__init__(**kwargs)
        layout = FloatLayout()
        self.string_value = string_value
        print(self.string_value)

        self.fio_label = MDLabel(text=self.string_value, halign="center")
        fio_label_pos_x = screen_width / 2 - len(self.string_value) * 10 / 2
        fio_label_pos_y = screen_height / 2 + screen_height / 3
        self.fio_label.pos = (fio_label_pos_x, fio_label_pos_y)
        layout.add_widget(self.fio_label)

        button1 = MDRectangleFlatButton(text='Открыть смену', pos_hint={"center_x": 0.3, "center_y": 0.2})
        button1.bind(on_press=self.open_qr_screen)
        layout.add_widget(button1)

        button2 = MDRectangleFlatButton(text='Закрыть смену', pos_hint={"center_x": 0.7, "center_y": 0.2})
        button2.bind(on_press=self.open_qr_screen)
        layout.add_widget(button2)

        hours_label = MDLabel(text='Часов отработано 13', halign="center", pos_hint={"center_x": 0.5, "center_y": 0.3})
        layout.add_widget(hours_label)

        days_label = MDLabel(text='Дней отработано 13', halign="center", pos_hint={"center_x": 0.5, "center_y": 0.4})
        layout.add_widget(days_label)

        button3 = MDRectangleFlatButton(text='Выход', pos_hint={"center_x": 0.9, "center_y": 0.1})
        button3.bind(on_press=self.open_first_screen)
        layout.add_widget(button3)

        self.add_widget(layout)

    def open_qr_screen(self, instance):
        self.manager.current = 'QR_Screen'

    def open_first_screen(self, instance):
        self.manager.current = 'LoginScreen'

class QR_Screen(Screen):
    def __init__(self, **kwargs):
        super(QR_Screen, self).__init__(**kwargs)
        layout = RelativeLayout()

        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.camera_widget = Camera(play=True)

        qr_label = MDLabel(text='Отсканируйте QR код', halign="center", pos_hint={"center_x": 0.5, "center_y": 0.9})

        button = MDRectangleFlatButton(text='Назад', pos_hint={"center_x": 0.9, "center_y": 0.1})
        button.bind(on_press=self.open_second_screen)

        button_start = MDRectangleFlatButton(text='Начать сканирование', pos_hint={"center_x": 0.5, "center_y": 0.2})
        button_start.bind(on_press=self.update_camera)

        layout.add_widget(self.camera_widget)
        layout.add_widget(button)
        layout.add_widget(button_start)
        layout.add_widget(qr_label)

        self.add_widget(layout)

    def open_second_screen(self, instance):
        self.manager.current = 'NextScreen'

    # функция считывающая данные с QR кода
    def update_camera(self, *args):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            decoded_objects = decode(frame)

            texture = Texture.create(size=(frame.shape[1], frame.shape[0]))
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            for obj in decoded_objects:
                if obj.type == 'QRCODE':
                    qr_data = obj.data.decode('utf-8')
                    print("QR Code Data:", qr_data)
                    # Дальнейшие действия с данными QR кода

            self.camera_widget.texture = texture

    # Подключить обмен данных через фласк



class TestApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='LoginScreen'))
        sm.add_widget(NextScreen(name='NextScreen'))
        sm.add_widget(QR_Screen(name='QR_Screen'))

        return sm

if __name__ == '__main__':
    TestApp().run()