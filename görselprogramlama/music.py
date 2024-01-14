import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLineEdit, QPushButton, QFileDialog, QSlider, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QMenu, QAction, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from pymongo import MongoClient

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["deneme"]
        self.users_collection = self.db["kullanicilar"]

        self.setWindowTitle("Music Player")
        self.setGeometry(100, 100, 600, 400)

        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        self.login_page = QWidget(self)
        self.stacked_widget.addWidget(self.login_page)
        self.setup_login_page()

        self.music_page = QWidget(self)
        self.stacked_widget.addWidget(self.music_page)
        self.setup_music_page()

        self.stacked_widget.setCurrentIndex(0)  

    def setup_login_page(self):
        layout = QVBoxLayout(self.login_page)

        self.username_edit = QLineEdit(self)
        self.username_edit.setPlaceholderText("Username")
        layout.addWidget(self.username_edit)

        self.password_edit = QLineEdit(self)
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        login_button = QPushButton("Login", self)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        signup_button = QPushButton("Sign Up", self)
        signup_button.clicked.connect(self.signup)
        layout.addWidget(signup_button)

    def setup_music_page(self):
        layout = QVBoxLayout(self.music_page)

        self.add_button = QPushButton("Add Music", self)
        self.add_button.clicked.connect(self.add_music)
        layout.addWidget(self.add_button)

        self.music_list = QListWidget(self)
        self.music_list.itemClicked.connect(self.select_music)
        layout.addWidget(self.music_list)

        self.seek_slider = QSlider(Qt.Horizontal, self)
        self.seek_slider.setMinimum(0)
        self.seek_slider.sliderMoved.connect(self.seek_music)
        self.seek_slider.sliderPressed.connect(self.slider_pressed)
        self.seek_slider.sliderReleased.connect(self.slider_released)
        layout.addWidget(self.seek_slider)

        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("Volume: 50", self)
        layout.addWidget(self.volume_label)

        self.duration_label = QLabel("00:00 / 00:00", self)
        layout.addWidget(self.duration_label)

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.play_or_stop_music)
        layout.addWidget(self.play_button)

        self.player = QMediaPlayer()
        self.is_slider_pressed = False
        self.player.positionChanged.connect(self.update_duration_label)
        self.create_theme_menu()

    def add_music(self):
        file_dialog = QFileDialog()
        self.file_path = file_dialog.getOpenFileName(self, "Select Music")[0]

        if self.file_path:
            music_url = QUrl.fromLocalFile(self.file_path)
            music_content = QMediaContent(music_url)
            self.player.setMedia(music_content)
            self.player.durationChanged.connect(self.update_slider_range)
            self.update_slider_range()

            music_name = self.file_path.split("/")[-1]
            item = QListWidgetItem(music_name)
            item.setData(Qt.UserRole, self.file_path)
            self.music_list.addItem(item)

    def select_music(self, item):
        music_name = item.text()
        file_path = item.data(Qt.UserRole)
        if file_path:
            music_url = QUrl.fromLocalFile(file_path)
            music_content = QMediaContent(music_url)
            self.player.setMedia(music_content)
            self.player.durationChanged.connect(self.update_slider_range)
            self.update_slider_range()
    
    def create_theme_menu(self):
        theme_menu = self.menuBar().addMenu("Theme")

        light_theme_action = QAction("Light", self)
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dark", self)
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        blue_theme_action = QAction("Blue", self)
        blue_theme_action.triggered.connect(lambda: self.set_theme("blue"))
        theme_menu.addAction(blue_theme_action)

        green_theme_action = QAction("Green", self)
        green_theme_action.triggered.connect(lambda: self.set_theme("green"))
        theme_menu.addAction(green_theme_action)

        purple_theme_action = QAction("Purple", self)
        purple_theme_action.triggered.connect(lambda: self.set_theme("purple"))
        theme_menu.addAction(purple_theme_action)

    def set_theme(self, theme):
        if theme == "light":
            self.setStyleSheet("")
        elif theme == "dark":
            self.setStyleSheet("background-color: #333; color: #fff;")
        elif theme == "blue":
            self.setStyleSheet("background-color: #3498db; color: #fff;")
        elif theme == "green":
            self.setStyleSheet("background-color: #2ecc71; color: #fff;")
        elif theme == "purple":
            self.setStyleSheet("background-color: #9b59b6; color: #fff;")

    # You can define more themes with detailed color settings as needed
    def play_or_stop_music(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_button.setText("Play")
        else:
            if self.player.mediaStatus() == QMediaPlayer.NoMedia:
                if self.music_url:
                    music_content = QMediaContent(self.music_url)
                    self.player.setMedia(music_content)
                    self.player.durationChanged.connect(self.update_slider_range)
                    self.update_slider_range()
            self.player.play()
            self.play_button.setText("Stop")

    def seek_music(self, position):
        if not self.is_slider_pressed:
            self.player.setPosition(position)

    def slider_pressed(self):
        self.is_slider_pressed = True

    def slider_released(self):
        self.is_slider_pressed = False
        position = self.seek_slider.value()
        self.player.setPosition(position)
        if self.player.state() == QMediaPlayer.PausedState:
            self.player.play()


    def set_volume(self, value):
        self.player.setVolume(value)
        self.volume_label.setText(f"Volume: {value}")

    def update_slider_range(self):
        duration = self.player.duration()
        self.seek_slider.setRange(0, duration)

    def update_duration_label(self, position):
        duration = self.player.duration()
        current_position = self.player.position()
        duration_text = self.format_time(duration)
        current_position_text = self.format_time(current_position)
        self.duration_label.setText(f"{current_position_text} / {duration_text}")
        self.seek_slider.setValue(position)

    def format_time(self, milliseconds):
        seconds = int((milliseconds / 1000) % 60)
        minutes = int((milliseconds / (1000 * 60)) % 60)
        return "{:02d}:{:02d}".format(minutes, seconds)

    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Username and password cannot be empty.")
            return

        user_data = self.users_collection.find_one({"kullanici_adi": username, "sifre": password})

        if user_data:
            QMessageBox.information(self, "Login Successful", "Welcome, {}".format(username))
            self.show_music_page()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def signup(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "Sign Up Failed", "Username and password cannot be empty.")
            return

        existing_user = self.users_collection.find_one({"kullanici_adi": username})

        if existing_user:
            QMessageBox.warning(self, "Sign Up Failed", "Username already exists.")
        else:
            self.users_collection.insert_one({"kullanici_adi": username, "sifre": password})
            QMessageBox.information(self, "Sign Up Successful", "User registered successfully.")

    def show_music_page(self):
        self.stacked_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())
