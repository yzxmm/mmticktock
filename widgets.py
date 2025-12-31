from PyQt5.QtWidgets import QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QFont, QColor

class DraggableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # Enable mouse tracking for hover effects
        self.is_editing = False # Local edit state
        
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.drag_start_pos = QPoint()
        self.resize_start_pos = QPoint()
        self.initial_geometry = QRect()
        self.window_start_pos = None # For window dragging
        
        self._original_pixmap = None  # Store original pixmap for scaling
        
        # Callbacks
        self.on_resize_start = None
        self.on_resize = None

    def setPixmap(self, pixmap):
        self._original_pixmap = pixmap
        self.update_scaled_pixmap()
    
    def resizeEvent(self, event):
        try:
            self.update_scaled_pixmap()
            super().resizeEvent(event)
        except Exception as e:
            print(f"Error in DraggableLabel.resizeEvent: {e}")
        
    def update_scaled_pixmap(self):
        try:
            if self._original_pixmap and not self._original_pixmap.isNull() and self.width() > 1 and self.height() > 1:
                scaled = self._original_pixmap.scaled(
                    self.size(), 
                    Qt.IgnoreAspectRatio, 
                    Qt.SmoothTransformation
                )
                super().setPixmap(scaled)
        except Exception as e:
            print(f"Error scaling pixmap: {e}")

    def set_editing(self, editing):
        self.is_editing = editing
        self.update_style()
        
    def update_style(self):
        if self.is_editing:
            # Dashed border, semi-transparent background to see the area
            self.setStyleSheet("border: 2px dashed #FF4444; background-color: rgba(255, 68, 68, 30);")
        else:
            self.setStyleSheet("border: none; background-color: transparent;")
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        # Access the main window (CountdownWindow)
        main_window = self.window()
        
        if not self.is_editing:
            # Non-edit mode: Allow dragging the entire window
            if event.button() == Qt.LeftButton:
                self.dragging = True
                self.drag_start_global = event.globalPos()
                self.window_start_pos = main_window.frameGeometry().topLeft()
            # Pass event to parent (CountdownWindow) for context menu etc.
            super().mousePressEvent(event)
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
                self.drag_start_global = event.globalPos()
                self.initial_global_pos = self.mapToGlobal(QPoint(0,0))

    def mouseMoveEvent(self, event):
        main_window = self.window()
        
        if not self.is_editing:
             # Non-edit mode: Drag the window
            if self.dragging and event.buttons() & Qt.LeftButton:
                delta = event.globalPos() - self.drag_start_global
                main_window.move(self.window_start_pos + delta)
            return

        # Cursor update
        if self.rect().bottomRight() in QRect(event.pos() - QPoint(15, 15), QSize(30, 30)):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.SizeAllCursor)

        if self.dragging:
            delta = event.globalPos() - self.drag_start_global
            target_global = self.initial_global_pos + delta
            if self.parent():
                target_local = self.parent().mapFromGlobal(target_global)
                margin = 20
                mw = main_window.width()
                mh = main_window.height()
                new_x = max(margin, min(target_local.x(), mw - self.width() - margin))
                new_y = max(margin, min(target_local.y(), mh - self.height() - margin))
                self.move(new_x, new_y)
            
            # Update container to fit new digit position
            if hasattr(main_window, 'update_container_geometry'):
                main_window.update_container_geometry()
            
            # Ensure bounds call moved to mouseReleaseEvent to prevent crash/recursive loops
            
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
                    if ratio > 0.0001:
                        new_height = int(new_width / ratio)
                else:
                    new_width = int(new_height * ratio)
            
            self.resize(new_width, new_height)
            if self.on_resize:
                self.on_resize()
            
            # Update container to fit new digit size
            if hasattr(main_window, 'update_container_geometry'):
                main_window.update_container_geometry()
            
            # Ensure bounds call moved to mouseReleaseEvent

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        
        main_window = self.window()
        if hasattr(main_window, 'ensure_bounds'):
            main_window.ensure_bounds()
        
        main_window = self.window()
        if hasattr(main_window, 'ensure_bounds'):
            main_window.ensure_bounds()
            
        super().mouseReleaseEvent(event)


class ContainerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True) # Allow stylesheet to paint background/border
        self.setStyleSheet("border: 4px dashed #00BFFF; background-color: rgba(0, 191, 255, 40);")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.dragging = False
        self.resizing = False
        self.resize_edge = None # 'bottom-right', etc.
        self.drag_start_pos = QPoint()
        self.resize_start_pos = QPoint()
        self.initial_geometry = QRect()
        self.initial_digits_geo = []

    def mousePressEvent(self, event):
        main_window = self.window()
        if not hasattr(main_window, 'is_editing') or not main_window.is_editing:
            event.ignore() # Pass to parent (Window) for window drag
            return

        if event.button() == Qt.LeftButton:
            # Check for resize (bottom-right corner)
            if self.rect().bottomRight() in QRect(event.pos() - QPoint(20, 20), QSize(40, 40)):
                self.resizing = True
                self.resize_start_pos = event.globalPos()
                self.initial_geometry = self.geometry()
                # Capture initial state of all digits for scaling
                self.initial_digits_geo = [lbl.geometry() for lbl in main_window.digit_labels]
            else:
                self.dragging = True
                self.drag_start_global = event.globalPos()
                self.initial_global_pos = self.mapToGlobal(QPoint(0,0))
                # Store global positions of digits
                self.initial_digit_global_positions = [lbl.mapToGlobal(QPoint(0,0)) for lbl in main_window.digit_labels]

    def mouseMoveEvent(self, event):
        main_window = self.window()
        if not hasattr(main_window, 'is_editing') or not main_window.is_editing:
            return

        # Cursor
        if self.rect().bottomRight() in QRect(event.pos() - QPoint(20, 20), QSize(40, 40)):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.SizeAllCursor)

        if self.dragging:
            delta = event.globalPos() - self.drag_start_global
            target_global = self.initial_global_pos + delta
            if self.parent():
                target_local = self.parent().mapFromGlobal(target_global)
                margin = 10
                mw = main_window.width()
                mh = main_window.height()
                new_x = max(margin, min(target_local.x(), mw - self.width() - margin))
                new_y = max(margin, min(target_local.y(), mh - self.height() - margin))
                self.move(new_x, new_y)
                actual_global = self.parent().mapToGlobal(QPoint(new_x, new_y))
                actual_delta_global = actual_global - self.initial_global_pos
            
            # Move all digits by the same delta (using global logic)
            for i, lbl in enumerate(main_window.digit_labels):
                if i < len(self.initial_digit_global_positions):
                    t_global = self.initial_digit_global_positions[i] + actual_delta_global
                    t_local = main_window.central_widget.mapFromGlobal(t_global)
                    lbl.move(t_local)
            
            main_window.update() 
            
        elif self.resizing:
            delta = event.globalPos() - self.resize_start_pos
            
            new_w = max(50, self.initial_geometry.width() + delta.x())
            new_h = max(50, self.initial_geometry.height() + delta.y())
            
            keep_aspect_ratio = (event.modifiers() & Qt.ShiftModifier)
            if keep_aspect_ratio and self.initial_geometry.height() > 0:
                ratio = self.initial_geometry.width() / self.initial_geometry.height()
                if abs(delta.x()) > abs(delta.y()):
                    if ratio > 0.0001:
                        new_h = int(new_w / ratio)
                else:
                    new_w = int(new_h * ratio)
            margin = 10
            mw = main_window.width()
            mh = main_window.height()
            # Clamp size to available space without moving window
            max_w = max(50, mw - self.x() - margin)
            max_h = max(50, mh - self.y() - margin)
            new_w = min(new_w, max_w)
            new_h = min(new_h, max_h)
            self.resize(new_w, new_h)
            
            scale_x = new_w / self.initial_geometry.width()
            scale_y = new_h / self.initial_geometry.height()
            
            for i, lbl in enumerate(main_window.digit_labels):
                orig_geo = self.initial_digits_geo[i]
                
                # Calculate new position relative to container's top-left
                rel_x = orig_geo.x() - self.initial_geometry.x()
                rel_y = orig_geo.y() - self.initial_geometry.y()
                
                new_rel_x = rel_x * scale_x
                new_rel_y = rel_y * scale_y
                
                new_x = self.x() + int(new_rel_x)
                new_y = self.y() + int(new_rel_y)
                
                new_lbl_w = int(orig_geo.width() * scale_x)
                new_lbl_h = int(orig_geo.height() * scale_y)
                
                lbl.setGeometry(new_x, new_y, new_lbl_w, new_lbl_h)
            
            main_window.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
