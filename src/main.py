from gpio import listen_serial, select_button, get_selected_button, deselect_button
from prefController import load_pref, save_pref
from gui import init_pygame, draw_buttons, find_button_click
import pygame
import pyperclip
import tray
import gui

def open_gui():
    config = load_pref()
    init_pygame()
    pygame.key.set_repeat(300, 30)

    running = True
    while running:
        selected = get_selected_button()
        draw_buttons(config, selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                # Click inside the URL input field
                if gui.input_rect and gui.input_rect.collidepoint(mx, my):
                    gui.input_active = True
                else:
                    gui.input_active = False
                # Click on "Cancel"
                if gui.cancel_button_rect and gui.cancel_button_rect.collidepoint(mx, my):
                    gui.temp_config_type = None
                    gui.temp_config_value = None
                    gui.save_enabled = False
                    gui.save_clicked = False
                    deselect_button()
                    break
                
                # Click on "Save"
                if hasattr(gui, "save_button_rect") and gui.save_button_rect.collidepoint(mx, my):
                    config[selected] = {
                        "type": gui.temp_config_type or "none",
                        "value": gui.temp_config_value or ""
                    }
                    gui.temp_config_type = None
                    gui.temp_config_value = None
                    gui.save_enabled = False
                    gui.save_clicked = True
                    save_pref(config)
                    gui.save_clicked = False
                # Click on one of the 3 exclusive buttons (LINK, EXE, NONE)
                if selected and hasattr(gui, "type_button_rects"):
                    for name, rect in gui.type_button_rects.items():
                        if rect.collidepoint(mx, my):
                            button_type = name.lower()
                            gui.temp_config_type = button_type
                            if button_type == "none":
                                gui.temp_config_value = ""
                            else:
                                if gui.temp_config_value is None:
                                    gui.temp_config_value = config[selected].get("value", "")
                            gui.save_enabled = gui.is_dirty(selected, config)
                            break
                        
                # Click on "Browse"
                if selected and (gui.temp_config_type or config[selected]["type"]) == "exe":
                    if hasattr(gui, "browse_button_rect") and gui.browse_button_rect.collidepoint(mx, my):
                        from tkinter import filedialog
                        import tkinter as tk
                        import os
                        root = tk.Tk()
                        root.withdraw()  # Hide the main window
                        path = filedialog.askopenfilename(
                            title="Select Executable",
                            filetypes=[("Executable files", "*.exe")],
                            initialdir=os.path.expanduser("~")
                        )
                        if path:
                            gui.temp_config_value = path
                            gui.save_enabled = gui.is_dirty(selected, config)
                        root.destroy()
                # Click on one of the buttons 1-9
                btn = find_button_click(mx, my)
                if btn:
                    select_button(btn)
                    gui.temp_config_type = None
                    gui.temp_config_value = None
                    gui.save_enabled = gui.is_dirty(selected, config)
            
            # Text field handling for URL input
            elif event.type == pygame.KEYDOWN and gui.input_active:
                if event.key == pygame.K_BACKSPACE:
                    gui.temp_config_value = (gui.temp_config_value or "")[:-1]
                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Ctrl+V: paste from clipboard
                    clipboard_text = pyperclip.paste()
                    if clipboard_text:
                        gui.temp_config_value = (gui.temp_config_value or "") + clipboard_text
                elif event.key == pygame.K_a and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Ctrl+A → Select all (symbolic, no visual action)
                    pass  # nothing to do here (everything is already "selected")
                elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Ctrl+C → Copy entire field
                    if gui.temp_config_value:
                        pyperclip.copy(gui.temp_config_value)
                elif event.key == pygame.K_x and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Ctrl+X → Cut everything
                    if gui.temp_config_value:
                        pyperclip.copy(gui.temp_config_value)
                        gui.temp_config_value = ""
                        gui.save_enabled = gui.is_dirty(selected, config)        
                else:
                    char = event.unicode
                    if char.isprintable():
                        gui.temp_config_value = (gui.temp_config_value or "") + char
                gui.save_enabled = gui.is_dirty(selected, config)
    pygame.quit()
    
    # Signal the serial thread to reload config after GUI closes
    from gpio import signal_config_reload
    signal_config_reload()
    print("[GUI] Configuration changes applied to serial monitoring")

def start_serial_background():
    """Start serial listening in background thread with config reload capability"""
    import threading
    from gpio import listen_serial_with_reload
    
    # Start the enhanced serial listener that can reload config
    serial_thread = threading.Thread(target=listen_serial_with_reload, daemon=True)
    serial_thread.start()
    print("[MAIN] Serial monitoring started in background")

def main():
    print("StreamDeck V2 - Starting background service...")
    start_serial_background()
    # Run system tray (this blocks until quit)
    tray.create_tray_icon(open_gui)

if __name__ == "__main__":
    main()