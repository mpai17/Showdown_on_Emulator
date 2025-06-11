import requests
import math

class PokemonAPI:
    def __init__(self):
        self.api_url = "https://play.pokemonshowdown.com/data/pokedex.json"
        
    def get_pokemon_name_from_line(self, line):
        """Extract Pokemon name from a battle line"""
        if '|' in line:
            parts = line.split('|')
            for part in parts:
                if ':' in part and any(char.isalpha() for char in part):
                    # Extract name after colon (e.g., "p1a: Alakazam" -> "Alakazam")
                    name_part = part.split(':')[-1].strip()
                    if name_part and not name_part.startswith('p'):
                        return name_part.lower()
                elif ',' in part and any(char.isalpha() for char in part):
                    # Extract name before comma (e.g., "Alakazam, L50, M" -> "Alakazam")
                    name_part = part.split(',')[0].strip()
                    if name_part and not name_part.startswith('p') and len(name_part) > 2:
                        return name_part.lower()
        return None

    async def query_pokemon_stats(self, pokemon_name, level=100):
        """Query Pokemon Showdown for Pokemon base stats and calculate max HP"""
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                pokedex_data = response.json()
                
                pokemon_key = pokemon_name.lower().replace(' ', '').replace('-', '')
                
                if pokemon_key in pokedex_data:
                    pokemon = pokedex_data[pokemon_key]
                    base_hp = pokemon.get('baseStats', {}).get('hp', 50)
                    
                    # Gen 1 HP formula: floor((((Base + IV) × 2 + floor(ceil(sqrt(EV)) ÷ 4)) × Level) ÷ 100) + Level + 10
                    max_iv = 15  # Gen 1 max IV
                    max_ev = 65535  # Gen 1 theoretical max EV
                    
                    # Calculate the EV component: floor(ceil(sqrt(EV)) / 4)
                    ev_component = math.floor(math.ceil(math.sqrt(max_ev)) / 4)
                    
                    # Gen 1 HP formula
                    max_hp = math.floor((((base_hp + max_iv) * 2 + ev_component) * level) / 100) + level + 10
                    
                    return max_hp, base_hp
                    
        except Exception as e:
            print(f"Error querying Pokemon stats for {pokemon_name}: {str(e)}")
        
        return None, None