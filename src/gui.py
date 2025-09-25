import pygame
import os
import sys
import tkinter as tk
from tkinter import simpledialog, filedialog
import webbrowser
from gpio import execute_action

def get_resource_path(relative_path):
    """Get the absolute path to a resource, works for PyInstaller bundles and source"""
    try:
        # If running from PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        
        # If running from source
        if __file__:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)
        
        # If running from installed app
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    except:
        return relative_path

# Global constants
FONT = None
SMALL_FONT = None
MEDIUM_FONT = None  # Add medium font for consistency
SCREEN = None

BTN_SIZE = 100
SPACING_X = 140
SPACING_Y = 120
MARGIN_Y = 20
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 650

# Configuration panel constants
CONFIG_PANEL_Y = 460
CONFIG_BTN_WIDTH = 120
CONFIG_BTN_HEIGHT = 40
CONFIG_BTN_SPACING = 20
CONFIG_INPUT_WIDTH = 540
CONFIG_INPUT_HEIGHT = 30

# UI state variables - properly initialized
cancel_button_rect = None
type_button_rects = {}
browse_button_rect = None
save_button_rect = None
input_rect = None

# Temporary configuration state
temp_config_type = None
temp_config_value = None

# UI interaction state
save_enabled = False
save_clicked = False
input_active = False

# Cursor variables for text input
cursor_visible = True
cursor_timer = 0
CURSOR_BLINK_RATE = 500  # milliseconds

def init_pygame():
    global FONT, SMALL_FONT, MEDIUM_FONT, SCREEN
    pygame.init()
    FONT = pygame.font.SysFont(None, 24)
    SMALL_FONT = pygame.font.SysFont(None, 16)
    MEDIUM_FONT = pygame.font.SysFont(None, 18)  # Create once, reuse everywhere
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("StreamDeck")
    
    # Set window icon using utility function
    try:
        from icon_utils import set_pygame_window_icon
        set_pygame_window_icon()
    except ImportError:
        print("[GUI WARNING] Icon utils not available, using fallback")
        # Fallback if icon_utils is not available
        try:
            icon_path = get_resource_path(os.path.join('assets', 'icon.ico'))
            if os.path.exists(icon_path):
                icon_surface = pygame.image.load(icon_path)
                pygame.display.set_icon(icon_surface)
                print(f"[GUI] Window icon loaded from: {icon_path}")
        except Exception as e:
            print(f"[GUI WARNING] Failed to load window icon: {e}")

def update_cursor():
    """Update cursor blink state"""
    global cursor_visible, cursor_timer
    current_time = pygame.time.get_ticks()
    if current_time - cursor_timer > CURSOR_BLINK_RATE:
        cursor_visible = not cursor_visible
        cursor_timer = current_time


def reset_ui_state():
    """Reset all UI state variables to ensure clean state"""
    global temp_config_type, temp_config_value, save_enabled, save_clicked, input_active
    global cancel_button_rect, type_button_rects, browse_button_rect, save_button_rect, input_rect
    
    temp_config_type = None
    temp_config_value = None
    save_enabled = False
    save_clicked = False
    input_active = False
    
    cancel_button_rect = None
    type_button_rects = {}
    browse_button_rect = None
    save_button_rect = None
    input_rect = None
    
    print("[GUI DEBUG] UI state reset")

