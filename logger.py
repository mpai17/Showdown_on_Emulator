import os
from datetime import datetime

class Logger:
    def __init__(self, log_filename="showdown_log.txt"):
        self.log_filename = log_filename
        self.log_file = None
        self.callbacks = []
        
    def add_callback(self, callback):
        """Add a callback function to receive log messages"""
        self.callbacks.append(callback)
        
    def remove_callback(self, callback):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
        
    def open_log_file(self):
        """Open the log file for writing"""
        try:
            self.log_file = open(self.log_filename, "a", encoding="utf-8")
            self.log_message(f"Logging to {self.log_filename}", "SYSTEM")
            return True
        except Exception as e:
            print(f"Could not open log file: {e}")
            return False
            
    def close_log_file(self):
        """Close the log file"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None
            
    def log_message(self, message, log_type="INFO"):
        """Log message to file, terminal and registered callbacks"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] [{log_type}] {message}"
        
        # Print to terminal
        print(formatted_msg)
        
        # Write to log file
        if self.log_file:
            try:
                self.log_file.write(formatted_msg + "\n")
                self.log_file.flush()
            except:
                pass
        
        # Call all registered callbacks
        for callback in self.callbacks[:]:  # Use slice copy to avoid modification during iteration
            try:
                callback(formatted_msg, log_type, timestamp)
            except Exception as e:
                # Remove callbacks that cause errors (likely from destroyed GUI elements)
                print(f"Removing failed log callback: {e}")
                self.callbacks.remove(callback)