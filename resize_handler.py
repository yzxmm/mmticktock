from PyQt5.QtCore import Qt, QRect
from layout_helper import LayoutHelper

class ResizeHandler:
    @staticmethod
    def handle_global_resize(window, event):
        delta = event.globalPos() - window.window_resize_start_pos
        mode = getattr(window, 'resize_mode', 'bottom-right')
        
        # Calculate new size based on mode
        new_w = window.initial_window_size.width()
        new_h = window.initial_window_size.height()
        
        if mode == 'bottom-right':
            new_w = max(100, window.initial_window_size.width() + delta.x())
            new_h = max(50, window.initial_window_size.height() + delta.y())
        elif mode == 'right':
            new_w = max(100, window.initial_window_size.width() + delta.x())
            # Height remains, but allow Shift for aspect ratio if wanted (usually right handle just changes width, but for aspect ratio we might force height)
            # Standard behavior: Right handle changes width.
        elif mode == 'bottom':
            new_h = max(50, window.initial_window_size.height() + delta.y())
            
        # Shift Aspect Ratio Logic
        if (event.modifiers() & Qt.ShiftModifier) and window.initial_window_size.height() > 0:
            ratio = window.initial_window_size.width() / window.initial_window_size.height()
            
            if mode == 'bottom-right':
                if abs(delta.x()) > abs(delta.y()): new_h = int(new_w / ratio)
                else: new_w = int(new_h * ratio)
            elif mode == 'right':
                # Force height to match width change
                new_h = int(new_w / ratio)
            elif mode == 'bottom':
                # Force width to match height change
                new_w = int(new_h * ratio)
        
        # New yellow rect size (which maps to window size)
        # r0 was removed from logic but kept for reference, but check if needed.
        # Actually window.initial_yellow_rect might not be set correctly in main.py changes?
        # Let's verify main.py logic too. But here r0 is not used.
        
        # Resize window directly
        window.global_resizing = True
        window.resize(new_w, new_h)
        window.bg_rect = QRect(0, 0, new_w, new_h)
        window.yellow_rect = QRect(0, 0, new_w, new_h)
        
        # We do NOT resize digits or container anymore.
        # Just update visuals.
        window.update()
