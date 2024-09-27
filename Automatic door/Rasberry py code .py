import socket
import time
import os
import RPi.GPIO as GPIO
import pio
import Ports

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))  # Bind to all interfaces on port 12345
server_socket.listen(1)
print("Server listening on port 12345...")

# Accept a client connection
conn, addr = server_socket.accept()
print(f"Connection from {addr}")

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 11
LCD_D4 = 12
LCD_D5 = 13
LCD_D6 = 15
LCD_D7 = 16
pir_pin = 29
buzzer_pin = 31
switch_pin = 32
motor_pin1 = 33
motor_pin2 = 36
motor_pin3 = 35
motor_pin4 = 38
piezout1 = 37
piezout2 = 40
piezin1 = 3
piezin2 = 5

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
delay = 1

GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(switch_pin, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(motor_pin1, GPIO.OUT)
GPIO.setup(motor_pin2, GPIO.OUT)
GPIO.setup(motor_pin3, GPIO.OUT)
GPIO.setup(motor_pin4, GPIO.OUT)
GPIO.setup(piezin1, GPIO.IN)
GPIO.setup(piezin2, GPIO.IN)
GPIO.setup(piezout1, GPIO.IN)
GPIO.setup(piezout2, GPIO.IN)

LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    GPIO.output(LCD_RS, mode)
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)
    lcd_toggle_enable()
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)
    lcd_toggle_enable()

def lcd_toggle_enable():
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

lcd_init()
lcd_string("..Welcome..", LCD_LINE_1)
time.sleep(0.2)
lcd_byte(0x01, LCD_CMD)
lcd_string("Face Detection", LCD_LINE_1)
lcd_string("System..", LCD_LINE_2)
time.sleep(0.3)

