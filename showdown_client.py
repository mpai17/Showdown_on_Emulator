import asyncio
import websockets
import json
import requests

class ShowdownClient:
    def __init__(self, username, password, message_handler):
        self.username = username
        self.password = password
        self.message_handler = message_handler
        self.websocket = None
        self.challstr = ""
        self.assertion = ""
        self.connected = False
        self.running = False
        
    async def connect_and_listen(self):
        """Connect to Pokemon Showdown and listen for messages"""
        servers = [
            "wss://sim3.psim.us/showdown/websocket",
            "wss://sim2.psim.us/showdown/websocket", 
            "wss://sim.psim.us/showdown/websocket",
            "wss://sim.smogon.com/showdown/websocket"
        ]
        
        for server_uri in servers:
            if not self.running:  # Check if we should stop
                return
                
            try:
                print(f"Connecting to {server_uri}...")
                
                async with websockets.connect(server_uri) as websocket:
                    self.websocket = websocket
                    print(f"Connected to {server_uri}")
                    self.connected = True
                    
                    try:
                        # Listen for messages
                        async for message in websocket:
                            if not self.running:
                                break
                            await self.handle_message(message)
                    except asyncio.CancelledError:
                        print("WebSocket connection cancelled")
                        break
                    except websockets.exceptions.ConnectionClosed:
                        print("WebSocket connection closed")
                        break
                    return
                    
            except asyncio.CancelledError:
                print("Connection attempt cancelled")
                return
            except Exception as e:
                if self.running:  # Only log errors if we're still supposed to be running
                    print(f"Failed to connect to {server_uri}: {str(e)}")
                continue
        
        if self.running:  # Only raise exception if we're still supposed to be running
            raise Exception("Failed to connect to any Pokemon Showdown server")
            
    async def handle_message(self, message):
        """Handle incoming messages from the server"""
        try:
            lines = message.strip().split('\n')
            
            for line in lines:
                if not line:
                    continue
                
                # Pass message to handler
                await self.message_handler(line)
                
                # Handle authentication
                if line.startswith('|challstr|'):
                    parts = line.split('|')
                    if len(parts) >= 3:
                        self.challstr = '|'.join(parts[2:])
                        print("Received challenge string, attempting login...")
                        await self.login()
                        
                elif line.startswith('|updateuser|'):
                    parts = line.split('|')
                    if len(parts) >= 3:
                        username = parts[2]
                        if username == self.username:
                            print(f"Successfully logged in as {username}")
                            self.connected = True
                            
        except Exception as e:
            print(f"Error handling message: {str(e)}")
            
    async def login(self):
        """Login to Pokemon Showdown"""
        try:
            login_url = "https://play.pokemonshowdown.com/~~showdown/action.php"
            
            data = {
                'act': 'login',
                'name': self.username,
                'pass': self.password,
                'challstr': self.challstr
            }
            
            print(f"Attempting login for user: {self.username}")
            
            response = requests.post(login_url, data=data)
            
            if response.status_code == 200:
                response_text = response.text
                
                if response_text.startswith(']'):
                    response_text = response_text[1:]
                    
                try:
                    login_data = json.loads(response_text)
                    
                    if 'assertion' in login_data and login_data['assertion']:
                        self.assertion = login_data['assertion']
                        
                        if "invalid login key" in self.assertion.lower() or "error" in self.assertion.lower():
                            print(f"Login assertion contains error: {self.assertion}")
                            return
                        
                        login_command = f"|/trn {self.username},0,{self.assertion}"
                        await self.websocket.send(login_command)
                        print("Login command sent")
                        
                    elif 'error' in login_data:
                        print(f"Login failed: {login_data['error']}")
                        
                except json.JSONDecodeError as e:
                    print(f"Failed to parse login response: {e}")
                    
            else:
                print(f"Login request failed with status {response.status_code}")
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            
    def start(self):
        """Start the client"""
        self.running = True
        
    def stop(self):
        """Stop the client"""
        self.running = False