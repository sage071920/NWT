import random
import json

class User:
    def __init__(self, username, password, role, initial_balance=100):
        self.username = username
        self.password = password
        self.balance = initial_balance
        self.role = role
        self.history = []

    def to_dict(self):
        return {'username': self.username, 'password': self.password, 'balance': self.balance, 'history': self.history, 'role': self.role}

    @classmethod
    def from_dict(cls, user_data):
        return cls(user_data['username'], user_data['password'], user_data['role'], user_data['balance'])
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

    # Methode zum Hinzufügen von Geld zum Guthaben des Benutzers
    def give_money(self, amount):
        # Funktion, um Geld zum Guthaben des Benutzers hinzuzufügen
        self.balance += amount
        print(f"{amount} zum Guthaben von {self.username} hinzugefügt. Neues Guthaben: {self.balance}")
        self.history.append(f"Admin hat {amount} hinzugefügt. Guthaben: {self.balance}")

    def is_admin(self):
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


class AuthenticationManager:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.admin_password = "admin_password"
        self.user_data_file = "user_data.json"

    def register_user(self, username, password):
        if username in self.users:
            print(f"Benutzername '{username}' ist bereits vergeben. Bitte wählen Sie einen anderen.")
        elif password == self.admin_password:
            self.users[username] = Admin(username, password, role='admin')
            print(f"Admin {username} erfolgreich registriert.")
        else:
            self.users[username] = User(username, password, role='user')
            print(f"Benutzer {username} erfolgreich registriert.")
        self.save_user_data()

    def login(self, username, password):
        if username in self.users and self.users[username].password == password:
            self.current_user = self.users[username]
            if self.current_user.is_admin():
                print(f"Willkommen, {username} (Admin)!")
            else:
                print(f"Willkommen, {username}!")
        else:
            print("Ungültige Anmeldeinformationen. Zurück zum Hauptmenü.")
            self.current_user = None

    def load_user_data(self):
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
        user_data = {username: user.to_dict() for username, user in self.users.items()}
        with open(self.user_data_file, 'w') as file:
            json.dump(user_data, file, indent=2)

    def view_all_users(self):
        print("\nAlle Benutzer:")
        for username, user in self.users.items():
            print(f"Benutzername: {username}, Guthaben: {user.balance}, Rolle: {user.role}")

    def delete_user(self, username_to_delete):
        if username_to_delete in self.users:
            del self.users[username_to_delete]
            print(f"Benutzer {username_to_delete} gelöscht.")
        else:
            print("Ungültiger Benutzername. Löschen fehlgeschlagen.")


