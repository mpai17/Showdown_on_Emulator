import json
import asyncio
from pokemon_api import PokemonAPI

class BattleParser:
    def __init__(self, battle_state, pokemon_api, log_callback):
        self.battle_state = battle_state
        self.pokemon_api = pokemon_api
        self.log = log_callback
        
    def parse_gen1_battle_data(self, line):
        """Parse line for Gen 1 specific battle mechanics"""
        try:
            # Track move order to determine speed ties
            if '|move|' in line:
                self._parse_move(line)
                
            # Critical hit detection
            elif '|-crit|' in line:
                self._parse_critical_hit(line)
                
            # Miss detection
            elif '|-miss|' in line:
                self._parse_miss(line)
                
            # Damage parsing to extract exact damage numbers
            elif '|-damage|' in line:
                self._parse_damage(line)
                
            # Status condition detection
            elif '|-status|' in line:
                self._parse_status(line)
                
            # Status recovery
            elif '|-curestatus|' in line:
                self._parse_status_recovery(line)
                
            # Full paralysis and sleep detection
            elif '|cant|' in line:
                self._parse_cant_move(line)
                
            # Confusion hit detection
            elif '|-activate|' in line and 'confusion' in line:
                self._parse_confusion_activate(line)
                
            # Check for confusion in various message formats
            elif 'hurt itself in its confusion' in line.lower() or '[from] confusion' in line:
                self._parse_confusion_damage(line)
                
            # End confusion
            elif '|-end|' in line and 'confusion' in line:
                self._parse_confusion_end(line)
                
            # Stat changes (both decreases and increases)
            elif '|-unboost|' in line or '|-boost|' in line:
                self._parse_stat_change(line)
                
            # Turn tracking
            elif '|turn|' in line:
                self._parse_turn(line)
                
            # Switch/Drag events
            elif '|switch|' in line or '|drag|' in line:
                self._parse_switch(line)
                
            # Request messages for exact HP
            elif '|request|' in line:
                self._parse_request(line)
                
            # Faint detection
            elif '|faint|' in line:
                self._parse_faint(line)
                
            # Heal detection for HP updates
            elif '|-heal|' in line:
                self._parse_heal(line)
                
        except Exception as e:
            self.log(f"Error parsing battle data: {str(e)}", "ERROR")
            
    def _parse_move(self, line):
        """Parse move messages to track turn order"""
        parts = line.split('|')
        if len(parts) >= 3:
            player = parts[2]
            move = parts[3] if len(parts) > 3 else "unknown"
            
            # Initialize turn_moves if this is the first move of a new turn
            if not hasattr(self.battle_state, 'turn_moves'):
                self.battle_state.turn_moves = []
            
            self.battle_state.turn_moves.append(player)
            
            # If this is the first move of the turn, reset turn-specific values and determine speed
            if len(self.battle_state.turn_moves) == 1:
                # Reset all turn-specific battle state values at start of new turn
                self.battle_state.state['playerCrit'] = 0
                self.battle_state.state['playerMoveMiss'] = 0
                self.battle_state.state['playerFullyParalyzed'] = False
                self.battle_state.state['playerHitConfuse'] = False
                self.battle_state.state['playerStatused'] = False
                self.battle_state.state['playerDamage'] = 0
                self.battle_state.state['playerStatDownEffect'] = False
                self.battle_state.state['playerMoveUsed'] = ""
                self.battle_state.state['playerFainted'] = False
                
                self.battle_state.state['enemyCrit'] = 0
                self.battle_state.state['enemyMoveMiss'] = 0
                self.battle_state.state['enemyFullyParalyzed'] = False
                self.battle_state.state['enemyHitConfuse'] = False
                self.battle_state.state['enemyStatused'] = False
                self.battle_state.state['enemyDamage'] = 0
                self.battle_state.state['enemyStatDownEffect'] = False
                self.battle_state.state['enemyMoveUsed'] = ""
                self.battle_state.state['enemyFainted'] = False
                
                self.battle_state.state['flinched'] = False
                
                if 'p1a' in player:
                    self.battle_state.state['playerFirst'] = True
                    self.log("Player moved first (won speed tie or faster)", "BATTLE_STATE")
                elif 'p2a' in player:
                    self.battle_state.state['playerFirst'] = False
                    self.log("Enemy moved first (won speed tie or faster)", "BATTLE_STATE")
            
            # Track moves used by each Pokemon and set current turn move
            if 'p1a' in player and move != "unknown":
                self.battle_state.state['playerMoveUsed'] = move
                move_slot = self.battle_state.add_player_move(move)
                if move_slot >= 0:
                    self.log(f"Player used {move} (slot {move_slot + 1}, PP remaining: {self.battle_state.player_pokemon['movesPP'][move_slot]})", "BATTLE_STATE")
                else:
                    self.log(f"Player used {move} (move not in database or no moveslot available)", "BATTLE_STATE")
            elif 'p2a' in player and move != "unknown":
                self.battle_state.state['enemyMoveUsed'] = move
                move_slot = self.battle_state.add_enemy_move(move)
                if move_slot >= 0:
                    self.log(f"Enemy used {move} (slot {move_slot + 1}, PP remaining: {self.battle_state.enemy_pokemon['movesPP'][move_slot]})", "BATTLE_STATE")
                else:
                    self.log(f"Enemy used {move} (move not in database or no moveslot available)", "BATTLE_STATE")
            
            self.log(f"Move: {player} used {move}", "BATTLE_STATE")
            
    def _parse_critical_hit(self, line):
        """Parse critical hit messages"""
        parts = line.split('|')
        if len(parts) >= 3:
            target = parts[2]  # This is the Pokemon that GOT crit
            if 'p1a' in target:
                self.battle_state.state['enemyCrit'] = 1
                self.log("Enemy scored critical hit on Player!", "BATTLE_STATE")
            elif 'p2a' in target:
                self.battle_state.state['playerCrit'] = 1
                self.log("Player scored critical hit on Enemy!", "BATTLE_STATE")
                
    def _parse_miss(self, line):
        """Parse miss messages"""
        parts = line.split('|')
        if len(parts) >= 3:
            attacker = parts[2]
            if 'p1a' in attacker:
                self.battle_state.state['playerMoveMiss'] = 1
                self.log("Player move missed!", "BATTLE_STATE")
            elif 'p2a' in attacker:
                self.battle_state.state['enemyMoveMiss'] = 1
                self.log("Enemy move missed!", "BATTLE_STATE")
                
    def _parse_damage(self, line):
        """Parse damage messages"""
        parts = line.split('|')
        if len(parts) >= 4:
            target = parts[2]
            damage_info = parts[3]
            
            # Check if damage is from confusion
            is_confusion_damage = '[from] confusion' in line or 'confusion' in line.lower()
            
            # Handle faint format: "0 fnt"
            if 'fnt' in damage_info:
                current_hp = 0
                # Use previous HP as max HP for calculation purposes
                if 'p1a' in target:
                    max_hp = 100  # Will be handled in damage calculation
                    self._handle_player_damage(current_hp, max_hp, is_confusion_damage, is_faint=True)
                elif 'p2a' in target:
                    max_hp = 100  # Will be handled in damage calculation  
                    self._handle_enemy_damage(current_hp, max_hp, is_confusion_damage, is_faint=True)
            elif '/' in damage_info:
                try:
                    current_hp_str, max_hp_str = damage_info.split('/')
                    current_hp = int(current_hp_str.strip())
                    max_hp = int(max_hp_str.split()[0].strip())
                    
                    if 'p1a' in target:
                        self._handle_player_damage(current_hp, max_hp, is_confusion_damage, is_faint=False)
                    elif 'p2a' in target:
                        self._handle_enemy_damage(current_hp, max_hp, is_confusion_damage, is_faint=False)
                        
                except ValueError:
                    pass
                    
    def _handle_player_damage(self, current_hp, max_hp, is_confusion_damage, is_faint=False):
        """Handle damage dealt to player"""
        if is_faint:
            # For faint scenarios, damage is exactly the previous HP
            actual_damage = 0
            
            # Priority 1: Use the exact HP tracking current value if available
            if (hasattr(self.battle_state, 'player_exact_hp') and 
                self.battle_state.player_exact_hp["current"] > 0 and
                self.battle_state.player_exact_hp["current"] != self.battle_state.player_exact_hp["max"]):
                actual_damage = self.battle_state.player_exact_hp["current"]
                self.log(f"Using exact HP tracking: {actual_damage}", "BATTLE_STATE")
            
            # Priority 2: Use previous display HP converted to real HP
            elif (hasattr(self.battle_state, 'player_prev_hp_display') and 
                  self.battle_state.player_prev_hp_display > 0 and
                  self.battle_state.player_real_max_hp > 0):
                if self.battle_state.player_prev_hp_display <= 100:
                    # Convert percentage to actual HP
                    actual_damage = int((self.battle_state.player_prev_hp_display / 100.0) * self.battle_state.player_real_max_hp)
                    self.log(f"Using percentage conversion: {self.battle_state.player_prev_hp_display}% of {self.battle_state.player_real_max_hp} = {actual_damage}", "BATTLE_STATE")
                else:
                    # Already real HP
                    actual_damage = self.battle_state.player_prev_hp_display
                    self.log(f"Using real HP directly: {actual_damage}", "BATTLE_STATE")
            
            # Priority 3: Use Pokemon data structure current HP
            elif self.battle_state.player_pokemon["currentHP"] > 0:
                actual_damage = self.battle_state.player_pokemon["currentHP"]
                self.log(f"Using Pokemon data current HP: {actual_damage}", "BATTLE_STATE")
            
            if actual_damage > 0:
                if not is_confusion_damage:
                    self.battle_state.state['enemyDamage'] = actual_damage
                    self.log(f"Enemy dealt {actual_damage} damage to player - PLAYER FAINTED!", "BATTLE_STATE")
                else:
                    self.battle_state.state['playerHitConfuse'] = True
                    self.log(f"Player hit itself in confusion for {actual_damage} damage - PLAYER FAINTED!", "BATTLE_STATE")
            
            # Update Pokemon HP
            self.battle_state.player_pokemon["currentHP"] = 0
            self.battle_state.player_prev_hp_display = 0
            # Reset exact HP tracking
            if hasattr(self.battle_state, 'player_exact_hp'):
                self.battle_state.player_exact_hp["current"] = 0
            return
        
        # Normal damage handling (non-faint)
        damage_display = self.battle_state.player_prev_hp_display - current_hp if hasattr(self.battle_state, 'player_prev_hp_display') else 0
        
        # Update Pokemon HP in data structure
        self.battle_state.player_pokemon["currentHP"] = current_hp
        if max_hp > 100:
            self.battle_state.player_pokemon["maxHP"] = max_hp
        
        # Update exact HP tracking if we have real HP values
        if max_hp > 100:
            # Real HP display - update exact HP tracking
            if hasattr(self.battle_state, 'player_exact_hp'):
                self.battle_state.player_exact_hp["current"] = current_hp
                self.battle_state.player_exact_hp["max"] = max_hp
            self.battle_state.player_real_max_hp = max_hp
        elif self.battle_state.player_real_max_hp > 0:
            # Percentage display - calculate and update exact HP
            if hasattr(self.battle_state, 'player_exact_hp'):
                exact_current = int((current_hp / 100.0) * self.battle_state.player_real_max_hp)
                self.battle_state.player_exact_hp["current"] = exact_current
                self.battle_state.player_exact_hp["max"] = self.battle_state.player_real_max_hp
        
        # Only calculate damage if we have server-queried max HP
        if self.battle_state.player_real_max_hp > 0:
            if max_hp == 100:  # Percentage display
                actual_damage = int((damage_display / 100.0) * self.battle_state.player_real_max_hp)
            else:  # Real HP display
                actual_damage = damage_display
                self.battle_state.player_real_max_hp = max_hp
            
            if actual_damage > 0:
                if is_confusion_damage:
                    self.battle_state.state['playerHitConfuse'] = True
                    self.log(f"Player hit itself in confusion for {actual_damage} damage ({current_hp}/{max_hp} remaining)", "BATTLE_STATE")
                else:
                    self.battle_state.state['enemyDamage'] = actual_damage
                    self.log(f"Enemy dealt {actual_damage} damage to player ({current_hp}/{max_hp} remaining)", "BATTLE_STATE")
        else:
            self.log(f"Player took {damage_display}% damage (awaiting server HP data)", "BATTLE_STATE")
            
        self.battle_state.player_prev_hp_display = current_hp
        
    def _handle_enemy_damage(self, current_hp, max_hp, is_confusion_damage, is_faint=False):
        """Handle damage dealt to enemy"""
        if is_faint:
            # For faint scenarios, damage is exactly the previous HP
            actual_damage = 0
            
            # Use simplified 100 HP system - just use the previous percentage HP
            if hasattr(self.battle_state, 'enemy_prev_hp_display') and self.battle_state.enemy_prev_hp_display > 0:
                actual_damage = self.battle_state.enemy_prev_hp_display
                self.log(f"Using simplified HP system: {actual_damage}", "BATTLE_STATE")
            
            if actual_damage > 0:
                if not is_confusion_damage:
                    self.battle_state.state['playerDamage'] = actual_damage
                    self.log(f"Player dealt {actual_damage} damage to enemy - ENEMY FAINTED!", "BATTLE_STATE")
                else:
                    self.battle_state.state['enemyHitConfuse'] = True
                    self.log(f"Enemy hit itself in confusion for {actual_damage} damage - ENEMY FAINTED!", "BATTLE_STATE")
            
            # Update Pokemon HP
            self.battle_state.enemy_pokemon["currentHP"] = 0
            self.battle_state.enemy_prev_hp_display = 0
            return
        
        # Normal damage handling (non-faint) - use simplified 100 HP system
        damage_display = self.battle_state.enemy_prev_hp_display - current_hp if hasattr(self.battle_state, 'enemy_prev_hp_display') else 0
        
        # Update Pokemon HP in data structure using percentage values
        self.battle_state.enemy_pokemon["currentHP"] = current_hp
        self.battle_state.enemy_pokemon["maxHP"] = 100  # Always use 100 for simplicity
        
        # For enemy, always use the percentage damage as actual damage (simplified system)
        if damage_display > 0:
            if is_confusion_damage:
                self.battle_state.state['enemyHitConfuse'] = True
                self.log(f"Enemy hit itself in confusion for {damage_display} damage ({current_hp}/100 remaining)", "BATTLE_STATE")
            else:
                self.battle_state.state['playerDamage'] = damage_display
                self.log(f"Player dealt {damage_display} damage to enemy ({current_hp}/100 remaining)", "BATTLE_STATE")
            
        self.battle_state.enemy_prev_hp_display = current_hp
        
    def _parse_status(self, line):
        """Parse status condition messages"""
        parts = line.split('|')
        if len(parts) >= 4:
            target = parts[2]
            status = parts[3]
            
            if 'p1a' in target:
                self.battle_state.state['enemyStatused'] = True
                self.log(f"Enemy inflicted {status} status on player", "BATTLE_STATE")
            elif 'p2a' in target:
                self.battle_state.state['playerStatused'] = True
                self.log(f"Player inflicted {status} status on enemy", "BATTLE_STATE")
                
    def _parse_status_recovery(self, line):
        """Parse status recovery messages"""
        parts = line.split('|')
        if len(parts) >= 4:
            target = parts[2]
            status = parts[3]
            
            # Initialize turn_moves if not already done
            if not hasattr(self.battle_state, 'turn_moves'):
                self.battle_state.turn_moves = []
            
            # If this is the first action of the turn, reset battle state values and determine turn order
            if len(self.battle_state.turn_moves) == 0:
                # Reset all turn-specific battle state values at start of new turn
                self.battle_state.state['playerCrit'] = 0
                self.battle_state.state['playerMoveMiss'] = 0
                self.battle_state.state['playerFullyParalyzed'] = False
                self.battle_state.state['playerHitConfuse'] = False
                self.battle_state.state['playerStatused'] = False
                self.battle_state.state['playerDamage'] = 0
                self.battle_state.state['playerStatDownEffect'] = False
                self.battle_state.state['playerMoveUsed'] = ""
                self.battle_state.state['playerFainted'] = False
                
                self.battle_state.state['enemyCrit'] = 0
                self.battle_state.state['enemyMoveMiss'] = 0
                self.battle_state.state['enemyFullyParalyzed'] = False
                self.battle_state.state['enemyHitConfuse'] = False
                self.battle_state.state['enemyStatused'] = False
                self.battle_state.state['enemyDamage'] = 0
                self.battle_state.state['enemyStatDownEffect'] = False
                self.battle_state.state['enemyMoveUsed'] = ""
                self.battle_state.state['enemyFainted'] = False
                
                self.battle_state.state['flinched'] = False
                
                # Track who acted first (status recovery counts as an action)
                if 'p1a' in target:
                    self.battle_state.state['playerFirst'] = True
                    self.log("Player acted first (status recovery)", "BATTLE_STATE")
                elif 'p2a' in target:
                    self.battle_state.state['playerFirst'] = False
                    self.log("Enemy acted first (status recovery)", "BATTLE_STATE")
            
            # Track this as a turn action
            self.battle_state.turn_moves.append(target)
            
            if 'p1a' in target and status == 'slp':
                self.battle_state.state['playerWokeUp'] = True
                self.log("Player woke up from sleep", "BATTLE_STATE")
            elif 'p2a' in target and status == 'slp':
                self.battle_state.state['enemyWokeUp'] = True
                self.log("Enemy woke up from sleep", "BATTLE_STATE")
                
    def _parse_cant_move(self, line):
        """Parse can't move messages (paralysis, sleep, etc.)"""
        parts = line.split('|')
        if len(parts) >= 4:
            pokemon = parts[2]
            reason = parts[3]
            
            # Initialize turn_moves if not already done
            if not hasattr(self.battle_state, 'turn_moves'):
                self.battle_state.turn_moves = []
            
            # If this is the first "can't move" of the turn, reset battle state values
            if len(self.battle_state.turn_moves) == 0:
                # Reset all turn-specific battle state values at start of new turn
                self.battle_state.state['playerCrit'] = 0
                self.battle_state.state['playerMoveMiss'] = 0
                self.battle_state.state['playerFullyParalyzed'] = False
                self.battle_state.state['playerHitConfuse'] = False
                self.battle_state.state['playerStatused'] = False
                self.battle_state.state['playerDamage'] = 0
                self.battle_state.state['playerStatDownEffect'] = False
                self.battle_state.state['playerMoveUsed'] = ""
                self.battle_state.state['playerFainted'] = False
                
                self.battle_state.state['enemyCrit'] = 0
                self.battle_state.state['enemyMoveMiss'] = 0
                self.battle_state.state['enemyFullyParalyzed'] = False
                self.battle_state.state['enemyHitConfuse'] = False
                self.battle_state.state['enemyStatused'] = False
                self.battle_state.state['enemyDamage'] = 0
                self.battle_state.state['enemyStatDownEffect'] = False
                self.battle_state.state['enemyMoveUsed'] = ""
                self.battle_state.state['enemyFainted'] = False
                
                self.battle_state.state['flinched'] = False
            
            # Track who would have moved first (even if they can't move)
            self.battle_state.turn_moves.append(pokemon)
            if len(self.battle_state.turn_moves) == 1:
                if 'p1a' in pokemon:
                    self.battle_state.state['playerFirst'] = True
                    self.log("Player would have moved first (but can't move)", "BATTLE_STATE")
                elif 'p2a' in pokemon:
                    self.battle_state.state['playerFirst'] = False
                    self.log("Enemy would have moved first (but can't move)", "BATTLE_STATE")
            
            # Set the specific paralysis/sleep flags
            if reason == 'par':
                if 'p1a' in pokemon:
                    self.battle_state.state['playerFullyParalyzed'] = True
                    self.log("Player is fully paralyzed!", "BATTLE_STATE")
                elif 'p2a' in pokemon:
                    self.battle_state.state['enemyFullyParalyzed'] = True
                    self.log("Enemy is fully paralyzed!", "BATTLE_STATE")
            elif reason == 'slp':
                if 'p1a' in pokemon:
                    self.log("Player is asleep and can't move!", "BATTLE_STATE")
                elif 'p2a' in pokemon:
                    self.log("Enemy is asleep and can't move!", "BATTLE_STATE")
                    
    def _parse_confusion_activate(self, line):
        """Parse confusion activation messages"""
        parts = line.split('|')
        if len(parts) >= 3:
            pokemon = parts[2]
            if 'p1a' in pokemon:
                self.battle_state.state['playerHitConfuse'] = True
                self.log("Player hit by confusion! [ACTIVATE]", "BATTLE_STATE")
            elif 'p2a' in pokemon:
                self.battle_state.state['enemyHitConfuse'] = True
                self.log("Enemy hit by confusion! [ACTIVATE]", "BATTLE_STATE")
                
    def _parse_confusion_damage(self, line):
        """Parse confusion self-damage messages"""
        self.log(f"Confusion damage line detected: {line}", "BATTLE_STATE")
        
        if 'p1a' in line:
            self.battle_state.state['playerHitConfuse'] = True
            self.log("Player hit by confusion! [FROM LINE]", "BATTLE_STATE")
        elif 'p2a' in line:
            self.battle_state.state['enemyHitConfuse'] = True
            self.log("Enemy hit by confusion! [FROM LINE]", "BATTLE_STATE")
            
    def _parse_confusion_end(self, line):
        """Parse end of confusion messages"""
        parts = line.split('|')
        if len(parts) >= 3:
            pokemon = parts[2]
            
            if 'p1a' in pokemon:
                self.battle_state.state['playerSnappedOut'] = True
                self.log("Player snapped out of confusion!", "BATTLE_STATE")
            elif 'p2a' in pokemon:
                self.battle_state.state['enemySnappedOut'] = True
                self.log("Enemy snapped out of confusion!", "BATTLE_STATE")
                
    def _parse_stat_change(self, line):
        """Parse stat change messages"""
        if '|-unboost|' in line:
            parts = line.split('|')
            if len(parts) >= 5:
                target = parts[2]
                stat = parts[3]
                stages = int(parts[4])
                
                if 'p2a' in target:
                    # Enemy's stat was lowered
                    self.battle_state.state['playerStatDownEffect'] = True
                    self.log(f"Player's move lowered enemy's {stat} by {stages} stage(s)! [FLAG SET]", "BATTLE_STATE")
                elif 'p1a' in target:
                    # Player's stat was lowered
                    self.battle_state.state['enemyStatDownEffect'] = True
                    self.log(f"Enemy's move lowered player's {stat} by {stages} stage(s)! [FLAG SET]", "BATTLE_STATE")
        
        # Also check for stat increases (|-boost|)
        elif '|-boost|' in line:
            parts = line.split('|')
            if len(parts) >= 5:
                target = parts[2]
                stat = parts[3]
                stages = int(parts[4])
                
                # Log stat boosts but don't set stat down flags
                if 'p1a' in target:
                    self.log(f"Player's {stat} rose by {stages} stage(s)!", "BATTLE_STATE")
                elif 'p2a' in target:
                    self.log(f"Enemy's {stat} rose by {stages} stage(s)!", "BATTLE_STATE")
                
    def _parse_turn(self, line):
        """Parse turn messages"""
        turn_num = line.split('|')[2] if len(line.split('|')) > 2 else "?"
        self.log(f"=== TURN {turn_num} ===", "BATTLE_STATE")
        
        # Log current battle state BEFORE starting new turn
        if hasattr(self.battle_state, 'turn_moves') and len(self.battle_state.turn_moves) > 0:
            self.log("=== PREVIOUS TURN SUMMARY ===", "BATTLE_STATE")
            self.log(f"Player used: {self.battle_state.state.get('playerMoveUsed', 'None')}", "BATTLE_STATE")
            self.log(f"Enemy used: {self.battle_state.state.get('enemyMoveUsed', 'None')}", "BATTLE_STATE")
            self.log(f"Player dealt {self.battle_state.state['playerDamage']} damage", "BATTLE_STATE")
            self.log(f"Enemy dealt {self.battle_state.state['enemyDamage']} damage", "BATTLE_STATE")
            self.log(f"Player stat down effect: {self.battle_state.state['playerStatDownEffect']}", "BATTLE_STATE")
            self.log(f"Enemy stat down effect: {self.battle_state.state['enemyStatDownEffect']}", "BATTLE_STATE")
            if self.battle_state.state['playerFainted']:
                self.log("Player Pokemon fainted this turn!", "BATTLE_STATE")
            if self.battle_state.state['enemyFainted']:
                self.log("Enemy Pokemon fainted this turn!", "BATTLE_STATE")
        
        self.battle_state.current_turn = turn_num
        
        # Initialize turn_moves for the new turn (values will be reset when first move is parsed)
        self.battle_state.turn_moves = []
        
        # Clear wakeup flags after they've been logged for one full turn
        if hasattr(self.battle_state, 'clear_wakeup_flags_next_turn') and self.battle_state.clear_wakeup_flags_next_turn:
            self.battle_state.state['playerWokeUp'] = False
            self.battle_state.state['enemyWokeUp'] = False
            self.battle_state.state['playerSnappedOut'] = False
            self.battle_state.state['enemySnappedOut'] = False
            self.battle_state.clear_wakeup_flags_next_turn = False
            self.log("Cleared persistent status flags from previous turn", "BATTLE_STATE")
        
        # Set flag to clear wakeup flags next turn if any are currently set
        if any([self.battle_state.state['playerWokeUp'], self.battle_state.state['enemyWokeUp'],
                self.battle_state.state['playerSnappedOut'], self.battle_state.state['enemySnappedOut']]):
            self.battle_state.clear_wakeup_flags_next_turn = True
            
    def _parse_switch(self, line):
        """Parse switch/drag messages"""
        parts = line.split('|')
        if len(parts) >= 4:
            pokemon = parts[2]
            hp_info = parts[4] if len(parts) > 4 else ""
            
            # Extract Pokemon name and queue stats lookup
            pokemon_name = self.pokemon_api.get_pokemon_name_from_line(line)
            
            if '/' in hp_info:
                try:
                    current_hp_str, max_hp_str = hp_info.split('/')
                    current_hp = int(current_hp_str.strip())
                    max_hp = int(max_hp_str.split()[0].strip())
                    
                    if 'p1a' in pokemon:
                        self._handle_player_switch(pokemon_name, current_hp, max_hp)
                    elif 'p2a' in pokemon:
                        self._handle_enemy_switch(pokemon_name, current_hp, max_hp)
                except ValueError:
                    pass
                    
        self.log(f"Switch/Drag: {line}", "BATTLE")
        
    def _handle_player_switch(self, pokemon_name, current_hp, max_hp):
        """Handle player Pokemon switch"""
        self.battle_state.player_prev_hp_display = current_hp
        
        # Update Pokemon data structure
        self.battle_state.update_player_pokemon(pokemon_name, current_hp, max_hp)
        
        if max_hp > 100:  # Real HP, not percentage
            self.battle_state.player_exact_hp = {"current": current_hp, "max": max_hp}
            self.battle_state.player_real_max_hp = max_hp
            self.log(f"Player switched in {pokemon_name} with {current_hp}/{max_hp} HP [EXACT]", "BATTLE_STATE")
        else:  # Percentage display
            if pokemon_name:
                asyncio.create_task(self._update_player_max_hp(pokemon_name))
            self.log(f"Player switched in {pokemon_name} with {current_hp}% HP (querying server...)", "BATTLE_STATE")
            
    def _handle_enemy_switch(self, pokemon_name, current_hp, max_hp):
        """Handle enemy Pokemon switch"""
        self.battle_state.enemy_prev_hp_display = current_hp
        
        # Update Pokemon data structure
        self.battle_state.update_enemy_pokemon(pokemon_name, current_hp, max_hp)
        
        if max_hp > 100:  # Real HP, not percentage
            self.battle_state.enemy_exact_hp = {"current": current_hp, "max": max_hp}
            self.battle_state.enemy_real_max_hp = max_hp
            self.log(f"Enemy switched in {pokemon_name} with {current_hp}/{max_hp} HP [EXACT]", "BATTLE_STATE")
        else:  # Percentage display
            if pokemon_name:
                asyncio.create_task(self._update_enemy_max_hp(pokemon_name))
            self.log(f"Enemy switched in {pokemon_name} with {current_hp}% HP (querying server...)", "BATTLE_STATE")
            
    async def _update_player_max_hp(self, pokemon_name):
        """Update player max HP from API"""
        try:
            queried_max_hp, base_hp = await self.pokemon_api.query_pokemon_stats(pokemon_name, level=100)
            if queried_max_hp:
                self.battle_state.player_real_max_hp = queried_max_hp
                if hasattr(self.battle_state, 'player_prev_hp_display'):
                    estimated_current = int((self.battle_state.player_prev_hp_display / 100.0) * queried_max_hp)
                    self.battle_state.player_exact_hp = {"current": estimated_current, "max": queried_max_hp}
                    self.log(f"Updated player max HP from server (L100): {queried_max_hp} (current: {estimated_current})", "BATTLE_STATE")
        except Exception as e:
            self.log(f"Error updating player max HP: {str(e)}", "ERROR")
            
    async def _update_enemy_max_hp(self, pokemon_name):
        """Update enemy max HP from API"""
        try:
            queried_max_hp, base_hp = await self.pokemon_api.query_pokemon_stats(pokemon_name, level=100)
            if queried_max_hp:
                self.battle_state.enemy_real_max_hp = queried_max_hp
                if hasattr(self.battle_state, 'enemy_prev_hp_display'):
                    estimated_current = int((self.battle_state.enemy_prev_hp_display / 100.0) * queried_max_hp)
                    self.battle_state.enemy_exact_hp = {"current": estimated_current, "max": queried_max_hp}
                    self.log(f"Updated enemy max HP from server (L100): {queried_max_hp} (current: {estimated_current})", "BATTLE_STATE")
        except Exception as e:
            self.log(f"Error updating enemy max HP: {str(e)}", "ERROR")
            
    def _parse_request(self, line):
        """Parse request messages for exact HP"""
        try:
            json_start = line.find('|request|') + 9
            json_data = line[json_start:]
            request_data = json.loads(json_data)
            
            # Extract exact HP from side pokemon data
            if 'side' in request_data and 'pokemon' in request_data['side']:
                for pokemon in request_data['side']['pokemon']:
                    if pokemon.get('active', False) and 'condition' in pokemon:
                        condition = pokemon['condition']
                        if '/' in condition:
                            # Parse exact HP values like "270/323"
                            hp_parts = condition.split('/')
                            current_hp = int(hp_parts[0])
                            max_hp = int(hp_parts[1].split()[0])  # Remove status conditions
                            
                            # Store previous HP for damage calculation
                            if self.battle_state.player_exact_hp["current"] > 0:
                                prev_hp = self.battle_state.player_exact_hp["current"]
                                damage_dealt = prev_hp - current_hp
                                
                                if damage_dealt > 0:
                                    # Player took damage, so enemy dealt it
                                    self.battle_state.state['enemyDamage'] = damage_dealt
                                    damage_pct = (damage_dealt / max_hp) * 100
                                    self.log(f"Enemy dealt {damage_dealt} damage to player ({damage_pct:.1f}% of max HP) [EXACT]", "BATTLE_STATE")
                            
                            # Update exact HP tracking
                            self.battle_state.player_exact_hp = {"current": current_hp, "max": max_hp}
                            self.battle_state.player_real_max_hp = max_hp
                            break
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # If JSON parsing fails, continue with normal processing
            pass
            
    def _parse_faint(self, line):
        """Parse faint messages"""
        parts = line.split('|')
        if len(parts) >= 3:
            pokemon = parts[2]
            
            if 'p1a' in pokemon:
                self.battle_state.state['playerFainted'] = True
                self.log("Player Pokemon fainted!", "BATTLE_STATE")
            elif 'p2a' in pokemon:
                self.battle_state.state['enemyFainted'] = True
                self.log("Enemy Pokemon fainted!", "BATTLE_STATE")
                
    def _parse_heal(self, line):
        """Parse heal messages to update HP tracking"""
        parts = line.split('|')
        if len(parts) >= 4:
            target = parts[2]
            hp_info = parts[3]
            
            if '/' in hp_info:
                try:
                    current_hp_str, max_hp_str = hp_info.split('/')
                    current_hp = int(current_hp_str.strip())
                    max_hp = int(max_hp_str.split()[0].strip())
                    
                    if 'p1a' in target:
                        # Update player HP tracking after heal
                        self.battle_state.player_prev_hp_display = current_hp
                        self.battle_state.player_pokemon["currentHP"] = current_hp
                        
                        if max_hp > 100:
                            # Real HP values
                            if hasattr(self.battle_state, 'player_exact_hp'):
                                self.battle_state.player_exact_hp["current"] = current_hp
                                self.battle_state.player_exact_hp["max"] = max_hp
                            self.battle_state.player_real_max_hp = max_hp
                            self.log(f"Player healed to {current_hp}/{max_hp} HP [EXACT]", "BATTLE_STATE")
                        else:
                            # Percentage display - update exact HP if we have real max
                            if hasattr(self.battle_state, 'player_exact_hp') and self.battle_state.player_real_max_hp > 0:
                                exact_current = int((current_hp / 100.0) * self.battle_state.player_real_max_hp)
                                self.battle_state.player_exact_hp["current"] = exact_current
                                self.log(f"Player healed to {current_hp}% HP (exact: {exact_current}/{self.battle_state.player_real_max_hp})", "BATTLE_STATE")
                            else:
                                self.log(f"Player healed to {current_hp}% HP", "BATTLE_STATE")
                        
                    elif 'p2a' in target:
                        # Update enemy HP tracking after heal (using simplified 100 HP system)
                        self.battle_state.enemy_prev_hp_display = current_hp
                        self.battle_state.enemy_pokemon["currentHP"] = current_hp
                        self.battle_state.enemy_pokemon["maxHP"] = 100  # Always use 100 for enemy
                        self.log(f"Enemy healed to {current_hp}/100 HP", "BATTLE_STATE")
                        
                except ValueError:
                    pass