from machine import I2C, Pin, ADC
from machine_i2c_lcd import I2cLcd
import time
import sys

class Userinterface():
    def __init__(self):
        self.i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)
        self.lcd = I2cLcd(self.i2c, 0x27, 4, 20)
        self.options = ["Registrieren", "Anmelden", "Beenden"]
        self.selected_option = 0  # Start with the first option selected

        # Joystick-Pins
        self.joystick_x_pin = ADC(Pin(26))  # Replace with the actual pin number for X-axis
        self.joystick_y_pin = ADC(Pin(27))  # Replace with the actual pin number for Y-axis
        self.joystick_button_pin = Pin(14, Pin.IN, Pin.PULL_UP)  # Replace with the actual pin number for the button

        # Additional variables for blinking effect
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.selected_letter_index = 0
        self.current_word = ""
        self.is_login_mode = False
        self.blink_timer = time.ticks_ms()
        self.blink_interval = 500  # Adjust as needed

    def display_options(self):
        displayed_text = ""
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                displayed_text += ">" + option
            else:
                displayed_text += " " + option
            if i < len(self.options) - 1:
                displayed_text += "\n"
        return displayed_text

    def handle_joystick_input(self):
        x_value = self.joystick_x_pin.read_u16()
        y_value = self.joystick_y_pin.read_u16()
        button_state = self.joystick_button_pin.value()

        if self.is_login_mode:
            self.handle_keyboard_input(button_state, x_value)
        else:
            self.handle_option_selection(button_state, y_value)


    def handle_keyboard_input(self, button_state, x_value):
        current_time = time.ticks_ms()
    
        if current_time - self.blink_timer >= self.blink_interval:
            self.blink_timer = current_time
            self.lcd.move_to(1, 2)
            self.lcd.putstr(self.alphabet[self.selected_letter_index])
    
        if x_value > 61000 and self.selected_letter_index > 0:
            self.selected_letter_index -= 1
        elif x_value < 500 and self.selected_letter_index < len(self.alphabet) - 1:
            self.selected_letter_index += 1
    
        if button_state == 0:
            selected_letter = self.alphabet[self.selected_letter_index]
            self.current_word += selected_letter
    
            # Zeige den ausgewählten Buchstaben an der aktuellen Position an
            self.lcd.putstr(selected_letter)
    
            # Lösche das Zeichen links davon (falls möglich)
            if self.lcd.get_cursor_position()[0] > 0:
                self.lcd.move_to(self.lcd.get_cursor_position()[0] - 1, self.lcd.get_cursor_position()[1])
                self.lcd.putstr(' ')  # Oder ein Löschbefehl, falls von der Bibliothek unterstützt
    
            # Setze den Index des ausgewählten Buchstabens zurück
            self.selected_letter_index = 0
    
            while self.joystick_button_pin.value() == 0:
                time.sleep_ms(50)

    def handle_option_selection(self, button_state, y_value):
        if y_value > 61000 and self.selected_option > 0:
            self.selected_option -= 1
        elif y_value < 500 and self.selected_option < len(self.options) - 1:
            self.selected_option += 1

        if self.selected_option == 0:
            pass  # Füge die Logik für "Registrieren" hinzu
        elif self.selected_option == 1:
            if button_state == 0:
                self.start_login_mode()
        elif self.selected_option == 2:
            if button_state == 0:
                self.lcd.clear()
                sys.exit()

    def start_login_mode(self):
        self.lcd.clear()
        self.is_login_mode = True
        self.selected_letter_index = 0
        self.current_word = ''
        self.blink_timer = time.ticks_ms()

    def run(self):
        last_displayed_text = ""
        while True:
            self.handle_joystick_input()

            current_displayed_text = self.display_options()
            if last_displayed_text != current_displayed_text:
                self.lcd.clear()
                self.lcd.putstr(current_displayed_text)
                last_displayed_text = current_displayed_text

            time.sleep_ms(100)


if __name__ == "__main__":
    ui = Userinterface()
    ui.run()
