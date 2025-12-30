import sys
import os
import datetime
import pytz
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QHBoxLayout, QVBoxLayout, QMenu, QAction, 
                             QGraphicsDropShadowEffect, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QSize, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QCursor, QIcon

# Configuration File Path
CONFIG_FILE = "layout_config.json"

class DraggableLabel(QLabel):
    def __init__(self, parent=None, name="", border_color="red"):
        super().__init__(parent)
        self.name = name
        self.border_color = border_color
        self.setMouseTracking(True)
        self.is_editing = False
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.drag_start_pos = QPoint()
        self.resize_start_pos = QPoint()
        self.initial_geometry = QRect()
        
        self._original_pixmap = None
        
        # Callbacks for resize events
        self.on_resize_start = None
        self.on_resize = None
        
        # Style
        self.default_style = "border: none;"
        self.update_style()

    def setPixmap(self, pixmap):
        self._original_pixmap = pixmap
        self.update_scaled_pixmap()
    
    def resizeEvent(self, event):
        self.update_scaled_pixmap()
        super().resizeEvent(event)
        
    def update_scaled_pixmap(self):
        try:
            if self._original_pixmap and not self._original_pixmap.isNull() and self.width() > 1 and self.height() > 1:
                scaled = self._original_pixmap.scaled(
                    self.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                super().setPixmap(scaled)
        except Exception as e:
            print(f"Error scaling pixmap: {e}")

    def update_style(self):
        if self.is_editing:
            # Dashed border, semi-transparent background to see the area
            self.setStyleSheet(f"border: 2px dashed {self.border_color}; background-color: rgba(255, 255, 255, 20);")
        else:
            self.setStyleSheet("border: none; background-color: transparent;")
            self.setCursor(Qt.ArrowCursor)

    def set_editing(self, editing):
        self.is_editing = editing
        self.update_style()

    def mousePressEvent(self, event):
        if not self.is_editing:
            event.ignore()
            return

        if event.button() == Qt.LeftButton:
            # Check for resize (bottom-right corner)
            if self.rect().bottomRight() in QRect(event.pos() - QPoint(15, 15), QSize(30, 30)):
                self.resizing = True
                self.resize_start_pos = event.globalPos()
                self.initial_geometry = self.geometry()
                if self.on_resize_start:
                    self.on_resize_start()
            else:
                self.dragging = True
                self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.is_editing:
            return

        # Cursor update
        if self.rect().bottomRight() in QRect(event.pos() - QPoint(15, 15), QSize(30, 30)):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.SizeAllCursor)

        if self.dragging:
            # Move widget
            # Map to parent coordinates
            new_pos = self.mapToParent(event.pos() - self.drag_start_pos)
            self.move(new_pos)
            
        elif self.resizing:
            # Resize widget
            delta = event.globalPos() - self.resize_start_pos
            
            # Check for Shift key (Keep Aspect Ratio)
            keep_aspect_ratio = (event.modifiers() & Qt.ShiftModifier)
            
            new_width = max(20, self.initial_geometry.width() + delta.x())
            new_height = max(20, self.initial_geometry.height() + delta.y())
            
            if keep_aspect_ratio and self.initial_geometry.height() > 0:
                ratio = self.initial_geometry.width() / self.initial_geometry.height()
                # Use the larger change to drive the resize
                if abs(delta.x()) > abs(delta.y()):
                    # Avoid division by zero if ratio is very small (though width/height check handles most)
                    if ratio > 0.0001:
                        new_height = int(new_width / ratio)
                else:
                    new_width = int(new_height * ratio)
            
            self.resize(new_width, new_height)
            if self.on_resize:
                self.on_resize()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
            
class AssetLoader:
    def __init__(self, asset_dir="assets"):
        self.asset_dir = self.resource_path(asset_dir)
        self.digits = {}
        self.colon = None
        self.bg = None
        try:
            self.load_assets()
        except Exception as e:
            print(f"Resource loading skipped: {e}")

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            # use the directory of the script file instead of current working directory
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def load_assets(self):
        print(f"Loading assets from: {self.asset_dir}")
        if not os.path.exists(self.asset_dir):
            print(f"Asset directory not found: {self.asset_dir}")
            return

        for i in range(10):
            path = os.path.join(self.asset_dir, f"{i}.png")
            if os.path.exists(path):
                self.digits[str(i)] = QPixmap(path)
                
        colon_path = os.path.join(self.asset_dir, "colon.png")
        if os.path.exists(colon_path):
            self.colon = QPixmap(colon_path)
            
        bg_path = os.path.join(self.asset_dir, "bg.png")
        if os.path.exists(bg_path):
            self.bg = QPixmap(bg_path)

class CountdownWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.loader = AssetLoader()
        self.target_year = 2026
        self.current_tz = pytz.timezone('Asia/Shanghai') 
        self.is_editing = False
        
        # Resize flags for Window
        self.window_resizing = False
        self.window_resize_start_pos = None
        self.window_initial_size = None
        
        # Config Data
        self.config = {
            "window_size": [500, 200],
            "digits_container": {"x": 20, "y": 50, "w": 460, "h": 100},
            "digits": {}, 
            "timezone": "Asia/Shanghai",
            "target_date": "2026-01-01 00:00:00",
            "top_most": False
        }
        self.load_config()

        self.init_ui()
        self.init_timer()
        
        self.old_pos = None
        self.setMouseTracking(True) # Important for cursor update on window

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved_config = json.load(f)
                    for k, v in saved_config.items():
                        if k in self.config:
                            self.config[k] = v
                    if "timezone" in self.config:
                         try:
                             self.current_tz = pytz.timezone(self.config["timezone"])
                         except:
                             pass
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        self.config["window_size"] = [self.width(), self.height()]
        self.config["window_position"] = [self.x(), self.y()]
        self.config["digits_container"] = [
            self.digits_container.x(), self.digits_container.y(),
            self.digits_container.width(), self.digits_container.height()
        ]
        
        for i, lbl in enumerate(self.digit_labels):
            self.config["digits"][str(i)] = [lbl.x(), lbl.y(), lbl.width(), lbl.height()]
            
        self.config["timezone"] = str(self.current_tz)
        # target_date and top_most are updated in their respective methods or just kept

        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def reset_layout(self):
        if self.loader.bg:
            w, h = self.loader.bg.width(), self.loader.bg.height()
            w = max(w, 200)
            h = max(h, 100)
        else:
            w, h = 500, 200
        
        self.resize(w, h)
        
        cont_w = int(w * 0.9)
        cont_h = int(h * 0.6)
        self.digits_container.setGeometry((w - cont_w)//2, (h - cont_h)//2, cont_w, cont_h)
        
        # Add padding inside container to avoid edge overlap issues
        padding_x = 50 # Increased padding to make container easier to grab (Blue Box bigger)
        padding_y = 25
        available_w = max(10, cont_w - 2 * padding_x)
        available_h = max(10, cont_h - 2 * padding_y)
        
        digit_w = available_w // 5
        for i, lbl in enumerate(self.digit_labels):
            lbl.setGeometry(padding_x + i * digit_w, padding_y, digit_w, available_h)
            
        self.save_config()

    def handle_container_resize_start(self):
        self.initial_child_geoms = [lbl.geometry() for lbl in self.digit_labels]
        self.initial_container_size = self.digits_container.size()

    def handle_container_resize(self):
        if not hasattr(self, 'initial_container_size') or self.initial_container_size.isEmpty():
            return
            
        current_size = self.digits_container.size()
        if self.initial_container_size.width() <= 0 or self.initial_container_size.height() <= 0:
            return

        scale_x = current_size.width() / self.initial_container_size.width()
        scale_y = current_size.height() / self.initial_container_size.height()
        
        for i, lbl in enumerate(self.digit_labels):
            initial_rect = self.initial_child_geoms[i]
            new_x = int(initial_rect.x() * scale_x)
            new_y = int(initial_rect.y() * scale_y)
            new_w = int(initial_rect.width() * scale_x)
            new_h = int(initial_rect.height() * scale_y)
            lbl.setGeometry(new_x, new_y, new_w, new_h)

    def init_ui(self):
        self.setWindowTitle("mmticktock")
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.config.get("top_most", False):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        w, h = self.config["window_size"]
        self.resize(w, h)
        
        # Center on screen if no position is saved OR if saved position is off-screen
        screen_geo = QApplication.primaryScreen().availableGeometry()
        
        should_center = True
        if "window_position" in self.config and len(self.config["window_position"]) == 2:
            x, y = self.config["window_position"]
            # Check if the window is within the screen bounds
            if screen_geo.contains(x + 20, y + 20): # Check if at least top-left corner is visible
                self.move(x, y)
                should_center = False
            else:
                print(f"Saved position ({x}, {y}) is off-screen. Resetting to center.")
        
        if should_center:
            self.move((screen_geo.width() - w) // 2, (screen_geo.height() - h) // 2)

        # Digits Container (Blue border)
        self.digits_container = DraggableLabel(self.central_widget, "Container", border_color="#00AAFF")
        self.digits_container.on_resize_start = self.handle_container_resize_start
        self.digits_container.on_resize = self.handle_container_resize
        
        dc_conf = self.config["digits_container"]
        if isinstance(dc_conf, dict):
             self.digits_container.setGeometry(dc_conf["x"], dc_conf["y"], dc_conf["w"], dc_conf["h"])
        elif isinstance(dc_conf, list):
             self.digits_container.setGeometry(*dc_conf)
        else:
             self.digits_container.setGeometry(20, 50, 460, 100)

        # Digits (Red border)
        self.digit_labels = []
        for i in range(5):
            lbl = DraggableLabel(self.digits_container, f"Digit_{i}", border_color="#FF4444")
            lbl.setAlignment(Qt.AlignCenter)
            # lbl.setScaledContents(True)  # Removed to keep aspect ratio
            
            if str(i) in self.config["digits"]:
                rect = self.config["digits"][str(i)]
                lbl.setGeometry(*rect)
            else:
                cw = self.digits_container.width()
                ch = self.digits_container.height()
                dw = cw // 5
                lbl.setGeometry(i * dw, 0, dw, ch)

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
            
        self.update_display()

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.loader.bg:
            painter.drawPixmap(self.rect(), self.loader.bg)
        else:
            painter.setBrush(QColor(40, 40, 40, 200))
            pen = QPen(QColor(255, 255, 255, 200))
            pen.setWidth(4)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            rect = self.rect().adjusted(5, 5, -5, -5)
            painter.drawRoundedRect(rect, 30, 30)
            
        if self.is_editing:
            # Yellow border for window (Background)
            painter.setPen(QPen(Qt.yellow, 3, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect().adjusted(2, 2, -2, -2))
            
            # Resize handle hint for window
            painter.setBrush(Qt.yellow)
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.width()-20, self.height()-20, 20, 20)

    def get_time_str(self):
        now = datetime.datetime.now(self.current_tz)
        
        target_str = self.config.get("target_date", "2026-01-01 00:00:00")
        try:
            target_naive = datetime.datetime.strptime(target_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            target_naive = datetime.datetime(2026, 1, 1, 0, 0, 0)

        # Use localize to ensure correct timezone handling without double-adjustment
        try:
            target = self.current_tz.localize(target_naive)
        except AttributeError:
             # Fallback if timezone object doesn't have localize (shouldn't happen with pytz)
             target = target_naive.replace(tzinfo=self.current_tz)
        
        is_countdown = now < target
        if is_countdown:
            diff = target - now
        else:
            diff = now - target
        
        total_seconds = int(diff.total_seconds())
        
        if total_seconds > 3600: 
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 99: hours, minutes = 99, 99
            val1, val2 = hours, minutes
        else:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            if not is_countdown and minutes > 99: minutes, seconds = 99, 99
            val1, val2 = minutes, seconds
        
        return f"{val1:02d}", f"{val2:02d}"

    def update_display(self):
        v1_str, v2_str = self.get_time_str()
        self.set_digit(0, v1_str[0])
        self.set_digit(1, v1_str[1])
        # self.set_digit(2, ":") 
        self.set_digit(3, v2_str[0])
        self.set_digit(4, v2_str[1])

    def set_digit(self, index, char):
        lbl = self.digit_labels[index]
        if index == 2: return 
        
        if char in self.loader.digits:
            lbl.setPixmap(self.loader.digits[char])
        else:
            lbl.setText(char)

    # --- Interaction ---
    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        
        self.digits_container.set_editing(self.is_editing)
        for lbl in self.digit_labels:
            lbl.set_editing(self.is_editing)
            
        if not self.is_editing:
            self.save_config()
            self.setCursor(Qt.ArrowCursor)
            
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_editing:
                # Check for Window Resize (Bottom Right)
                if event.pos() in QRect(self.width()-20, self.height()-20, 20, 20):
                    self.window_resizing = True
                    self.window_resize_start_pos = event.globalPos()
                    self.window_initial_size = self.size()
                    return
            
            # Default Move behavior (Available in both modes now)
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.is_editing:
            # Update cursor for Window Resize
            if event.pos() in QRect(self.width()-20, self.height()-20, 20, 20):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
                
            if self.window_resizing:
                delta = event.globalPos() - self.window_resize_start_pos
                new_w = max(100, self.window_initial_size.width() + delta.x())
                new_h = max(50, self.window_initial_size.height() + delta.y())
                self.resize(new_w, new_h)
                return

        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.window_resizing = False

    def contextMenuEvent(self, event):
        try:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu { background-color: #333; color: white; border: 1px solid #555; }
                QMenu::item { padding: 5px 25px 5px 25px; }
                QMenu::item:selected { background-color: #555; }
                QMenu::indicator { width: 15px; height: 15px; }
            """)
            
            # Helper to create a transparent icon for alignment
            transparent_pixmap = QPixmap(15, 15)
            transparent_pixmap.fill(Qt.transparent)
            transparent_icon = QIcon(transparent_pixmap)
    
            # 1. Edit Mode (Checkable)
            edit_action = QAction("🛠️ 调整模式", self)
            edit_action.setCheckable(True)
            edit_action.setChecked(self.is_editing)
            edit_action.triggered.connect(self.toggle_edit_mode)
            menu.addAction(edit_action)
            
            # 2. Top Most (Checkable)
            top_action = QAction("📌 窗口置顶", self)
            top_action.setCheckable(True)
            top_action.setChecked(self.config.get("top_most", False))
            top_action.triggered.connect(self.toggle_top_most)
            menu.addAction(top_action)
            
            # 3. Reset Layout (Not Checkable -> Needs Icon for alignment)
            reset_action = QAction(transparent_icon, "↺   重置布局", self)
            reset_action.triggered.connect(self.reset_layout)
            menu.addAction(reset_action)
            
            menu.addSeparator()
            
            # 4. Timezone (Submenu -> Needs Icon for alignment)
            tz_menu = menu.addMenu("🌐 选择时区")
            tz_menu.setIcon(transparent_icon)
            
            common_timezones = [
                'Asia/Shanghai', 'Asia/Tokyo', 'America/New_York', 
                'Europe/London', 'Australia/Sydney', 'UTC'
            ]
            
            for tz_name in common_timezones:
                action = QAction(tz_name, self)
                if str(self.current_tz) == tz_name:
                    action.setCheckable(True)
                    action.setChecked(True)
                action.triggered.connect(lambda checked, name=tz_name: self.change_timezone(name))
                tz_menu.addAction(action)
                
            # 5. Exit (Not Checkable -> Needs Icon for alignment)
            exit_action = QAction(transparent_icon, "❌ 退出程序", self)
            exit_action.triggered.connect(self.close)
            menu.addAction(exit_action)
            
            menu.exec_(event.globalPos())
        except Exception as e:
            print(f"Context menu error: {e}")

    def toggle_top_most(self, checked):
        self.config["top_most"] = checked
        self.save_config()
        
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint
            
        self.setWindowFlags(flags)
        self.show()

    def change_timezone(self, tz_name):
        try:
            self.current_tz = pytz.timezone(tz_name)
            self.save_config()
            self.update_display()
        except Exception as e:
            print(f"Error changing timezone: {e}")

    def closeEvent(self, event):
        self.save_config()
        event.accept()

if __name__ == "__main__":
    print("Application starting...")
    try:
        app = QApplication(sys.argv)
        print("QApplication created.")
        window = CountdownWindow()
        print("Window created.")
        window.show()
        print("Window shown.")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Critical Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            input("Press Enter to exit...")
        except:
            pass
