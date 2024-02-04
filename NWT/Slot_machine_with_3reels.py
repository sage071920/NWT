import random
import json
import hashlib
import getpass

class User():
    def __init__(self, username, password_hash, role, initial_balance=100):
        self.username = username
        self.password_hash = password_hash
        self.balance = initial_balance
        self.role = role
        self.history = []
    @classmethod
    # Hashen des passworts
    def hash_password(self, password):
        # Verwendet SHA-256 für die Hash-Funktion 
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()
    def to_dict(self):
        return {'username': self.username, 'password_hash': self.password_hash, 'balance': self.balance, 'history': self.history, 'role': self.role}

    @classmethod
    def from_dict(cls, user_data):
        if 'password_hash' in user_data:
            return cls(user_data['username'], user_data['password_hash'], user_data['role'], user_data['balance'])
        elif 'password' in user_data:
            password_hash = cls.hash_password(user_data['password'])
            return cls(user_data['username'], password_hash, user_data['role'], user_data['balance'])
        else:
            raise ValueError("Benutzerdaten enthalten weder 'password_hash' noch 'password'.")

    # Methode zum Überweisen von Geld an einen anderen Benutzer
    def give_money_to_user(self, username, amount, auth_manager):
        # Überprüfung, ob der Benutzer im Authentifizierungsmanager vorhanden ist
        if username in auth_manager.users:
            user = auth_manager.users[username]
            # Überprüfung, ob es sich bei dem Benutzer um einen regulären Benutzer handelt
            if isinstance(user, User):
                user.give_money(amount)
                auth_manager.save_user_data()
            else:
                print(f"Benutzer {username} ist kein regulärer Benutzer und kann kein Geld erhalten.")
        else:
            print(f"Benutzer {username} nicht gefunden.")

    def give_money(self, amount):
        # Funktion, um Geld zum Guthaben des Benutzers hinzuzufügen
        self.balance += amount
        print(f"{amount} zum Guthaben von {self.username} hinzugefügt. Neues Guthaben: {self.balance}")
        self.history.append(f"Admin hat {amount} hinzugefügt. Guthaben: {self.balance}")

    def is_admin(self):
        # überprüft ob user die rolle admin hat
        return self.role == 'admin'


class Admin(User):
    def __init__(self, username, password, role):
        super().__init__(username, password, role, 100)

    def give_money_to_user(self, username, amount, auth_manager):
        if username in auth_manager.users:
            user = auth_manager.users[username]
            if isinstance(user, User):
                user.give_money(amount)
            else:
                print(f"Benutzer {username} ist kein regulärer Benutzer und kann kein Geld erhalten.")
        else:
            print(f"Benutzer {username} nicht gefunden.")


class AuthenticationManager():
    def __init__(self):
        self.users = {}
        self.current_user = None

        # Lese die Konfigurationsdatei ein
        with open('config.json') as config_file:
            config_data = json.load(config_file)

        self.admin_password = config_data.get('admin_password', None)
        if self.admin_password is None:
            raise ValueError("Admin-Passwort in der Konfigurationsdatei fehlt.")

        self.user_data_file = "user_data.json"
    
    def register_user(self, username, password):
        # Methode zum Registrieren eines Benutzers
        if username in self.users:
            print(f"Benutzername '{username}' ist bereits vergeben. Bitte wählen Sie einen anderen.")
        elif password == self.admin_password: # überprüfung, ob user ein admin wird 
            hashed_password = User.hash_password(password)
            self.users[username] = Admin(username, hashed_password, role='admin')
            print(f"Admin {username} erfolgreich registriert.")
        else:
            hashed_password = User.hash_password(password)
            self.users[username] = User(username, hashed_password, role='user')
            print(f"Benutzer {username} erfolgreich registriert.")
        self.save_user_data()

    def login(self, username):
        # Methode zum Anmelden eines Benutzers
        if username in self.users:
            entered_password = self.get_masked_input("Geben Sie Ihr Passwort ein: ")

            # Vergleiche das eingegebene Passwort mit dem gehashten Passwort
            if self.users[username].password_hash == User.hash_password(entered_password):
                self.current_user = self.users[username]
                if self.current_user.is_admin():
                    print(f"Willkommen, {username} (Admin)!")
                else:
                    print(f"Willkommen, {username}!")
            else:
                print("Ungültige Anmeldeinformationen. Zurück zum Hauptmenü.")
                self.current_user = None
        else:
            print("Ungültiger Benutzername. Zurück zum Hauptmenü.")
            self.current_user = None

    def get_masked_input(self, prompt):
        # Methode zum Maskieren der Benutzereingabe (Passwort)
        return getpass.getpass(prompt)

    def load_user_data(self):
        # Methode zum Laden von Benutzerdaten aus einer JSON-Datei
        try:
            with open(self.user_data_file, 'r') as file:
                user_data = json.load(file)
                for username, data in user_data.items():
                    if 'balance' in data:
                        self.users[username] = User.from_dict(data)
                    else:
                        self.users[username] = Admin.from_dict(data)
        except FileNotFoundError:
            pass

    def save_user_data(self):
        # Methode zum Speichern von Benutzerdaten in einer JSON-Datei
        user_data = {username: user.to_dict() for username, user in self.users.items()}
        with open(self.user_data_file, 'w') as file:
            json.dump(user_data, file, indent=2)

    def view_all_users(self):
        # Methode zum Anzeigen aller Benutzer für Admins
        print("\nAlle Benutzer:")
        for username, user in self.users.items():
            print(f"Benutzername: {username}, Guthaben: {user.balance}, Rolle: {user.role}")

    def delete_user(self, username_to_delete):
        # Methode zum Löschen eines Benutzers
        if username_to_delete in self.users:
            del self.users[username_to_delete]
            print(f"Benutzer {username_to_delete} gelöscht.")
            self.save_user_data()
        else:
            print("Ungültiger Benutzername. Löschen fehlgeschlagen.")


