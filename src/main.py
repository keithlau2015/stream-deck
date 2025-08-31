from gpio import listen_serial, select_button, get_selected_button, deselect_button
from prefController import load_pref, save_pref
from gui import init_pygame, draw_buttons, find_button_click
import pygame
import pyperclip
import tray
import gui

def open_gui():
    """Open the button preferences GUI with proper error handling and cleanup"""
    try:
        print("[GUI] Starting button preferences GUI...")
        
        # Load configuration with error handling
        try:
            config = load_pref()
        except Exception as e:
            print(f"[GUI ERROR] Failed to load preferences: {e}")
            return
        
        # Clean up any existing pygame instance
        try:
            pygame.quit()
        except:
            pass  # Ignore if pygame wasn't initialized
        
        # Initialize pygame with error handling
        try:
            init_pygame()
            pygame.key.set_repeat(300, 30)
        except Exception as e:
            print(f"[GUI ERROR] Failed to initialize pygame: {e}")
            return

        running = True
        while running:
            try:
                selected = get_selected_button()
                draw_buttons(config, selected)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
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
                            try:
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
                            except Exception as e:
                                print(f"[GUI ERROR] Failed to save preferences: {e}")
                                
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
                                try:
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
                                except Exception as e:
                                    print(f"[GUI ERROR] Failed to open file dialog: {e}")
                                    
                        # Click on one of the buttons 1-9
                        btn = find_button_click(mx, my)
                        if btn:
                            select_button(btn)
                            gui.temp_config_type = None
                            gui.temp_config_value = None
                            gui.save_enabled = gui.is_dirty(selected, config)
                    
                    # Text field handling for URL input
                    elif event.type == pygame.KEYDOWN and gui.input_active:
                        try:
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
                        except Exception as e:
                            print(f"[GUI ERROR] Keyboard input error: {e}")
                            
            except Exception as e:
                print(f"[GUI ERROR] Error in main loop: {e}")
                # Continue running even if there's an error in the loop
                continue
                
    except Exception as e:
        print(f"[GUI ERROR] Critical error in GUI: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always clean up pygame
        try:
            pygame.quit()
            print("[GUI] Pygame cleaned up")
        except:
            pass
        
        # Signal the serial thread to reload config after GUI closes
        try:
            from gpio import signal_config_reload
            signal_config_reload()
            print("[GUI] Configuration changes applied to serial monitoring")
        except Exception as e:
            print(f"[GUI ERROR] Failed to signal config reload: {e}")

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
    
    # Check for command line parameters
    import sys
    if len(sys.argv) > 1:
        if "--config-gpio" in sys.argv:
            print("[MAIN] Opening GPIO configuration GUI...")
            try:
                from gpioController import open_gpio_config_gui
                open_gpio_config_gui()
                return  # Exit after GPIO config
            except Exception as e:
                print(f"[MAIN ERROR] Failed to open GPIO configuration: {e}")
                return
        elif "--config-buttons" in sys.argv:
            print("[MAIN] Opening button preferences GUI...")
            try:
                open_gui()
                return  # Exit after button config
            except Exception as e:
                print(f"[MAIN ERROR] Failed to open button configuration: {e}")
                return
    
    # Normal startup - start background service and tray
    start_serial_background()
    # Run system tray (this blocks until quit)
    tray.create_tray_icon(open_gui)

if __name__ == "__main__":
    main()