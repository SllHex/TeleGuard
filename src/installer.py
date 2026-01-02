"""
TeleGuard Installer - Beautiful Modern UI with CustomTkinter
"""

import customtkinter as ctk
import subprocess
import os
import sys
from pathlib import Path
import threading
import time


# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TeleGuardInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("TeleGuard Setup")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"500x600+{x}+{y}")
        
        # Get base path (where installer is running from)
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys.executable).parent
            # Bundled files are in _MEIPASS
            self.bundled_path = Path(sys._MEIPASS)
        else:
            self.base_path = Path(__file__).parent
            self.bundled_path = self.base_path / "dist"
        
        # Set window icon
        icon_path = self.bundled_path / "setup_icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except:
                pass
        
        self.exe_path = self.base_path / "TeleGuard.exe"
        self.config_path = self.base_path / "config.txt"
        
        # Variables
        self.bot_token = ctk.StringVar()
        self.admin_id = ctk.StringVar()
        default_path = str(Path(os.environ['USERPROFILE']) / "Documents" / "TeleGuard")
        self.install_path = ctk.StringVar(value=default_path)
        self.current_step = 0
        
        # Create pages
        self.pages = []
        self.configure(fg_color="#0a0a0a")
        
        self.create_welcome_page()
        self.create_token_page()
        self.create_chatid_page()
        self.create_location_page()  # New page
        self.create_install_page()
        self.create_complete_page()
        
        self.show_page(0)
    
    def add_context_menu(self, entry):
        """Add right-click context menu with paste option"""
        menu = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=5)
        
        paste_btn = ctk.CTkButton(
            menu, text="Paste", width=80, height=30,
            fg_color="transparent", hover_color="#3a3a3a",
            command=lambda: self.do_paste(entry, menu)
        )
        paste_btn.pack(padx=5, pady=5)
        
        def show_menu(event):
            menu.place(x=event.x_root - self.winfo_x(), 
                      y=event.y_root - self.winfo_y())
            self.bind("<Button-1>", lambda e: menu.place_forget())
        
        entry.bind("<Button-3>", show_menu)
    
    def do_paste(self, entry, menu):
        """Paste from clipboard"""
        try:
            text = self.clipboard_get()
            entry.delete(0, "end")
            entry.insert(0, text)
        except:
            pass
        menu.place_forget()
    
    def create_header(self, parent, step_num=0, total_steps=3):
        header = ctk.CTkFrame(parent, fg_color="transparent", height=120)
        header.pack(fill="x", pady=(20, 0))
        header.pack_propagate(False)
        
        # Logo
        logo = ctk.CTkButton(
            header,
            text="📦",
            font=ctk.CTkFont(size=40),
            width=80, height=80,
            corner_radius=40,
            fg_color="#1a5f7a",
            hover_color="#1a5f7a",
            text_color="white"
        )
        logo.pack()
        
        if step_num > 0:
            # Progress indicator
            progress_frame = ctk.CTkFrame(header, fg_color="transparent")
            progress_frame.pack(pady=(15, 0))
            
            for i in range(1, total_steps + 1):
                color = "#00d4aa" if i <= step_num else "#333333"
                dot = ctk.CTkFrame(progress_frame, width=10, height=10, 
                                  corner_radius=5, fg_color=color)
                dot.pack(side="left", padx=5)
        
        return header
    
    def create_footer(self, parent, back_cmd=None, next_cmd=None, next_text="Next"):
        footer = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        footer.pack(side="bottom", fill="x", pady=20, padx=30)
        footer.pack_propagate(False)
        
        if back_cmd:
            back_btn = ctk.CTkButton(
                footer, text="Back", width=100, height=40,
                corner_radius=20, fg_color="#2a2a2a", hover_color="#3a3a3a",
                command=back_cmd
            )
            back_btn.pack(side="left")
        
        next_btn = ctk.CTkButton(
            footer, text=next_text, width=120, height=40,
            corner_radius=20, fg_color="#00d4aa", hover_color="#00b894",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=next_cmd
        )
        next_btn.pack(side="right")
        
        return footer
    
    def create_welcome_page(self):
        page = ctk.CTkFrame(self, fg_color="transparent")
        
        # Footer first (at bottom)
        footer = ctk.CTkFrame(page, fg_color="transparent", height=70)
        footer.pack(side="bottom", fill="x", pady=20, padx=30)
        
        next_btn = ctk.CTkButton(
            footer, text="Get Started", width=140, height=45,
            corner_radius=22, fg_color="#00d4aa", hover_color="#00b894",
            text_color="#000000", font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.show_page(1)
        )
        next_btn.pack(side="right")
        
        # Header
        self.create_header(page)
        
        # Content
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        title = ctk.CTkLabel(
            content, text="Welcome to TeleGuard",
            font=ctk.CTkFont(size=26, weight="bold"), text_color="white"
        )
        title.pack(pady=(10, 5))
        
        subtitle = ctk.CTkLabel(
            content, text="Security Monitoring System",
            font=ctk.CTkFont(size=13), text_color="#666666"
        )
        subtitle.pack()
        
        desc = ctk.CTkLabel(
            content,
            text="This wizard will guide you through the installation.",
            font=ctk.CTkFont(size=12), text_color="#888888",
            justify="center"
        )
        desc.pack(pady=20)
        
        # Feature cards
        features_frame = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=15)
        features_frame.pack(fill="x")
        
        features = [
            ("📷", "Webcam Capture"),
            ("📍", "Location Tracking"),
            ("📱", "Telegram Alerts"),
        ]
        
        for icon, title_text in features:
            row = ctk.CTkFrame(features_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=18)).pack(side="left")
            ctk.CTkLabel(row, text=title_text, font=ctk.CTkFont(size=13),
                        text_color="white").pack(side="left", padx=15)
        
        self.pages.append(page)
    
    def create_token_page(self):
        page = ctk.CTkFrame(self, fg_color="transparent")
        
        # Footer first
        footer = ctk.CTkFrame(page, fg_color="transparent", height=70)
        footer.pack(side="bottom", fill="x", pady=20, padx=30)
        
        back_btn = ctk.CTkButton(
            footer, text="Back", width=100, height=40,
            corner_radius=20, fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=lambda: self.show_page(0)
        )
        back_btn.pack(side="left")
        
        next_btn = ctk.CTkButton(
            footer, text="Next", width=120, height=40,
            corner_radius=20, fg_color="#00d4aa", hover_color="#00b894",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=self.validate_token
        )
        next_btn.pack(side="right")
        
        self.create_header(page, step_num=1)
        
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=10)
        
        title = ctk.CTkLabel(
            content, text="Bot Token",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="white"
        )
        title.pack(pady=(10, 5))
        
        # Input
        input_label = ctk.CTkLabel(
            content, text="Paste your Bot Token:",
            font=ctk.CTkFont(size=12), text_color="#888888"
        )
        input_label.pack(anchor="w", pady=(20, 8))
        
        self.token_entry = ctk.CTkEntry(
            content, textvariable=self.bot_token,
            width=400, height=50, corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=13),
            placeholder_text="123456789:ABCdefGHI..."
        )
        self.token_entry.pack()
        self.add_context_menu(self.token_entry)
        
        hint = ctk.CTkLabel(
            content, text="Get it from @BotFather on Telegram",
            font=ctk.CTkFont(size=11), text_color="#555555"
        )
        hint.pack(pady=10)
        
        self.pages.append(page)
    
    def validate_token(self):
        if not self.bot_token.get().strip():
            self.token_entry.configure(border_color="#ff4444")
            return
        self.token_entry.configure(border_color="#333333")
        self.show_page(2)
    
    def create_chatid_page(self):
        page = ctk.CTkFrame(self, fg_color="transparent")
        
        # Footer first
        footer = ctk.CTkFrame(page, fg_color="transparent", height=70)
        footer.pack(side="bottom", fill="x", pady=20, padx=30)
        
        back_btn = ctk.CTkButton(
            footer, text="Back", width=100, height=40,
            corner_radius=20, fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=lambda: self.show_page(1)
        )
        back_btn.pack(side="left")
        
        next_btn = ctk.CTkButton(
            footer, text="Install", width=120, height=40,
            corner_radius=20, fg_color="#00d4aa", hover_color="#00b894",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=self.validate_chatid
        )
        next_btn.pack(side="right")
        
        self.create_header(page, step_num=2)
        
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=10)
        
        title = ctk.CTkLabel(
            content, text="Chat ID",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="white"
        )
        title.pack(pady=(10, 5))
        
        # Input
        input_label = ctk.CTkLabel(
            content, text="Enter your Chat ID:",
            font=ctk.CTkFont(size=12), text_color="#888888"
        )
        input_label.pack(anchor="w", pady=(20, 8))
        
        self.chatid_entry = ctk.CTkEntry(
            content, textvariable=self.admin_id,
            width=250, height=50, corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=14),
            placeholder_text="123456789"
        )
        self.chatid_entry.pack(anchor="w")
        self.add_context_menu(self.chatid_entry)
        
        hint = ctk.CTkLabel(
            content, text="Get it from @userinfobot on Telegram",
            font=ctk.CTkFont(size=11), text_color="#555555"
        )
        hint.pack(anchor="w", pady=10)
        
        self.pages.append(page)
    
    def validate_chatid(self):
        if not self.admin_id.get().strip():
            self.chatid_entry.configure(border_color="#ff4444")
            return
        self.chatid_entry.configure(border_color="#333333")
        self.show_page(3)  # Go to location page
    
    def create_location_page(self):
        from tkinter import filedialog
        
        page = ctk.CTkFrame(self, fg_color="transparent")
        
        # Footer first
        footer = ctk.CTkFrame(page, fg_color="transparent", height=70)
        footer.pack(side="bottom", fill="x", pady=20, padx=30)
        
        back_btn = ctk.CTkButton(
            footer, text="Back", width=100, height=40,
            corner_radius=20, fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=lambda: self.show_page(2)
        )
        back_btn.pack(side="left")
        
        def start_installation():
            self.show_page(4)  # Go to install page
            self.start_install()
        
        next_btn = ctk.CTkButton(
            footer, text="Install", width=120, height=40,
            corner_radius=20, fg_color="#00d4aa", hover_color="#00b894",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=start_installation
        )
        next_btn.pack(side="right")
        
        self.create_header(page, step_num=3, total_steps=4)
        
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=10)
        
        title = ctk.CTkLabel(
            content, text="Install Location",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="white"
        )
        title.pack(pady=(10, 5))
        
        subtitle = ctk.CTkLabel(
            content, text="Choose where to install TeleGuard",
            font=ctk.CTkFont(size=12), text_color="#888888"
        )
        subtitle.pack(pady=(0, 20))
        
        # Path entry frame
        path_frame = ctk.CTkFrame(content, fg_color="transparent")
        path_frame.pack(fill="x", pady=10)
        
        self.path_entry = ctk.CTkEntry(
            path_frame, textvariable=self.install_path,
            width=320, height=45, corner_radius=10,
            font=ctk.CTkFont(size=11)
        )
        self.path_entry.pack(side="left")
        
        def browse_folder():
            folder = filedialog.askdirectory(
                initialdir=self.install_path.get(),
                title="Select Installation Folder"
            )
            if folder:
                self.install_path.set(folder)
        
        browse_btn = ctk.CTkButton(
            path_frame, text="Browse", width=80, height=45,
            corner_radius=10, fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=browse_folder
        )
        browse_btn.pack(side="left", padx=(10, 0))
        
        # Info
        info = ctk.CTkLabel(
            content, text="Files will be installed to this folder",
            font=ctk.CTkFont(size=11), text_color="#555555"
        )
        info.pack(pady=15)
        
        self.pages.append(page)
    
    def create_install_page(self):
        page = ctk.CTkFrame(self, fg_color="transparent")
        
        self.create_header(page, step_num=3)
        
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        title = ctk.CTkLabel(
            content, text="Installing...",
            font=ctk.CTkFont(size=24, weight="bold"), text_color="white"
        )
        title.pack(pady=(40, 20))
        
        self.progress = ctk.CTkProgressBar(
            content, width=350, height=8, corner_radius=4,
            fg_color="#1a1a1a", progress_color="#00d4aa"
        )
        self.progress.pack(pady=20)
        self.progress.set(0)
        
        self.install_status = ctk.CTkLabel(
            content, text="Preparing...",
            font=ctk.CTkFont(size=12), text_color="#888888"
        )
        self.install_status.pack(pady=10)
        
        self.pages.append(page)
    
    def start_install(self):
        threading.Thread(target=self.do_install, daemon=True).start()
    
    def do_install(self):
        try:
            # Installation folder (user selected)
            install_dir = Path(self.install_path.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            self.install_dir = install_dir
            exe_path = install_dir / "TeleGuard.exe"
            bot_path = install_dir / "bot.py"
            config_path = install_dir / "config.txt"
            icon_path = install_dir / "app_icon.ico"
            
            # Step 1: Copy files from bundled location
            self.update_install(0.2, "Extracting files...")
            
            # Copy files from bundled location (inside Setup.exe)
            src_exe = self.bundled_path / "TeleGuard.exe"
            src_bot = self.bundled_path / "bot.py"
            src_icon = self.bundled_path / "app_icon.ico"
            
            import shutil
            if src_exe.exists():
                shutil.copy2(src_exe, exe_path)
            if src_bot.exists():
                shutil.copy2(src_bot, bot_path)
            if src_icon.exists():
                shutil.copy2(src_icon, icon_path)
            
            time.sleep(0.5)
            
            # Step 2: Save config
            self.update_install(0.4, "Saving configuration...")
            with open(config_path, 'w') as f:
                f.write(f"BOT_TOKEN={self.bot_token.get()}\n")
                f.write(f"ADMIN_ID={self.admin_id.get()}\n")
            time.sleep(0.5)
            
            # Step 3: Enable location services (multiple registry keys for full access)
            self.update_install(0.6, "Enabling location services...")
            try:
                # PowerShell script to enable all location settings
                ps_script = '''
# Enable Location for current user
$locationPath = 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location'
if (!(Test-Path $locationPath)) { New-Item -Path $locationPath -Force | Out-Null }
Set-ItemProperty -Path $locationPath -Name 'Value' -Value 'Allow' -ErrorAction SilentlyContinue

# Enable Location Services in registry
$sensorPath = 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location'
Set-ItemProperty -Path $sensorPath -Name 'Value' -Value 'Allow' -ErrorAction SilentlyContinue

# Enable location for desktop apps
$desktopPath = 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location\\NonPackaged'
if (!(Test-Path $desktopPath)) { New-Item -Path $desktopPath -Force | Out-Null }
Set-ItemProperty -Path $desktopPath -Name 'Value' -Value 'Allow' -ErrorAction SilentlyContinue

# Enable Windows Location Provider
$providerPath = 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\lfsvc\\Service\\Configuration'
if (!(Test-Path $providerPath)) { New-Item -Path $providerPath -Force | Out-Null }
Set-ItemProperty -Path $providerPath -Name 'Status' -Value 1 -Type DWord -ErrorAction SilentlyContinue

# Start Location Service
Start-Service lfsvc -ErrorAction SilentlyContinue
'''
                subprocess.run(
                    ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=15
                )
            except:
                pass
            time.sleep(0.5)
            
            # Step 4: Create startup entry
            self.update_install(0.8, "Creating startup entry...")
            startup_path = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            vbs = f'''Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{startup_path}\\TeleGuard.lnk")
Shortcut.TargetPath = "{exe_path}"
Shortcut.WorkingDirectory = "{install_dir}"
Shortcut.WindowStyle = 7
Shortcut.Save'''
            
            vbs_file = Path(os.environ['TEMP']) / "_tg_setup.vbs"
            with open(vbs_file, 'w') as f:
                f.write(vbs)
            subprocess.run(['cscript', '//nologo', str(vbs_file)],
                          capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            vbs_file.unlink(missing_ok=True)
            time.sleep(0.5)
            
            # Step 5: Launch TeleGuard
            self.update_install(1.0, "Launching TeleGuard...")
            if exe_path.exists():
                subprocess.Popen([str(exe_path)], cwd=str(install_dir), creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Open installation folder
            subprocess.Popen(['explorer', str(install_dir)])
            
            time.sleep(1)
            
            self.after(0, lambda: self.show_page(5))
            
        except Exception as e:
            self.after(0, lambda: self.install_status.configure(
                text=f"Error: {str(e)[:40]}", text_color="#ff4444"))
    
    def update_install(self, value, text):
        self.after(0, lambda: self.progress.set(value))
        self.after(0, lambda: self.install_status.configure(text=text))
    
    def create_complete_page(self):
        page = ctk.CTkFrame(self, fg_color="transparent")
        
        # Success header
        header = ctk.CTkFrame(page, fg_color="transparent", height=150)
        header.pack(fill="x", pady=(40, 0))
        
        # Checkmark
        check = ctk.CTkButton(
            header,
            text="✓",
            font=ctk.CTkFont(size=40, weight="bold"),
            width=90, height=90,
            corner_radius=45,
            fg_color="#00d4aa",
            hover_color="#00d4aa",
            text_color="white"
        )
        check.pack()
        
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        title = ctk.CTkLabel(
            content, text="Installation Complete!",
            font=ctk.CTkFont(size=24, weight="bold"), text_color="white"
        )
        title.pack(pady=(30, 10))
        
        subtitle = ctk.CTkLabel(
            content, text="TeleGuard is now running",
            font=ctk.CTkFont(size=13), text_color="#00d4aa"
        )
        subtitle.pack()
        
        # Info card
        info_card = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=12)
        info_card.pack(fill="x", pady=30)
        
        info_items = [
            ("📱", "Check Telegram for startup alert"),
            ("🔄", "TeleGuard will auto-start with Windows"),
            ("⚙️", "Use TeleGuard.exe to manage settings"),
        ]
        
        for icon, text in info_items:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=12)
            
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=16)).pack(side="left")
            ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=12),
                        text_color="#cccccc").pack(side="left", padx=15)
        
        # Finish button
        footer = ctk.CTkFrame(page, fg_color="transparent", height=60)
        footer.pack(side="bottom", fill="x", pady=20, padx=30)
        
        finish_btn = ctk.CTkButton(
            footer, text="Finish", width=120, height=40,
            corner_radius=20, fg_color="#00d4aa", hover_color="#00b894",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=self.destroy
        )
        finish_btn.pack(side="right")
        
        self.pages.append(page)
    
    def show_page(self, index):
        self.current_step = index
        for page in self.pages:
            page.pack_forget()
        self.pages[index].pack(fill="both", expand=True)


if __name__ == "__main__":
    app = TeleGuardInstaller()
    app.mainloop()
