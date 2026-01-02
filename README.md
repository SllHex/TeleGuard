<div align="center">

<img src="assets/logo.png" width="120" alt="TeleGuard Logo"/>

# TeleGuard

### 🔒 Windows Security Monitoring via Telegram

[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://telegram.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0-8b5cf6?style=flat-square)]()

**Keep your Windows device secure with real-time Telegram alerts**

[⬇️ Download](#-installation) • [✨ Features](#-features) • [📖 Setup](#-step-by-step-setup) • [❓ FAQ](#-faq)

</div>

---

## 🎯 About

TeleGuard is a lightweight security monitoring tool that runs silently on your Windows PC. When your device turns on, you get an instant Telegram notification with:

- 📷 **Webcam snapshot** of who's using it
- 📍 **Location data** showing where it is  
- 💻 **System info** about the device

Perfect for **monitoring lost/stolen laptops** or keeping an eye on your home computer.

---

## ✨ Features

<table>
<tr>
<td align="center" width="33%">
<h3>📷</h3>
<b>Webcam Capture</b><br/>
<sub>Take photos remotely on demand</sub>
</td>
<td align="center" width="33%">
<h3>📍</h3>
<b>Location Tracking</b><br/>
<sub>GPS & Wi-Fi based positioning</sub>
</td>
<td align="center" width="33%">
<h3>🚨</h3>
<b>Startup Alerts</b><br/>
<sub>Instant boot notifications</sub>
</td>
</tr>
<tr>
<td align="center">
<h3>💾</h3>
<b>Offline Storage</b><br/>
<sub>Saves data when offline</sub>
</td>
<td align="center">
<h3>🔇</h3>
<b>Silent Mode</b><br/>
<sub>Runs completely hidden</sub>
</td>
<td align="center">
<h3>⚡</h3>
<b>Auto-Start</b><br/>
<sub>Launches with Windows</sub>
</td>
</tr>
</table>

---

## � Installation

### Requirements

| Requirement | Details |
|:-----------:|---------|
| 💻 **OS** | Windows 10/11 (64-bit) |
| 📱 **Telegram** | Account with Bot Token |
| 🌐 **Internet** | Required for setup |

### Quick Install

1. **Download** `Setup.exe` from this repository
2. **Run** the installer
3. **Enter** your Telegram credentials
4. **Done!** ✅

---

## 📖 Step-by-Step Setup

### 📌 Step 1: Create Your Telegram Bot

Before installing TeleGuard, you need to create a Telegram bot to receive alerts.

<details>
<summary><b>🤖 1.1 - Get Your Bot Token</b></summary>

<br/>

1. Open **Telegram** on your phone or desktop

2. Search for **`@BotFather`** (official Telegram bot)

3. Start a chat and send: `/newbot`

4. Follow the prompts:
   - **Name:** Choose any name (e.g., "My Security Bot")
   - **Username:** Must end with `bot` (e.g., "mysecurity_bot")

5. **Copy the token** that looks like:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

> ⚠️ **Keep this token secret!** Anyone with it can control your bot.

</details>

<details>
<summary><b>🆔 1.2 - Get Your Chat ID</b></summary>

<br/>

1. Open **Telegram** and search for **`@userinfobot`**

2. Start a chat and send any message

3. The bot will reply with your information:
   ```
   Id: 123456789
   First: Your Name
   Lang: en
   ```

4. **Copy the `Id` number** - this is your Chat ID

> 💡 This ID tells TeleGuard where to send alerts.

</details>

---

### 📌 Step 2: Run the Installer

<details>
<summary><b>📦 2.1 - Launch Setup.exe</b></summary>

<br/>

1. **Double-click** `Setup.exe`

2. If Windows shows a warning:
   - Click **"More info"**
   - Click **"Run anyway"**

> 🛡️ This warning appears because the app isn't signed with an expensive certificate.

</details>

<details>
<summary><b>✍️ 2.2 - Enter Your Credentials</b></summary>

<br/>

**Screen 1: Welcome**
- Click **"Get Started"**

**Screen 2: Bot Token**
- Paste your **Bot Token** from Step 1.1
- Click **"Next"**

**Screen 3: Chat ID**  
- Enter your **Chat ID** from Step 1.2
- Click **"Next"**

**Screen 4: Install Location**
- Default: `Documents\TeleGuard`
- Click **"Install"**

</details>

<details>
<summary><b>✅ 2.3 - Installation Complete</b></summary>

<br/>

When you see the **"Installation Complete!"** screen:

1. TeleGuard is now running in the background
2. The installation folder will open automatically
3. Click **"Finish"** to close the installer

> 🎉 Check your Telegram - you should receive a startup alert!

</details>

---

### 📌 Step 3: Activate Your Bot

<details>
<summary><b>🚀 3.1 - Start Your Bot</b></summary>

<br/>

1. Open **Telegram** and find your bot (search by username)

2. Click **"Start"** or send `/start`

3. You'll see the **TeleGuard menu** with these options:
   - 📷 **Capture Photo** - Take a webcam photo now
   - 📍 **Get Location** - Get current location
   - 📂 **Pending Files** - Send any saved files
   - ℹ️ **Status** - View system status

</details>

<details>
<summary><b>✨ 3.2 - Test the Features</b></summary>

<br/>

**Test Webcam:**
1. Click **"📷 Capture Photo"**
2. Wait for the progress bar
3. Photo will be sent to the chat

**Test Location:**
1. Click **"📍 Get Location"**
2. You'll receive:
   - IP address & ISP info
   - City & Country
   - Map pin with coordinates

</details>

---

## 🎮 Using TeleGuard

### Bot Commands

| Button | Action |
|:------:|--------|
| 📷 **Capture** | Take webcam photo now |
| 📍 **Location** | Get current GPS/Wi-Fi location |
| 📂 **Pending** | Send any saved offline files |
| ℹ️ **Status** | View system information |

### Control Panel

After installation, find `TeleGuard.exe` in your Documents\TeleGuard folder:

| Feature | Description |
|:-------:|-------------|
| **Protection Toggle** | Turn monitoring ON/OFF |
| **Status Indicator** | Shows if protection is active |
| **Auto-Start** | Automatically runs with Windows |

> 💡 When Protection is **ON**, TeleGuard runs silently with Windows startup.

---

## ❓ FAQ

<details>
<summary><b>Windows blocks the installer?</b></summary>

<br/>

Click **"More info"** → **"Run anyway"**

This happens because the app isn't signed with an expensive code signing certificate. The app is completely safe - you can verify the source code yourself.

</details>

<details>
<summary><b>Antivirus flags TeleGuard?</b></summary>

<br/>

Add the TeleGuard folder to your antivirus exceptions:

1. Open your antivirus settings
2. Find "Exclusions" or "Exceptions"
3. Add: `C:\Users\[YourName]\Documents\TeleGuard\`

The app uses webcam and location APIs which may trigger false positives.

</details>

<details>
<summary><b>Location not accurate?</b></summary>

<br/>

**Enable Windows Location Services:**

1. Press `Win + I` to open Settings
2. Go to **Privacy & Security** → **Location**
3. Turn ON:
   - ✅ Location services
   - ✅ Let apps access your location
   - ✅ Let desktop apps access your location

**For better accuracy:**
- Keep Wi-Fi ON (even if not connected)
- Location uses nearby Wi-Fi networks for positioning

</details>

<details>
<summary><b>Not receiving alerts?</b></summary>

<br/>

**Check these things:**

1. ✅ Bot Token is correct (no extra spaces)
2. ✅ Chat ID is correct (numbers only)
3. ✅ You've sent `/start` to your bot
4. ✅ Internet connection is working
5. ✅ Protection is turned ON in the control panel

</details>

<details>
<summary><b>How to completely uninstall?</b></summary>

<br/>

1. Open the control panel and turn Protection **OFF**
2. Delete the folder: `Documents\TeleGuard\`
3. Remove startup entry:
   - Press `Win + R`
   - Type `shell:startup`
   - Delete `TeleGuard.lnk` if present

</details>

---

## 🔒 Privacy & Security

| ✅ | All data sent **only to your Telegram** |
|:--:|----------------------------------------|
| ✅ | No external servers or analytics |
| ✅ | Photos deleted after sending |
| ✅ | Works completely offline (stores locally) |
| ✅ | Open source - verify the code yourself |

---

## 📁 Project Structure

```
TeleGuard/
├── Setup.exe              # One-click installer
├── README.md              # This file
├── LICENSE                # MIT License
├── src/
│   ├── bot.py             # Telegram bot logic
│   ├── control_panel.py   # GUI control panel
│   └── installer.py       # Setup wizard
└── assets/
    ├── app_icon.ico       # Application icon
    ├── setup_icon.ico     # Installer icon
    └── logo.png           # Logo for README
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file.

---

## ⚠️ Disclaimer

> **For personal security use only.**
>
> Only install on devices you own or have explicit permission to monitor.
> Unauthorized surveillance is illegal.

---

<div align="center">

**Made with ❤️ for personal security**

⭐ **Star this repo if you find it useful!**

---

*TeleGuard v1.0 | © 2025*

</div>