class SlotMachine():
    SYMBOLS = ['🍒', '🍊', '🍇', '🔔', '🅱️', '7️⃣']

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.multiplier_dict = {
            '🍒': {2: 1, 1: 1.5},
            '🍊': {2: 1.5, 1: 1.75},
            '🍇': {2: 1.75, 1: 2},
            '🔔': {2: 2.5, 1: 2.75},
            '🅱️': {2: 3, 1: 3.5},
            '7️⃣': {2: 4, 1: 5}
        }
        self.weights = [
            [6, 5, 4, 3, 2, 1],
            [1, 2, 3, 4, 5, 6],
            [1, 1, 1, 1, 1, 1],
            [6, 5, 4, 3, 2, 1],
            [1, 2, 3, 4, 5, 6],
            [1, 1, 1, 1, 1, 1],
            [6, 5, 4, 3, 2, 1],
            [1, 2, 3, 4, 5, 6],
            [1, 1, 1, 1, 1, 1]
        ]

    def spin_reels(self):

        reels = [
            random.choices(self.SYMBOLS, weights=self.weights[i], k=1)[0] for i in range(9)
        ]

        for i in range(0, 9, 3):
            print(f'{reels[i]} | {reels[i + 1]} | {reels[i + 2]}')

        return tuple(reels)

    def place_bet(self, bet_amount):
        if bet_amount > self.auth_manager.current_user.balance:
            print("Nicht genügend Guthaben. Bitte platzieren Sie einen niedrigeren Einsatz.")
            return False
        else:
            self.auth_manager.current_user.balance -= bet_amount
            return True

    def calculate_payout(self, bet_amount, symbols):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        max_multiplier = 0

        for combo in winning_combinations:
            current_multiplier = 0

            if symbols[combo[0]] == symbols[combo[1]] == symbols[combo[2]]:
                current_multiplier = self.multiplier_dict.get(symbols[combo[0]], {}).get(1, 0) if symbols[combo[0]] in self.multiplier_dict else 0
            elif symbols[combo[0]] == symbols[combo[1]] or symbols[combo[0]] == symbols[combo[2]]:
                current_multiplier = self.multiplier_dict.get(symbols[combo[0]], {}).get(2, 0) if symbols[combo[0]] in self.multiplier_dict else 0
            elif symbols[combo[1]] == symbols[combo[2]]:
                current_multiplier = self.multiplier_dict.get(symbols[combo[1]], {}).get(2, 0) if symbols[combo[1]] in self.multiplier_dict else 0

            max_multiplier = max(max_multiplier, current_multiplier)

        return int(bet_amount * max_multiplier)

    def display_history(self):
        print("Gewinnhistorie:")
        for item in self.auth_manager.current_user.history:
            print(item)

    def play(self):
        while True:
            try:
                print(f"Aktuelles Guthaben: {self.auth_manager.current_user.balance}")
                bet_amount = int(input("Platzieren Sie Ihren Einsatz (Geben Sie 0 ein, um zu beenden): "))

                if bet_amount == 0:
                    print('Danke fürs Spielen. Auf Wiedersehen!')
                    self.auth_manager.current_user.history.append(f"Beenden: Guthaben: {self.auth_manager.current_user.balance}")
                    auth_manager.save_user_data()
                    break

                if bet_amount < 0:
                    print('ungültiger Einsatz')
                    continue

                if self.place_bet(bet_amount):
                    symbols = self.spin_reels()
                    payout = self.calculate_payout(bet_amount, symbols)

                    if payout > 0:
                        auth_manager.current_user.balance += payout
                        auth_manager.current_user.history.append(
                            f"Einsatz: {bet_amount}, Gewinn: {payout}, Guthaben: {auth_manager.current_user.balance}")
                        auth_manager.save_user_data()
                        print(f'Herzlichen Glückwunsch! Sie gewinnen {payout}!')
                    else:
                        auth_manager.current_user.history.append(
                            f"Einsatz: {bet_amount}, Gewinn: 0, Guthaben: {auth_manager.current_user.balance}")
                        auth_manager.save_user_data()
                        print('Sorry, dieses Mal kein Gewinn.')
            except ValueError:
                print('ungültiger Einsatz')
                continue


