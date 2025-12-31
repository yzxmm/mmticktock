import sys
import pytz

# Try importing ctypes safely
try:
    import ctypes
except ImportError:
    ctypes = None

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QMenu, QAction, 
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QRect, QSize, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QIcon

from assets import AssetLoader
from widgets import DraggableLabel, ContainerWidget
from core_utils import ConfigManager, TimeCalculator
from layout_helper import LayoutHelper
from resize_handler import ResizeHandler

class CountdownWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.loader = AssetLoader()
        self.config = ConfigManager.load_config()
        self.current_tz = pytz.timezone('Asia/Shanghai') 
        self.is_editing = False
        self.global_resizing = False
        self.initial_window_size = None
        self.initial_digits_geo = []
        self.yellow_rect = QRect()
        
        # Background Geometry Handling
        self.bg_rect = QRect() # Relative to Window (0,0)
        
        # Resize flags for Window
        self.window_resizing = False
        self.window_resize_start_pos = None
        self.is_yellow_dragging = False
        
        # Window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set Window Icon
        if self.loader.icon:
            self.setWindowIcon(QIcon(self.loader.icon))
        
        self.init_ui()
        self.init_timer()
        
        if self.config.get("top_most", False):
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.show()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        w, h = self.config["window_size"]
        screen_geo = QApplication.desktop().screenGeometry()
        w = min(w, screen_geo.width())
        h = min(h, screen_geo.height())
        self.resize(w, h)
        
        if "window_pos" in self.config:
            x, y = self.config["window_pos"]
            if x < -w + 20 or x > screen_geo.width() - 20 or y < -h + 20 or y > screen_geo.height() - 20:
                 x, y = 100, 100
            self.move(x, y)
        else:
            self.move(100, 100)

        self.digit_labels = []
        
        # Digits Container (Blue Box)
        self.digits_container = ContainerWidget(self.central_widget)
        self.digits_container.setGeometry(50, 50, 400, 100)
        self.digits_container.hide()
        
        # Create digit labels (00:00)
        for i in range(5):
            lbl = DraggableLabel(self.central_widget)
            if i == 2: # Colon
                lbl.setText(":")
                lbl.setAlignment(Qt.AlignCenter)
            else:
                lbl.setText("0")
                lbl.setAlignment(Qt.AlignCenter)
            
            # Default style
            if not self.loader.digits:
                font = QFont("Comic Sans MS", 80, QFont.Bold)
                font.setStyleStrategy(QFont.PreferAntialias)
                lbl.setFont(font)
                lbl.setStyleSheet("color: white;")
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(10)
                shadow.setColor(QColor(0, 0, 0, 150))
                shadow.setOffset(2, 2)
                lbl.setGraphicsEffect(shadow)
            
            self.digit_labels.append(lbl)
            
        if self.loader.colon:
            self.digit_labels[2].setPixmap(self.loader.colon)
        else:
            self.digit_labels[2].setText(":")

        LayoutHelper.reset_layout(self)
        self.update_display()

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    def save_config(self):
        # Wrapper for ConfigManager to include current state
        self.config["window_size"] = [self.width(), self.height()]
        self.config["window_pos"] = [self.x(), self.y()]
        ConfigManager.save_config(self.config)

    def update_display(self):
        target_date = self.config.get("target_date", "2026-01-01 00:00:00")
        val1, val2 = TimeCalculator.get_time_str(target_date, self.current_tz)
        
        if self.loader.digits:
            if val1[0] in self.loader.digits: self.digit_labels[0].setPixmap(self.loader.digits[val1[0]])
            if val1[1] in self.loader.digits: self.digit_labels[1].setPixmap(self.loader.digits[val1[1]])
            if val2[0] in self.loader.digits: self.digit_labels[3].setPixmap(self.loader.digits[val2[0]])
            if val2[1] in self.loader.digits: self.digit_labels[4].setPixmap(self.loader.digits[val2[1]])
        else:
            self.digit_labels[0].setText(val1[0])
            self.digit_labels[1].setText(val1[1])
            self.digit_labels[3].setText(val2[0])
            self.digit_labels[4].setText(val2[1])

    def resizeEvent(self, event):
        # Cache background only when window size changes to avoid heavy scaling during moves
        if self.loader.bg:
            self.bg_rect = self.rect()
            self.cached_bg = self.loader.bg.scaled(self.bg_rect.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
        else:
            self.bg_rect = self.rect()
        super().resizeEvent(event)
 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw Background
        if self.loader.bg and hasattr(self, 'cached_bg') and self.cached_bg:
            painter.drawPixmap(0, 0, self.cached_bg)
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
            
        if self.is_editing:
            pen = QPen(Qt.yellow, 12, Qt.DashLine)
            painter.setPen(pen)
            r = self.rect()
            painter.drawRect(r.adjusted(2,2,-2,-2))
            painter.setBrush(Qt.yellow)
            painter.setPen(Qt.NoPen)
            handle_size = 10
            painter.drawRect(r.right() - handle_size, r.bottom() - handle_size, handle_size, handle_size)
            painter.drawRect(r.right() - handle_size, r.top() + r.height()//2 - handle_size//2, handle_size, handle_size)
            painter.drawRect(r.left() + r.width()//2 - handle_size//2, r.bottom() - handle_size, handle_size, handle_size)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # Edit Mode
        edit_action = QAction("调整布局" if not self.is_editing else "退出调整", self)
        edit_action.triggered.connect(self.toggle_edit_mode)
        menu.addAction(edit_action)
        
        if self.is_editing:
            reset_action = QAction("重置布局 (修复间距)", self)
            reset_action.triggered.connect(lambda: LayoutHelper.reset_layout(self))
            menu.addAction(reset_action)
        
        menu.addSeparator()
        
        # TopMost
        is_top = self.windowFlags() & Qt.WindowStaysOnTopHint
        top_action = QAction("置顶窗口", self)
        top_action.setCheckable(True)
        top_action.setChecked(bool(is_top))
        top_action.triggered.connect(self.toggle_top_most)
        menu.addAction(top_action)
        
        menu.addSeparator()
        
        # Timezone
        tz_menu = menu.addMenu("切换时区")
        common_timezones = [
            'Asia/Shanghai', 'Asia/Tokyo', 'Asia/Hong_Kong',
            'America/New_York', 'America/Los_Angeles', 'America/Chicago',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Moscow',
            'Australia/Sydney', 'Pacific/Auckland', 'Asia/Dubai', 'UTC'
        ]
        for tz_name in common_timezones:
            action = QAction(tz_name, self)
            action.triggered.connect(lambda checked, name=tz_name: self.change_timezone(name))
            if str(self.current_tz) == tz_name:
                action.setCheckable(True); action.setChecked(True)
            tz_menu.addAction(action)
            
        menu.addSeparator()
        menu.addAction("退出", self.close)
        menu.exec_(event.globalPos())

    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        if self.is_editing:
            self.digits_container.show()
            self.digits_container.lower()
            self.update_container_geometry()
            for lbl in self.digit_labels:
                lbl.raise_()
        else:
            self.digits_container.hide()
        for lbl in self.digit_labels:
            lbl.set_editing(self.is_editing)
        self.update()

    def toggle_top_most(self, checked):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, checked)
        self.show()
        self.config["top_most"] = checked
        self.save_config()

    def change_timezone(self, tz_name):
        try:
            self.current_tz = pytz.timezone(tz_name)
            self.update_display()
        except Exception as e:
            print(f"Error setting timezone: {e}")

    def mousePressEvent(self, event):
        if not self.is_editing:
            if event.button() == Qt.LeftButton:
                self.window_resizing = False
                self.window_frame_pos = self.frameGeometry().topLeft()
                self.drag_start_pos = event.globalPos()
        else:
            if event.button() == Qt.LeftButton:
                handle_size = 10
                r = self.rect()
                handle_br = QRect(r.right() - handle_size, r.bottom() - handle_size, handle_size, handle_size)
                handle_r = QRect(r.right() - handle_size, r.top() + r.height()//2 - handle_size//2, handle_size, handle_size)
                handle_b = QRect(r.left() + r.width()//2 - handle_size//2, r.bottom() - handle_size, handle_size, handle_size)
                resize_mode = None
                if handle_br.contains(event.pos()):
                    resize_mode = 'bottom-right'
                elif handle_r.contains(event.pos()):
                    resize_mode = 'right'
                elif handle_b.contains(event.pos()):
                    resize_mode = 'bottom'
                if resize_mode:
                    self.global_resizing = True
                    self.resize_mode = resize_mode
                    self.window_resize_start_pos = event.globalPos()
                    self.initial_window_size = r.size()
                    self.initial_yellow_rect = QRect(r)
                elif r.contains(event.pos()):
                    self.is_yellow_dragging = True
                    self.window_frame_pos = self.frameGeometry().topLeft()
                    self.drag_start_global = event.globalPos()
                     
    def mouseMoveEvent(self, event):
        if not self.is_editing:
            if event.buttons() & Qt.LeftButton:
                self.move(self.window_frame_pos + (event.globalPos() - self.drag_start_pos))
        else:
            if not self.is_editing:
                if event.buttons() & Qt.LeftButton:
                    self.move(self.window_frame_pos + (event.globalPos() - self.drag_start_pos))
            else:
                if self.global_resizing:
                    ResizeHandler.handle_global_resize(self, event)
                elif self.is_yellow_dragging:
                    delta = event.globalPos() - self.drag_start_global
                    self.move(self.window_frame_pos + delta)
                    self.update()

    def mouseReleaseEvent(self, event):
        self.window_resizing = False
        self.global_resizing = False
        self.is_yellow_dragging = False
        self.is_window_dragging_in_edit = False
        self.global_resizing = False
        
        self.ensure_bounds()
    
    def update_container_geometry(self):
        LayoutHelper.update_container_geometry(self)
        # Sync yellow to wrap window
        self.yellow_rect = self.rect()

    def ensure_bounds(self):
        LayoutHelper.ensure_bounds(self)

if __name__ == "__main__":
    if ctypes:
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('yzxmm.mmticktock.countdown.1.0')
        except: pass
    app = QApplication(sys.argv)
    window = CountdownWindow()
    window.show()
    sys.exit(app.exec_())
