"""
TeleGuard Control Panel - Modern Beautiful UI with CustomTkinter
"""

import customtkinter as ctk
import subprocess
import os
import sys
from pathlib import Path
import json


# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TeleGuardApp(ctk.CTk):
    def __init__(self, start_hidden=False):
        super().__init__()
        
        # Window setup
        self.title("TeleGuard")
        self.geometry("420x580")
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 420) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"420x580+{x}+{y}")
        
        # Get base path
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys.executable).parent
        else:
            self.base_path = Path(__file__).parent
        
        # Set window icon
        icon_path = self.base_path / "app_icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except:
                pass
        
        # State
        self.state_file = self.base_path / "state.json"
        self.is_running = self.load_state()
        self.bot_process = None
        self.start_hidden = start_hidden
        
        # If started hidden (from startup) and protection is OFF, just exit
        if self.start_hidden and not self.is_running:
            self.destroy()
            return
        
        # If started hidden and protection is ON, start bot and hide
        if self.start_hidden and self.is_running:
            self.withdraw()  # Hide window completely
            self.start_protection()
            # Keep running in background - no mainloop needed for hidden mode
            return
        
        # Normal mode - create UI
        self.create_ui()
        
        # Auto-start bot if protection was enabled
        if self.is_running:
            self.start_protection()
    
    def load_state(self):
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f).get('running', False)
        except:
            pass
        return False
    
    def save_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump({'running': self.is_running}, f)
        except:
            pass
    
    def create_ui(self):
        # Main container with gradient background
        self.configure(fg_color=("#0f0f0f", "#0f0f0f"))
        
        # Header frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(40, 20))
        
        # Logo/Icon area
        icon_frame = ctk.CTkFrame(header, fg_color="transparent")
        icon_frame.pack()
        
        # Eye icon button (decorative)
        self.eye_color = "#00d4aa" if self.is_running else "#3a3a3a"
        self.eye_button = ctk.CTkButton(
            icon_frame,
            text="👁",
            font=ctk.CTkFont(size=48),
            width=100, height=100,
            corner_radius=50,
            fg_color=self.eye_color,
            hover_color=self.eye_color,
            text_color="white"
        )
        self.eye_button.pack()
        
        # Title
        title = ctk.CTkLabel(
            header,
            text="TeleGuard",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="white"
        )
        title.pack(pady=(25, 5))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            header,
            text="Security Monitoring System",
            font=ctk.CTkFont(size=13),
            text_color="#666666"
        )
        subtitle.pack()
        
        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Power switch card
        switch_card = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=15)
        switch_card.pack(fill="x", pady=(0, 15))
        
        switch_inner = ctk.CTkFrame(switch_card, fg_color="transparent")
        switch_inner.pack(fill="x", padx=25, pady=20)
        
        switch_label = ctk.CTkLabel(
            switch_inner,
            text="Protection",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        switch_label.pack(side="left")
        
        self.switch = ctk.CTkSwitch(
            switch_inner,
            text="",
            width=60,
            height=30,
            switch_width=50,
            switch_height=26,
            corner_radius=15,
            border_width=0,
            fg_color="#3a3a3a",
            progress_color="#00d4aa",
            button_color="white",
            button_hover_color="#f0f0f0",
            command=self.toggle_protection
        )
        self.switch.pack(side="right")
        
        if self.is_running:
            self.switch.select()
        
        # Status
        status_color = "#00d4aa" if self.is_running else "#666666"
        status_text = "Active" if self.is_running else "Inactive"
        self.status_label = ctk.CTkLabel(
            switch_card,
            text=f"Status: {status_text}",
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        self.status_label.pack(pady=(0, 15))
        
        # Features card
        features_card = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=15)
        features_card.pack(fill="x", pady=(0, 15))
        
        features_header = ctk.CTkLabel(
            features_card,
            text="Features",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#888888"
        )
        features_header.pack(anchor="w", padx=25, pady=(20, 15))
        
        features = [
            ("📷", "Webcam Capture", "Ready"),
            ("📍", "Location Tracking", "GPS/Wi-Fi"),
            ("📱", "Telegram Alerts", "Connected"),
            ("🔇", "Silent Mode", "Enabled"),
        ]
        
        for icon, name, status in features:
            row = ctk.CTkFrame(features_card, fg_color="transparent")
            row.pack(fill="x", padx=25, pady=5)
            
            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left")
            
            ctk.CTkLabel(left, text=icon, font=ctk.CTkFont(size=16)).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(left, text=name, font=ctk.CTkFont(size=13), 
                        text_color="white").pack(side="left")
            
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=12),
                        text_color="#00d4aa").pack(side="right")
        
        # Spacer
        ctk.CTkFrame(features_card, height=15, fg_color="transparent").pack()
        
        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent", height=50)
        footer.pack(side="bottom", fill="x", pady=20)
        
        version = ctk.CTkLabel(
            footer,
            text="TeleGuard v1.0",
            font=ctk.CTkFont(size=11),
            text_color="#444444"
        )
        version.pack()
    
    def toggle_protection(self):
        self.is_running = self.switch.get() == 1
        self.save_state()
        self.update_ui()
        
        if self.is_running:
            self.start_protection()
        else:
            self.stop_protection()
    
    def update_ui(self):
        # Update eye color
        self.eye_color = "#00d4aa" if self.is_running else "#3a3a3a"
        self.eye_button.configure(fg_color=self.eye_color, hover_color=self.eye_color)
        
        # Update status
        status_color = "#00d4aa" if self.is_running else "#666666"
        status_text = "Active" if self.is_running else "Inactive"
        self.status_label.configure(text=f"Status: {status_text}", text_color=status_color)
    
    def start_protection(self):
        """Start the bot as a background process"""
        # Find bot.py in same directory
        bot_py = self.base_path / "bot.py"
        
        if bot_py.exists():
            # Run bot.py with Python
            try:
                self.bot_process = subprocess.Popen(
                    ['pythonw', str(bot_py)],
                    cwd=str(self.base_path),
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except:
                try:
                    # Fallback to python if pythonw not available
                    self.bot_process = subprocess.Popen(
                        ['python', str(bot_py)],
                        cwd=str(self.base_path),
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except:
                    pass
        
        # Add/update startup shortcut with --hidden flag
        self.update_startup_shortcut(enabled=True)
    
    def stop_protection(self):
        """Stop the bot and remove from startup"""
        # Kill the bot process
        try:
            if hasattr(self, 'bot_process') and self.bot_process:
                self.bot_process.terminate()
        except:
            pass
        
        # Also kill any running pythonw with bot.py
        try:
            subprocess.run(
                ['taskkill', '/F', '/IM', 'pythonw.exe'],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except:
            pass
        
        # Remove from startup
        self.update_startup_shortcut(enabled=False)
    
    def update_startup_shortcut(self, enabled=True):
        """Create or remove startup shortcut"""
        startup_path = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        shortcut = startup_path / "TeleGuard.lnk"
        exe_path = self.base_path / "TeleGuard.exe"
        
        if enabled and exe_path.exists():
            try:
                # Create shortcut with --hidden argument
                vbs = f'''Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut}")
Shortcut.TargetPath = "{exe_path}"
Shortcut.Arguments = "--hidden"
Shortcut.WorkingDirectory = "{self.base_path}"
Shortcut.WindowStyle = 7
Shortcut.Save'''
                
                vbs_file = Path(os.environ['TEMP']) / "_tg.vbs"
                with open(vbs_file, 'w') as f:
                    f.write(vbs)
                subprocess.run(['cscript', '//nologo', str(vbs_file)],
                              capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                vbs_file.unlink(missing_ok=True)
            except:
                pass
        else:
            # Remove shortcut
            try:
                if shortcut.exists():
                    shortcut.unlink()
            except:
                pass


def run_hidden_bot():
    """Run just the bot without any UI when in hidden startup mode"""
    import importlib.util
    
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent
    
    state_file = base_path / "state.json"
    
    # Check if protection is enabled
    try:
        if state_file.exists():
            with open(state_file, 'r') as f:
                is_running = json.load(f).get('running', False)
        else:
            is_running = False
    except:
        is_running = False
    
    # If not enabled, just exit silently
    if not is_running:
        return
    
    # Import and run bot as a proper module
    bot_py = base_path / "bot.py"
    if bot_py.exists():
        try:
            # Add base_path to sys.path
            if str(base_path) not in sys.path:
                sys.path.insert(0, str(base_path))
            
            # Load bot.py as a module
            spec = importlib.util.spec_from_file_location("bot", bot_py)
            bot_module = importlib.util.module_from_spec(spec)
            sys.modules["bot"] = bot_module
            spec.loader.exec_module(bot_module)
            
            # Run main function
            if hasattr(bot_module, 'main'):
                bot_module.main()
                
        except Exception as e:
            # Log error to file since we have no console
            try:
                from datetime import datetime
                with open(base_path / "error.log", 'a') as f:
                    f.write(f"[{datetime.now()}] Bot error: {e}\n")
            except:
                pass


if __name__ == "__main__":
    # Check for --hidden argument (used when starting from Windows startup)
    if "--hidden" in sys.argv:
        run_hidden_bot()
        # run_hidden_bot runs the bot directly, it only returns if there's an error
    else:
        app = TeleGuardApp()
        app.mainloop()


