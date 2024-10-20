import traceback
import time
import os
from rpi_ws281x import PixelStrip, Color
from itertools import cycle
import signal
import sys
import threading
import logging

# LED strip configuration:
LED_COUNT = 210        # Number of LED pixels.
LED_PIN = 21         # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800kHz)
LED_DMA = 10         # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 150  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0      # Set to 1 for GPIOs 13, 19, 41, 45 or 53

# Create PixelStrip object
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()  # Initialize the library (must be called once before other functions)

def blink_leds(strip, led_indices, color, frequency_hz, stop_event):
    """Blink a group of LEDs with a specific color and frequency."""
    delay_s = 1.0 / frequency_hz
    while not stop_event.is_set():
        # Turn selected LEDs on
        for i in led_indices:
            strip.setPixelColor(i, color)
        strip.show()
        time.sleep(delay_s / 2)

        # Turn selected LEDs off
        for i in led_indices:
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(delay_s / 2)

def apply_predefined_settings(strip, predefined_settings, pause_duration, pause_after, long_pause_after, stop_event, overall_program_time):
    """Apply predefined indices, frequency, and color settings to LED groups with pauses and long pause."""
    setting_index = 0
    pause_counter = 0
    start_time = time.time()

    while not stop_event.is_set():
        # Check if overall program time has elapsed
        if time.time() - start_time >= overall_program_time:
            print("Overall program time elapsed. Shutting down LEDs.")
            break

        current_settings = predefined_settings[setting_index]

        # Start blinking LEDs with the current settings
        threads = []
        for group in current_settings:
            thread = threading.Thread(target=blink_leds, args=(
                strip, group["indices"], group["color"], group["frequency"], stop_event))
            threads.append(thread)
            thread.start()

        # Let the LEDs blink for the defined duration
        time.sleep(pause_duration)

        # Pause the blinking by stopping all threads
        stop_event.set()
        for thread in threads:
            thread.join()  # Ensure threads are stopped before changing settings

        # Reset the stop_event to allow threads to restart
        stop_event.clear()

        # Increment the pause counter
        pause_counter += 1

        # Determine whether to apply a regular pause or a long pause
        if pause_counter == long_pause_after:
            print(f"Long pause for 60 seconds...")
            
            time.sleep(10)  # 1-minute long pause
            
            pause_counter = 0  # Reset the pause counter
        else:
           
            print(f"tripping balls for {pause_counter * 10} seconds ")
            time.sleep(pause_after)

        # Move to the next set of settings
        setting_index = (setting_index + 1) % len(predefined_settings)

    # Turn off all LEDs after overall program time is reached
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

