from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton,
    QLabel, QFrame
)
from PySide6.QtCore import Qt

class ModernMessage(QDialog):
    def __init__(self, parent, title, message, icon_type="info"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        
        # El contenedor con estilo
        self.frame = QFrame()
        self.frame.setObjectName("msgFrame")
        self.frame.setStyleSheet("""
            QFrame#msgFrame {
                background-color: white;
                border: 2px solid #1d6fa5;
                border-radius: 20px;
            }
            QLabel#msgTitle {
                color: #112433;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel#msgText {
                color: #4a5568;
                font-size: 14px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(25, 20, 25, 20)
        
        title_label = QLabel(title)
        title_label.setObjectName("msgTitle")
        
        body_label = QLabel(message)
        body_label.setObjectName("msgText")
        body_label.setWordWrap(True)
        
        btn = QPushButton("Entendido")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedWidth(120)
        btn.clicked.connect(self.accept)
        
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(body_label)
        frame_layout.addSpacing(15)
        frame_layout.addWidget(btn, 0, Qt.AlignCenter)
        
        layout.addWidget(self.frame)

    @staticmethod
    def show_message(parent, title, message):
        dialog = ModernMessage(parent, title, message)
        dialog.exec()