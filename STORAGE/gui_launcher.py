import sys
import os
import cv2
import csv
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, 
                             QFileDialog, QMessageBox, QFrame, QScrollArea, QGridLayout,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QPoint, QEasingCurve
from PyQt6.QtGui import QColor, QCursor, QLinearGradient, QGradient, QPalette

def launch_setup_gui():
    """
    Launches a massive Single-Page PyQt6 Desktop Dashboard with depth and pleasing colors.
    Returns: cap, source_desc, use_mirror, username, voice_gender
    """
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    result = {}

    # --- PRESET THEMES ---
    LIGHT_STYLESHEET = """
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
        border-bottom: 2px solid #E2E8F0;
    }
    
    QLabel#Logo {
        color: #1A202C; /* Deep Slate Bold */
        font-size: 30px;
        font-weight: 900;
        letter-spacing: 2px;
    }
    
    QLineEdit#NavInput, QComboBox#NavInput {
        padding: 12px 20px;
        border-radius: 12px;
        border: 1px solid #CBD5E0;
        font-size: 15px;
        font-weight: 600;
        background-color: #F8FAFC;
        color: #2D3748;
    }
    QLineEdit#NavInput:focus, QComboBox#NavInput:focus {
        border: 2px solid #4A90E2;
        background-color: #FFFFFF;
    }
    
    /* Hero Section (Soft Premium Gradient) */
    QWidget#Hero {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A90E2, stop:0.4 #357ABD, stop:1 #50E3C2);
        border: 1px solid #E2E8F0;
        border-radius: 24px;
    }
    QLabel#HeroTitle {
        color: #FFFFFF;
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 5px;
        letter-spacing: -2px;
    }
    QLabel#HeroSub {
        color: #F1F5F9;
        font-size: 20px;
        font-weight: 500;
    }
    
    /* Section Headings */
    QLabel#SectionTitle {
        color: #1A202C;
        font-size: 28px;
        font-weight: 900;
        margin-top: 45px;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Workout Cards (Floating depth) */
    QFrame#HoverCard {
        background-color: #FFFFFF;
        border-radius: 24px;
        border: 1px solid #E2E8F0;
    }
    
    QLabel#CardTitle {
        color: #2D3748;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: -1px;
    }
    QLabel#CardDesc {
        color: #718096;
        font-size: 15px;
        font-weight: 500;
        line-height: 1.5;
    }
    QLabel#Tag {
        background-color: #EDF2F7;
        color: #4A90E2;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 800;
        padding: 5px 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    QPushButton#CardButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90E2, stop:1 #357ABD);
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 800;
        border-radius: 25px; /* Pill Shape */
        padding: 18px;
        border: none;
    }
    QPushButton#CardButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5AA0F2, stop:1 #458ACD);
    }

    QPushButton#ThemeToggle {
        background-color: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 8px 15px;
        font-weight: 700;
        color: #2D3748;
    }
    QPushButton#ThemeToggle:hover {
        background-color: #E2E8F0;
    }
    
    /* Activity List */
    QFrame#HistoryBox {
        background-color: #FFFFFF;
        border-radius: 28px;
        border: 1px solid #E2E8F0;
    }
    
    /* Top Rank Highlights (Soft Lite tint) */
    QWidget#GoldRow { background-color: #FFF9E6; border-radius: 16px; }
    QWidget#SilverRow { background-color: #F7FAFC; border-radius: 16px; }
    QWidget#BronzeRow { background-color: #FFF5F2; border-radius: 16px; }
    QWidget#StandardRow { background-color: transparent; border-radius: 16px; }
    
    QLabel#HistTitle {
        color: #2D3748;
        font-size: 19px;
        font-weight: 800;
    }
    QLabel#HistSub {
        color: #718096;
        font-size: 14px;
        font-weight: 500;
    }
    QLabel#HistScore {
        color: #48BB78;
        font-size: 26px;
        font-weight: 900;
    }
    
    QLabel#AIStatus {
        background-color: rgba(16, 185, 129, 0.1); 
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        padding: 5px 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    """

    DARK_STYLESHEET = """
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    QScrollArea {
        border: none;
        background-color: #0F172A;
    }
    QWidget#MainContainer {
        background-color: #0F172A;
    }
    
    /* Top Navbar */
    QWidget#NavBar {
        background-color: #1E293B;
        border-bottom: 2px solid #334155;
    }
    
    QLabel#Logo {
        color: #F1F5F9;
        font-size: 30px;
        font-weight: 900;
        letter-spacing: 2px;
    }
    
    QLineEdit#NavInput, QComboBox#NavInput {
        padding: 12px 20px;
        border-radius: 12px;
        border: 1px solid #475569;
        font-size: 15px;
        font-weight: 600;
        background-color: #0F172A;
        color: #F1F5F9;
    }
    QLineEdit#NavInput:focus, QComboBox#NavInput:focus {
        border: 2px solid #38B2AC;
        background-color: #1E293B;
    }
    
    /* Hero Section (Deep Dark Gradient) */
    QWidget#Hero {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E40AF, stop:0.4 #312E81, stop:1 #4F46E5);
        border: 1px solid #334155;
        border-radius: 24px;
    }
    QLabel#HeroTitle {
        color: #FFFFFF;
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 5px;
        letter-spacing: -2px;
    }
    QLabel#HeroSub {
        color: #E2E8F0;
        font-size: 20px;
        font-weight: 500;
    }
    
    /* Section Headings */
    QLabel#SectionTitle {
        color: #F1F5F9;
        font-size: 28px;
        font-weight: 900;
        margin-top: 45px;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Workout Cards (Floating depth) */
    QFrame#HoverCard {
        background-color: #1E293B;
        border-radius: 24px;
        border: 1px solid #334155;
    }
    
    QLabel#CardTitle {
        color: #F1F5F9;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: -1px;
    }
    QLabel#CardDesc {
        color: #94A3B8;
        font-size: 15px;
        font-weight: 500;
    }
    QLabel#Tag {
        background-color: #334155;
        color: #38B2AC;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 800;
        padding: 5px 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    QPushButton#CardButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38B2AC, stop:1 #2C7A7B);
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 800;
        border-radius: 25px;
        padding: 18px;
        border: none;
    }
    QPushButton#CardButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4FD1C5, stop:1 #38B2AC);
    }

    QPushButton#ThemeToggle {
        background-color: #334155;
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 8px 15px;
        font-weight: 700;
        color: #F1F5F9;
    }
    QPushButton#ThemeToggle:hover {
        background-color: #475569;
    }
    
    /* Activity List */
    QFrame#HistoryBox {
        background-color: #1E293B;
        border-radius: 28px;
        border: 1px solid #334155;
    }
    
    /* Top Rank Highlights (Dark variants) */
    QWidget#GoldRow { background-color: #3B2E0A; border-radius: 16px; }
    QWidget#SilverRow { background-color: #1E293B; border-radius: 16px; }
    QWidget#BronzeRow { background-color: #3B1B10; border-radius: 16px; }
    QWidget#StandardRow { background-color: transparent; border-radius: 16px; }
    
    QLabel#HistTitle {
        color: #F1F5F9;
        font-size: 19px;
        font-weight: 800;
    }
    QLabel#HistSub {
        color: #94A3B8;
        font-size: 14px;
        font-weight: 500;
    }
    QLabel#HistScore {
        color: #4ADE80;
        font-size: 26px;
        font-weight: 900;
    }
    
    QLabel#AIStatus {
        background-color: rgba(56, 178, 172, 0.1); 
        color: #38B2AC;
        border: 1px solid rgba(56, 178, 172, 0.3);
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        padding: 5px 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
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
            # Premium "Light Elevation" Effect
            self.shadow.setBlurRadius(50)
            self.shadow.setColor(QColor(0, 0, 0, 35) if self.parent_window.current_theme == "light" else QColor(0, 0, 0, 60))
            self.shadow.setOffset(0, 15)
            
            accent = "#4A90E2" if self.parent_window.current_theme == "light" else "#38B2AC"
            bg = "#FFFFFF" if self.parent_window.current_theme == "light" else "#1E293B"
            
            self.setStyleSheet(f"QFrame#HoverCard {{ background-color: {bg}; border-radius: 24px; border: 2px solid {accent}; margin-top: -8px; margin-bottom: 8px; }}")
            super().enterEvent(event)
            
        def leaveEvent(self, event):
            # Return to base light state
            self.shadow.setBlurRadius(25)
            self.shadow.setColor(QColor(0, 0, 0, 15) if self.parent_window.current_theme == "light" else QColor(0, 0, 0, 40))
            self.shadow.setOffset(0, 10)
            
            bg = "#FFFFFF" if self.parent_window.current_theme == "light" else "#1E293B"
            border = "#E2E8F0" if self.parent_window.current_theme == "light" else "#334155"
            
            self.setStyleSheet(f"QFrame#HoverCard {{ background-color: {bg}; border-radius: 24px; border: 1px solid {border}; margin-top: 0px; margin-bottom: 0px; }}")
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
            self.current_theme = "light"
            self.setStyleSheet(LIGHT_STYLESHEET)
            
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
            
            nav_layout.addSpacing(25)
            ai_badge = QLabel("● LOCAL AI READY")
            ai_badge.setObjectName("AIStatus")
            nav_layout.addWidget(ai_badge)
            
            nav_layout.addStretch()
            
            self.nav_user = QLineEdit()
            self.nav_user.setObjectName("NavInput")
            self.nav_user.setPlaceholderText("Name")
            self.nav_user.setFixedWidth(220)
            
            self.nav_voice = QComboBox()
            self.nav_voice.setObjectName("NavInput")
            self.nav_voice.addItems(["Male Coach", "Female Coach"])
            self.nav_voice.setFixedWidth(180)
            self.nav_voice.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
            # --- Theme Toggle ---
            self.theme_btn = QPushButton("🌙 DARK MODE")
            self.theme_btn.setObjectName("ThemeToggle")
            self.theme_btn.setFixedWidth(140)
            self.theme_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.theme_btn.clicked.connect(self.toggle_theme)

            nav_layout.addWidget(self.nav_user)
            nav_layout.addSpacing(15)
            nav_layout.addWidget(self.nav_voice)
            nav_layout.addSpacing(15)
            nav_layout.addWidget(self.theme_btn)
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
                        reader = csv.DictReader(f)
                        
                        # Dictionary to keep highest Score per user per exercise:
                        # key -> "Username_Exercise", value -> dict
                        user_best = {}
                        
                        for row in reader:
                            try:
                                user = row.get("Username", "Athlete").strip().title()
                                ex = row.get("Exercise", "Unknown").title()
                                score = float(row.get("Score", 0))
                                reps = float(row.get("Reps/Seconds", 0))
                                date = row.get("Date", "")
                                
                                key = f"{user}_{ex}"
                                if key not in user_best or score > user_best[key]['score']:
                                    user_best[key] = {
                                        'user': user,
                                        'ex': ex,
                                        'score': score,
                                        'reps': reps,
                                        'date': date
                                    }
                            except Exception:
                                continue
                                
                        # Sort all best records globally purely by score to create a true Global Leaderboard
                        sorted_records = sorted(user_best.values(), key=lambda x: x['score'], reverse=True)
                        limit = min(6, len(sorted_records)) # Show Top 6 globally
                        
                        for i in range(limit):
                            rec = sorted_records[i]
                            
                            row_widget = QWidget()
                            
                            # Specific Row Highlighting for top 3
                            row_id = "GoldRow" if i == 0 else "SilverRow" if i == 1 else "BronzeRow" if i == 2 else "StandardRow"
                            row_widget.setObjectName(row_id)
                            
                            row_lyt = QHBoxLayout(row_widget)
                            row_lyt.setContentsMargins(15, 12, 15, 12)
                            
                            info_lyt = QVBoxLayout()
                            
                            # Rank icon
                            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                            
                            t_lbl = QLabel(f"{medal} {rec['user']} • {rec['ex']}")
                            t_lbl.setObjectName("HistTitle")
                            sub_lbl = QLabel(f"{rec['date']} — {int(rec['reps'])} Repetitions")
                            sub_lbl.setObjectName("HistSub")
                            
                            info_lyt.addWidget(t_lbl)
                            info_lyt.addWidget(sub_lbl)
                            
                            score_lbl = QLabel(f"SCORE: {int(rec['score'])}")
                            score_lbl.setObjectName("HistScore")
                            
                            row_lyt.addLayout(info_lyt)
                            row_lyt.addStretch()
                            row_lyt.addWidget(score_lbl)
                            
                            history_layout.addWidget(row_widget)
                            
                            if i < limit - 1:
                                divider = QFrame()
                                divider.setFixedHeight(1)
                                divider.setStyleSheet("background-color: #EDF2F7;")
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

        def toggle_theme(self):
            if self.current_theme == "light":
                self.current_theme = "dark"
                self.setStyleSheet(DARK_STYLESHEET)
                self.theme_btn.setText("☀️ LIGHT MODE")
            else:
                self.current_theme = "light"
                self.setStyleSheet(LIGHT_STYLESHEET)
                self.theme_btn.setText("🌙 DARK MODE")
            
            # Refresh all HoverCards to update their internal styles
            # (Though they mostly use IDs, the shadows/dynamic borders need a reload if we were caching them)
            # This toggle will naturally affect new hover events.

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
