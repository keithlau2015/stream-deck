import pygame
import os
import tkinter as tk
from tkinter import simpledialog, filedialog
import webbrowser
from gpio import execute_action

# Global constants
FONT = None
SMALL_FONT = None
SCREEN = None

BTN_SIZE = 100
SPACING_X = 140
SPACING_Y = 120
MARGIN_Y = 20
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 650

cancel_button_rect = None

temp_config_type = None
temp_config_value = None

save_enabled = False
save_clicked = False

input_active = False
input_rect = None

def init_pygame():
    global FONT, SMALL_FONT, SCREEN
    pygame.init()
    FONT = pygame.font.SysFont(None, 24)
    SMALL_FONT = pygame.font.SysFont(None, 16)
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ConsoleDeck V2")


def draw_buttons(config, selected=None):
    SCREEN.fill((30, 30, 30))

    btn_size = 100
    spacing_x = 140
    spacing_y = 120
    total_width = 3 * btn_size + 2 * (spacing_x - btn_size)
    start_x = (640 - total_width) // 2
    margin_y = 20

    for i in range(9):
        key = f"BUTTON_{i+1}"
        x = start_x + (i % 3) * spacing_x
        y = margin_y + (i // 3) * spacing_y

        # Button background
        pygame.draw.rect(SCREEN, (50, 50, 50), (x, y, btn_size, btn_size), border_radius=8)

        # Borders
        if selected == key:
            border_color = (200, 120, 40)
        else:
            border_color = (200, 200, 200) 

        pygame.draw.rect(SCREEN, border_color, (x, y, btn_size, btn_size), width=3, border_radius=8)

        # Central number
        num_text = FONT.render(str(i+1), True, (255, 255, 255))
        num_x = x + (btn_size - num_text.get_width()) // 2
        num_y = y + (btn_size - num_text.get_height()) // 2
        SCREEN.blit(num_text, (num_x, num_y))

    linea_y = margin_y + 3 * spacing_y + 5
    pygame.draw.line(SCREEN, (180, 180, 180), (start_x, linea_y), (start_x + total_width, linea_y), 2)

    font_18 = pygame.font.SysFont(None, 18)

    if selected:
        text = f"Program button {selected[-1]}"
    else:
        text = "Click on a button to program it"

    text_render = font_18.render(text, True, (255, 255, 255))
    text_area_y = linea_y + 10
    text_area_height = btn_size

    text_x = (640 - text_render.get_width()) // 2
    text_y = text_area_y + (text_area_height - text_render.get_height()) // 2

    SCREEN.blit(text_render, (text_x, text_y))

    if selected:
        draw_advanced_configurator(selected, config)

    pygame.display.flip()

def draw_advanced_configurator(selected, config):
    global type_button_rects, cancel_button_rect
    small_font = pygame.font.SysFont(None, 16)

    data = config.get(selected, {"type": "none", "value": ""})

    global temp_config_type, temp_config_value

    button_type = temp_config_type if temp_config_type is not None else data.get("type", "none")
    value = temp_config_value if temp_config_value is not None else data.get("value", "")

    options = ["LINK", "EXE", "NONE"]
    base_y = 460
    btn_width = 120
    btn_height = 40
    spacing = 20
    total_width = len(options) * btn_width + (len(options) - 1) * spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    type_button_rects = {}

    for i, name in enumerate(options):
        x = start_x + i * (btn_width + spacing)
        y = base_y
        active = (name.lower() == button_type)
        color = (200, 120, 40) if active else (80, 80, 80)

        rect = pygame.Rect(x, y, btn_width, btn_height)
        type_button_rects[name] = rect

        pygame.draw.rect(SCREEN, color, rect, border_radius=6)
        text = small_font.render(name, True, (255, 255, 255))
        SCREEN.blit(text, text.get_rect(center=rect.center))

    base_y += btn_height + 15

    if button_type == "link":
        label = small_font.render("ENTER URL:", True, (200, 200, 200))
        SCREEN.blit(label, (50, base_y))

        base_y += label.get_height() + 5

        global input_rect
        input_rect = pygame.Rect(50, base_y, 540, 30)
        pygame.draw.rect(SCREEN, (255, 255, 255), input_rect, border_radius=4)

        color_text = (0, 0, 0)
        text_url = value if value else ""
        render_text = small_font.render(text_url, True, color_text)
        SCREEN.blit(render_text, (input_rect.x + 5, input_rect.y + 7))

        base_y += 40

    elif button_type == "exe":
        label = small_font.render("SELECT EXECUTABLE FILE:", True, (200, 200, 200))
        SCREEN.blit(label, (50, base_y))

        base_y += label.get_height() + 5
        browse_rect = pygame.Rect(50, base_y, 100, 30)
        pygame.draw.rect(SCREEN, (200, 120, 40), browse_rect, border_radius=5)
        btn_text = small_font.render("BROWSE", True, (255, 255, 255))
        SCREEN.blit(btn_text, btn_text.get_rect(center=browse_rect.center))
        global browse_button_rect
        browse_button_rect = browse_rect
        
        base_y += 40


    # Cancel and Save buttons (layout only, actions elsewhere)
    button_y = base_y + 20
    total_button_width = 80 + 20 + 80
    start_x = (SCREEN_WIDTH - total_button_width) // 2

    cancel_text = small_font.render("Cancel", True, (200, 120, 40))
    cancel_rect = cancel_text.get_rect()
    SCREEN.blit(cancel_text, (start_x, button_y + (30 - cancel_rect.height) // 2))
    cancel_button_rect = pygame.Rect(start_x, button_y, 60, 30)

    save_rect = pygame.Rect(start_x + 100, button_y, 80, 30)

    if save_clicked:
        color_save = (200, 120, 40)  # standard orange (after click)
    elif save_enabled:
        color_save = (200, 120, 40)  # dark orange (modified)
    else:
        color_save = (100, 100, 100)  # disabled

    pygame.draw.rect(SCREEN, color_save, save_rect, border_radius=5)

    save_text = small_font.render("Save", True, (255, 255, 255))
    text_rect = save_text.get_rect(center=save_rect.center)
    SCREEN.blit(save_text, text_rect)

    # save global clickable area
    global save_button_rect
    save_button_rect = save_rect


def is_dirty(selected, config):
    global temp_config_type, temp_config_value
    if not selected:
        return False

    current = config.get(selected, {"type": "none", "value": ""})
    button_type = temp_config_type if temp_config_type is not None else current["type"]
    value = temp_config_value if temp_config_value is not None else current["value"]

    return button_type != current["type"] or value != current["value"]


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