def draw_buttons(config, selected=None):
    """
    Draw the main StreamDeck interface including:
    - 9 button grid (3x3)
    - Status text
    - Configuration panel (if a button is selected)
    """
    # Update cursor blink state
    update_cursor()
    
    SCREEN.fill((30, 30, 30))

    # === MAIN BUTTON GRID ===
    total_width = 3 * BTN_SIZE + 2 * (SPACING_X - BTN_SIZE)
    start_x = (SCREEN_WIDTH - total_width) // 2

    for i in range(9):
        key = f"BUTTON_{i+1}"
        x = start_x + (i % 3) * SPACING_X
        y = MARGIN_Y + (i // 3) * SPACING_Y

        # Button background
        pygame.draw.rect(SCREEN, (50, 50, 50), (x, y, BTN_SIZE, BTN_SIZE), border_radius=8)

        # Border (highlight selected button)
        if selected == key:
            border_color = (200, 120, 40)  # Orange for selected
        else:
            border_color = (200, 200, 200)  # Gray for normal

        pygame.draw.rect(SCREEN, border_color, (x, y, BTN_SIZE, BTN_SIZE), width=3, border_radius=8)

        # Button number
        num_text = FONT.render(str(i+1), True, (255, 255, 255))
        num_x = x + (BTN_SIZE - num_text.get_width()) // 2
        num_y = y + (BTN_SIZE - num_text.get_height()) // 2
        SCREEN.blit(num_text, (num_x, num_y))

    # === SEPARATOR LINE ===
    linea_y = MARGIN_Y + 3 * SPACING_Y + 5
    pygame.draw.line(SCREEN, (180, 180, 180), (start_x, linea_y), (start_x + total_width, linea_y), 2)

    # === STATUS TEXT ===
    if selected:
        text = f"Program button {selected[-1]}"
    else:
        text = "Click on a button to program it"

    text_render = MEDIUM_FONT.render(text, True, (255, 255, 255))
    text_area_y = linea_y + 10
    text_area_height = BTN_SIZE

    text_x = (SCREEN_WIDTH - text_render.get_width()) // 2
    text_y = text_area_y + (text_area_height - text_render.get_height()) // 2

    SCREEN.blit(text_render, (text_x, text_y))

    # === CONFIGURATION PANEL ===
    if selected:
        # Global variables for UI interaction
        global type_button_rects, cancel_button_rect, input_rect, browse_button_rect, save_button_rect
        global temp_config_type, temp_config_value
        
        # Get current or temporary configuration
        data = config.get(selected, {"type": "none", "value": ""})
        button_type = temp_config_type if temp_config_type is not None else data.get("type", "none")
        value = temp_config_value if temp_config_value is not None else data.get("value", "")

        # Draw action type buttons (LINK, EXE, NONE)
        options = ["LINK", "EXE", "NONE"]
        config_panel_y = CONFIG_PANEL_Y
        total_width = len(options) * CONFIG_BTN_WIDTH + (len(options) - 1) * CONFIG_BTN_SPACING
        config_start_x = (SCREEN_WIDTH - total_width) // 2
        type_button_rects = {}

        for i, name in enumerate(options):
            x = config_start_x + i * (CONFIG_BTN_WIDTH + CONFIG_BTN_SPACING)
            y = config_panel_y
            active = (name.lower() == button_type)
            color = (200, 120, 40) if active else (80, 80, 80)

            rect = pygame.Rect(x, y, CONFIG_BTN_WIDTH, CONFIG_BTN_HEIGHT)
            type_button_rects[name] = rect

            pygame.draw.rect(SCREEN, color, rect, border_radius=6)
            text = SMALL_FONT.render(name, True, (255, 255, 255))
            SCREEN.blit(text, text.get_rect(center=rect.center))

        config_panel_y += CONFIG_BTN_HEIGHT + 15

        # Draw input fields based on selected type
        if button_type == "link":
            # URL input field
            label = SMALL_FONT.render("ENTER URL:", True, (200, 200, 200))
            SCREEN.blit(label, (50, config_panel_y))

            config_panel_y += label.get_height() + 5

            input_rect = pygame.Rect(50, config_panel_y, CONFIG_INPUT_WIDTH, CONFIG_INPUT_HEIGHT)
            
            # Input field background with focus indication
            if input_active:
                pygame.draw.rect(SCREEN, (255, 255, 255), input_rect, border_radius=4)
                pygame.draw.rect(SCREEN, (200, 120, 40), input_rect, width=2, border_radius=4)  # Orange border when active
            else:
                pygame.draw.rect(SCREEN, (240, 240, 240), input_rect, border_radius=4)
                pygame.draw.rect(SCREEN, (180, 180, 180), input_rect, width=1, border_radius=4)  # Gray border when inactive

            # Text content with placeholder
            text_x = input_rect.x + 5
            text_y = input_rect.y + 7
            
            if value and value.strip():
                # Display actual text
                color_text = (0, 0, 0)
                render_text = SMALL_FONT.render(value, True, color_text)
                SCREEN.blit(render_text, (text_x, text_y))
                text_width = render_text.get_width()
            else:
                # Display placeholder text
                if input_active:
                    # Show empty field when active
                    render_text = SMALL_FONT.render("", True, (0, 0, 0))
                    text_width = 0
                else:
                    # Show placeholder when inactive
                    placeholder = "https://example.com"
                    color_placeholder = (150, 150, 150)
                    render_text = SMALL_FONT.render(placeholder, True, color_placeholder)
                    SCREEN.blit(render_text, (text_x, text_y))
                    text_width = 0  # Don't show cursor for placeholder

            # Draw cursor if input is active
            if input_active and cursor_visible:
                cursor_x = text_x + text_width
                cursor_y = text_y
                cursor_height = SMALL_FONT.get_height()
                pygame.draw.line(SCREEN, (0, 0, 0), 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + cursor_height), 2)

            config_panel_y += 40

        elif button_type == "exe":
            # Executable file browser
            label = SMALL_FONT.render("SELECT EXECUTABLE FILE:", True, (200, 200, 200))
            SCREEN.blit(label, (50, config_panel_y))

            config_panel_y += label.get_height() + 5
            
            # Browse button with hover effect
            browse_rect = pygame.Rect(50, config_panel_y, 100, 30)
            
            # Check if mouse is over the button (basic hover effect)
            mouse_pos = pygame.mouse.get_pos()
            is_hover = browse_rect.collidepoint(mouse_pos)
            
            if is_hover:
                pygame.draw.rect(SCREEN, (220, 140, 60), browse_rect, border_radius=5)  # Lighter on hover
            else:
                pygame.draw.rect(SCREEN, (200, 120, 40), browse_rect, border_radius=5)  # Normal color
                
            btn_text = SMALL_FONT.render("BROWSE", True, (255, 255, 255))
            SCREEN.blit(btn_text, btn_text.get_rect(center=browse_rect.center))
            browse_button_rect = browse_rect
            
            # Show selected file path or prompt
            if value and value.strip():
                import os
                # Display the selected file information
                filename = os.path.basename(value)
                full_path = value
                
                # Create a display area for the path
                path_display_y = config_panel_y + 35
                path_label = SMALL_FONT.render("Selected:", True, (150, 150, 150))
                SCREEN.blit(path_label, (160, config_panel_y + 8))
                
                # Show filename prominently
                filename_text = SMALL_FONT.render(filename, True, (50, 150, 50))  # Green for selected file
                SCREEN.blit(filename_text, (220, config_panel_y + 8))
                
                # Show full path below in smaller text
                if len(full_path) > 65:  # Truncate long paths
                    display_path = "..." + full_path[-62:]
                else:
                    display_path = full_path
                    
                path_text = SMALL_FONT.render(display_path, True, (100, 100, 100))
                SCREEN.blit(path_text, (50, path_display_y))
                
                config_panel_y += 20  # Extra space for path display
            else:
                # Show prompt when no file is selected
                prompt_text = SMALL_FONT.render("No file selected", True, (150, 150, 150))
                SCREEN.blit(prompt_text, (160, config_panel_y + 8))
            
            config_panel_y += 40

        # Draw Cancel and Save buttons
        button_y = config_panel_y + 20
        total_button_width = 80 + 20 + 80
        button_start_x = (SCREEN_WIDTH - total_button_width) // 2
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Cancel button with hover effect
        cancel_button_rect = pygame.Rect(button_start_x, button_y, 60, 30)
        is_cancel_hover = cancel_button_rect.collidepoint(mouse_pos)
        
        if is_cancel_hover:
            cancel_color = (220, 140, 60)  # Lighter on hover
        else:
            cancel_color = (200, 120, 40)  # Normal color
            
        cancel_text = SMALL_FONT.render("Cancel", True, cancel_color)
        cancel_rect = cancel_text.get_rect()
        SCREEN.blit(cancel_text, (button_start_x, button_y + (30 - cancel_rect.height) // 2))

        # Save button with improved state handling
        save_rect = pygame.Rect(button_start_x + 100, button_y, 80, 30)
        is_save_hover = save_rect.collidepoint(mouse_pos)

        # Determine save button color based on state
        if save_clicked:
            color_save = (100, 200, 100)  # Green when saving
            save_text_content = "Saving..."
        elif save_enabled:
            if is_save_hover:
                color_save = (220, 140, 60)  # Lighter orange on hover when enabled
            else:
                color_save = (200, 120, 40)  # Orange when changes detected
            save_text_content = "Save"
        else:
            color_save = (100, 100, 100)  # Gray when disabled
            save_text_content = "Save"

        # Draw save button background
        pygame.draw.rect(SCREEN, color_save, save_rect, border_radius=5)
        
        # Add border to show when button is enabled
        if save_enabled and not save_clicked:
            pygame.draw.rect(SCREEN, (255, 255, 255), save_rect, width=1, border_radius=5)

        # Render save button text
        text_color = (255, 255, 255) if save_enabled or save_clicked else (150, 150, 150)
        save_text = SMALL_FONT.render(save_text_content, True, text_color)
        text_rect = save_text.get_rect(center=save_rect.center)
        SCREEN.blit(save_text, text_rect)

        save_button_rect = save_rect

    pygame.display.flip()


def is_dirty(selected, config):
    """Check if current button configuration has unsaved changes"""
    global temp_config_type, temp_config_value
    
    if not selected:
        return False

    # Get current saved configuration
    current = config.get(selected, {"type": "none", "value": ""})
    
    # Get the current temporary state (what user has entered)
    current_type = temp_config_type if temp_config_type is not None else current.get("type", "none")
    current_value = temp_config_value if temp_config_value is not None else current.get("value", "")
    
    # Normalize values for comparison
    saved_type = current.get("type", "none")
    saved_value = current.get("value", "")
    
    # Handle None values properly
    if current_value is None:
        current_value = ""
    if saved_value is None:
        saved_value = ""
    
    # Check if there are actual changes
    type_changed = current_type != saved_type
    value_changed = str(current_value).strip() != str(saved_value).strip()
    
    # Debug logging for troubleshooting
    if type_changed or value_changed:
        print(f"[GUI DEBUG] Button {selected} dirty - Type: {saved_type} -> {current_type}, Value: '{saved_value}' -> '{current_value}'")
    
    return type_changed or value_changed


def find_button_click(mx, my):
    total_width = 3 * BTN_SIZE + 2 * (SPACING_X - BTN_SIZE)
    start_x = (SCREEN_WIDTH - total_width) // 2

    for i in range(9):
        x = start_x + (i % 3) * SPACING_X
        y = MARGIN_Y + (i // 3) * SPACING_Y
        if x <= mx <= x + BTN_SIZE and y <= my <= y + BTN_SIZE:
            return f"BUTTON_{i+1}"
    return None


def configure_button(button_key, config):
    root = tk.Tk()
    root.title(f"Configure {button_key}")
    
    # Set window icon (if available)
    try:
        from icon_utils import set_tkinter_window_icon
        set_tkinter_window_icon(root)
    except ImportError:
        # Fallback if icon_utils is not available
        try:
            icon_path = get_resource_path(os.path.join('assets', 'icon.ico'))
            if os.path.exists(icon_path):
                root.iconbitmap(default=icon_path)
        except:
            pass  # Ignore if icon file doesn't exist

    choice_var = tk.StringVar(root)
    choice_var.set(config[button_key]["type"])

    value_var = tk.StringVar(root)
    value_var.set(config[button_key].get("value", ""))

    def update_value_widget(button_type):
        for widget in root.pack_slaves():
            if getattr(widget, "is_value_widget", False):
                widget.destroy()

        if button_type == "link":
            tk.Label(root, text="Enter URL:").pack()
            entry = tk.Entry(root, width=50, textvariable=value_var)
            entry.pack()
            entry.is_value_widget = True

            tk.Button(root, text="Test Action", command=lambda: webbrowser.open(value_var.get())).pack()
            tk.Button(root, text="Save", command=save).pack()

        elif button_type == "exe":
            def open_file():
                path = filedialog.askopenfilename(title="Select executable file")
                if path:
                    value_var.set(path)

            tk.Button(root, text="Choose .exe file", command=open_file).pack()
            lbl_file = tk.Label(root, textvariable=value_var)
            lbl_file.pack()
            lbl_file.is_value_widget = True

            tk.Button(root, text="Test Action", command=lambda: execute_action({"type": "exe", "value": value_var.get()})).pack()
            tk.Button(root, text="Save", command=save).pack()

    def save():
        button_type = choice_var.get()
        val = value_var.get()
        config[button_key] = {"type": button_type, "value": val} if button_type != "none" else {"type": "none", "value": ""}
        root.destroy()

    tk.Label(root, text="Select action type:").pack()
    tk.OptionMenu(root, choice_var, "link", "exe", "none", command=update_value_widget).pack()
    update_value_widget(choice_var.get())

    root.mainloop()