try:
    while True:
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Press Bell...", LCD_LINE_1)
        time.sleep(0.2)
        switch_data = GPIO.input(switch_pin)
        time.sleep(0.2)
        if not switch_data:
            conn.sendall(b'a')  # Send bell pressed signal
            GPIO.output(buzzer_pin, True)
            time.sleep(0.2)
            GPIO.output(buzzer_pin, False)
            print("Bell pressed, waiting for data...")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received data: {data.decode('utf-8')}")
                if data == b'1':
                    if GPIO.input(piezout1) == 1 and GPIO.input(piezout2) == 0:
                        lcd_byte(0x01, LCD_CMD)
                        lcd_string("Valid Person", LCD_LINE_1)
                        lcd_string("Door Open...", LCD_LINE_2)
                        GPIO.output(motor_pin1, False)
                        GPIO.output(motor_pin2, True)
                        time.sleep(0.2)
                        GPIO.output(motor_pin1, False)
                        GPIO.output(motor_pin2, False)
                        while GPIO.input(piezout1) == 1 and GPIO.input(piezout2) == 0:
                            if GPIO.input(piezin1) == 0:
                                print('waiting for the person to pass')
                            lcd_byte(0x01, LCD_CMD)
                            lcd_string("Waiting person", LCD_LINE_1)
                            lcd_string("to enter...", LCD_LINE_2)
                            time.sleep(0.2)
                            if GPIO.input(piezin1) == 1:
                                lcd_byte(0x01, LCD_CMD)
                                lcd_string('person entered', LCD_LINE_1)
                                time.sleep(0.2)
                                break
                        lcd_byte(0x01, LCD_CMD)
                        lcd_string("Closing...", LCD_LINE_1)
                        GPIO.output(motor_pin1, True)
                        GPIO.output(motor_pin2, False)
                        time.sleep(0.2)
                        GPIO.output(motor_pin1, False)
                        GPIO.output(motor_pin2, False)
                        break
                    elif GPIO.input(piezout1) == 1 and GPIO.input(piezout2) == 1:
                        lcd_byte(0x01, LCD_CMD)
                        lcd_string("Valid Person", LCD_LINE_1)
                        lcd_string("Car Door Opening", LCD_LINE_2)
                        GPIO.output(motor_pin3, False)
                        GPIO.output(motor_pin4, True)
                        time.sleep(0.2)
                        GPIO.output(motor_pin3, False)
                        GPIO.output(motor_pin4, False)
                        while GPIO.input(piezout1) == 1 and GPIO.input(piezout2) == 1:
                            if GPIO.input(piezin2) == 0:
                                print('waiting for the car to pass')
                            lcd_byte(0x01, LCD_CMD)
                            lcd_string("Waiting vehicle", LCD_LINE_1)
                            lcd_string("to enter", LCD_LINE_2)
                            time.sleep(0.2)
                            if GPIO.input(piezin2) == 1:
                                lcd_byte(0x01, LCD_CMD)
                                lcd_string('Vehicle entered', LCD_LINE_1)
                                time.sleep(0.2)
                                break
                        lcd_byte(0x01, LCD_CMD)
                        lcd_string("Closing...", LCD_LINE_1)
                        GPIO.output(motor_pin3, True)
                        GPIO.output(motor_pin4, False)
                        time.sleep(0.2)
                        GPIO.output(motor_pin3, False)
                        GPIO.output(motor_pin4, False)
                        break
                elif data == b'0':
                    lcd_byte(0x01, LCD_CMD)
                    lcd_string("Unknown Person", LCD_LINE_1)
                    lcd_string("Door close", LCD_LINE_2)
                    time.sleep(0.2)
                    pir_data = GPIO.input(pir_pin)
                    time.sleep(0.2)
                    if pir_data:
                        conn.sendall(b'p')
                    else:
                        conn.sendall(b'q')
                    time.sleep(1)
                    break
                else:
                    print("No data received yet.")
                time.sleep(0.1)
        elif (GPIO.input(piezin1) == 1 and GPIO.input(piezin2) == 0):
            lcd_byte(0x01,LCD_CMD) # 000001 Clear display
            lcd_string("person detected",LCD_LINE_1)
            lcd_string("Opening",LCD_LINE_2)
            time.sleep(1)  
            GPIO.output(motor_pin1, True)
            GPIO.output(motor_pin2, False)
            time.sleep(1)
            GPIO.output(motor_pin1, False)
            GPIO.output(motor_pin2, False)
            while(GPIO.input(piezin1) == 1 and GPIO.input(piezin2) == 0):
                lcd_byte(0x01,LCD_CMD)
                lcd_string("Waiting person",LCD_LINE_1)
                lcd_string("to exit",LCD_LINE_2)
                time.sleep(0.5)
            lcd_byte(0x01,LCD_CMD)
            lcd_string("Closing...",LCD_LINE_1)
            GPIO.output(motor_pin1, False)
            GPIO.output(motor_pin2, True)
            time.sleep(0.5)
            GPIO.output(motor_pin1, False)
            GPIO.output(motor_pin2, False)  
        elif (GPIO.input(piezin1) == 1 and GPIO.input(piezin1) == 1):
            lcd_byte(0x01,LCD_CMD) # 000001 Clear display
            lcd_string("Vehicle detected",LCD_LINE_1)
            lcd_string("Opening",LCD_LINE_2)
            time.sleep(0.5)  
            GPIO.output(motor_pin3, True)
            GPIO.output(motor_pin4, False)
            time.sleep(1)
            GPIO.output(motor_pin3, False)
            GPIO.output(motor_pin4, False)
            while(GPIO.input(piezin1) == 1 and GPIO.input(piezin2) == 1):
                lcd_byte(0x01,LCD_CMD)
                lcd_string("Waiting vehicle",LCD_LINE_1)
                lcd_string("to exit",LCD_LINE_2)
                time.sleep(0.5)
            lcd_byte(0x01,LCD_CMD)
            lcd_string("Closing...",LCD_LINE_1)
            GPIO.output(motor_pin3, False)
            GPIO.output(motor_pin4, True)
            time.sleep(1)
            GPIO.output(motor_pin1, False)
            GPIO.output(motor_pin2, False)        