class SlotMachine:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.symbols = ['Cherry', 'Orange', 'Plum', 'Bell', 'Bar', 'Seven']

    def spin_reels(self):
        weights = [
            [6, 5, 4, 3, 2, 1],
            [1, 2, 3, 4, 5, 6],
            [4, 3, 6, 5, 2, 1]
        ]
        reel1 = random.choices(self.symbols, weights=weights[0], k=1)[0]
        reel2 = random.choices(self.symbols, weights=weights[1], k=1)[0]
        reel3 = random.choices(self.symbols, weights=weights[2], k=1)[0]

        print(f'{reel1} | {reel2} | {reel3}')
        return reel1, reel2, reel3

    def place_bet(self, bet_amount):
        if bet_amount > self.auth_manager.current_user.balance:
            print("Nicht genügend Guthaben. Bitte platzieren Sie einen niedrigeren Einsatz.")
            return False
        else:
            self.auth_manager.current_user.balance -= bet_amount
            return True

    def calculate_payout(self, bet_amount, symbols):
        multiplier_dict = {
            'Cherry': {2: 1, 1: 1.5},
            'Orange': {2: 1.5, 1: 1.75},
            'Plum': {2: 1.75, 1: 3},
            'Bell': {2: 3, 1: 3.25},
            'Bar': {2: 3.25, 1: 3.5},
            'Seven': {2: 3.5, 1: 3.75}
        }

        if symbols[0] == symbols[1] == symbols[2]:
            multiplier = multiplier_dict.get(symbols[0], {}).get(1, 0)
        elif symbols[0] == symbols[1] or symbols[0] == symbols[2]:
            multiplier = multiplier_dict.get(symbols[0], {}).get(2, 0)
        elif symbols[1] == symbols[2]:
            multiplier = multiplier_dict.get(symbols[1], {}).get(2, 0)
        else:
            multiplier = 0

        return int(bet_amount * multiplier)

    def display_history(self):
        print("Gewinnhistorie:")
        for item in self.auth_manager.current_user.history:
            print(item)

    def play(self):
        while True:
            print(f"Aktuelles Guthaben: {self.auth_manager.current_user.balance}")
            bet_amount = int(input("Platzieren Sie Ihren Einsatz (Geben Sie 0 ein, um zu beenden): "))

            if bet_amount == 0:
                print('Danke fürs Spielen. Auf Wiedersehen!')
                self.auth_manager.current_user.history.append(f"Beenden: Guthaben: {self.auth_manager.current_user.balance}")
                self.auth_manager.save_user_data()
                break

            if bet_amount < 0:
                print('invalid bet_amount new_bet = 1')
                bet_amount = 1

            if self.place_bet(bet_amount):
                symbols = self.spin_reels()
                payout = self.calculate_payout(bet_amount, symbols)

                if payout > 0:
                    print(f'Herzlichen Glückwunsch! Sie gewinnen {payout}!')
                    auth_manager.current_user.balance += payout
                    auth_manager.current_user.history.append(
                        f"Einsatz: {bet_amount}, Gewinn: {payout}, Guthaben: {auth_manager.current_user.balance}")
                else:
                    print('Sorry, dieses Mal kein Gewinn.')
                    auth_manager.current_user.history.append(
                        f"Einsatz: {bet_amount}, Gewinn: 0, Guthaben: {auth_manager.current_user.balance}")


if __name__ == "__main__":

    auth_manager = AuthenticationManager()
    auth_manager.load_user_data()

    while True:
        print("\n1. Registrieren")
        print("2. Anmelden")
        print("3. Beenden")
        choice = input("Geben Sie Ihre Auswahl ein: ")

        if choice == "1":
            username = input("Geben Sie einen Benutzernamen ein: ")
            password = input("Geben Sie ein Passwort ein: ")
            auth_manager.register_user(username, password)
        elif choice == "2":
            username = input("Geben Sie Ihren Benutzernamen ein: ")
            password = input("Geben Sie Ihr Passwort ein: ")
            auth_manager.login(username, password)
            if auth_manager.current_user:
                if auth_manager.current_user.is_admin():
                    # Admin interface
                    while True:
                        print("\nAdmin-Menü:")
                        print("1. Alle Benutzer anzeigen")
                        print("2. Benutzer löschen")
                        print("3. Geld an Benutzer geben")
                        print("4. play SlotMachine") 
                        print("5. Beenden")
                        admin_choice = input("Geben Sie Ihre Auswahl ein: ")

                        if admin_choice == "1":
                            auth_manager.view_all_users()
                        elif admin_choice == "2":
                            username_to_delete = input("Geben Sie den zu löschenden Benutzernamen ein: ")
                            if username_to_delete in auth_manager.users:
                                auth_manager.delete_user(username_to_delete)
                                print(f"Benutzer {username_to_delete} gelöscht.")
                            else:
                                print(f"Benutzer {username_to_delete} nicht gefunden.")
                            
                        elif admin_choice == "3":
                            username_to_give_money = input(
                                "Geben Sie den Benutzernamen ein, dem Sie Geld geben möchten: ")
                            amount_to_give = int(input("Geben Sie den Betrag ein, den Sie geben möchten: "))
                            auth_manager.current_user.give_money_to_user(username_to_give_money, amount_to_give, auth_manager)

                        elif admin_choice == "4":
                            game = SlotMachine(auth_manager)
                            game.play()
                        elif admin_choice == "5":
                            break
                        else:
                            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")
                else:
                    # User interface (Slot machine)
                    game = SlotMachine(auth_manager)
                    game.play()
        elif choice == "3":
            break
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")
