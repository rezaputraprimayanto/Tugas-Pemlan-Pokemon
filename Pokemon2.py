import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
from random import choice

class Pokemon:
    def __init__(self, name, element, hp):
        self.name = name
        self.element = element
        self.hp = hp
        self.skills = {"Tackle": 20, "Ember": 30, "Water Gun": 25}
        self.elemental_effectiveness = {
            "water": {"effective": ["fire"], "ineffective": ["electric"]},
            "fire": {"effective": ["grass"], "ineffective": ["water"]},
            "grass": {"effective": ["water"], "ineffective": ["fire"]},
            "electric": {"effective": ["water"], "ineffective": ["grass"]}
        }
        self.battle_log = []

    def attack(self, target, skill_name):
        damage = self.skills[skill_name]
        effectiveness = self.get_effectiveness(target.element)
        damage *= effectiveness
        target.receive_damage(damage, self.element)

        if effectiveness > 1:
            self.battle_log.append(f"{self.name}'s {skill_name} is SUPER EFFECTIVE! Damage: {damage}")
        elif effectiveness < 1:
            self.battle_log.append(f"{self.name}'s {skill_name} is not very effective. Damage: {damage}")
        else:
            self.battle_log.append(f"{self.name}'s {skill_name} hits. Damage: {damage}")

        return damage

    def receive_damage(self, damage, attacker_element):
        effectiveness = self.get_effectiveness(attacker_element)
        damage *= effectiveness
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0

    def get_effectiveness(self, target_element):
        if target_element in self.elemental_effectiveness[self.element]["effective"]:
            return 2
        elif target_element in self.elemental_effectiveness[self.element]["ineffective"]:
            return 0.5
        else:
            return 1

    def is_knocked_out(self):
        return self.hp == 0

class BattleSimulator:
    def __init__(self, player_pokemon, opponent_pokemon):
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon

    def player_attack(self, skill_name):
        damage_dealt = self.player_pokemon.attack(self.opponent_pokemon, skill_name)
        log_entry = f"{self.player_pokemon.name} using {skill_name}, dealing damage to {self.opponent_pokemon.name}, Damage: {damage_dealt}"

        if self.opponent_pokemon.is_knocked_out():
            log_entry += f"\n{self.opponent_pokemon.name} is KO'd, {self.player_pokemon.name} WINS"

        self.player_pokemon.battle_log.append(log_entry)

        if not self.opponent_pokemon.is_knocked_out():
            self.opponent_attack()

    def opponent_attack(self):
        if not self.player_pokemon.is_knocked_out():
            opponent_skills = list(self.opponent_pokemon.skills.keys())
            selected_skill = choice(opponent_skills)

            damage_dealt = self.opponent_pokemon.attack(self.player_pokemon, selected_skill)
            log_entry = f"{self.opponent_pokemon.name} using {selected_skill}, dealing damage to {self.player_pokemon.name}, Damage: {damage_dealt}"

            if self.player_pokemon.is_knocked_out():
                log_entry += f"\n{self.player_pokemon.name} is KO'd, {self.opponent_pokemon.name} WINS"

            self.opponent_pokemon.battle_log.append(log_entry)
            self.player_pokemon.battle_log.append(log_entry)
            
