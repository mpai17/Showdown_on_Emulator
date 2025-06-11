import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class ShowdownGUI:
    def __init__(self, on_start_callback, on_stop_callback):
        self.on_start = on_start_callback
        self.on_stop = on_stop_callback
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Pokemon Showdown Gen 1 Battle Logger")
        self.root.geometry("600x500")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Credentials section
        ttk.Label(main_frame, text="Pokemon Showdown Credentials", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.connect_btn = ttk.Button(button_frame, text="Start Gen 1 Logging", command=self.start_logging)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Logging", command=self.stop_logging, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Battle State Tab
        state_frame = ttk.Frame(notebook)
        notebook.add(state_frame, text="Battle State")
        
        ttk.Label(state_frame, text="Gen 1 Battle State:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 5))
        
        self.state_text = scrolledtext.ScrolledText(state_frame, width=70, height=12, font=("Consolas", 9))
        self.state_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Battle Events Tab
        battle_frame = ttk.Frame(notebook)
        notebook.add(battle_frame, text="Battle Events")
        
        ttk.Label(battle_frame, text="Battle Events Log:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 5))
        
        self.battle_log_text = scrolledtext.ScrolledText(battle_frame, width=70, height=20, font=("Consolas", 8))
        self.battle_log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Full Log Tab
        full_log_frame = ttk.Frame(notebook)
        notebook.add(full_log_frame, text="Full Server Log")
        
        ttk.Label(full_log_frame, text="All Server Messages:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 5))
        
        self.log_text = scrolledtext.ScrolledText(full_log_frame, width=70, height=20, font=("Consolas", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def set_credentials(self, username, password):
        """Set the credential fields"""
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        
    def get_credentials(self):
        """Get the current credentials from the form"""
        return self.username_entry.get().strip(), self.password_entry.get().strip()
        
    def start_logging(self):
        """Handle start logging button"""
        username, password = self.get_credentials()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        self.connect_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Connecting...", foreground="orange")
        
        # Call the callback
        self.on_start(username, password)
        
    def stop_logging(self):
        """Handle stop logging button"""
        self.connect_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Disconnected", foreground="red")
        
        # Call the callback
        self.on_stop()
        
    def set_status(self, status, color="black"):
        """Set the status label"""
        self.status_label.config(text=f"Status: {status}", foreground=color)
        
    def connection_failed(self):
        """Handle connection failure"""
        self.connect_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Connection Failed", foreground="red")
        
    def add_log_message(self, formatted_msg, log_type, timestamp):
        """Add a message to the appropriate log tabs"""
        # Add to Full Server Log tab (all messages)
        self.log_text.insert(tk.END, formatted_msg + "\n")
        self.log_text.see(tk.END)
        
        # Keep only last 300 lines in full log
        lines = self.log_text.get("1.0", tk.END).split("\n")
        if len(lines) > 300:
            self.log_text.delete("1.0", f"{len(lines)-300}.0")
        
        # Add to Battle Events tab (only battle-related messages)
        if log_type in ["BATTLE", "BATTLE_STATE"]:
            battle_formatted = f"[{timestamp.split()[1]}] {formatted_msg.split('] ', 2)[-1]}"
            self.battle_log_text.insert(tk.END, battle_formatted + "\n")
            self.battle_log_text.see(tk.END)
            
            # Keep only last 200 lines in battle log
            battle_lines = self.battle_log_text.get("1.0", tk.END).split("\n")
            if len(battle_lines) > 200:
                self.battle_log_text.delete("1.0", f"{len(battle_lines)-200}.0")
                
    def update_battle_state_display(self, state_display):
        """Update the battle state display"""
        self.state_text.delete("1.0", tk.END)
        self.state_text.insert("1.0", state_display)
        
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing"""
        try:
            # Disable further logging callbacks to prevent GUI update errors
            self.root.withdraw()  # Hide the window immediately
            # Stop the logging gracefully
            self.on_stop()
            # Give time for cleanup, then destroy the window
            self.root.after(300, self._force_close)
        except Exception as e:
            print(f"Error during closing: {e}")
            # Force quit if there's an error
            self._force_close()
            
    def _force_close(self):
        """Force close the application"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            import sys
            sys.exit(0)