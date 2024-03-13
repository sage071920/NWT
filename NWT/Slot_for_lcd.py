from machine import I2C, Pin, ADC
from machine_i2c_lcd import I2cLcd
import time
import sys
import random

class SlotMachine():

    def weighted_choice(self, choices, weights):
        total = sum(weights)
        r = random.uniform(0, total)
        current_sum = 0 
        for choice, weight in zip(choices, weights):
            current_sum += weight
            if r <= current_sum:
                return choice

    def __init__(self):
        self.joystick_x_pin = ADC(Pin(26))  
        self.joystick_y_pin = ADC(Pin(27))  
        self.joystick_button_pin = Pin(14, Pin.IN, Pin.PULL_UP)
        self.i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)
        self.lcd = I2cLcd(self.i2c, 0x27, 4, 20)
        self.symbols = ['🍒', '🍊', '🍇', '🔔', '🅱️','7️⃣']
        self.balance = 100
        self.x_value = self.joystick_x_pin.read_u16()
        self.y_value = self.joystick_y_pin.read_u16()
        self.button_state = self.joystick_button_pin.value() 
        self.number_sequence = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
        self.bet_amount = 0
        self.selected_letter_index = 0
        self.current_word = ''
        self.blink_timer = 0
        self.blink_interval = 500
        self.joystick_moved_left = False

    def handle_keyboard_input(self):
        self.lcd.putstr(f"Guthaben: {self.balance}")
        while True:
            time.sleep(0.25)
            joystick_y_value = self.joystick_y_pin.read_u16() 
            if joystick_y_value > 61000:
                self.lcd.clear()
                self.selected_letter_index = (self.selected_letter_index + 1) % len(self.number_sequence)
                print("oben")
                self.lcd.putstr(f"Guthaben: {self.balance}")
                self.lcd.move_to(0, 1)             
                self.lcd.putstr("bet: {}".format(current_number))
            elif joystick_y_value < 500:
                self.lcd.clear()
                print("unten")
                self.selected_letter_index = (self.selected_letter_index - 1) % len(self.number_sequence) 
                self.lcd.putstr(f"Guthaben: {self.balance}")
                self.lcd.move_to(0, 1)
                self.lcd.putstr("bet: {}".format(current_number))
            current_number = self.number_sequence[self.selected_letter_index]

    def spin_reels(self):
        weights = [
            [6, 5, 4, 3, 2, 1],
            [1, 2, 3, 4, 5, 6],          
            [1, 1, 1, 1, 1, 1],
        ]
        reel1_1 = self.weighted_choice(self.symbols, weights[0])
        reel2_1 = self.weighted_choice(self.symbols, weights[1])
        reel3_1 = self.weighted_choice(self.symbols, weights[2])
        print(f'{reel1_1} | {reel2_1} | {reel3_1}')
        return reel1_1, reel2_1, reel3_1

    def place_bet(self, bet_amount):
        if self.bet_amount > self.balance:
            print("Nicht genügend Guthaben. Bitte platzieren Sie einen niedrigeren Einsatz.")
            return False
        else:
            self.balance -= self.bet_amount
            return True

    def calculate_payout(self, bet_amount, symbols):
        multiplier_dict = {
            '🍒': {2: 1, 1: 1.5},
            '🍊': {2: 1.5, 1: 1.75},
            '🍇': {2: 1.75, 1: 2},
            '🔔': {2: 2.5, 1: 2.75},
            '🅱️': {2: 3, 1: 3.5},
            '7️⃣': {2: 4, 1: 5}
        }
        if symbols[0] == symbols[1] == symbols[2]:
            multiplier = multiplier_dict.get(symbols[0], {}).get(1, 0)
        elif symbols[0] == symbols[1] or symbols[0] == symbols[2]:
            multiplier = multiplier_dict.get(symbols[0], {}).get(2, 0)
        elif symbols[1] == symbols[2]:
            multiplier = multiplier_dict.get(symbols[1], {}).get(2, 0)
        else:
            multiplier = 0
        return int(self.bet_amount * multiplier)

    def play(self):
        x = 1
        self.lcd.clear()
        while True:
            try:
                self.x_value = self.joystick_x_pin.read_u16()
                self.y_value = self.joystick_y_pin.read_u16()
                self.bet_amount = self.handle_keyboard_input()
                if self.bet_amount > 0:
                    self.lcd.clear()
                    if self.place_bet(self.bet_amount):
                        symbols = self.spin_reels()
                        payout = self.calculate_payout(self.bet_amount, symbols)
                        if payout > 0:
                            self.balance += payout
                            print(f'Herzlichen Glückwunsch! Sie gewinnen {payout}!')
                        else:
                            print('Sorry, dieses Mal kein Gewinn.')
            except ValueError:
                print('Ungültiger Einsatz')
                continue

class Userinterface():

    def __init__(self):
        self.slot = SlotMachine()
        self.i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=100000)
        self.lcd = I2cLcd(self.i2c, 0x27, 4, 20)
        self.options = ["Registrieren", "Slot", "Beenden"]
        self.selected_option = 0

        self.joystick_x_pin = ADC(Pin(26))
        self.joystick_y_pin = ADC(Pin(27))
        self.joystick_button_pin = Pin(14, Pin.IN, Pin.PULL_UP)

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
        if y_value > 61000 and self.selected_option > 0:
            self.selected_option -= 1
        elif y_value < 500 and self.selected_option < len(self.options) - 1:
            self.selected_option += 1
        button_state = self.joystick_button_pin.value()

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
            self.lcd.clear()
            self.lcd.backlight_off()
            sys.exit()
        elif button_state == 0 and self.options[self.selected_option] == "Slot":
            self.slot.play()

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
