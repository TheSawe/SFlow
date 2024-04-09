from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QWidget, QLineEdit
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QRect, QPoint, QPropertyAnimation, QEasingCurve, QTimer

import json
import pyaudio
from vosk import Model, KaldiRecognizer
import random
import ctypes

import pymysql
from Db.config import host, user, password, db_name, port

from email_sender import send_reg_code

# For displaying taskbar app icon in win11
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('TheSaweMadeIt')


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # SQL Server Connection Setup

        try:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                port=port,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            print('log: Successfully connected')
        except Exception as ex:
            print('Connection refused...')
            print(ex)
            app.exec()

        self.console_text = {}
        self.count_of_launches = 0
        self.speed = 500
        self.toggle_pos = False
        self.sign_pos = False
        self.name = ''
        self.email_list = []
        self.secrete_code = random.randint(100000, 999999)

        self.setWindowIcon(QIcon('img/icon_nobg.png'))
        self.setWindowTitle('PyProject-Assistant')
        self.setFixedHeight(600)
        self.setFixedWidth(400)

        self.top_rect = QLabel(self)
        self.top_rect.setGeometry(QRect(0, -100, 400, 700))  # -100
        self.animation1 = QPropertyAnimation(self.top_rect, b"pos")

        self.reg_bg = QLabel(self)
        self.reg_bg.setGeometry(QRect(0, 0, 400, 600))
        self.reg_bg.setPixmap(QPixmap('img/reg_bg.jpg'))
        self.animation2 = QPropertyAnimation(self.reg_bg, b"pos")

        self.sign_up = QPushButton('Sign Up', self)
        self.sign_up.setGeometry(QRect(13, 13, 45, 17))
        self.sign_up.clicked.connect(self.sign_up_func)
        self.sign_up.setFlat(True)

        self.sign_in = QPushButton('Sign In', self)
        self.sign_in.setGeometry(QRect(70, 13, 46, 17))
        self.sign_in.clicked.connect(self.sign_in_func)
        self.sign_in.setFlat(True)

        self.recommendation_sign_in = QLabel(self)
        self.recommendation_sign_in.setGeometry(122, 149, 150, 13)
        self.recommendation_sign_in.setPixmap(QPixmap('img/recommendation.jpg'))
        self.animation14 = QPropertyAnimation(self.recommendation_sign_in, b'pos')

        self.recommendation_sign_up = QLabel(self)
        self.recommendation_sign_up.setGeometry(400, 149, 159, 13)
        self.recommendation_sign_up.setPixmap(QPixmap('img/recommendation_sign_up.jpg'))
        self.animation15 = QPropertyAnimation(self.recommendation_sign_up, b'pos')

        self.nickname = QLabel(self)
        self.nickname.setGeometry(QRect(103, 216, 74, 9))
        self.nickname.setPixmap(QPixmap('img/username.jpg'))
        self.animation16 = QPropertyAnimation(self.nickname, b'pos')

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Your Nickname')
        self.username_input.setGeometry(QRect(86, 231, 222, 34))
        self.animation17 = QPropertyAnimation(self.username_input, b'pos')

        self.email = QLabel(self)
        self.email.setGeometry(QRect(400, 251, 39, 8))
        self.email.setPixmap(QPixmap('img/email.jpg'))
        self.animation20 = QPropertyAnimation(self.email, b'pos')

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('name.example@pyproject.com')
        self.email_input.setGeometry(QRect(400, 264, 222, 34))  # 86
        self.animation21 = QPropertyAnimation(self.email_input, b'pos')

        self.reg_code = QLabel(self)
        self.reg_code.setGeometry(QRect(400, 251, 136, 8))
        self.reg_code.setPixmap(QPixmap('img/reg_code.jpg'))
        self.animation27 = QPropertyAnimation(self.reg_code, b'pos')

        self.reg_code_input = QLineEdit(self)
        self.reg_code_input.setPlaceholderText('Code')
        self.reg_code_input.setGeometry(QRect(400, 264, 222, 34))  # 86
        self.animation28 = QPropertyAnimation(self.reg_code_input, b'pos')

        self.reg_code_btn = QPushButton('Confirm Code', self)
        self.reg_code_btn.setGeometry(QRect(400, 484, 228, 34))
        self.reg_code_btn.pressed.connect(self.reg_code_check)
        self.animation29 = QPropertyAnimation(self.reg_code_btn, b"pos")

        self.password = QLabel(self)
        self.password.setGeometry(QRect(103, 295, 71, 9))
        self.password.setPixmap(QPixmap('img/password.jpg'))
        self.animation18 = QPropertyAnimation(self.password, b'pos')

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setGeometry(QRect(86, 310, 222, 34))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.animation19 = QPropertyAnimation(self.password_input, b'pos')

        self.conf_password = QLabel(self)
        self.conf_password.setGeometry(QRect(400, 375, 136, 9))  # 103
        self.conf_password.setPixmap(QPixmap('img/conf_password.jpg'))
        self.animation22 = QPropertyAnimation(self.conf_password, b'pos')

        self.conf_password_input = QLineEdit(self)
        self.conf_password_input.setPlaceholderText('Confirm Password')
        self.conf_password_input.setGeometry(QRect(400, 392, 222, 34))
        self.conf_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.animation23 = QPropertyAnimation(self.conf_password_input, b'pos')

        self.toggle_bg = QPushButton(self)
        self.toggle_bg.setGeometry(QRect(400, 452, 40, 18))
        self.animation24 = QPropertyAnimation(self.toggle_bg, b'pos')
        self.toggle_bg.clicked.connect(self.toggle_func)

        self.toggle_circle = QPushButton(self)
        self.toggle_circle.setGeometry(QRect(98, 454, 14, 14))
        self.toggle_circle.clicked.connect(self.toggle_func)
        self.animation25 = QPropertyAnimation(self.toggle_circle, b'pos')

        self.toggle_text = QLabel(self)
        self.toggle_text.setGeometry(QRect(400, 455, 141, 9))  # 147
        self.toggle_text.setPixmap(QPixmap('img/agreement.jpg'))
        self.animation26 = QPropertyAnimation(self.toggle_text, b'pos')

        self.sign_btn = QPushButton('Sign In', self)
        self.sign_btn.setGeometry(QRect(86, 402, 228, 34))
        self.sign_btn.pressed.connect(self.check_reg)
        self.animation3 = QPropertyAnimation(self.sign_btn, b"pos")

        self.line = QLabel(self)
        self.line.setGeometry(QRect(60, 500, 280, 2))
        self.animation12 = QPropertyAnimation(self.line, b'pos')

        self.forgot_password = QLabel('Forgot password', self)
        self.forgot_password.setGeometry(QRect(138, 518, 123, 11))
        self.forgot_password.setPixmap(QPixmap('img/forgot_password.jpg'))
        self.animation13 = QPropertyAnimation(self.forgot_password, b'pos')

        self.top_rect_design = QLabel(self)
        self.top_rect_design.setGeometry(QRect(0, 600, 400, 285))  # 0
        self.top_rect_design.setPixmap(QPixmap('img/bg.jpg'))
        self.animation4 = QPropertyAnimation(self.top_rect_design, b"pos")

        self.user_name = QLabel(self)
        self.user_name.setGeometry(QRect(112, 600, 176, 27))  # 198
        self.user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.animation5 = QPropertyAnimation(self.user_name, b"pos")

        self.user_icon = QLabel(self)
        self.user_icon.setGeometry(146, 600, 107, 107)  # 58
        self.animation6 = QPropertyAnimation(self.user_icon, b"pos")

        self.circle1 = QLabel(self)
        self.circle1.setGeometry(QRect(182, 600, 6, 6))  # 300
        self.animation7 = QPropertyAnimation(self.circle1, b"pos")

        self.circle2 = QLabel(self)
        self.circle2.setGeometry(QRect(196, 600, 6, 6))
        self.animation8 = QPropertyAnimation(self.circle2, b"pos")

        self.circle3 = QLabel(self)
        self.circle3.setGeometry(QRect(210, 600, 6, 6))
        self.animation9 = QPropertyAnimation(self.circle3, b"pos")

        self.console = QLabel(self)
        self.console.setGeometry(20, 600, 360, 273)
        self.console.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.text_console_animation = QPropertyAnimation(self.console, b"pos")
        self.animation10 = QPropertyAnimation(self.text_console_animation, b"pos")

        self.talk_btn = QPushButton('Talk', self)
        self.talk_btn.setGeometry(QRect(145, 600, 110, 30))  # 247
        self.talk_btn.pressed.connect(self.stt)
        self.animation11 = QPropertyAnimation(self.talk_btn, b"pos")

        self.setStyleSheet('QMainWindow{background: qlineargradient(x1:1, y1:0, x2:1, y2:1,stop:0 blue, stop: 0.5\
        #0038FF, stop:1 #FFFFFF)}')
        self.sign_up.setStyleSheet('QPushButton{color: #5f5f5f; font-weight: 600; border-radius: 8px;}')
        self.sign_in.setStyleSheet('QPushButton{font-weight: 600;  border-radius: 8px;}')
        self.username_input.setStyleSheet('QLineEdit{color: #959595; font: bold italic; border-radius: 16px;\
        padding-left: 12px; padding-right: 12px; border: 1px solid #257CFF;}')
        self.email_input.setStyleSheet('QLineEdit{color: #959595; font: bold italic; border-radius: 16px;\
        padding-left: 12px; padding-right: 12px; border: 1px solid #257CFF;}')
        self.reg_code_input.setStyleSheet('QLineEdit{color: #959595; font: bold italic; border-radius: 16px;\
        padding-left: 12px; padding-right: 12px; border: 1px solid #257CFF;}')
        self.reg_code_btn.setStyleSheet('QPushButton{background-color: #257cff; border-radius: 15px; color: #fff; \
        font-size: 11px; font-weight: 700;}')
        self.password_input.setStyleSheet('QLineEdit{color: #959595; border-radius: 16px; padding-left: 12px; font: \
        bold italic; padding-right: 12px; border: 1px solid #257CFF;}')
        self.conf_password_input.setStyleSheet('QLineEdit{color: #959595; border-radius: 16px; padding-left: 12px; \
        font: bold italic; padding-right: 12px; border: 1px solid #257CFF;}')
        self.toggle_bg.setStyleSheet('QPushButton{background-color: #959595; border-radius: 9px;}')
        self.toggle_circle.setStyleSheet('QPushButton{border-radius: 6px; background-color: #fff;}')
        self.sign_btn.setStyleSheet('QPushButton{background-color: #257cff; border-radius: 15px; color: #fff; \
        font-size: 11px; font-weight: 700;}')
        self.line.setStyleSheet('QLabel{background-color: #CDCCFF;}')
        self.forgot_password.setStyleSheet('QLabel{color: #959595; font-size: 10px; letter-spacing: 0.3em;\
        font-weight: 700;}')
        self.top_rect.setStyleSheet('QLabel{background-color: #fff; border-radius: 45px;}')
        self.user_name.setStyleSheet('QLabel{font-size: 19px; font-weight: 700;}')
        self.user_icon.setStyleSheet('QLabel{background-color: #d9d9d9; border-radius: 30px;}')
        self.circle1.setStyleSheet('QLabel{background-color: #d1d1d1; border-radius: 3px;}')
        self.circle2.setStyleSheet('QLabel{background-color: #d1d1d1; border-radius: 3px;}')
        self.circle3.setStyleSheet('QLabel{background-color: #d1d1d1; border-radius: 3px;}')
        self.console.setStyleSheet('QLabel{background-color: #fff; border-radius: 15px; color: #5e5e5e; font-weight:\
        700; font-size: 12px; padding-top: 10px;}')
        self.talk_btn.setStyleSheet('QPushButton{background-color: #257cff; border-radius: 15px; color: #fff;\
        font-size: 11px; font-weight: 700; padding-bottom: 3px;}')

    def check_reg(self):
        if not self.sign_pos:
            with self.connection.cursor() as cursor:
                select_all_rows = "SELECT * FROM `users`"
                cursor.execute(select_all_rows)
                rows = cursor.fetchall()
                for row in rows:
                    if row['nickname'] == self.username_input.text() and row['password'] == self.password_input.text():
                        self.reg_to_menu()
                        self.name = row['nickname']
                        self.user_name.setText(self.name)
                return
        else:
            with self.connection.cursor() as cursor:
                select_all_rows = "SELECT * FROM `users`"
                cursor.execute(select_all_rows)
                rows = cursor.fetchall()
                for row in rows:
                    if row['email'] not in self.email_list:
                        self.email_list.append(row['email'])
                if len(self.username_input.text()) >= 3 and '@' in self.email_input.text() \
                        and '.' in self.email_input.text() and len(self.email_input.text()) >= 10 \
                        and self.password_input.text() == self.conf_password_input.text() \
                        and len(self.password_input.text()) >= 8 and self.toggle_pos\
                        and self.email_input.text() not in self.email_list:
                    self.reg_code_send()
                else:
                    print('log: Bad entered data!')

    def reg_code_send(self):
        self.username_input.setReadOnly(True)
        self.password_input.setReadOnly(True)
        self.conf_password_input.setReadOnly(True)
        self.toggle_bg.setEnabled(False)
        self.toggle_circle.setEnabled(False)
        self.sign_in.setEnabled(False)

        self.animation20.setEndValue(QPoint(-100, 251))
        self.animation20.setDuration(self.speed)
        self.animation20.start()

        self.animation21.setEndValue(QPoint(-222, 264))
        self.animation21.setDuration(self.speed)
        self.animation21.start()

        self.animation27.setEndValue(QPoint(103, 250))
        self.animation27.setDuration(self.speed)
        self.animation27.start()

        self.animation28.setEndValue(QPoint(86, 264))
        self.animation28.setDuration(self.speed)
        self.animation28.start()

        self.animation29.setEndValue(QPoint(86, 484))
        self.animation29.setDuration(self.speed)
        self.animation29.start()

        self.animation3.setEndValue(QPoint(-228, 484))
        self.animation3.setDuration(self.speed)
        self.animation3.start()

        send_reg_code(self.secrete_code, self.email_input.text())

    def reg_code_check(self):
        if int(self.reg_code_input.text()) == self.secrete_code:
            with self.connection.cursor() as cursor:
                insert_query = f"INSERT INTO users (nickname, email, password) VALUES ('{self.username_input.text()}', \
'{self.email_input.text()}', '{self.password_input.text()}');"
                print(insert_query)
                cursor.execute(insert_query)
                self.connection.commit()
            print('log: Successfully registered')
            self.reg_code_input.hide()
            self.reg_code.hide()
            self.reg_code_btn.hide()
            self.username_input.setReadOnly(False)
            self.password_input.setReadOnly(False)
            self.conf_password_input.setReadOnly(False)
            self.toggle_bg.setEnabled(True)
            self.toggle_circle.setEnabled(True)
            self.sign_in.setEnabled(True)
            self.sign_in_func()

        else:
            print('log: Invalid Code')

    def sign_in_func(self):
        self.sign_up.setStyleSheet('QPushButton{color: #5f5f5f; font-weight: 600;  border-radius: 8px;}')
        self.sign_in.setStyleSheet('QPushButton{color: #000; font-weight: 600;  border-radius: 8px;}')
        self.toggle_bg.setStyleSheet('QPushButton{background-color: #959595; border-radius: 9px;}')
        self.toggle_pos = False
        self.sign_pos = False
        self.sign_btn.setText('Sign In')

        self.animation14.setEndValue(QPoint(122, 149))
        self.animation14.setDuration(self.speed)
        self.animation14.start()

        self.animation15.setEndValue(QPoint(400, 149))
        self.animation15.setDuration(self.speed)
        self.animation15.start()

        self.animation16.setEndValue(QPoint(103, 216))
        self.animation16.setDuration(self.speed)
        self.animation16.start()

        self.animation17.setEndValue(QPoint(86, 231))
        self.animation17.setDuration(self.speed)
        self.animation17.start()

        self.animation20.setEndValue(QPoint(400, 250))
        self.animation20.setDuration(self.speed)
        self.animation20.start()

        self.animation21.setEndValue(QPoint(400, 264))
        self.animation21.setDuration(self.speed)
        self.animation21.start()

        self.animation18.setEndValue(QPoint(103, 295))
        self.animation18.setDuration(self.speed)
        self.animation18.start()

        self.animation19.setEndValue(QPoint(86, 310))
        self.animation19.setDuration(self.speed)
        self.animation19.start()

        self.animation22.setEndValue(QPoint(400, 375))
        self.animation22.setDuration(self.speed)
        self.animation22.start()

        self.animation23.setEndValue(QPoint(400, 392))
        self.animation23.setDuration(self.speed)
        self.animation23.start()

        self.animation24.setEndValue(QPoint(400, 452))
        self.animation24.setDuration(self.speed)
        self.animation24.start()

        self.animation25.setEndValue(QPoint(98, 454))
        self.animation25.setDuration(self.speed)
        self.animation25.start()

        self.animation26.setEndValue(QPoint(400, 455))
        self.animation26.setDuration(self.speed)
        self.animation26.start()

        self.animation3.setEndValue(QPoint(86, 402))
        self.animation3.setDuration(self.speed)
        self.animation3.start()

        self.animation12.setEndValue(QPoint(60, 500))
        self.animation12.setDuration(self.speed)
        self.animation12.start()

        self.animation13.setEndValue(QPoint(138, 518))
        self.animation13.setDuration(self.speed)
        self.animation13.start()

    def sign_up_func(self):
        self.sign_up.setStyleSheet('QPushButton{color: #000; font-weight: 600;  border-radius: 8px;}')
        self.sign_in.setStyleSheet('QPushButton{color: #5f5f5f; font-weight: 600;  border-radius: 8px;}')
        self.sign_btn.setText('Sign Up')
        self.sign_pos = True

        self.animation3.setEndValue(QPoint(86, 484))
        self.animation3.setDuration(self.speed)
        self.animation3.start()

        self.animation12.setEndValue(QPoint(60, 545))
        self.animation12.setDuration(self.speed)
        self.animation12.start()

        self.animation13.setEndValue(QPoint(138, 563))
        self.animation13.setDuration(self.speed)
        self.animation13.start()

        self.animation14.setEndValue(QPoint(-150, 149))
        self.animation14.setDuration(self.speed)
        self.animation14.start()

        self.animation15.setEndValue(QPoint(120, 149))
        self.animation15.setDuration(self.speed)
        self.animation15.start()

        self.animation16.setEndValue(QPoint(103, 181))
        self.animation16.setDuration(self.speed)
        self.animation16.start()

        self.animation17.setEndValue(QPoint(86, 195))
        self.animation17.setDuration(self.speed)
        self.animation17.start()

        self.animation18.setEndValue(QPoint(103, 319))
        self.animation18.setDuration(self.speed)
        self.animation18.start()

        self.animation19.setEndValue(QPoint(86, 333))
        self.animation19.setDuration(self.speed)
        self.animation19.start()

        self.animation20.setEndValue(QPoint(103, 250))
        self.animation20.setDuration(self.speed)
        self.animation20.start()

        self.animation21.setEndValue(QPoint(86, 264))
        self.animation21.setDuration(self.speed)
        self.animation21.start()

        self.animation22.setEndValue(QPoint(103, 375))
        self.animation22.setDuration(self.speed)
        self.animation22.start()

        self.animation23.setEndValue(QPoint(86, 392))
        self.animation23.setDuration(self.speed)
        self.animation23.start()

        self.animation24.setEndValue(QPoint(96, 452))
        self.animation24.setDuration(self.speed)
        self.animation24.start()

        self.animation26.setEndValue(QPoint(147, 455))
        self.animation26.setDuration(self.speed)
        self.animation26.start()

    def toggle_func(self):
        if self.toggle_pos:
            self.animation25.setEndValue(QPoint(98, 454))
            self.animation25.setDuration(0)
            self.animation25.start()
            self.toggle_bg.setStyleSheet('QPushButton{background-color: #959595; border-radius: 9px;}')
        else:
            self.animation25.setEndValue(QPoint(120, 454))
            self.animation25.setDuration(0)
            self.animation25.start()
            self.toggle_bg.setStyleSheet('QPushButton{background-color: #257CFF; border-radius: 9px;}')
        self.toggle_pos = not self.toggle_pos

    def reg_to_menu(self):
        self.animation1.setEndValue(QPoint(0, -371))
        self.animation1.setDuration(2000)
        self.animation1.start()

        self.animation2.setEndValue(QPoint(0, -600))
        self.animation2.setDuration(2000)
        self.animation2.start()

        self.animation3.setEndValue(QPoint(86, -191))
        self.animation3.setDuration(2000)
        self.animation3.start()

        self.animation4.setEndValue(QPoint(0, 0))
        self.animation4.setDuration(2000)
        self.animation4.start()

        self.animation5.setEndValue(QPoint(112, 198))
        self.animation5.setDuration(2000)
        self.animation5.start()

        self.animation6.setEndValue(QPoint(146, 58))
        self.animation6.setDuration(2000)
        self.animation6.start()

        self.animation7.setEndValue(QPoint(182, 300))
        self.animation7.setDuration(2000)
        self.animation7.start()

        self.animation8.setEndValue(QPoint(196, 300))
        self.animation8.setDuration(2000)
        self.animation8.start()

        self.animation9.setEndValue(QPoint(210, 300))
        self.animation9.setDuration(2000)
        self.animation9.start()

        self.animation10.setEndValue(QPoint(600, 20))
        self.animation10.setDuration(2000)
        self.animation10.start()

        self.animation11.setEndValue(QPoint(145, 247))
        self.animation11.setDuration(2000)
        self.animation11.start()

        self.animation12.setEndValue(QPoint(60, 600))
        self.animation12.setDuration(self.speed)
        self.animation12.start()

        self.animation13.setEndValue(QPoint(138, 600))
        self.animation13.setDuration(self.speed)
        self.animation13.start()

        self.animation18.setEndValue(QPoint(103, -100))
        self.animation18.setDuration(self.speed + 1000)
        self.animation18.start()

        self.animation19.setEndValue(QPoint(86, -100))
        self.animation19.setDuration(self.speed + 1000)
        self.animation19.start()

        self.animation25.setEndValue(QPoint(98, -100))
        self.animation25.setDuration(self.speed + 1000)
        self.animation25.start()

    def stt(self):
        model = Model('vosk-model-small-ru-0.22')
        recognizer = KaldiRecognizer(model, 16000)
        p = pyaudio.PyAudio()
        live = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        live.start_stream()

        def listen():
            while True:
                data = live.read(4000, exception_on_overflow=False)
                if (recognizer.AcceptWaveform(data)) and (len(data) > 0):
                    answer = json.loads(recognizer.Result())
                    if answer['text']:
                        return answer['text']

        self.circle1.setStyleSheet('QLabel{background-color: #000; border-radius: 3px;}')
        self.circle2.setStyleSheet('QLabel{background-color: #000; border-radius: 3px;}')
        self.circle3.setStyleSheet('QLabel{background-color: #000; border-radius: 3px;}')

        if self.count_of_launches == 15:
            self.count_of_launches = 0
            self.console_text = {}

        self.count_of_launches += 1
        self.console_text[f'{self.count_of_launches} line'] = f'   User: {listen().capitalize()}\n'

        self.text_console_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.text_console_animation.setEndValue(QPoint(20, 342))
        self.text_console_animation.setDuration(2000)
        self.text_console_animation.start()

        self.console.setText(''.join(list(self.console_text.values())))


app = QApplication([])
window = Window()
window.show()
app.exec()
window.connection.close()
