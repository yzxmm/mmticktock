from PyQt5.QtCore import QRect

class LayoutHelper:
    @staticmethod
    def update_container_geometry(window):
        """Update the blue box to wrap around all digits"""
        if not window.digit_labels:
            return
            
        min_x, min_y = 10000, 10000
        max_x, max_y = -10000, -10000
        
        for lbl in window.digit_labels:
            geo = lbl.geometry()
            min_x = min(min_x, geo.left())
            min_y = min(min_y, geo.top())
            max_x = max(max_x, geo.right())
            max_y = max(max_y, geo.bottom())
            
        # Add padding
        padding = 40
        window.digits_container.setGeometry(
            min_x - padding, 
            min_y - padding, 
            max_x - min_x + 2 * padding, 
            max_y - min_y + 2 * padding
        )
        if window.is_editing:
            window.digits_container.show()
            window.digits_container.lower()

    @staticmethod
    def ensure_bounds(window):
        """
        Expand window if digits are dragged out, and shift content if needed.
        
        [DISABLED] User requested to disable "Yellow-Blue Linkage".
        The window size will no longer automatically adjust to fit the digits.
        """
        pass
        # if not window.digit_labels:
        #     return
        # ... (rest of the logic commented out implicitly by 'pass' and not executing)

    @staticmethod
    def reset_layout(window):
        # Use current window size or sensible default
        w = window.width()
        h = window.height()
        window.resize(w, h)
        # Background follows window rect
        window.bg_rect = QRect(0, 0, w, h)
        
        # Calculate max container size (90% of window)
        max_cont_w = int(w * 0.9)
        max_cont_h = int(h * 0.8)
        
        # Target digit aspect ratio (width / height) ~ 0.66 (2:3)
        target_ratio = 0.66
        num_digits = 5
        
        # padding inside container
        pad = 20
        
        available_w = max(50, max_cont_w - 2 * pad)
        available_h = max(50, max_cont_h - 2 * pad)
        
        # Calc based on width limit
        digit_w_by_width = available_w / num_digits
        digit_h_by_width = digit_w_by_width / target_ratio
        
        # Calc based on height limit
        digit_h_by_height = available_h
        digit_w_by_height = digit_h_by_height * target_ratio
        
        # Choose the one that fits both
        if digit_h_by_width <= available_h:
            digit_w = digit_w_by_width
            digit_h = digit_h_by_width
        else:
            digit_w = digit_w_by_height
            digit_h = digit_h_by_height
            
        digit_w = max(20, int(digit_w))
        digit_h = max(30, int(digit_h))
        
        inner_w = digit_w * num_digits
        inner_h = digit_h
        
        cont_w = inner_w + 2 * pad
        cont_h = inner_h + 2 * pad
        
        start_x = (w - cont_w) // 2
        start_y = (h - cont_h) // 2
        
        for i, lbl in enumerate(window.digit_labels):
            lbl.setGeometry(
                start_x + pad + i * digit_w, 
                start_y + pad, 
                digit_w, 
                digit_h
            )
        
        LayoutHelper.update_container_geometry(window)
        # Sync yellow to wrap blue - DECOUPLED
        # window.yellow_rect will be managed by ResizeHandler/Main as window rect
        if hasattr(window, 'yellow_rect'):
            window.yellow_rect = window.rect()
        window.save_config()
