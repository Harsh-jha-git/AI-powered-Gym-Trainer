import sys
import os
import cv2
import csv
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, 
                             QFileDialog, QMessageBox, QFrame, QScrollArea, QGridLayout,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QColor, QCursor

def launch_setup_gui():
    """
    Launches a massive Single-Page PyQt6 Desktop Dashboard with depth and pleasing colors.
    Returns: cap, source_desc, use_mirror, username, voice_gender
    """
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    result = {}

    # Premium "Soft Pleasing" Aesthetics (Light Mode with Deep Shadows)
    APP_STYLESHEET = """
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    QScrollArea {
        border: none;
        background-color: #F4F7F6;
    }
    QWidget#MainContainer {
        background-color: #F4F7F6;
    }
    
    /* Top Navbar */
    QWidget#NavBar {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E1E8ED;
    }
    
    QLabel#Logo {
        color: #4A90E2; /* Pleasing Ocean Blue */
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 2px;
    }
    
    QLineEdit#NavInput, QComboBox#NavInput {
        padding: 12px 20px;
        border-radius: 12px;
        border: 1px solid #D1D9E6;
        font-size: 15px;
        font-weight: 600;
        background-color: #F9FBFC;
        color: #2D3748;
    }
    QLineEdit#NavInput:focus, QComboBox#NavInput:focus {
        border: 2px solid #4A90E2;
        background-color: #FFFFFF;
    }
    
    /* Hero Section (Soft Gradient) */
    QWidget#Hero {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A90E2, stop:1 #50E3C2);
        border-radius: 20px;
    }
    QLabel#HeroTitle {
        color: #FFFFFF;
        font-size: 44px;
        font-weight: 900;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    QLabel#HeroSub {
        color: #F4F7F6;
        font-size: 18px;
        font-weight: 500;
    }
    
    /* Section Headings */
    QLabel#SectionTitle {
        color: #2D3748;
        font-size: 24px;
        font-weight: 900;
        margin-top: 35px;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }
    
    /* Workout Cards Base */
    QFrame#HoverCard {
        background-color: #FFFFFF;
        border-radius: 20px;
        border: 1px solid #E1E8ED; /* Extremely soft border, relying on drop shadow */
    }
    
    QLabel#CardTitle {
        color: #2D3748;
        font-size: 22px;
        font-weight: 900;
    }
    QLabel#CardDesc {
        color: #718096;
        font-size: 14px;
        font-weight: 500;
        line-height: 1.5;
    }
    QLabel#Tag {
        background-color: #EBF4FF;
        color: #4A90E2;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 800;
        padding: 6px 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    QPushButton#CardButton {
        background-color: #4A90E2;
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 800;
        border-radius: 12px;
        padding: 16px;
        border: none;
    }
    QPushButton#CardButton:hover {
        background-color: #357ABD;
    }
    QPushButton#CardButton:pressed {
        background-color: #2A5D93;
    }
    
    /* Activity List */
    QFrame#HistoryBox {
        background-color: #FFFFFF;
        border-radius: 20px;
        border: 1px solid #E1E8ED;
    }
    QLabel#HistTitle {
        color: #2D3748;
        font-size: 18px;
        font-weight: 800;
    }
    QLabel#HistSub {
        color: #A0AEC0;
        font-size: 13px;
        font-weight: 500;
    }
    QLabel#HistScore {
        color: #48BB78; /* Soft pleasing green */
        font-size: 22px;
        font-weight: 900;
    }
    """

    class HoverCard(QFrame):
        """Custom interactive card with real 3D Drop Shadows for a massively interactive feel."""
        def __init__(self, title, desc, tag_text=None, accent_color="#4A90E2", is_upload=False, parent_window=None):
            super().__init__()
            self.setObjectName("HoverCard")
            self.parent_window = parent_window
            self.is_upload = is_upload
            
            # Massive structural drop shadow (Default State)
            self.shadow = QGraphicsDropShadowEffect()
            self.shadow.setBlurRadius(25)
            self.shadow.setColor(QColor(0, 0, 0, 15)) # 15% opacity black
            self.shadow.setOffset(0, 10)
            self.setGraphicsEffect(self.shadow)
            
            layout = QVBoxLayout(self)
            layout.setContentsMargins(25, 25, 25, 25)
            layout.setSpacing(12)
            
            top_layout = QHBoxLayout()
            if tag_text:
                tag = QLabel(tag_text)
                tag.setObjectName("Tag")
                top_layout.addWidget(tag)
            top_layout.addStretch()
            layout.addLayout(top_layout)
            
            t_label = QLabel(title)
            t_label.setObjectName("CardTitle")
            t_label.setWordWrap(True)
            t_label.setStyleSheet(f"border-left: 5px solid {accent_color}; padding-left: 12px;")
            
            d_label = QLabel(desc)
            d_label.setObjectName("CardDesc")
            d_label.setWordWrap(True)
            d_label.setMinimumHeight(45)
            
            layout.addWidget(t_label)
            layout.addWidget(d_label)
            layout.addStretch()
            
            self.btn = QPushButton("START DETECTOR" if not is_upload else "UPLOAD VIDEO")
            self.btn.setObjectName("CardButton")
            self.btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.btn.clicked.connect(self.trigger_workout)
            if is_upload:
                self.btn.setStyleSheet("background-color: #FF6B6B; color: #FFFFFF;") # Coral override for upload
                
            layout.addWidget(self.btn)
            self.setMinimumWidth(280)
            
        def enterEvent(self, event):
            # Interactive Pop: Increase shadow depth beautifully 
            self.shadow.setBlurRadius(40)
            self.shadow.setColor(QColor(0, 0, 0, 30))
            self.shadow.setOffset(0, 20)
            self.setStyleSheet("QFrame#HoverCard { background-color: #FFFFFF; border-radius: 20px; border: 1px solid #4A90E2; margin-top: -5px; margin-bottom: 5px; }")
            super().enterEvent(event)
            
        def leaveEvent(self, event):
            # Return to soft shadow
            self.shadow.setBlurRadius(25)
            self.shadow.setColor(QColor(0, 0, 0, 15))
            self.shadow.setOffset(0, 10)
            self.setStyleSheet("QFrame#HoverCard { background-color: #FFFFFF; border-radius: 20px; border: 1px solid #E1E8ED; margin-top: 0px; margin-bottom: 0px; }")
            super().leaveEvent(event)

        def trigger_workout(self):
            username = self.parent_window.nav_user.text().strip()
            if not username:
                QMessageBox.warning(self.parent_window, "Identification Required", "Please enter your Name in the top right corner.")
                self.parent_window.nav_user.setFocus()
                return
                
            voice = "male" if self.parent_window.nav_voice.currentText() == "Male Coach" else "female"
            
            if not self.is_upload:
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                source_desc = "Webcam"
                use_mirror = True
            else:
                video_path, _ = QFileDialog.getOpenFileName(
                    self.parent_window, "Select Training Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
                )
                if not video_path:
                    return # Cancelled
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    QMessageBox.critical(self.parent_window, "Error", f"Failed to open video: {os.path.basename(video_path)}")
                    return
                source_desc = os.path.basename(video_path)
                use_mirror = False
                
            self.btn.setText("CAMERA PREPARING...")
            self.btn.setStyleSheet("background-color: #48BB78; color: white;") # Turn pleasing green on success
            
            # Save payload to global
            result['cap'] = cap
            result['source_desc'] = source_desc
            result['use_mirror'] = use_mirror
            result['username'] = username
            result['voice_gender'] = voice
            
            self.parent_window.close()


    class AppDashboard(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("THR Training Framework")
            self.resize(1150, 850)
            self.setStyleSheet(APP_STYLESHEET)
            
            # Parent scroll area
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            
            main_container = QWidget()
            main_container.setObjectName("MainContainer")
            scroll.setWidget(main_container)
            
            page_layout = QVBoxLayout(main_container)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layout.setSpacing(0)
            
            # --- 1. Top Navbar ---
            navbar = QWidget()
            navbar.setObjectName("NavBar")
            navbar.setFixedHeight(85)
            
            # Add subtle drop shadow to navbar for depth
            nav_shadow = QGraphicsDropShadowEffect()
            nav_shadow.setBlurRadius(15)
            nav_shadow.setOffset(0, 5)
            nav_shadow.setColor(QColor(0, 0, 0, 10))
            navbar.setGraphicsEffect(nav_shadow)
            
            nav_layout = QHBoxLayout(navbar)
            nav_layout.setContentsMargins(40, 0, 40, 0)
            
            logo = QLabel("THR FITNESS")
            logo.setObjectName("Logo")
            nav_layout.addWidget(logo)
            nav_layout.addStretch()
            
            self.nav_user = QLineEdit()
            self.nav_user.setObjectName("NavInput")
            self.nav_user.setPlaceholderText("Athlete Name")
            self.nav_user.setFixedWidth(220)
            
            self.nav_voice = QComboBox()
            self.nav_voice.setObjectName("NavInput")
            self.nav_voice.addItems(["Male Coach", "Female Coach"])
            self.nav_voice.setFixedWidth(180)
            self.nav_voice.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
            nav_layout.addWidget(self.nav_user)
            nav_layout.addSpacing(15)
            nav_layout.addWidget(self.nav_voice)
            page_layout.addWidget(navbar)
            
            # --- 2. Content Wrapper ---
            content_wrapper = QWidget()
            content_layout = QVBoxLayout(content_wrapper)
            content_layout.setContentsMargins(40, 40, 40, 60)
            content_layout.setSpacing(10)
            page_layout.addWidget(content_wrapper)
            
            # --- Hero Banner Layer ---
            hero = QWidget()
            hero.setObjectName("Hero")
            hero.setFixedHeight(220)
            
            hero_shadow = QGraphicsDropShadowEffect()
            hero_shadow.setBlurRadius(30)
            hero_shadow.setOffset(0, 15)
            hero_shadow.setColor(QColor(74, 144, 226, 80)) # Glow effect using blue
            hero.setGraphicsEffect(hero_shadow)
            
            hero_layout = QVBoxLayout(hero)
            hero_layout.setContentsMargins(50, 40, 50, 40)
            
            h1 = QLabel("Refine Your Form. Elevate Your Output.")
            h1.setObjectName("HeroTitle")
            sub = QLabel("Select an intelligent tracking module below to instantly boot OpenCV.")
            sub.setObjectName("HeroSub")
            
            hero_layout.addStretch()
            hero_layout.addWidget(h1)
            hero_layout.addWidget(sub)
            hero_layout.addStretch()
            
            content_layout.addWidget(hero)
            content_layout.addSpacing(40)
            
            # --- 3. Workout Cards Grid ---
            sec1_title = QLabel("Tracking Modules")
            sec1_title.setObjectName("SectionTitle")
            content_layout.addWidget(sec1_title)
            
            grid_layout = QGridLayout()
            grid_layout.setSpacing(35)
            
            # The 8 specific modules requested by user
            card_auto = HoverCard("Smart Auto-Session", "AI automatically tracks the movement you commit to with high precision.", tag_text="AUTODETECT", accent_color="#50E3C2", parent_window=self)
            grid_layout.addWidget(card_auto, 0, 0)
            
            card_squat = HoverCard("Squats", "Tracks hip depth below knee crease for perfect biomechanical squats.", parent_window=self)
            grid_layout.addWidget(card_squat, 0, 1)
            
            card_push = HoverCard("Push-Ups", "Chest to floor precision endurance tracking. Do not break strict form.", parent_window=self)
            grid_layout.addWidget(card_push, 0, 2)
            
            card_pull = HoverCard("Pull-Ups", "Chin over bar clearance detection and heavy lat activation monitoring.", parent_window=self)
            grid_layout.addWidget(card_pull, 1, 0)
            
            card_plank = HoverCard("Planks", "Static duration tracking. Ensure spinal alignment remains perfectly flat.", parent_window=self)
            grid_layout.addWidget(card_plank, 1, 1)
            
            card_bicep = HoverCard("Bicep Curls", "Pin elbows strictly. Maximize contraction. Perfect repetition counting.", parent_window=self)
            grid_layout.addWidget(card_bicep, 1, 2)
            
            card_crunch = HoverCard("Crunches", "Abdominal isolation tracking for core velocity and muscular endurance.", parent_window=self)
            grid_layout.addWidget(card_crunch, 2, 0)
            
            card_upload = HoverCard("Analyze Video", "Provide a pre-recorded workout file to review your mechanics post-workout.", accent_color="#FF6B6B", is_upload=True, parent_window=self)
            grid_layout.addWidget(card_upload, 2, 1)
            
            content_layout.addLayout(grid_layout)
            
            # --- 4. History Leaderboard ---
            content_layout.addSpacing(50)
            sec2_title = QLabel("Global Leaderboard")
            sec2_title.setObjectName("SectionTitle")
            content_layout.addWidget(sec2_title)
            
            history_box = QFrame()
            history_box.setObjectName("HistoryBox")
            
            hist_shadow = QGraphicsDropShadowEffect()
            hist_shadow.setBlurRadius(20)
            hist_shadow.setOffset(0, 10)
            hist_shadow.setColor(QColor(0, 0, 0, 10))
            history_box.setGraphicsEffect(hist_shadow)
            
            history_layout = QVBoxLayout(history_box)
            history_layout.setContentsMargins(40, 30, 40, 30)
            history_layout.setSpacing(20)
            
            # Read CSV
            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workout_history.csv")
            try:
                if not os.path.exists(csv_path):
                    em = QLabel("No workout history found yet. You're the first to log in!")
                    em.setStyleSheet("color: #A0AEC0; font-size: 16px;")
                    history_layout.addWidget(em)
                else:
                    with open(csv_path, mode='r') as f:
                        reader = list(csv.DictReader(f))
                        reader.reverse() # Latest first
                        
                        limit = min(6, len(reader)) # Show top 6
                        for i in range(limit):
                            row = reader[i]
                            
                            row_widget = QWidget()
                            row_lyt = QHBoxLayout(row_widget)
                            row_lyt.setContentsMargins(0, 5, 0, 5)
                            
                            info_lyt = QVBoxLayout()
                            t_lbl = QLabel(f"{row.get('Username', 'Athlete').title()} • {row.get('Exercise', 'Unknown').title()}")
                            t_lbl.setObjectName("HistTitle")
                            sub_lbl = QLabel(f"{row.get('Date', '')} — {row.get('Reps/Seconds', 0)} Repetitions")
                            sub_lbl.setObjectName("HistSub")
                            
                            info_lyt.addWidget(t_lbl)
                            info_lyt.addWidget(sub_lbl)
                            
                            score_lbl = QLabel(f"SCORE: {row.get('Score', 0)}")
                            score_lbl.setObjectName("HistScore")
                            
                            row_lyt.addLayout(info_lyt)
                            row_lyt.addStretch()
                            row_lyt.addWidget(score_lbl)
                            
                            history_layout.addWidget(row_widget)
                            
                            if i < limit - 1:
                                divider = QFrame()
                                divider.setFixedHeight(1)
                                divider.setStyleSheet("background-color: #E1E8ED;")
                                history_layout.addWidget(divider)
            except Exception as e:
                history_layout.addWidget(QLabel("Failed to sync leaderboard data."))
                
            content_layout.addWidget(history_box)
            
            # Fill bottom
            page_layout.addStretch()
            
            # Setup Parent Window Layout
            parent_layout = QVBoxLayout(self)
            parent_layout.setContentsMargins(0, 0, 0, 0)
            parent_layout.addWidget(scroll)

    # Launch it!
    window = AppDashboard()
    window.show()
    app.exec() # Halt execute until window is closed!

    if 'cap' not in result:
        sys.exit(0) # Window closed via 'X'

    return result['cap'], result['source_desc'], result['use_mirror'], result['username'], result['voice_gender']

if __name__ == '__main__':
    # Add fake default imports if called specifically standalone for immediate tests
    # But usually called from exercise_detector.py
    launch_setup_gui()
