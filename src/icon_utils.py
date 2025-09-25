"""
Icon utilities for StreamDeck application
统一的图标管理工具
"""

import os
import sys
from PIL import Image
import pygame


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


def find_icon_file():
    """Find the icon file from multiple possible locations"""
    possible_paths = []
    
    # Method 1: Using resource path function
    icon_path1 = get_resource_path(os.path.join('assets', 'icon.ico'))
    possible_paths.append(icon_path1)
    
    # Method 2: Relative to current working directory
    icon_path2 = os.path.join('assets', 'icon.ico')
    possible_paths.append(icon_path2)
    
    # Method 3: Relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path3 = os.path.join(os.path.dirname(script_dir), 'assets', 'icon.ico')
    possible_paths.append(icon_path3)
    
    # Method 4: If running from source
    if not getattr(sys, 'frozen', False):
        icon_path4 = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico')
        possible_paths.append(icon_path4)
    
    print(f"[ICON] Searching for icon in paths:")
    for i, path in enumerate(possible_paths, 1):
        exists = os.path.exists(path)
        print(f"[ICON]   {i}. {path} - {'EXISTS' if exists else 'NOT FOUND'}")
        if exists:
            return path
    
    print("[ICON] No icon file found in any location")
    return None


def set_tkinter_window_icon(window):
    """Set icon for a Tkinter window"""
    try:
        icon_path = find_icon_file()
        if icon_path:
            print(f"[ICON] Setting Tkinter window icon from: {icon_path}")
            # Check file size for debugging
            file_size = os.path.getsize(icon_path)
            print(f"[ICON] Icon file size: {file_size} bytes")
            
            window.iconbitmap(default=icon_path)
            print(f"[ICON] Tkinter window icon successfully set!")
            return True
        else:
            print("[ICON] No icon file found for Tkinter window")
    except Exception as e:
        print(f"[ICON WARNING] Failed to set Tkinter window icon: {e}")
        print(f"[ICON] Error details: {type(e).__name__}: {str(e)}")
        # Don't print full traceback by default to reduce noise
    return False


def set_pygame_window_icon():
    """Set icon for a Pygame window"""
    try:
        icon_path = find_icon_file()
        if icon_path:
            print(f"[ICON] Setting Pygame window icon from: {icon_path}")
            
            # Try direct loading first
            try:
                icon_surface = pygame.image.load(icon_path)
                pygame.display.set_icon(icon_surface)
                print(f"[ICON] Pygame window icon successfully set!")
                return True
            except Exception as direct_error:
                print(f"[ICON] Direct load failed: {direct_error}, trying PIL conversion")
                
                # Try converting via PIL for better ICO support
                from PIL import Image
                pil_image = Image.open(icon_path)
                # Convert to RGBA if needed
                if pil_image.mode != 'RGBA':
                    pil_image = pil_image.convert('RGBA')
                
                # Convert PIL image to pygame surface
                image_string = pil_image.tobytes()
                icon_surface = pygame.image.fromstring(image_string, pil_image.size, 'RGBA')
                pygame.display.set_icon(icon_surface)
                print(f"[ICON] Pygame window icon set via PIL conversion!")
                return True
        else:
            print("[ICON] No icon file found for Pygame window, creating fallback")
    except Exception as e:
        print(f"[ICON WARNING] Failed to set Pygame window icon: {e}")
        print("[ICON] Creating fallback icon for Pygame window")
        
    # Create a fallback icon for pygame
    try:
        icon_surface = pygame.Surface((32, 32))
        icon_surface.fill((200, 120, 40))  # Orange background
        # Draw a simple pattern
        pygame.draw.rect(icon_surface, (255, 255, 255), (8, 8, 16, 16))
        pygame.display.set_icon(icon_surface)
        print("[ICON] Pygame fallback window icon created")
        return True
    except Exception as fallback_error:
        print(f"[ICON WARNING] Failed to create fallback icon: {fallback_error}")
    
    return False


def load_pil_icon():
    """Load icon as PIL Image for tray usage"""
    try:
        icon_path = find_icon_file()
        if icon_path:
            print(f"[ICON] Loading PIL icon from: {icon_path}")
            return Image.open(icon_path)
    except Exception as e:
        print(f"[ICON WARNING] Failed to load PIL icon: {e}")
    
    # Create fallback PIL image
    print("[ICON] Creating fallback PIL icon")
    image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))  # Transparent background
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    
    # Draw a more modern looking icon
    # Background circle
    draw.ellipse([4, 4, 60, 60], fill=(45, 45, 45), outline=(255, 255, 255), width=2)
    
    # Draw a 3x3 grid pattern representing stream deck buttons
    for i in range(3):
        for j in range(3):
            x1 = 16 + i * 12
            y1 = 16 + j * 12
            x2 = x1 + 8
            y2 = y1 + 8
            # Alternate colors for a more interesting pattern
            color = (255, 140, 0) if (i + j) % 2 == 0 else (100, 180, 255)
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=(255, 255, 255), width=1)
    
    print("[ICON] Fallback PIL icon created successfully")
    return image
