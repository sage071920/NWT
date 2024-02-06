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
        # Read analog values from the joystick
        x_value = self.joystick_x_pin.read_u16()
        y_value = self.joystick_y_pin.read_u16()

        # Determine joystick direction based on analog values
        # Add hysteresis to joystick input
        if y_value > 61000 and self.selected_option > 0:
            self.selected_option -= 1
        elif y_value < 500 and self.selected_option < len(self.options) - 1:
            self.selected_option += 1

        # Read the button state
        button_state = self.joystick_button_pin.value()

        # Exit the script only if the option is "Beenden" and the button is pressed
        if button_state == 0 and self.options[self.selected_option] == "Beenden":
            self.lcd.clear()
            self.lcd.putstr("shuting down 3")
            time.sleep(1)
            self.lcd.clear()
            self.lcd.putstr("shuting down 2")
            time.sleep(1)
            self.lcd.clear()
            self.lcd.putstr("shuting down 1")
            time.sleep(1)
            self.lcd.clear()  # Clear the display
            self.lcd.backlight_off()
            sys.exit()

        # Add additional logic based on button state if needed

    def run(self):
        last_displayed_text = ""
        while True:
            # Handle joystick input
            self.handle_joystick_input()

            # Check if the displayed text has changed
            current_displayed_text = self.display_options()
            if last_displayed_text != current_displayed_text:
                # Update the display
                self.lcd.clear()
                self.lcd.putstr(current_displayed_text)
                last_displayed_text = current_displayed_text

            # Add a delay to stabilize the display
            time.sleep_ms(100)

if __name__ == "__main__":
    ui = Userinterface()
    ui.run()
