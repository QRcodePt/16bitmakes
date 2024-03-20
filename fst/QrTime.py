import kivy
import pygame
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
import base64
from io import BytesIO
import qrcode
import time
import requests
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock


class MyQRCodeGenerator(BoxLayout):
    def __init__(self, **kwargs):
        super(MyQRCodeGenerator, self).__init__(**kwargs)
        # Вызываем функцию для генерации QR-кода
        self.generate_qr_code()
        # Назначаем функцию обновления для вызова каждые 20 секунд
        Clock.schedule_interval(lambda *dt: self.generate_qr_code(), 20)

    def generate_qr_code(self):
        # Генерируем QR код с использованием текущего времени в качестве данных
        data = str(time.time())
        # Создаем QR код с использованием kivy и qrcode библиотек
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Конвертируем изображение в base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Отправляем данные о QR коде на сервер Flask
        url = 'http://127.0.0.1:5000/qrcodes/add'
        payload = {'data': data, 'image': image_base64}
        r = requests.post(url, json=payload)

        # Удаляем старые виджеты, чтобы обновить QR код
        self.clear_widgets()

        # Отображение нового QR кода в приложении Kivy
        buffer.seek(0)
        texture = CoreImage(BytesIO(buffer.read()), ext="png").texture
        qr_image = Image(texture=texture)
        self.add_widget(qr_image)


class QRCodeGeneratorApp(App):
    def build(self):
        return MyQRCodeGenerator()


if __name__ == '__main__':
    QRCodeGeneratorApp().run()