class BattleLogWindow:
    def __init__(self, root, player_pokemon, simulator):
        self.root = root
        self.player_pokemon = player_pokemon
        self.simulator = simulator

        root.title("Pokemon Battle Simulator")

        hp_frame = ttk.Frame(root)
        hp_frame.grid(row=0, column=0, columnspan=3, pady=10)

        self.player_hp_label = ttk.Label(hp_frame, text=f"{player_pokemon.name} HP: {player_pokemon.hp}")
        self.player_hp_label.grid(row=0, column=0, padx=5)

        self.opponent_hp_label = ttk.Label(hp_frame, text=f"{simulator.opponent_pokemon.name} HP: {simulator.opponent_pokemon.hp}")
        self.opponent_hp_label.grid(row=0, column=1, padx=5)

        image_frame = ttk.Frame(root)
        image_frame.grid(row=1, column=0, columnspan=3, pady=10)

        # Load gambar-gambar Pokemon untuk player dan opponent
        self.player_image_label = tk.Label(image_frame, image=self.load_pokemon_image(player_pokemon.name.lower()))
        self.player_image_label.grid(row=0, column=0, padx=5)

        self.opponent_image_label = tk.Label(image_frame, image=self.load_pokemon_image(simulator.opponent_pokemon.name.lower()))
        self.opponent_image_label.grid(row=0, column=1, padx=5)

        log_frame = ttk.Frame(root)
        log_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.text_widget = scrolledtext.ScrolledText(log_frame, height=10, width=50)
        self.text_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        frame = ttk.Frame(log_frame)
        frame.grid(row=1, column=0, pady=10)

        # Tambahkan label untuk menampilkan gambar Pokemon
        self.player_image = self.load_pokemon_image(player_pokemon.name.lower())
        player_image_label = tk.Label(image_frame, image=self.player_image)
        player_image_label.grid(row=0, column=0, padx=5)

        self.opponent_image = self.load_pokemon_image(simulator.opponent_pokemon.name.lower())
        opponent_image_label = tk.Label(image_frame, image=self.opponent_image)
        opponent_image_label.grid(row=0, column=1, padx=5)

        # Modified button style to create a rounded rectangle illusion
        s = ttk.Style()
        s.configure('Rounded.TButton', relief="flat", background=root.cget('bg'))

        self.player_attack_button = ttk.Button(frame, text="Player Attack", style='Rounded.TButton', command=self.player_attack)
        self.player_attack_button.grid(row=0, column=0, padx=5)

        skill_label = tk.Label(frame, text="Choose a skill:")
        skill_label.grid(row=0, column=1, padx=5)

        self.skill_var = tk.StringVar(frame)
        self.skill_var.set(list(player_pokemon.skills.keys())[0])

        # Create a themed Combobox for skills with rounded rectangle style
        skill_menu = ttk.Combobox(frame, textvariable=self.skill_var, values=list(player_pokemon.skills.keys()), style='Rounded.TCombobox')
        skill_menu.grid(row=0, column=2, padx=5)

        root.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # Display initial HP values
        self.update_battle_log()
        self.load_pokemon_images()

    def update_battle_log(self):
        # Update HP labels
        self.player_hp_label.config(text=f"{self.player_pokemon.name} HP: {self.player_pokemon.hp}")
        self.opponent_hp_label.config(text=f"{self.simulator.opponent_pokemon.name} HP: {self.simulator.opponent_pokemon.hp}")

        # Clear the existing log before updating
        self.text_widget.delete(1.0, tk.END)

        # Update the log with new entries
        for entry in self.player_pokemon.battle_log:
            self.text_widget.insert(tk.END, entry + "\n")

        # Scroll to the bottom to show the latest entries
        self.text_widget.yview(tk.END)

    def player_attack(self):
        selected_skill = self.skill_var.get()
        self.simulator.player_attack(selected_skill)
        self.update_battle_log()

    def load_pokemon_images(self):
        self.player_image_label['image'] = self.load_pokemon_image(self.player_pokemon.name.lower())
        self.opponent_image_label['image'] = self.load_pokemon_image(self.simulator.opponent_pokemon.name.lower())

    
    def load_pokemon_image(self, Charmander):
        image_path = f"D:/MATKUL SMT 5/Pemlan Dosen/{Charmander.lower()}.png"  
        pokemon_image = Image.open(image_path)
        pokemon_image = pokemon_image.resize((100, 100), Image.ANTIALIAS)  
        return ImageTk.PhotoImage(pokemon_image)
    
    def load_pokemon_image(self, Squirtle):
        image_path = f"D:/MATKUL SMT 5/Pemlan Dosen/{Squirtle.lower()}.png"  
        pokemon_image = Image.open(image_path)
        pokemon_image = pokemon_image.resize((100, 100), Image.BICUBIC)  
        return ImageTk.PhotoImage(pokemon_image)
    
    def load_pokemon_image(self, Bulbasaur):
        image_path = f"D:/MATKUL SMT 5/Pemlan Dosen/{Bulbasaur.lower()}.png"  
        pokemon_image = Image.open(image_path)
        pokemon_image = pokemon_image.resize((100, 100), Image.BICUBIC)  
        return ImageTk.PhotoImage(pokemon_image)

def choose_pokemon():
    root = tk.Tk()
    root.title("Choose Your Pokemon")

    pokemon_options = [
        {"name": "Charmander", "element": "fire", "hp": 100},
        {"name": "Squirtle", "element": "water", "hp": 100},
        {"name": "Bulbasaur", "element": "grass", "hp": 100},
    ]
    
    image_path = "D:/MATKUL SMT 5/Pemlan Dosen/Logo.png"
    pokemon_image = Image.open(image_path)
    pokemon_image = pokemon_image.resize((150, 150), Image.BICUBIC)
    image = ImageTk.PhotoImage(pokemon_image)
    image_label = tk.Label(root, image=image)
    image_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    def start_battle(player_choice, opponent_choice):
        player_pokemon = Pokemon(player_choice["name"], player_choice["element"], player_choice["hp"])
        opponent_pokemon = Pokemon(opponent_choice["name"], opponent_choice["element"], opponent_choice["hp"])

        simulator = BattleSimulator(player_pokemon, opponent_pokemon)

        battle_root = tk.Toplevel(root)
        battle_root.geometry("500x400")
        BattleLogWindow(battle_root, player_pokemon, simulator)

    ttk.Label(root, text="Choose Your Pokemon:").grid(row=1, column=0, padx=10, pady=5)  # Baris 1
    player_var = tk.StringVar(root)
    player_var.set(pokemon_options[0]["name"])
    player_menu = ttk.Combobox(root, textvariable=player_var, values=[pokemon["name"] for pokemon in pokemon_options], style='Rounded.TCombobox')
    player_menu.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(root, text="Choose Opponent's Pokemon:").grid(row=2, column=0, padx=10, pady=5)  # Baris 2
    opponent_var = tk.StringVar(root)
    opponent_var.set(pokemon_options[1]["name"])
    opponent_menu = ttk.Combobox(root, textvariable=opponent_var, values=[pokemon["name"] for pokemon in pokemon_options], style='Rounded.TCombobox')
    opponent_menu.grid(row=2, column=1, padx=10, pady=5)

    start_button = ttk.Button(root, text="Start Battle", command=lambda: start_battle(
        next(p for p in pokemon_options if p["name"] == player_var.get()),
        next(p for p in pokemon_options if p["name"] == opponent_var.get())
    ))
    start_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Create a themed style for the Combobox
    s = ttk.Style()
    s.configure('Rounded.TCombobox', relief="flat", background=root.cget('bg'))

    root.mainloop()

if __name__ == "__main__":
    choose_pokemon()
