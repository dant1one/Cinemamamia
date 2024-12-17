import sys
import requests
import random
import string
import subprocess
import re
import io
import requests
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QRegExpValidator, QFont, QPixmap
from PyQt5.QtCore import QSize, QCoreApplication, QRegExp, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QMessageBox,QLabel, QListView, QDialog,
                             QStackedWidget, QWidget, QVBoxLayout, QComboBox, QListWidget, QHBoxLayout, QSizePolicy, QSpacerItem)

class CustomButton(QPushButton):
    def __init__(self, text, width=200, height=50, parent=None):
        super().__init__(text, parent)
        self.width = width
        self.height = height
        self.color = "#8E8D8A"
        self.font_color = "#B4463E"
        self.pressed_color = "#7C7B7A"
        self.pressed_font_color = "#DC2727"
        self.setMinimumSize(self.width, self.height)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: {self.font_color};
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_color};
                color: {self.pressed_font_color};
            }}
        """)

class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder, width=200, height=40, color="#B4463E", background_colour="#E6ECFF", parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.color = color
        self.background_colour = background_colour
        self.setPlaceholderText(placeholder)
        self.setMinimumSize(self.width, self.height)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {self.color};
                background-color: {self.background_colour};
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
            }}
        """)

class LoginWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.spacing = 15

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(self.spacing)
        self.layout.setContentsMargins(10, 5, 10, 5)

        self.title_label = QLabel("MAMAMIA")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""font-size: 80px; font-weight: bold; color: #B4463E; margin-bottom: 20px;""")
        self.layout.addWidget(self.title_label)

        self.input_name = CustomLineEdit("Enter username...", parent=self)
        self.layout.addWidget(self.input_name)

        self.input_password = CustomLineEdit("Enter password...", parent=self)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.input_password)

        self.captcha_label = QLabel("Captcha")
        self.layout.addWidget(self.captcha_label)

        self.captcha_input = CustomLineEdit("Enter captcha...", parent=self)
        self.layout.addWidget(self.captcha_input)

        self.generated_captcha = self.generate_captcha()
        self.display_captcha(self.generated_captcha)

        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)

        self.login_button = CustomButton("LOGIN", height=60, parent=self)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.registration_button = CustomButton("REGISTER", height=60, parent=self)
        self.registration_button.clicked.connect(self.show_registration)
        self.layout.addWidget(self.registration_button)

        self.layout.addItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.setLayout(self.layout)

    def generate_captcha(self):
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return captcha_text

    def generate_captcha_image(self, captcha_text):
        image = Image.new('RGB', (150, 60), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            font = ImageFont.load_default()

        for i, char in enumerate(captcha_text):
            x = 10 + i * 30 + random.randint(-6, 6)
            y = random.randint(5, 15)
            draw.text((x, y), char, font=font, fill=(0, 0, 0))

        for _ in range(100):
            x = random.randint(0, image.size[0])
            y = random.randint(0, image.size[1])
            draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        for _ in range(5):
            x1 = random.randint(0, image.size[0])
            y1 = random.randint(0, image.size[1])
            x2 = random.randint(0, image.size[0])
            y2 = random.randint(0, image.size[1])
            draw.line((x1, y1, x2, y2), fill=(0, 0, 0), width=1)

        byte_io = io.BytesIO()
        image.save(byte_io, 'PNG')
        byte_io.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(byte_io.read())

        return pixmap

    def display_captcha(self, captcha_text):
        captcha_image = self.generate_captcha_image(captcha_text)
        self.captcha_label.setPixmap(captcha_image)
        self.captcha_label.repaint()  # Обновляем изображение

    def login(self):
        entered_captcha = self.captcha_input.text().strip().replace(" ", "").upper()

        if entered_captcha != self.generated_captcha.replace(" ", "").upper():
            QMessageBox.warning(self, "Captcha Error", "Incorrect captcha, please try again.")
            self.generated_captcha = self.generate_captcha()
            self.display_captcha(self.generated_captcha)
            self.captcha_input.clear()
            return

        name = self.input_name.text()
        password = self.input_password.text()

        if name == "admin" and password == "admin":
            self.stacked_widget.setCurrentIndex(3)
            return

        url = f'https://daniyalvaahunov.pythonanywhere.com/login?username={name}&password={password}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.stacked_widget.setCurrentIndex(2)
                self.stacked_widget.currentWidget().username = name
                self.stacked_widget.currentWidget().history_button.clicked.connect(
                    lambda: self.open_user_history(name)
                )
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials.", QMessageBox.Ok)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error sending request: {str(e)}", QMessageBox.Ok)

    def open_user_history(self, username):
        user_history_window = UserHistoryWindow(self.stacked_widget, username)
        self.stacked_widget.addWidget(user_history_window)
        self.stacked_widget.setCurrentWidget(user_history_window)

    def show_registration(self):
        self.stacked_widget.setCurrentIndex(1)

class RegistrationWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        spacing = 15

        layout = QVBoxLayout(self)
        layout.setSpacing(spacing)

        self.input_name = CustomLineEdit("Username...", parent=self)
        layout.addWidget(self.input_name)

        self.input_password = CustomLineEdit("Password...", parent=self)
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)

        self.input_confirm_password = CustomLineEdit("Confirm password...", parent=self)
        self.input_confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_confirm_password)

        self.register_button = CustomButton("REGISTER", height=60, parent=self)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register(self):
        name = self.input_name.text()
        password = self.input_password.text()
        confirm_password = self.input_confirm_password.text()

        if not name or not password or not confirm_password:
            QMessageBox.critical(self, "Error", "Please fill all fields.", QMessageBox.Ok)
            return

        if password != confirm_password:
            QMessageBox.critical(self, "Error", "Passwords do not match.", QMessageBox.Ok)
            return

        url = f'https://daniyalvaahunov.pythonanywhere.com/register?username={name}&password={password}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Registration successful!", QMessageBox.Ok)
                self.stacked_widget.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Error", response.text, QMessageBox.Ok)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error sending request: {str(e)}", QMessageBox.Ok)

class AdminWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout(self)

        self.input_title = CustomLineEdit("Movie title...", parent=self)
        layout.addWidget(self.input_title)

        self.input_hall = CustomLineEdit("1A|2A|1B|2B", parent=self)
        layout.addWidget(self.input_hall)

        self.input_price = CustomLineEdit("Movie price...", parent=self)
        layout.addWidget(self.input_price)

        self.input_date = CustomLineEdit("YYYY-MM-DD", parent=self)
        layout.addWidget(self.input_date)

        self.input_time = CustomLineEdit("HH:MM", parent=self)
        layout.addWidget(self.input_time)

        self.add_movie_button = CustomButton("ADD MOVIE", height=60, parent=self)
        self.add_movie_button.clicked.connect(self.add_movie)
        layout.addWidget(self.add_movie_button)

        self.done_button = CustomButton("DONE", parent=self)
        self.done_button.clicked.connect(self.restart_application)
        layout.addWidget(self.done_button)

        self.setLayout(layout)

        hall_validator = QRegExpValidator(QRegExp(r'^(1A|2A|1B|2B)$'), self)
        self.input_hall.setValidator(hall_validator)

        price_validator = QRegExpValidator(QRegExp(r'^\d+(\.\d{1,2})?$'), self)
        self.input_price.setValidator(price_validator)

        date_validator = QRegExpValidator(QRegExp(r'^\d{4}-\d{2}-\d{2}$'), self)
        self.input_date.setValidator(date_validator)

        time_validator = QRegExpValidator(QRegExp(r'^\d{2}:\d{2}$'), self)
        self.input_time.setValidator(time_validator)

    def add_movie(self):
        title = self.input_title.text()
        hall = self.input_hall.text()
        price = self.input_price.text()
        date = self.input_date.text()
        time = self.input_time.text()

        if not title or not time or not hall or not price or not date:
            QMessageBox.critical(self, "Error", "Please fill all fields.", QMessageBox.Ok)
            return

        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            QMessageBox.critical(self, "Error", "Invalid date format. Use YYYY-MM-DD.", QMessageBox.Ok)
            return

        if not re.match(r'^\d{2}:\d{2}$', time):
            QMessageBox.critical(self, "Error", "Invalid time format. Use HH:MM.", QMessageBox.Ok)
            return

        if not re.match(r'^\d+(\.\d{1,2})?$', price):
            QMessageBox.critical(self, "Error", "Invalid price format. Use a valid number.", QMessageBox.Ok)
            return

        if hall not in ['1A', '2A', '1B', '2B']:
            QMessageBox.critical(self, "Error", "Invalid hall. Choose one from: 1A, 2A, 1B, 2B.", QMessageBox.Ok)
            return

        if self.is_hall_reserved(hall, date, time):
            QMessageBox.critical(self, "Error", f"Hall {hall} is already reserved for {date} at {time}.", QMessageBox.Ok)
            return

        url = 'https://daniyalvaahunov.pythonanywhere.com/add_movie'
        params = {
            'title': title,
            'hall': hall,
            'price': price,
            'date': date,
            'time': time
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Movie added successfully!", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Error", f"Failed to add movie. Status code: {response.status_code}", QMessageBox.Ok)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error sending request: {str(e)}", QMessageBox.Ok)

    def is_hall_reserved(self, hall, date, time):
        url = 'https://daniyalvaahunov.pythonanywhere.com/check_hall_availability'
        params = {
            'hall': hall,
            'date': date,
            'time': time
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 409:
                return True
            elif response.status_code == 200:
                return False
            else:
                QMessageBox.warning(self, "Error", f"Failed to check hall availability. Status code: {response.status_code}", QMessageBox.Ok)
                return True
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error checking hall availability: {str(e)}", QMessageBox.Ok)
            return True

    def restart_application(self):
        QCoreApplication.quit()
        subprocess.Popen([sys.executable, 'cinema.py'])

class MovieWindow(QWidget):
    def __init__(self, stacked_widget, username=None):
        super().__init__()
        self.username = username
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Стиль для QComboBox
        self.combo_box = QComboBox(self)
        self.combo_box.setStyleSheet("""
            QComboBox {
                background-color: #E6ECFF;
                color: #B4463E;
                border: 2px solid #B4463E;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #E6ECFF;
            }
            QComboBox::down-arrow {
                image: url('down_arrow.png');
            }
            QComboBox QAbstractItemView {
                background-color: #E6ECFF;
                color: #B4463E;
                border: 2px solid #B4463E;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                font-size: 16px;
            }
        """)
        layout.addWidget(self.combo_box)

        # Стиль для QListWidget
        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #E6ECFF;
                color: #B4463E;
                border: 2px solid #B4463E;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                font-size: 16px;
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #B4463E;
                color: white;
            }
        """)
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        self.info_button = CustomButton("INFO", parent=self)
        button_layout.addWidget(self.info_button)

        self.buy_button = CustomButton("BUY", parent=self)
        button_layout.addWidget(self.buy_button)

        self.history_button = CustomButton("HISTORY", parent=self)
        button_layout.addWidget(self.history_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.info_button.clicked.connect(self.open_info_window)
        self.buy_button.clicked.connect(self.open_seats_window)
        self.history_button.clicked.connect(self.open_history_window)
        self.load_movies()

    def load_movies(self):
        url = 'https://daniyalvaahunov.pythonanywhere.com/get_onlymovies'
        try:
            movie_titles = requests.get(url).json()
            self.combo_box.addItems(movie_titles)
            self.combo_box.currentTextChanged.connect(self.update_list_widget)
            if movie_titles:
                self.update_list_widget()
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Network error. Failed to load movies.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {str(e)}")

    def update_list_widget(self):
        movie = self.combo_box.currentText()
        url = f'https://daniyalvaahunov.pythonanywhere.com/get_movie_info?title={movie}'
        try:
            movie_sessions = requests.get(url).json().get(movie, [])
            self.list_widget.clear()
            for session in movie_sessions:
                text = f"Time: {session['time']}, Date: {session['date']}, Hall: {session['hall']}, Price: {session['price']}"
                self.list_widget.addItem(text)
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Network error. Failed to load sessions.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {str(e)}")

    def open_info_window(self):
        movie_title = self.combo_box.currentText()
        if not movie_title:
            QMessageBox.warning(self, "Error", "No movie selected.")
            return
        info_window = InfoWindow(self.username, movie_title, self.stacked_widget)
        self.stacked_widget.addWidget(info_window)
        self.stacked_widget.setCurrentWidget(info_window)

    def open_seats_window(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            session_info = current_item.text().split(', ')
            date = session_info[1].split(': ')[1]
            time = session_info[0].split(': ')[1]
            seats_window = SeatsWindow(self.username, self.combo_box.currentText(), date, time)
            seats_window.show()

    def open_history_window(self):
        history_window = UserHistoryWindow(self.stacked_widget, self.username)
        self.stacked_widget.addWidget(history_window)
        self.stacked_widget.setCurrentWidget(history_window)

class InfoWindow(QWidget):
    def __init__(self, username, movie_title, stacked_widget):
        super().__init__()
        self.username = username
        self.movie_title = movie_title
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        font = QFont()
        font.setPointSize(16)

        self.profit_label = QLabel("Total Profit: $0", self)
        self.profit_label.setFont(font)
        self.profit_label.setAlignment(Qt.AlignCenter)

        self.passed_sessions_label = QLabel("Passed Sessions: 0", self)
        self.passed_sessions_label.setFont(font)
        self.passed_sessions_label.setAlignment(Qt.AlignCenter)

        self.booked_seats_label = QLabel("Total Booked Seats: 0", self)
        self.booked_seats_label.setFont(font)
        self.booked_seats_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.profit_label)
        layout.addWidget(self.passed_sessions_label)
        layout.addWidget(self.booked_seats_label)

        self.back_button = CustomButton("BACK", parent=self)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.load_movie_info()

    def load_movie_info(self):
        if not self.movie_title:
            QMessageBox.warning(self, "Error", "No movie title provided.")
            return

        url = f'https://daniyalvaahunov.pythonanywhere.com/get_movie_profit?title={self.movie_title}'
        try:
            response = requests.get(url).json()
            if "error" in response:
                QMessageBox.warning(self, "Error", response["error"])
            else:
                self.profit_label.setText(f"Total Profit: ${response['total_profit']}")
                self.passed_sessions_label.setText(f"Passed Sessions: {response['passed_sessions_count']}")
                self.booked_seats_label.setText(f"Total Booked Seats: {response['total_booked_seats']}")
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Network error. Failed to load movie info.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {str(e)}")

    def go_back(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.widget(2))

class SeatsWindow(QWidget):
    def __init__(self, username, movie_title, session_date, session_time):
        super().__init__()
        self.username = username
        self.movie_title = movie_title
        self.session_date = session_date
        self.session_time = session_time
        self.selected_seats = []

        self.setWindowTitle(f"Seat Selection for {movie_title}")
        self.setMinimumSize(500, 500)

        layout = QVBoxLayout(self)

        self.seat_buttons = {}
        rows = ['A', 'B', 'C', 'D', 'E']

        # Создаем кнопки для мест
        for row in rows:
            row_layout = QHBoxLayout()
            for col in range(1, 8):
                seat_id = f"{row}{col}"
                button = CustomButton(seat_id, width=60, height=60)
                button.clicked.connect(lambda _, sid=seat_id: self.toggle_seat(sid))
                self.seat_buttons[seat_id] = button
                row_layout.addWidget(button)
            layout.addLayout(row_layout)

        # Кнопка для подтверждения покупки
        buy_button = CustomButton("BUY", width=200, height=50)
        buy_button.clicked.connect(self.reserve_seats)
        layout.addWidget(buy_button)

        self.load_seats()

    def load_seats(self):
        url = f'https://daniyalvaahunov.pythonanywhere.com/get_session_seats?title={self.movie_title}&date={self.session_date}&time={self.session_time}'
        try:
            seats_data = requests.get(url).json()
            if not seats_data:
                QMessageBox.warning(self, "No Data", "No seat data available.")
                return
            self.update_seat_buttons(seats_data)
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Error", f"Failed to load seats: {str(e)}", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unexpected error: {str(e)}")

    def update_seat_buttons(self, seats_data):
        # Обновляем состояние кнопок в зависимости от данных с сервера
        for seat_id, seat_info in seats_data.items():
            button = self.seat_buttons.get(seat_id)
            if button:
                if seat_info['reserved']:
                    button.setEnabled(False)  # Место занято
                    button.setStyleSheet("background-color: #B4463E;")  # Зеленое, если занято
                else:
                    button.setStyleSheet("background-color: #7C7B7A;")  # Синий, если доступно

    def toggle_seat(self, seat_id):
        button = self.seat_buttons[seat_id]
        if seat_id in self.selected_seats:
            self.selected_seats.remove(seat_id)
            button.setStyleSheet("background-color: #7C7B7A;")  # Синий, если отменено
        else:
            self.selected_seats.append(seat_id)
            button.setStyleSheet("background-color: #4DB46E;")  # Оранжевый, если выбрано

    def reserve_seats(self):
        if not self.selected_seats:
            QMessageBox.warning(self, "No Seats", "Please select seats.")
            return

        # Проверка, что пользователь вошел в систему
        if not self.username:
            QMessageBox.warning(self, "Login Error", "Please login before reserving seats.")
            return

        seats_string = ','.join(self.selected_seats)

        url = f'https://daniyalvaahunov.pythonanywhere.com/reserve_seat/{self.username}/{self.movie_title}/{self.session_date}/{self.session_time}/{seats_string}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Seats reserved successfully!")
                for seat_id in self.selected_seats:
                    button = self.seat_buttons[seat_id]
                    button.setStyleSheet("background-color: #B4463E;")  # Занято
                    button.setEnabled(False)
                self.selected_seats.clear()  # Очистка выбранных мест
            else:
                QMessageBox.warning(self, "Error", f"Failed to reserve seats: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Error", f"Failed to reserve seats: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unexpected error: {str(e)}")

class UserHistoryWindow(QWidget):
    def __init__(self, stacked_widget, username):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.username = username
        self.setWindowTitle("User History")

        layout = QVBoxLayout(self)

        self.history_list = QListWidget(self)
        self.history_list.setStyleSheet("""
                    QListWidget {
                        background-color: #E6ECFF;
                        color: #B4463E;
                        border: 2px solid #B4463E;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QListWidget::item {
                        font-size: 16px;
                    }
                """)
        layout.addWidget(self.history_list)

        self.back_button = CustomButton("Back", height=60, parent=self)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.load_user_history()

    def go_back(self):
        self.stacked_widget.setCurrentIndex(2)

    def load_user_history(self):
        if not self.username:
            QMessageBox.warning(self, "Error", "User not logged in.", QMessageBox.Ok)
            return

        url = f'https://daniyalvaahunov.pythonanywhere.com/get_user_history?username={self.username}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                history_data = response.json()
                if history_data:
                    self.display_history(history_data)
                else:
                    self.history_list.addItem("No history available.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to load history. Status code: {response.status_code}", QMessageBox.Ok)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data: {str(e)}", QMessageBox.Ok)

    def display_history(self, history_data):
        self.history_list.clear()
        for record in history_data:
            movie_title = record.get('movie_title', 'N/A')
            date = record.get('date', 'N/A')
            time = record.get('time', 'N/A')
            hall = record.get('hall', 'N/A')
            seats = ', '.join(record.get('seats', []))  # Преобразуем список мест в строку
            item_text = f"Movie: {movie_title} | Date: {date} | Time: {time} | Hall: {hall} | Seats: {seats}"
            self.history_list.addItem(item_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cinemamamia")
        self.setGeometry(630, 300, 300, 500)
        self.setStyleSheet("background-color: #EAE7DC")

        # Create stacked widget to switch between views
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Create and add views to stacked widget
        self.login_window = LoginWindow(self.stacked_widget)
        self.stacked_widget.addWidget(self.login_window)

        self.registration_window = RegistrationWindow(self.stacked_widget)
        self.stacked_widget.addWidget(self.registration_window)

        self.movie_window = MovieWindow(self.stacked_widget)
        self.stacked_widget.addWidget(self.movie_window)

        self.admin_window = AdminWindow(self.stacked_widget)
        self.stacked_widget.addWidget(self.admin_window)

        self.stacked_widget.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