class CasinoGame():
    class Karte():
        # Klasse für die Spielkarten im Three Card Poker
        def __init__(self, symbol, wert):
            self.symbol = symbol
            self.wert = wert

    class Deck():
        # Klasse für das Kartendeck im Three Card Poker
        SYMBOLE = ['♥️:', '♦️:', '♠️:', '♣️:']
        WERTE = {'2|': 2, '3|': 3, '4|': 4, '5|': 5, '6|': 6, '7|': 7, '8|': 8, '9|': 9,
                 '10|': 10, 'Bube|': 10, 'Dame|': 10, 'König|': 10, 'Ass|': 11}

        def __init__(self):
            self.karten = [CasinoGame.Karte(symbol, wert) for symbol in self.SYMBOLE for wert in self.WERTE]
            self.mische()
    
        def mische(self):
            # Methode zum Mischen des Kartendecks
            random.shuffle(self.karten)

        def refill(self):
            # Methode um das Deck wieder aufzufüllen
            self.karten = [CasinoGame.Karte(symbol, wert) for symbol in self.SYMBOLE for wert in self.WERTE]

        def ziehe_karte(self):
            # Methode zum Ziehen einer Karte aus dem Deck
            if not self.karten:
                print("Deck ist leer. Mische es erneut.")
                self.refill()
                self.mische()
            return self.karten.pop()

    class ThreeCardPokerGame():
        ACE = 'Ass'

        def __init__(self, auth_manager):
            self.auth_manager = auth_manager
            self.deck = CasinoGame.Deck()

        def deal_hand(self):
            # Methode zum Austeilen einer Hand im Three Card Poker
            if not self.deck.karten:
                self.deck.mische()

            return [self.deck.ziehe_karte() for _ in range(3)]

        def play(self):
            # Methode zum Spielen des Three Card Poker
            while True:
                print("Willkommen beim Three Card Poker!")
                try:
                    print(f"Aktuelles Guthaben: {self.auth_manager.current_user.balance}")
                    bet_amount = int(input("Setzen Sie Ihren Einsatz (Geben Sie 0 ein, um zu beenden): "))
                    if not self.validate_bet(bet_amount):
                        break  # Verlasse die Schleife, wenn der Einsatz 0 ist

                    self.auth_manager.current_user.balance -= bet_amount
                    self.auth_manager.save_user_data()
                    self.deck.mische()  
                    spieler_hand = self.deal_hand()
                    dealer_hand = self.deal_hand()

                    print()

                    self.zeige_hand(spieler_hand, spieler=True)

                    result = self.determine_winner(spieler_hand, dealer_hand)
                    self.display_result(result, bet_amount)
                except ValueError:
                    print('Ungültiger Einsatz')
                    continue

        def validate_bet(self, bet_amount):
            if bet_amount == 0:
                print('Danke fürs Spielen. Auf Wiedersehen!')
                self.auth_manager.current_user.history.append(f"Beenden: Guthaben: {self.auth_manager.current_user.balance}")
                self.auth_manager.save_user_data()
                return False

            if bet_amount < 0:
                print('Ungültiger Einsatz. Neuer Einsatz wird auf 1 gesetzt.')
                return False

            if bet_amount > self.auth_manager.current_user.balance:
                print("Nicht genügend Guthaben. Bitte setzen Sie einen niedrigeren Einsatz.")
                return False

            return True

        def determine_winner(self, spieler_hand, dealer_hand):
            spieler_wert = self.wert_der_hand(spieler_hand)
            dealer_wert = self.wert_der_hand(dealer_hand)

            if spieler_wert > dealer_wert:
                return 'Spieler gewinnt'
            elif spieler_wert < dealer_wert:
                return 'Spieler verliert'
            else:
                return 'Unentschieden'

        def display_result(self, result, bet_amount):
            print(result)

            if 'gewinnt' in result:
                gewinn = bet_amount * 2
                self.auth_manager.current_user.balance += gewinn
                print(f"Ihr Gewinn: {gewinn}")
            else:
                gewinn = 0
                print("Sie verlieren!")

            self.auth_manager.save_user_data()
            self.auth_manager.current_user.history.append(
                f"Einsatz: {bet_amount}, Gewinn: {gewinn}, Guthaben: {self.auth_manager.current_user.balance}")

        def wert_der_hand(self, hand):
            # Methode zur Berechnung des Werts einer Hand im Three Card Poker
            gesamtwert = 0
            anzahl_ass = 0

            for karte in hand:
                gesamtwert += self.deck.WERTE[karte.wert]
                if karte.wert == self.ACE:
                    anzahl_ass += 1

            # Berücksichtige die Ass-Werte
            while anzahl_ass > 0 and gesamtwert > 21:
                gesamtwert -= 10
                anzahl_ass -= 1

            return gesamtwert

        def zeige_hand(self, hand, spieler=True):
            # Methode zum Anzeigen einer Hand im Three Card Poker
            print(f"{'Spieler' if spieler else 'Dealer'} Hand:")
            for karte in hand:
                print(f"{karte.symbol} {karte.wert}", end=' ')
            print(f'Gesamtwert: {self.wert_der_hand(hand)}')


