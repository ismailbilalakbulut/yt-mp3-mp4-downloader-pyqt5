import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui
import yt_dlp
from design import Ui_MainWindow

class DownloadThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, url, format_choice, desktop_path, ffmpeg_folder):
        super().__init__()
        self.url = url
        self.format_choice = format_choice
        self.desktop_path = desktop_path
        self.ffmpeg_folder = ffmpeg_folder

    def run(self):
        ydl_opts = {
            'outtmpl': os.path.join(self.desktop_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': self.ffmpeg_folder
        }
        if self.format_choice == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:  # mp4
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4'
            })
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit(True, f"İndirme tamamlandı! ({self.format_choice})")
        except Exception as e:
            self.finished.emit(False, f"İndirme sırasında hata oluştu:\n{str(e)}")

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("YouTube Video/Audio Downloader")
        self.setWindowIcon(QtGui.QIcon("icon.png"))  # İkon dosyası
        # Masaüstü yolu
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        # ffmpeg ve ffprobe yolu (proje klasöründe olmalı)
        self.ffmpeg_folder = os.path.dirname(os.path.abspath(__file__))

        # Butona tıklayınca çalışacak fonksiyon
        self.ui.pushButton.clicked.connect(self.download_video)
        self.download_thread = None

    def download_video(self):
        url = self.ui.lineEdit.text().strip()
        if not url:
            QMessageBox.warning(self, "Hata", "Lütfen bir YouTube linki girin.")
            return

        format_choice = self.ui.comboBox.currentText().lower()  # mp3 veya mp4

        # Butonu devre dışı bırak, kullanıcıya beklemesini söyle
        self.ui.pushButton.setEnabled(False)
        self.status = QMessageBox(self)
        self.status.setWindowTitle("İndiriliyor")
        self.status.setText("İndirme işlemi devam ediyor, lütfen bekleyin...")
        self.status.setStandardButtons(QMessageBox.NoButton)
        self.status.show()

        self.download_thread = DownloadThread(url, format_choice, self.desktop_path, self.ffmpeg_folder)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_finished(self, success, message):
        self.ui.pushButton.setEnabled(True)
        self.status.hide()
        if success:
            QMessageBox.information(self, "Başarılı", message)
        else:
            QMessageBox.critical(self, "Hata", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