if __name__ == '__main__':
    try:
        # Predefined indices, frequency, and color settings for each group
        predefined_settings = [
            
            [
                {"indices": [0,1,2,25,26,27,28,29,30],             "frequency": 21, "color": Color(255, 255, 255)},   # Right top
                {"indices": [11,12,13,14,15,16,39,40,41],           "frequency": 6, "color": Color(255, 255, 255)},   # Left top
                {"indices": [90,91,105,104,119,118],                "frequency": 10, "color": Color(255, 255, 255)} , # Center
                {"indices": [179,180,181,182,183,184,207,208,209], "frequency": 21, "color": Color(255, 255, 255)} ,  # Left bottom
                {"indices": [168,169,170,195,194,193,196,197,198], "frequency": 6, "color": Color(255, 255, 255)}     # Right bottom
            ],
            [
                {"indices": [0,1,2,25,26,27,28,29,30],             "frequency": 6, "color": Color(255, 255, 255)},    # Right top
                {"indices": [11,12,13,14,15,16,39,40,41],          "frequency": 6, "color": Color(255, 255, 255)},    # Left top
                {"indices": [90,91,105,104,119,118],               "frequency": 6, "color": Color(255, 255, 255)} ,   # Center
                {"indices": [179,180,181,182,183,184,207,208,209], "frequency": 6, "color": Color(255, 255, 255)} ,   # Left bottom
                {"indices": [168,169,170,195,194,193,196,197,198], "frequency": 6, "color": Color(255, 255, 255)}     # Right bottom

            ],
            [
                {"indices": [0,1,2,25,26,27,28,29,30],             "frequency": 4, "color": Color(255, 255, 255)},   # Right top
                {"indices": [11,12,13,14,15,16,39,40,41],           "frequency": 4, "color": Color(0, 0, 0)},        # Left top
                {"indices": [90,91,105,104,119,118],                "frequency": 4, "color": Color(0, 0, 0)} ,       # Center
                {"indices": [179,180,181,182,183,184,207,208,209], "frequency": 4, "color": Color(255, 255, 255)} ,  # Left bottom
                {"indices": [168,169,170,195,194,193,196,197,198], "frequency": 4, "color": Color(0, 0, 0)}          # Right bottom
                
            ],
            [
                {"indices": [0,1,2,25,26,27,28,29,30],             "frequency": 6, "color": Color(255, 255, 255)},       # Right top
                {"indices": [11,12,13,14,15,16,39,40,41],           "frequency": 21, "color": Color(255, 255, 255)},     # Left top
                {"indices": [90,91,105,104,119,118],                "frequency": 10, "color": Color(255, 255, 255)} ,    # Center
                {"indices": [179,180,181,182,183,184,207,208,209], "frequency": 6, "color": Color(255, 255, 255)} ,      # Left bottom
                {"indices": [168,169,170,195,194,193,196,197,198], "frequency": 21, "color": Color(255, 255, 255)}       # Right bottom
                
            ],
            [
                {"indices": [0,1,2,25,26,27,28,29,30],             "frequency": 6, "color": Color(255, 255, 255)},    # Right top
                {"indices": [11,12,13,14,15,16,39,40,41],           "frequency": 6, "color": Color(255, 255, 255)},   # Left top
                {"indices": [90,91,105,104,119,118],                "frequency": 2, "color": Color(255, 255, 255)} ,  # Center
                {"indices": [179,180,181,182,183,184,207,208,209], "frequency": 4, "color": Color(255, 255, 255)} ,   # Left bottom
                {"indices": [168,169,170,195,194,193,196,197,198], "frequency": 4, "color": Color(255, 255, 255)}     # Right bottom
                
            ],
            [
                {"indices": [0,1,2,25,26,27,28,29,30],             "frequency": 5, "color": Color(0, 0, 0)},          # Right top
                {"indices": [11,12,13,14,15,16,39,40,41],           "frequency": 5, "color": Color(255, 255, 255)},   # Left top
                {"indices": [90,91,105,104,119,118],                "frequency": 5, "color": Color(0, 0, 0)} ,        # Center
                {"indices": [179,180,181,182,183,184,207,208,209], "frequency": 5, "color": Color(0, 0, 0)} ,         # Left bottom
                {"indices": [168,169,170,195,194,193,196,197,198], "frequency": 5, "color": Color(255, 255, 255)}     # Right bottom
                
            ]
        ]

         # Set the pause duration between LED changes (e.g., 10 minutes)
        pause_duration = 10  # duration of runtime in seconds
       
        pause_after = 0.1  # pause between runtime in seconds

        long_pause_after = 15  # number of pauses before a long pause  (required time (in secs)/ pause_duration)

        # Set the overall program time (e.g., 30 minutes)
        overall_program_time = 15 * 60  # (required time in minutes)

        # Create an event to signal when to stop the threads
        stop_event = threading.Event()

        # Start the process with pauses, long pause, and predefined settings changes
        apply_predefined_settings(strip, predefined_settings, pause_duration, pause_after, long_pause_after, stop_event, overall_program_time)

    except KeyboardInterrupt:
        # Signal all threads to stop
        stop_event.set()

        # Clear the strip on exit
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