class UserInterface:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager

    def run(self):
        while True:
            print("\n1. Registrieren")
            print("2. Anmelden")
            print("3. Beenden")
            choice = input("Geben Sie Ihre Auswahl ein: ")

            if choice == "1":
                username = input("Geben Sie einen Benutzernamen ein: ")
                password = self.auth_manager.get_masked_input("Geben Sie Ihr Passwort ein: ")
                self.auth_manager.register_user(username, password)
            elif choice == "2":
                username = input("Geben Sie Ihren Benutzernamen ein: ")
                self.auth_manager.login(username)
                if self.auth_manager.current_user:
                    if self.auth_manager.current_user.is_admin():
                        self.run_admin_menu()
                    else:
                        self.run_user_menu()
            elif choice == "3":
                self.auth_manager.save_user_data()
                break
            else:
                print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

    def run_admin_menu(self):
        while True:
            print("\nAdmin-Menü:")
            print("1. Alle Benutzer anzeigen")
            print("2. Benutzer löschen")
            print("3. Geld an Benutzer geben")
            print("4. Play SlotMachine")
            print("5. Play Three Card Poker") 
            print("6. Ausloggen")
            admin_choice = input("Geben Sie Ihre Auswahl ein: ")

            if admin_choice == "1":
                self.auth_manager.view_all_users()
            elif admin_choice == "2":
                username_to_delete = input("Geben Sie den zu löschenden Benutzernamen ein: ")
                if username_to_delete in self.auth_manager.users:
                    self.auth_manager.delete_user(username_to_delete)
                else:
                    print(f"Benutzer {username_to_delete} nicht gefunden.")
                
            elif admin_choice == "3":
                username_to_give_money = input(
                    "Geben Sie den Benutzernamen ein, dem Sie Geld geben möchten: ")
                amount_to_give = int(input("Geben Sie den Betrag ein, den Sie geben möchten: "))
                self.auth_manager.current_user.give_money_to_user(username_to_give_money, amount_to_give, self.auth_manager)

            elif admin_choice == "4":
                game = SlotMachine(self.auth_manager)
                game.play()
                
            elif admin_choice == "5":
                poker_game = CasinoGame.ThreeCardPokerGame(self.auth_manager)
                poker_game.play()

            elif admin_choice == "6":
                break

            else:
                print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

    def run_user_menu(self):
        while True:
            print("\nBenutzermenu:")
            print("1. Spielautomat spielen")
            print("2. Three Card Poker spielen")
            print("3. Guthaben anzeigen")
            print("4. Historie anzeigen")
            print("5. Benutzer löschen")
            print("6. Ausloggen")
            user_choice = input("Geben Sie Ihre Auswahl ein: ")

            if user_choice == "1":
                game = SlotMachine(self.auth_manager)
                game.play()
            elif user_choice == "2":
                poker_game = CasinoGame.ThreeCardPokerGame(self.auth_manager)
                poker_game.play()
            elif user_choice == "3":
                print(f"Aktuelles Guthaben: {self.auth_manager.current_user.balance}")
            elif user_choice == "4":
                print("Gewinnhistorie:")
                for item in self.auth_manager.current_user.history:
                    print(item)
            elif user_choice == "5":
                username_to_delete = self.auth_manager.current_user.username
                self.auth_manager.delete_user(username_to_delete)
                break
            elif user_choice == "6":
                print("Sie wurden abgemeldet. Auf Wiedersehen!")
                break
            else:
                print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

if __name__ == "__main__":
    auth_manager = AuthenticationManager()
    auth_manager.load_user_data()

    ui = UserInterface(auth_manager)
    ui.run()