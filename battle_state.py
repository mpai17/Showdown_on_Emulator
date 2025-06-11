class BattleState:
    def __init__(self):
        # Move and type data from Gen 1
        self.MOVE_DATA = {
            "Pound": {"id": 0x01, "pp": 35}, "Karate Chop": {"id": 0x02, "pp": 25}, "Double Slap": {"id": 0x03, "pp": 10}, "Comet Punch": {"id": 0x04, "pp": 15}, "Mega Punch": {"id": 0x05, "pp": 20},
            "Pay Day": {"id": 0x06, "pp": 20}, "Fire Punch": {"id": 0x07, "pp": 15}, "Ice Punch": {"id": 0x08, "pp": 15}, "ThunderPunch": {"id": 0x09, "pp": 15}, "Scratch": {"id": 0x0A, "pp": 35},
            "ViceGrip": {"id": 0x0B, "pp": 30}, "Guillotine": {"id": 0x0C, "pp": 5}, "Razor Wind": {"id": 0x0D, "pp": 10}, "Swords Dance": {"id": 0x0E, "pp": 30}, "Cut": {"id": 0x0F, "pp": 30},
            "Gust": {"id": 0x10, "pp": 35}, "Wing Attack": {"id": 0x11, "pp": 35}, "Whirlwind": {"id": 0x12, "pp": 20}, "Fly": {"id": 0x13, "pp": 15}, "Bind": {"id": 0x14, "pp": 20},
            "Slam": {"id": 0x15, "pp": 20}, "Vine Whip": {"id": 0x16, "pp": 25}, "Stomp": {"id": 0x17, "pp": 20}, "Double Kick": {"id": 0x18, "pp": 30}, "Mega Kick": {"id": 0x19, "pp": 5},
            "Jump Kick": {"id": 0x1A, "pp": 10}, "Rolling Kick": {"id": 0x1B, "pp": 15}, "Sand-Attack": {"id": 0x1C, "pp": 15}, "Headbutt": {"id": 0x1D, "pp": 15}, "Horn Attack": {"id": 0x1E, "pp": 25},
            "Fury Attack": {"id": 0x1F, "pp": 20}, "Horn Drill": {"id": 0x20, "pp": 5}, "Tackle": {"id": 0x21, "pp": 35}, "Body Slam": {"id": 0x22, "pp": 15}, "Wrap": {"id": 0x23, "pp": 20},
            "Take Down": {"id": 0x24, "pp": 20}, "Thrash": {"id": 0x25, "pp": 10}, "Double-Edge": {"id": 0x26, "pp": 15}, "Tail Whip": {"id": 0x27, "pp": 30}, "Poison Sting": {"id": 0x28, "pp": 35},
            "Twineedle": {"id": 0x29, "pp": 20}, "Pin Missile": {"id": 0x2A, "pp": 20}, "Leer": {"id": 0x2B, "pp": 30}, "Bite": {"id": 0x2C, "pp": 25}, "Growl": {"id": 0x2D, "pp": 40},
            "Roar": {"id": 0x2E, "pp": 20}, "Sing": {"id": 0x2F, "pp": 15}, "Supersonic": {"id": 0x30, "pp": 20}, "SonicBoom": {"id": 0x31, "pp": 20}, "Disable": {"id": 0x32, "pp": 20},
            "Acid": {"id": 0x33, "pp": 30}, "Ember": {"id": 0x34, "pp": 25}, "Flamethrower": {"id": 0x35, "pp": 15}, "Mist": {"id": 0x36, "pp": 30}, "Water Gun": {"id": 0x37, "pp": 25},
            "Hydro Pump": {"id": 0x38, "pp": 5}, "Surf": {"id": 0x39, "pp": 15}, "Ice Beam": {"id": 0x3A, "pp": 10}, "Blizzard": {"id": 0x3B, "pp": 5}, "Psybeam": {"id": 0x3C, "pp": 20},
            "BubbleBeam": {"id": 0x3D, "pp": 20}, "Aurora Beam": {"id": 0x3E, "pp": 20}, "Hyper Beam": {"id": 0x3F, "pp": 5}, "Peck": {"id": 0x40, "pp": 35}, "Drill Peck": {"id": 0x41, "pp": 20},
            "Submission": {"id": 0x42, "pp": 25}, "Low Kick": {"id": 0x43, "pp": 20}, "Counter": {"id": 0x44, "pp": 20}, "Seismic Toss": {"id": 0x45, "pp": 20}, "Strength": {"id": 0x46, "pp": 15},
            "Absorb": {"id": 0x47, "pp": 25}, "Mega Drain": {"id": 0x48, "pp": 15}, "Leech Seed": {"id": 0x49, "pp": 10}, "Growth": {"id": 0x4A, "pp": 20}, "Razor Leaf": {"id": 0x4B, "pp": 25},
            "SolarBeam": {"id": 0x4C, "pp": 10}, "PoisonPowder": {"id": 0x4D, "pp": 35}, "Stun Spore": {"id": 0x4E, "pp": 30}, "Sleep Powder": {"id": 0x4F, "pp": 15}, "Petal Dance": {"id": 0x50, "pp": 10},
            "String Shot": {"id": 0x51, "pp": 40}, "Dragon Rage": {"id": 0x52, "pp": 10}, "Fire Spin": {"id": 0x53, "pp": 15}, "ThunderShock": {"id": 0x54, "pp": 30}, "Thunderbolt": {"id": 0x55, "pp": 15},
            "Thunder Wave": {"id": 0x56, "pp": 20}, "Thunder": {"id": 0x57, "pp": 10}, "Rock Throw": {"id": 0x58, "pp": 15}, "Earthquake": {"id": 0x59, "pp": 10}, "Fissure": {"id": 0x5A, "pp": 5},
            "Dig": {"id": 0x5B, "pp": 10}, "Toxic": {"id": 0x5C, "pp": 10}, "Confusion": {"id": 0x5D, "pp": 25}, "Psychic": {"id": 0x5E, "pp": 10}, "Hypnosis": {"id": 0x5F, "pp": 20},
            "Meditate": {"id": 0x60, "pp": 40}, "Agility": {"id": 0x61, "pp": 30}, "Quick Attack": {"id": 0x62, "pp": 30}, "Rage": {"id": 0x63, "pp": 20}, "Teleport": {"id": 0x64, "pp": 20},
            "Night Shade": {"id": 0x65, "pp": 15}, "Mimic": {"id": 0x66, "pp": 10}, "Screech": {"id": 0x67, "pp": 40}, "Double Team": {"id": 0x68, "pp": 15}, "Recover": {"id": 0x69, "pp": 20},
            "Harden": {"id": 0x6A, "pp": 30}, "Minimize": {"id": 0x6B, "pp": 10}, "SmokeScreen": {"id": 0x6C, "pp": 20}, "Confuse Ray": {"id": 0x6D, "pp": 10}, "Withdraw": {"id": 0x6E, "pp": 40},
            "Defense Curl": {"id": 0x6F, "pp": 40}, "Barrier": {"id": 0x70, "pp": 20}, "Light Screen": {"id": 0x71, "pp": 30}, "Haze": {"id": 0x72, "pp": 30}, "Reflect": {"id": 0x73, "pp": 20},
            "Focus Energy": {"id": 0x74, "pp": 30}, "Bide": {"id": 0x75, "pp": 10}, "Metronome": {"id": 0x76, "pp": 10}, "Mirror Move": {"id": 0x77, "pp": 20}, "Selfdestruct": {"id": 0x78, "pp": 5},
            "Egg Bomb": {"id": 0x79, "pp": 10}, "Lick": {"id": 0x7A, "pp": 30}, "Smog": {"id": 0x7B, "pp": 20}, "Sludge": {"id": 0x7C, "pp": 20}, "Bone Club": {"id": 0x7D, "pp": 20},
            "Fire Blast": {"id": 0x7E, "pp": 5}, "Waterfall": {"id": 0x7F, "pp": 15}, "Clamp": {"id": 0x80, "pp": 15}, "Swift": {"id": 0x81, "pp": 20}, "Skull Bash": {"id": 0x82, "pp": 10},
            "Spike Cannon": {"id": 0x83, "pp": 15}, "Constrict": {"id": 0x84, "pp": 35}, "Amnesia": {"id": 0x85, "pp": 20}, "Kinesis": {"id": 0x86, "pp": 15}, "Softboiled": {"id": 0x87, "pp": 10},
            "Hi Jump Kick": {"id": 0x88, "pp": 10}, "Glare": {"id": 0x89, "pp": 30}, "Dream Eater": {"id": 0x8A, "pp": 15}, "Poison Gas": {"id": 0x8B, "pp": 40}, "Barrage": {"id": 0x8C, "pp": 20},
            "Leech Life": {"id": 0x8D, "pp": 10}, "Lovely Kiss": {"id": 0x8E, "pp": 10}, "Sky Attack": {"id": 0x8F, "pp": 5}, "Transform": {"id": 0x90, "pp": 10}, "Bubble": {"id": 0x91, "pp": 30},
            "Dizzy Punch": {"id": 0x92, "pp": 10}, "Spore": {"id": 0x93, "pp": 15}, "Flash": {"id": 0x94, "pp": 20}, "Psywave": {"id": 0x95, "pp": 15}, "Splash": {"id": 0x96, "pp": 40},
            "Acid Armor": {"id": 0x97, "pp": 20}, "Crabhammer": {"id": 0x98, "pp": 10}, "Explosion": {"id": 0x99, "pp": 5}, "Fury Swipes": {"id": 0x9A, "pp": 15}, "Bonemerang": {"id": 0x9B, "pp": 10},
            "Rest": {"id": 0x9C, "pp": 10}, "Rock Slide": {"id": 0x9D, "pp": 10}, "Hyper Fang": {"id": 0x9E, "pp": 15}, "Sharpen": {"id": 0x9F, "pp": 30}, "Conversion": {"id": 0xA0, "pp": 30},
            "Tri Attack": {"id": 0xA1, "pp": 10}, "Super Fang": {"id": 0xA2, "pp": 10}, "Slash": {"id": 0xA3, "pp": 20}, "Substitute": {"id": 0xA4, "pp": 10}, "Struggle": {"id": 0xA5, "pp": 1}
        }
        
        self.TYPEMAP = {
            "Normal": 0x00, "Fighting": 0x01, "Flying": 0x02, "Poison": 0x03,
            "Ground": 0x04, "Rock": 0x05, "Bird": 0x06, "Bug": 0x07,
            "Ghost": 0x08, "Fire": 0x14, "Water": 0x15, "Grass": 0x16,
            "Electric": 0x17, "Psychic": 0x18, "Ice": 0x19, "Dragon": 0x1A
        }
        
        self.SPECIES_NAMES = {
            0x01: "Rhydon", 0x02: "Kangaskhan", 0x03: "Nidoran♂", 0x04: "Clefairy", 0x05: "Spearow",
            0x06: "Voltorb", 0x07: "Nidoking", 0x08: "Slowbro", 0x09: "Ivysaur", 0x0A: "Exeggutor",
            0x0B: "Lickitung", 0x0C: "Exeggcute", 0x0D: "Grimer", 0x0E: "Gengar", 0x0F: "Nidoran♀",
            0x10: "Nidoqueen", 0x11: "Cubone", 0x12: "Rhyhorn", 0x13: "Lapras", 0x14: "Arcanine",
            0x15: "Mew", 0x16: "Gyarados", 0x17: "Shellder", 0x18: "Tentacool", 0x19: "Gastly",
            0x1A: "Scyther", 0x1B: "Staryu", 0x1C: "Blastoise", 0x1D: "Pinsir", 0x1E: "Tangela",
            0x21: "Growlithe", 0x22: "Onix", 0x23: "Fearow", 0x24: "Pidgey", 0x25: "Slowpoke",
            0x26: "Kadabra", 0x27: "Graveler", 0x28: "Chansey", 0x29: "Machoke", 0x2A: "Mr. Mime",
            0x2B: "Hitmonlee", 0x2C: "Hitmonchan", 0x2D: "Arbok", 0x2E: "Parasect", 0x2F: "Psyduck",
            0x30: "Drowzee", 0x31: "Golem", 0x33: "Magmar", 0x35: "Electabuzz", 0x36: "Magneton",
            0x37: "Koffing", 0x39: "Mankey", 0x3A: "Seel", 0x3B: "Diglett", 0x3C: "Tauros",
            0x40: "Farfetch'd", 0x41: "Venonat", 0x42: "Dragonite", 0x46: "Doduo", 0x47: "Poliwag",
            0x48: "Jynx", 0x49: "Moltres", 0x4A: "Articuno", 0x4B: "Zapdos", 0x4C: "Ditto",
            0x4D: "Meowth", 0x4E: "Krabby", 0x52: "Vulpix", 0x53: "Ninetales", 0x54: "Pikachu",
            0x55: "Raichu", 0x58: "Dratini", 0x59: "Dragonair", 0x5A: "Kabuto", 0x5B: "Kabutops",
            0x5C: "Horsea", 0x5D: "Seadra", 0x60: "Sandshrew", 0x61: "Sandslash", 0x62: "Omanyte",
            0x63: "Omastar", 0x64: "Jigglypuff", 0x65: "Wigglytuff", 0x66: "Eevee", 0x67: "Flareon",
            0x68: "Jolteon", 0x69: "Vaporeon", 0x6A: "Machop", 0x6B: "Zubat", 0x6C: "Ekans",
            0x6D: "Paras", 0x6E: "Poliwhirl", 0x6F: "Poliwrath", 0x70: "Weedle", 0x71: "Kakuna",
            0x72: "Beedrill", 0x74: "Dodrio", 0x75: "Primeape", 0x76: "Dugtrio", 0x77: "Venomoth",
            0x78: "Dewgong", 0x7B: "Caterpie", 0x7C: "Metapod", 0x7D: "Butterfree", 0x7E: "Machamp",
            0x80: "Golduck", 0x81: "Hypno", 0x82: "Golbat", 0x83: "Mewtwo", 0x84: "Snorlax",
            0x85: "Magikarp", 0x88: "Muk", 0x8A: "Kingler", 0x8B: "Cloyster", 0x8D: "Electrode",
            0x8E: "Clefable", 0x8F: "Weezing", 0x90: "Persian", 0x91: "Marowak", 0x93: "Haunter",
            0x94: "Abra", 0x95: "Alakazam", 0x96: "Pidgeotto", 0x97: "Pidgeot", 0x98: "Starmie",
            0x99: "Bulbasaur", 0x9A: "Venusaur", 0x9B: "Tentacruel", 0x9D: "Goldeen", 0x9E: "Seaking",
            0xA3: "Ponyta", 0xA4: "Rapidash", 0xA5: "Rattata", 0xA6: "Raticate", 0xA7: "Nidorino",
            0xA8: "Nidorina", 0xA9: "Geodude", 0xAA: "Porygon", 0xAB: "Aerodactyl", 0xAD: "Magnemite",
            0xB0: "Charmander", 0xB1: "Squirtle", 0xB2: "Charmeleon", 0xB3: "Wartortle", 0xB4: "Charizard",
            0xB9: "Oddish", 0xBA: "Gloom", 0xBB: "Vileplume", 0xBC: "Bellsprout", 0xBD: "Weepinbell",
            0xBE: "Victreebel"
        }
        
        # Create reverse lookup for species data
        self.SPECIES_DATA = {}
        for species_id, name in self.SPECIES_NAMES.items():
            self.SPECIES_DATA[name] = species_id
            
        self.reset_all()
        
    def reset_all(self):
        """Reset all battle state variables"""
        self.state = {
            "playerFirst": True,
            "flinched": False,
            "playerDamage": 0,
            "playerCrit": 0,
            "playerMoveMiss": 0,
            "playerStatDownEffect": False,
            "playerFullyParalyzed": False,
            "playerHitConfuse": False,
            "playerStatused": False,
            "playerWokeUp": False,
            "playerSnappedOut": False,
            "enemyDamage": 0,
            "enemyCrit": 0,
            "enemyMoveMiss": 0,
            "enemyStatDownEffect": False,
            "enemyFullyParalyzed": False,
            "enemyHitConfuse": False,
            "enemyStatused": False,
            "enemyWokeUp": False,
            "enemySnappedOut": False
        }
        
        # HP tracking
        self.player_prev_hp_pct = 100
        self.enemy_prev_hp_pct = 100
        self.player_real_max_hp = 0
        self.enemy_real_max_hp = 0
        
        # Track exact HP from |request| messages
        self.player_exact_hp = {"current": 0, "max": 0}
        self.enemy_exact_hp = {"current": 0, "max": 0}
        
        # Pokemon data structures
        self.player_pokemon = self._create_empty_pokemon()
        self.enemy_pokemon = self._create_empty_pokemon()
        
        # Turn tracking
        self.turn_moves = []
        self.current_turn = "0"
        self.turn_started = False
        self.clear_wakeup_flags_next_turn = False
        
    def _create_empty_pokemon(self):
        """Create an empty Pokemon data structure"""
        return {
            "nickname": "",
            "species": 0x00,
            "species_name": "",
            "currentHP": 0,
            "maxHP": 0,
            "level": 100,
            "type1": 0x00,
            "type2": 0x00,
            "moves": [0, 0, 0, 0],
            "movesPP": [0, 0, 0, 0],
            "move_names": ["", "", "", ""],
            "attack": 0,
            "defense": 0,
            "speed": 0,
            "special": 0
        }
        
    def reset_turn_variables(self):
        """Reset per-turn battle state variables"""
        self.state['playerCrit'] = 0
        self.state['playerMoveMiss'] = 0
        self.state['playerFullyParalyzed'] = False
        self.state['playerHitConfuse'] = False
        self.state['playerStatused'] = False
        self.state['playerDamage'] = 0
        self.state['playerStatDownEffect'] = False
        
        self.state['enemyCrit'] = 0
        self.state['enemyMoveMiss'] = 0
        self.state['enemyFullyParalyzed'] = False
        self.state['enemyHitConfuse'] = False
        self.state['enemyStatused'] = False
        self.state['enemyDamage'] = 0
        self.state['enemyStatDownEffect'] = False
        
        self.state['flinched'] = False
        self.turn_moves = []
        
    def update_enemy_pokemon(self, name, current_hp=None, max_hp=None, level=100):
        """Update enemy Pokemon data when it switches in"""
        clean_name = name.replace("♂", "♂").replace("♀", "♀")  # Handle unicode
        
        self.enemy_pokemon["nickname"] = clean_name
        self.enemy_pokemon["species_name"] = clean_name
        self.enemy_pokemon["level"] = level
        
        # Get species ID if available
        if clean_name in self.SPECIES_DATA:
            self.enemy_pokemon["species"] = self.SPECIES_DATA[clean_name]
        
        # Update HP if provided
        if current_hp is not None:
            self.enemy_pokemon["currentHP"] = current_hp
        if max_hp is not None:
            self.enemy_pokemon["maxHP"] = max_hp
            
        # Reset moves when new Pokemon switches in - always exactly 4 zeros
        self.enemy_pokemon["moves"] = [0, 0, 0, 0]
        self.enemy_pokemon["movesPP"] = [0, 0, 0, 0]
        self.enemy_pokemon["move_names"] = ["", "", "", ""]
        
    def update_player_pokemon(self, name, current_hp=None, max_hp=None, level=100):
        """Update player Pokemon data when it switches in"""
        clean_name = name.replace("♂", "♂").replace("♀", "♀")  # Handle unicode
        
        self.player_pokemon["nickname"] = clean_name
        self.player_pokemon["species_name"] = clean_name
        self.player_pokemon["level"] = level
        
        # Get species ID if available
        if clean_name in self.SPECIES_DATA:
            self.player_pokemon["species"] = self.SPECIES_DATA[clean_name]
        
        # Update HP if provided
        if current_hp is not None:
            self.player_pokemon["currentHP"] = current_hp
        if max_hp is not None:
            self.player_pokemon["maxHP"] = max_hp
            
        # Reset moves when new Pokemon switches in - always exactly 4 zeros
        self.player_pokemon["moves"] = [0, 0, 0, 0]
        self.player_pokemon["movesPP"] = [0, 0, 0, 0]
        self.player_pokemon["move_names"] = ["", "", "", ""]
        
    def add_enemy_move(self, move_name):
        """Add a move to enemy Pokemon's moveset"""
        if move_name in self.MOVE_DATA:
            move_data = self.MOVE_DATA[move_name]
            move_id = move_data["id"]
            move_pp = int(move_data["pp"] * 1.6)  # Multiply by 1.6 for actual PP
            
            # Check if move already exists
            for i, existing_move in enumerate(self.enemy_pokemon["moves"]):
                if existing_move == move_id:
                    # Move already known, just decrement PP
                    if self.enemy_pokemon["movesPP"][i] > 0:
                        self.enemy_pokemon["movesPP"][i] -= 1
                    return i
            
            # Add new move to first empty slot
            for i in range(4):
                if self.enemy_pokemon["moves"][i] == 0:
                    self.enemy_pokemon["moves"][i] = move_id
                    self.enemy_pokemon["movesPP"][i] = move_pp - 1  # Used one PP
                    self.enemy_pokemon["move_names"][i] = move_name
                    return i
                    
        return -1  # Move not found or no space
        
    def add_player_move(self, move_name):
        """Add a move to player Pokemon's moveset"""
        if move_name in self.MOVE_DATA:
            move_data = self.MOVE_DATA[move_name]
            move_id = move_data["id"]
            move_pp = int(move_data["pp"] * 1.6)  # Multiply by 1.6 for actual PP
            
            # Check if move already exists
            for i, existing_move in enumerate(self.player_pokemon["moves"]):
                if existing_move == move_id:
                    # Move already known, just decrement PP
                    if self.player_pokemon["movesPP"][i] > 0:
                        self.player_pokemon["movesPP"][i] -= 1
                    return i
            
            # Add new move to first empty slot
            for i in range(4):
                if self.player_pokemon["moves"][i] == 0:
                    self.player_pokemon["moves"][i] = move_id
                    self.player_pokemon["movesPP"][i] = move_pp - 1  # Used one PP
                    self.player_pokemon["move_names"][i] = move_name
                    return i
                    
        return -1  # Move not found or no space

    def get_state_display(self):
        """Get formatted battle state display"""
        pokemon_info = f"""=== POKEMON DATA ===
PLAYER: {self.player_pokemon['species_name']} (L{self.player_pokemon['level']})
HP: {self.player_pokemon['currentHP']}/{self.player_pokemon['maxHP']}
Moves: {', '.join([name for name in self.player_pokemon['move_names'] if name])}
Move PP: {[pp for pp in self.player_pokemon['movesPP'] if pp > 0]}

ENEMY: {self.enemy_pokemon['species_name']} (L{self.enemy_pokemon['level']})
HP: {self.enemy_pokemon['currentHP']}/{self.enemy_pokemon['maxHP']}
Moves: {', '.join([name for name in self.enemy_pokemon['move_names'] if name])}
Move PP: {[pp for pp in self.enemy_pokemon['movesPP'] if pp > 0]}

=== BATTLE STATE (Last Turn Results) ===
Player First: {self.state['playerFirst']}
Flinched: {self.state['flinched']}

PLAYER:
Damage: {self.state['playerDamage']} (dealt to enemy)
Crit: {self.state['playerCrit']} (scored by player)
Move Miss: {self.state['playerMoveMiss']}
Stat Down Effect: {self.state['playerStatDownEffect']} (caused enemy stat drop)
Fully Paralyzed: {self.state['playerFullyParalyzed']}
Hit by Confusion: {self.state['playerHitConfuse']}
Statused: {self.state['playerStatused']} (inflicted status on enemy)
Woke Up: {self.state['playerWokeUp']}
Snapped Out: {self.state['playerSnappedOut']}

ENEMY:
Damage: {self.state['enemyDamage']} (dealt to player)
Crit: {self.state['enemyCrit']} (scored by enemy)
Move Miss: {self.state['enemyMoveMiss']}
Stat Down Effect: {self.state['enemyStatDownEffect']} (caused player stat drop)
Fully Paralyzed: {self.state['enemyFullyParalyzed']}
Hit by Confusion: {self.state['enemyHitConfuse']}
Statused: {self.state['enemyStatused']} (inflicted status on player)
Woke Up: {self.state['enemyWokeUp']}
Snapped Out: {self.state['enemySnappedOut']}"""
        
        return pokemon_info