# /// script
# dependencies = [
#   "pystray",
#   "pillow",
# ]
# ///

import pystray
from PIL import Image, ImageDraw
import time
import threading
import sys
import os

def create_image(color):
    # Generate an image with a colored square
    width = 64
    height = 64

    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # If color is None, return just the transparent background
    if color is None:
        return image
        
    dc = ImageDraw.Draw(image)
    
    # Draw a square (same size/location for all colors)
    dc.rectangle((8, 8, 56, 56), fill=color)

    return image

def sequence_logic(icon):
    # 1. Blue square for 3 seconds
    print("State 1: Blue for 3s")
    icon.icon = create_image("blue")
    time.sleep(3)
    
    if not icon._running: return

    # 2. Red square for 2 seconds (Blinking)
    print("State 2: Red (Blinking) for 2s")
    
    # Blink logic: Toggle every 0.25s for 2 seconds -> 8 frames
    end_time = time.time() + 2.0
    is_red = True
    
    while time.time() < end_time:
        if not icon._running: return
        
        if is_red:
            icon.icon = create_image("red")
        else:
            # Show empty/transparent image
            icon.icon = create_image(None) 
            
        is_red = not is_red
        time.sleep(0.25)
    
    if not icon._running: return

    # 3. Blue square for 3 seconds
    print("State 3: Blue for 3s")
    icon.icon = create_image("blue")
    time.sleep(3)
    
    # 4. Quit
    print("Sequence complete - quitting")
    icon.stop()
    os._exit(0)

def main():
    # Initial icon (starts blue)
    icon = pystray.Icon("notification_icon", create_image("blue"), "Notification")
    
    # Run the sequence in a separate thread
    t = threading.Thread(target=sequence_logic, args=(icon,))
    t.daemon = True
    t.start()
    
    print("Starting notification sequence...")
    icon.run()

if __name__ == "__main__":
    main()