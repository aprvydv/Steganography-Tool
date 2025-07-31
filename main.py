# main.py
import sys, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLineEdit, QTextEdit, QMessageBox,
    QProgressBar, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import strego

class DragDropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel{border:2px dashed #3ec4fc; color:#59d9fb; font-style:italic;}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [
            url.toLocalFile() for url in event.mimeData().urls()
        ]
        if files:
            self.parent().load_image(files[0])

class SteganoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SteganoPy — Colorful Steganography')
        self.setFixedSize(550, 400)
        self.image_path = None

        # Layouts
        layout = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()
        layout.addLayout(left, 2)
        layout.addLayout(right, 3)
        self.setLayout(layout)

        # Carrier image and preview
        self.lbl_preview = DragDropLabel("Drag & drop an image or click below to select")
        self.lbl_preview.setFixedSize(230, 230)
        left.addWidget(self.lbl_preview)

        btn_load = QPushButton("Select Image")
        btn_load.clicked.connect(self.select_image)
        left.addWidget(btn_load)

        self.lbl_capacity = QLabel("")
        left.addWidget(self.lbl_capacity)

        # Encode/Decode section
        right.addWidget(QLabel("<b>Hide/Extract Data</b>"))
        self.tabs = QComboBox()
        self.tabs.addItems(["Text", "File"])
        right.addWidget(self.tabs)

        # Encode widgets
        self.txt_message = QTextEdit()
        self.txt_message.setPlaceholderText("Text to hide (if encoding text)")
        right.addWidget(self.txt_message)

        self.btn_file = QPushButton("Choose File to Hide")
        self.btn_file.clicked.connect(self.select_file)
        right.addWidget(self.btn_file)
        self.selected_file = None
        self.lbl_file = QLabel("")
        right.addWidget(self.lbl_file)

        self.btn_encode = QPushButton("Encode & Save")
        self.btn_encode.clicked.connect(self.encode)
        right.addWidget(self.btn_encode)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        right.addWidget(self.progress)

        # Decode
        self.btn_decode = QPushButton("Decode From Image")
        self.btn_decode.clicked.connect(self.decode)
        right.addWidget(self.btn_decode)
        self.txt_output = QLabel("")
        right.addWidget(self.txt_output)

        # Connections
        self.lbl_preview.parent = self

        self.tabs.currentIndexChanged.connect(self.switch_mode)
        self.switch_mode(0)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image",
            "", "Images (*.png *.bmp *.jpg *.jpeg)"
        )
        if path:
            self.load_image(path)

    def load_image(self, path):
        if not path or not path.lower().endswith(strego.ALLOWED_IMAGE_EXTENSIONS):
            QMessageBox.warning(self, "Error", "Unsupported file format!")
            return
        self.image_path = path
        pix = QPixmap(path).scaled(210, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_preview.setPixmap(pix)
        cap = strego.max_capacity_bytes(path)
        self.lbl_capacity.setText(
            f"Image: <b>{os.path.basename(path)}</b><br><span style='color:#59d9fb'>Max data: {cap} bytes</span>")
        self.txt_output.setText("")
        self.progress.setVisible(False)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Hide", "", "All Files (*)"
        )
        if path:
            self.selected_file = path
            self.lbl_file.setText(f"<span style='color:#91baff'>File: {os.path.basename(path)}</span>")
        else:
            self.selected_file = None
            self.lbl_file.setText("")

    def switch_mode(self, idx):
        self.txt_message.setVisible(idx == 0)
        self.btn_file.setVisible(idx == 1)
        self.lbl_file.setVisible(idx == 1)

    def encode(self):
        if not self.image_path:
            QMessageBox.warning(self, "No Image", "Load a carrier image first.")
            return
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Stego Image", "", "Images (*.png *.bmp *.jpg *.jpeg)"
        )
        if not out_path:
            return

        try:
            self.progress.setVisible(True)
            self.progress.setMaximum(0)
            if self.tabs.currentIndex() == 0:
                # Text
                text = self.txt_message.toPlainText().strip()
                if not text:
                    QMessageBox.warning(self, "Empty", "No text entered!")
                    self.progress.setVisible(False)
                    return
                strego.encode_text(self.image_path, text, out_path)
            else:
                # File
                if not self.selected_file:
                    QMessageBox.warning(self, "No File", "No file selected!")
                    self.progress.setVisible(False)
                    return
                strego.encode_file(self.image_path, self.selected_file, out_path)
            self.progress.setMaximum(1)
            self.progress.setValue(1)
            QMessageBox.information(self, "Success", "Data encoded and image saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")
        finally:
            self.progress.setVisible(False)

    def decode(self):
        if not self.image_path:
            QMessageBox.warning(self, "No Image", "Load a stego image first.")
            return
        try:
            self.progress.setVisible(True)
            self.progress.setMaximum(0)
            typ, filename, payload = strego.decode_payload(self.image_path)
            self.progress.setMaximum(1)
            self.progress.setValue(1)
            if typ == 'text':
                self.txt_output.setText(f"<span style='color:#7cf2f7'>Hidden text:</span> {payload}")
            elif typ == 'file':
                savepath, _ = QFileDialog.getSaveFileName(self, "Save extracted file", filename, "All Files (*)")
                if savepath:
                    with open(savepath, 'wb') as f:
                        f.write(payload)
                    self.txt_output.setText(f"<span style='color:#9fe69e'>File extracted:</span> {savepath}")
                else:
                    self.txt_output.setText("<span style='color:#f9aa33'>Extraction cancelled.</span>")
            else:
                self.txt_output.setText("<span style='color:#f85149'>No recognizable data found.</span>")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Decoding failed: {e}")
        finally:
            self.progress.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Attach colorful QSS theme
    qss = """
    QWidget {
        background-color: #151B54;
        color: #e0e6f0;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }
    QPushButton {
        background-color: #91baff;
        color: #151B54;
        border-radius: 11px;
        padding: 8px 16px;
        border: none;
        font-weight: bold;
        transition: all 180ms;
    }
    QPushButton:hover {
        background-color: #3ec4fc;
        color: white;
    }
    QPushButton:pressed {
        background-color: #0766ad;
        color: #fff;
    }
    QLabel {
        color: #e0e6f0;
    }
    QTextEdit, QLineEdit {
        background-color: #282c39;
        color: #e0e6f0;
        border: 1.5px solid #3282f6;
        border-radius: 7px;
        padding: 7px;
    }
    QTextEdit:focus, QLineEdit:focus {
        border: 2px solid #59d9fb;
    }
    QComboBox {
        background-color: #282c39;
        color: #e0e6f0;
        border-radius: 7px;
        padding: 7px;
        border: 1.5px solid #006cff;
    }
    QComboBox QAbstractItemView {
        background-color: #181824;
        color: #61c1f6;
        border: none;
        selection-background-color: #3ec4fc;
    }
    QProgressBar {
        border: 1px solid #3282f6;
        border-radius: 6px;
        text-align: center;
        background: #282c39;
        color: #e0e6f0;
    }
    QProgressBar::chunk {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #3ec4fc, stop:1 #91baff);
        border-radius: 6px;
    }
    DragDropLabel, QLabel[frame="true"] {
        border: 2px dashed #3ec4fc;
        color: #59d9fb;
        font-style: italic;
    }
    """
    app.setStyleSheet(qss)

    w = SteganoApp()
    w.show()
    sys.exit(app.exec_())
