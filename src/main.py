from gpio import listen_serial, select_button, get_selected_button, deselect_button
from prefController import load_pref, save_pref
from gui import init_pygame, draw_buttons, find_button_click
import pygame
import pyperclip
import tray
import gui
import os

def open_gui():
    """Open the button preferences GUI with proper error handling and cleanup"""
    try:
        print("[GUI] Starting button preferences GUI...")
        
        # Reset UI state to ensure clean start
        gui.reset_ui_state()
        
        # Load configuration with error handling
        try:
            config = load_pref()
            print(f"[GUI] Loaded configuration with {len(config)} buttons")
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
            # Add FPS clock for better performance
            clock = pygame.time.Clock()
            FPS = 30  # Limit to 30 FPS for better performance
        except Exception as e:
            print(f"[GUI ERROR] Failed to initialize pygame: {e}")
            return

        running = True
        last_selected = None
        needs_redraw = True
        
        while running:
            try:
                selected = get_selected_button()
                
                # Only redraw if something changed
                if selected != last_selected or needs_redraw:
                    draw_buttons(config, selected)
                    last_selected = selected
                    needs_redraw = False
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        # Click inside the URL input field
                        if gui.input_rect and gui.input_rect.collidepoint(mx, my):
                            if not gui.input_active:
                                gui.input_active = True
                                needs_redraw = True
                        else:
                            if gui.input_active:
                                gui.input_active = False
                                needs_redraw = True
                        # Click on "Cancel"
                        if gui.cancel_button_rect and gui.cancel_button_rect.collidepoint(mx, my):
                            print("[GUI DEBUG] Cancel button clicked")
                            gui.temp_config_type = None
                            gui.temp_config_value = None
                            gui.save_enabled = False
                            gui.save_clicked = False
                            gui.input_active = False
                            # Don't deselect button on cancel, just reset the configuration state
                            needs_redraw = True
                            print("[GUI DEBUG] Configuration cancelled")
                            break
                        
                        # Click on "Save"
                        if hasattr(gui, "save_button_rect") and gui.save_button_rect and gui.save_button_rect.collidepoint(mx, my) and gui.save_enabled:
                            try:
                                # Validate the configuration before saving
                                new_type = gui.temp_config_type or "none"
                                new_value = gui.temp_config_value or ""
                                
                                # Additional validation for specific types
                                if new_type == "link" and new_value.strip():
                                    if not (new_value.startswith("http://") or new_value.startswith("https://")):
                                        new_value = "https://" + new_value.strip()
                                elif new_type == "exe" and new_value.strip():
                                    if not os.path.exists(new_value):
                                        print(f"[GUI WARNING] Executable file not found: {new_value}")
                                
                                # Save the configuration
                                config[selected] = {
                                    "type": new_type,
                                    "value": new_value
                                }
                                
                                print(f"[GUI] Saving button {selected}: type={new_type}, value={new_value}")
                                
                                # Reset temporary state but keep button selected
                                gui.temp_config_type = None
                                gui.temp_config_value = None
                                gui.save_enabled = False
                                gui.save_clicked = True
                                gui.input_active = False
                                
                                # Save to file
                                save_pref(config)
                                
                                # Reset clicked state
                                gui.save_clicked = False
                                needs_redraw = True
                                
                                print(f"[GUI] Button {selected} configuration saved successfully")
                                
                            except Exception as e:
                                print(f"[GUI ERROR] Failed to save preferences: {e}")
                                gui.save_clicked = False
                                import traceback
                                traceback.print_exc()
                                
                        # Click on one of the 3 exclusive buttons (LINK, EXE, NONE)
                        if selected and hasattr(gui, "type_button_rects") and gui.type_button_rects:
                            for name, rect in gui.type_button_rects.items():
                                if rect and rect.collidepoint(mx, my):
                                    button_type = name.lower()
                                    old_type = gui.temp_config_type
                                    gui.temp_config_type = button_type
                                    
                                    print(f"[GUI DEBUG] Button type changed: {old_type} -> {button_type}")
                                    
                                    # Handle value based on button type
                                    if button_type == "none":
                                        gui.temp_config_value = ""
                                    else:
                                        # If switching from a different type or this is the first selection
                                        if gui.temp_config_value is None or old_type != button_type:
                                            # Load existing value from config if available
                                            current_config = config.get(selected, {"type": "none", "value": ""})
                                            if current_config.get("type") == button_type:
                                                gui.temp_config_value = current_config.get("value", "")
                                            else:
                                                gui.temp_config_value = ""
                                    
                                    # Update save button state
                                    gui.save_enabled = gui.is_dirty(selected, config)
                                    needs_redraw = True
                                    
                                    print(f"[GUI DEBUG] Save enabled: {gui.save_enabled}")
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
                                        needs_redraw = True  # Force redraw to show selected file immediately
                                        print(f"[GUI DEBUG] File selected: {os.path.basename(path)}")
                                    root.destroy()
                                except Exception as e:
                                    print(f"[GUI ERROR] Failed to open file dialog: {e}")
                                    
                        # Click on one of the buttons 1-9
                        btn = find_button_click(mx, my)
                        if btn:
                            current_selected = get_selected_button()
                            print(f"[GUI DEBUG] Button clicked: {btn}, currently selected: {current_selected}")
                            
                            # Only change selection if it's a different button
                            if btn != current_selected:
                                print(f"[GUI DEBUG] Selecting new button: {btn}")
                                select_button(btn)
                                
                                # Reset temporary configuration state when selecting a new button
                                gui.temp_config_type = None
                                gui.temp_config_value = None
                                gui.save_enabled = False
                                gui.input_active = False
                                
                                needs_redraw = True
                            else:
                                print(f"[GUI DEBUG] Button {btn} already selected, ignoring duplicate click")
                    
                    # Text field handling for URL input
                    elif event.type == pygame.KEYDOWN and gui.input_active:
                        try:
                            current_value = gui.temp_config_value or ""
                            
                            if event.key == pygame.K_BACKSPACE:
                                gui.temp_config_value = current_value[:-1]
                            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                                # Ctrl+V: paste from clipboard
                                try:
                                    clipboard_text = pyperclip.paste()
                                    if clipboard_text:
                                        gui.temp_config_value = current_value + clipboard_text
                                except Exception as clipboard_error:
                                    print(f"[GUI WARNING] Clipboard paste failed: {clipboard_error}")
                            elif event.key == pygame.K_a and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                                # Ctrl+A → Select all (symbolic, no visual action)
                                pass  # nothing to do here (everything is already "selected")
                            elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                                # Ctrl+C → Copy entire field
                                if current_value:
                                    try:
                                        pyperclip.copy(current_value)
                                    except Exception as clipboard_error:
                                        print(f"[GUI WARNING] Clipboard copy failed: {clipboard_error}")
                            elif event.key == pygame.K_x and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                                # Ctrl+X → Cut everything
                                if current_value:
                                    try:
                                        pyperclip.copy(current_value)
                                        gui.temp_config_value = ""
                                    except Exception as clipboard_error:
                                        print(f"[GUI WARNING] Clipboard cut failed: {clipboard_error}")      
                            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                                # Enter key deactivates input field
                                gui.input_active = False
                            elif event.key == pygame.K_ESCAPE:
                                # Escape key cancels input and restores original value
                                gui.input_active = False
                                current_config = config.get(selected, {"type": "none", "value": ""})
                                gui.temp_config_value = current_config.get("value", "")
                            else:
                                char = event.unicode
                                if char.isprintable():
                                    gui.temp_config_value = current_value + char
                            
                            # Update save button state after any change
                            gui.save_enabled = gui.is_dirty(selected, config)
                            needs_redraw = True
                            
                        except Exception as e:
                            print(f"[GUI ERROR] Keyboard input error: {e}")
                            import traceback
                            traceback.print_exc()
                            
            except Exception as e:
                print(f"[GUI ERROR] Error in main loop: {e}")
                # Continue running even if there's an error in the loop
                continue
            
            # Limit FPS for better performance
            clock.tick(FPS)
                
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
    print("StreamDeck - Starting background service...")
    
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