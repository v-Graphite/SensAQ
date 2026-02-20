import time
from sensors import read, read_bmp
import pygame
import RPi.GPIO as GPIO
import threading
import os

# ------------------------ GPIO ------------------------ #
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(17, GPIO.IN)

# ------------------------ Audio ------------------------ #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sound_path = os.path.join(BASE_DIR, "mixkit-vintage-warning-alarm-990.wav")
sound_alarm = None
try:
    pygame.mixer.init()
    sound_alarm = pygame.mixer.Sound(sound_path)
except Exception as e:
    print("Audio nicht verfügbar:", e)

# ------------------------ Display ------------------------ #

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
text_font = pygame .font.SysFont("Arial", 20)
text_font2 = pygame.font.SysFont("Arial", 100)
text_font3 = pygame.font.SysFont("Arial", 24)
text_font4 = pygame.font.SysFont("Arial", 44)
text_font5 = pygame.font.SysFont("Arial", 22)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img,(x,y))

# ------------------------ Status ------------------------ #

alarm_once = False
alarm_always = False
alarm_quit = False

last_bmp = 0
max_co2 = 0
blink_active = False

co2 = 0
relative_humidity = 0.0
bmp_temp = 0.0
bmp_pressure = 0.0

air_text = "W"
air_color = (255, 255, 255)

now = time.time()
air_color = (255, 255, 255)

width = 800
height = 480

# ------------------------ LED Blink Thread ------------------------ #

def blink_led():
    while True:
        if blink_active:
            GPIO.output(27, True)
            time.sleep(1)
            GPIO.output(27, False)
            time.sleep(1)
        else:
            GPIO.output(27, False)
            time.sleep(0.1)

threading.Thread(target=blink_led, daemon=True).start()

# ------------------------ MAIN ------------------------ #

while True:
    screen.fill((0,0,0))
    
    # --- Sensoren lesen --- #
    v = read()
    if v:
        co2, relative_humidity = v
        print(co2, relative_humidity)
        if co2 > max_co2:
            max_co2 = co2
        # --- AQ text, color, LED --- #
        if co2 < 400:
            air_text = "Air Quality - Outdoor Level"
            air_color = (0, 200, 0)
            GPIO.output(27, False)
        elif co2 < 800:
            air_text = "Air Quality - Excellent"
            air_color = (0, 255, 0)
            GPIO.output(27, False)
        elif co2 < 1000:
            air_text = "Air Quality - Good"
            air_color = (150, 255, 0)
            GPIO.output(27, False)
        elif co2 < 1400:
            air_text = "Air Quality - Moderate"
            air_color = (255, 200, 0) 
            GPIO.output(27, False)
        elif co2 < 2000:
            air_text = "Air Quality - Poor"
            air_color = (255, 100, 0) 
            GPIO.output(27, True)

        elif co2 <3000: 
            air_text = "Air Quality - Very Poor"
            air_color = (255, 0, 0)
            blink_active = False

        else: 
            air_text = "Air Quality - Very Poor"
            air_color = (255, 0, 0)
            blink_active = True
        # --- Einmaliger Alarm ab 2000 --- #
        if 2000 <= co2 < 3000:
            if not alarm_once:
                if sound_alarm:
                    sound_alarm.play()
                alarm_once = True
        else: 
            alarm_once = False
        # --- Button ---
        button_pressed = GPIO.input(17) == 0
        # Durchgehend Ton bis man den Button drückt ab 3000
        if co2 >= 3000 and not alarm_quit:
            if not alarm_always:
                if sound_alarm:
                    sound_alarm.play(loops=-1)
                alarm_always = True
        if button_pressed and alarm_always:
            if sound_alarm:
                sound_alarm.stop()
            alarm_always= False
            alarm_quit = True
    
        if co2 < 3000:
            alarm_quit = False

    draw_text(air_text, text_font, air_color, 100, 30)
    # --- BMP liest alle 60s ---
    if (now - last_bmp >= 60):
        now = time.time()
        x = read_bmp()
        if x: 
            bmp_temp, bmp_pressure = x 
            print(bmp_temp, bmp_pressure)
        last_bmp = now

    # UI zeichnen
    current_time = time.strftime("%H:%M") # Uhrzeit
    current_date = time.strftime("%d.%m.%Y") # Datum
    
    draw_text("SensAQ", text_font, (255, 255, 255), 700, 30)
    draw_text(current_time, text_font2, (255, 255, 255), 300, 100)
    draw_text(current_date, text_font, (255, 255, 255), 380, 200)
    pygame.draw.line(screen, (255, 255, 255), (0, 238), (800, 238), 4)

    # alle Sensorwerte perfekt nebeneinander
    bottom_start = height // 2
    section_width = width // 4
    #Sensorwerte 
    items = [
        ("CO2", f"{co2} ppm"),
        ("RH",  f"{relative_humidity:.1f} %"),
        ("T",   f"{bmp_temp:.1f} °C"),
        ("P",   f"{bmp_pressure:.1f} hPa"),
    ]
    # Spaltenbreite bestimmten
    for i in range(4):
        x_center = i * section_width + section_width // 2
    # Surface aus Text
        label_s = text_font3.render(items[i][0], True, (180,180,180))
        value_s = text_font4.render(items[i][1], True, (255,255,255))
    # Rechteck, damit der Text zentriert ist
        label_r = label_s.get_rect(center=(x_center, bottom_start + 60))
        value_r = value_s.get_rect(center=(x_center, bottom_start + 120))
    # Text zeichnen
        screen.blit(label_s, label_r)
        screen.blit(value_s, value_r)
    # Max Co2 in der ersten Spalte
        if i == 0:
            max_s = text_font5.render(f"Max: {max_co2} ppm", True, (150,150,150))
            max_r = max_s.get_rect(center=(x_center, bottom_start + 150))
            screen.blit(max_s, max_r)
    # Trennlinien zwischen den Spaltern
        if i < 3:
            pygame.draw.line(
                screen, (100,100,100),
                ((i+1)*section_width, bottom_start + 20),
                ((i+1)*section_width, height - 20),
                2
            )
    
    pygame.display.flip()
    time.sleep(0.01)
GPIO.cleanup()
pygame.quit()