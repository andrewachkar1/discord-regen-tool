# 🎁 Discord Regeneration Tool

**Discord Regeneration Tool** is a command-line utility designed to **fetch, generate, and regenerate Discord Nitro gift links** directly from your account.

---

## ⚙️ Features

* 🌀 **Link Fetcher** – Retrieve all active Nitro gift links from your account
* 💨 **Generate New Links** – Create new links for unclaimed Nitro gifts
* 🔄 **Mass Link Regeneration** – Regenerate all active links at once
* 🔧 **Single Link Regeneration** – Regenerate a specific gift link
* 🌐 **Proxy Support** – Optional proxies for requests, or run proxyless
* ⏱️ **Rate-Limit Aware** – Automatically handles HTTP 429 rate limits
* 🧩 **Simple CLI Interface** – Shows codes, names, and expiration times

---

## 🧠 Requirements

* Python 3.9+
* Discord account (with valid token)
* KeyAuth license for NitroRegenTool
* Stable internet connection

---

## 🧰 Installation

```bash
# Clone this repository
git clone https://github.com/imlittledoo/discord-regen-tool.git

# Navigate to the folder
cd discord-regen-tool
```

Create a `config.json` file in the root directory:

```json
{
  "TOKEN": "YOUR_DISCORD_TOKEN",
  "proxyless": true
}
```

Optional: Add proxies to `input/proxies.txt` (one per line) if using proxy mode.

---

## ▶️ Usage

```bash
python main.py
```

Follow the on-screen menu to:

1. **Link Fetcher** – Fetch all active links
2. **Generate New Links** – Create new gift links
3. **Mass Link Regeneration** – Regenerate all links
4. **Single Link Regeneration** – Regenerate a specific link
5. **Exit** – Close the tool

The tool automatically saves outputs to organized directories under `output/`.

---

## ⚠️ Disclaimer

This tool is intended for **personal use only**. Misuse of Discord tokens or accounts may violate Discord’s Terms of Service.
Use responsibly and at your **own risk**.

---

## 🧑‍💻 Author

Developed by **Andrew AL ACHKAR**
If you like this project, consider giving it a ⭐

---
