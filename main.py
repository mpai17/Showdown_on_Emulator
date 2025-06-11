import asyncio
import threading
import tkinter as tk

from config import Config
from battle_state import BattleState
from pokemon_api import PokemonAPI
from battle_parser import BattleParser
from showdown_client import ShowdownClient
from logger import Logger
from gui import ShowdownGUI

class PokemonShowdownLogger:
    def __init__(self):
        # Initialize components
        self.config = Config()
        self.battle_state = BattleState()
        self.pokemon_api = PokemonAPI()
        self.logger = Logger()
        self.client = None
        
        # Setup logger callback
        self.logger.add_callback(self.on_log_message)
        
        # Initialize battle parser with dependencies
        self.battle_parser = BattleParser(
            self.battle_state, 
            self.pokemon_api, 
            self.logger.log_message
        )
        
        # Load credentials and setup GUI
        username, password = self.config.load_credentials()
        self.gui = ShowdownGUI(self.start_logging, self.stop_logging)
        self.gui.set_credentials(username, password)
        
        # Threading
        self.running = False
        self.connection_thread = None
        self.connection_task = None
        self.loop = None
        
    def on_log_message(self, formatted_msg, log_type, timestamp):
        """Handle log messages from the logger"""
        # Check if GUI is still valid before updating
        try:
            if hasattr(self.gui, 'root') and self.gui.root.winfo_exists():
                # Update GUI logs
                self.gui.add_log_message(formatted_msg, log_type, timestamp)
                
                # Update battle state display if it's a battle state message
                if log_type == "BATTLE_STATE":
                    self.gui.update_battle_state_display(self.battle_state.get_state_display())
        except tk.TclError:
            # GUI has been destroyed, remove this callback
            self.logger.remove_callback(self.on_log_message)
            
    async def handle_message(self, line):
        """Handle messages from the WebSocket client"""
        # Log all messages
        self.logger.log_message(line, "RAW")
        
        # Handle connection status updates
        if line.startswith('|updateuser|'):
            parts = line.split('|')
            if len(parts) >= 3:
                username = parts[2]
                if username and username != ' ':  # Successfully logged in
                    self.gui.root.after(0, lambda: self.gui.set_status("Connected", "green"))
                    self.logger.log_message(f"Successfully connected and logged in as {username}", "SYSTEM")
        
        # Parse battle-specific messages
        self.battle_parser.parse_gen1_battle_data(line)
        
        # Handle special events
        if '|start|' in line:
            self.logger.log_message("BATTLE STARTED!", "BATTLE")
            self.battle_state.reset_all()
            
        elif line.startswith('>battle-gen1ou-') or line.startswith('>battle-'):
            battle_room = line[1:]  # Remove the '>' prefix
            self.logger.log_message(f"Entering battle room: {battle_room}", "BATTLE")
            
    def start_logging(self, username, password):
        """Start the logging process"""
        # Save credentials
        self.config.save_credentials(username, password)
        
        # Open log file
        if not self.logger.open_log_file():
            self.gui.connection_failed()
            return
        
        # Initialize client
        self.client = ShowdownClient(username, password, self.handle_message)
        self.client.start()
        
        # Start connection in separate thread
        self.running = True
        self.connection_thread = threading.Thread(target=self.run_connection)
        self.connection_thread.daemon = True
        self.connection_thread.start()
        
    def stop_logging(self):
        """Stop the logging process"""
        if not self.running:
            return  # Already stopped
            
        self.running = False
        
        if self.client:
            self.client.stop()
            
        # Cancel the connection task if it exists
        if self.connection_task and not self.connection_task.done():
            if self.loop and not self.loop.is_closed():
                try:
                    self.loop.call_soon_threadsafe(self.connection_task.cancel)
                except RuntimeError:
                    pass
            
        # Wait for the connection thread to finish
        if self.connection_thread and self.connection_thread.is_alive():
            self.connection_thread.join(timeout=2.0)  # Wait max 2 seconds
            
        if self.logger:
            self.logger.close_log_file()
            
        # Only log if we have a valid logger and GUI
        try:
            self.logger.log_message("Logging stopped", "SYSTEM")
        except:
            print("Logging stopped")
        
    def run_connection(self):
        """Run the websocket connection in a separate thread"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Create and store the connection task
            self.connection_task = self.loop.create_task(self.client.connect_and_listen())
            
            # Run the event loop
            try:
                self.loop.run_until_complete(self.connection_task)
            except asyncio.CancelledError:
                print("Connection task was cancelled")
            except Exception as e:
                if self.running:  # Only log if we're still supposed to be running
                    self.logger.log_message(f"Connection error: {str(e)}", "ERROR")
                    self.gui.root.after(0, self.gui.connection_failed)
                    
        except Exception as e:
            if self.running:  # Only log if we're still supposed to be running
                self.logger.log_message(f"Connection setup error: {str(e)}", "ERROR")
                self.gui.root.after(0, self.gui.connection_failed)
        finally:
            # Clean up the loop
            if self.loop and not self.loop.is_closed():
                try:
                    # Cancel any remaining tasks
                    pending = asyncio.all_tasks(self.loop)
                    for task in pending:
                        task.cancel()
                    
                    # Wait for tasks to be cancelled
                    if pending:
                        self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                        
                    self.loop.close()
                except Exception:
                    pass
        
    def run(self):
        """Run the application"""
        try:
            self.gui.run()
        except KeyboardInterrupt:
            print("Application interrupted by user")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            # Ensure cleanup
            self.stop_logging()

if __name__ == "__main__":
    app = PokemonShowdownLogger()
    app.run()