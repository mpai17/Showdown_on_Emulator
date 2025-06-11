import os
import configparser

class Config:
    def __init__(self, config_file="showdown_config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
    def load_credentials(self):
        """Load saved credentials from config file"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            if "credentials" in self.config:
                username = self.config["credentials"].get("username", "")
                password = self.config["credentials"].get("password", "")
                return username, password
        return "", ""
                
    def save_credentials(self, username, password):
        """Save credentials to config file"""
        self.config["credentials"] = {
            "username": username,
            "password": password
        }
        with open(self.config_file, "w") as f:
            self.config.write(f)