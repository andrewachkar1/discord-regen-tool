# Discord Gift Management Tool

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Version](https://img.shields.io/badge/Version-1.0-purple)

**Discord Gift Management Tool** is a powerful Discord Nitro gift link management tool that allows users to fetch, generate, and regenerate Nitro gift codes directly from their account. It features full rate-limit handling, proxy support, and a simple command-line interface.

---

## Features

* ✅ **Link Fetcher** – Retrieve all active Nitro gift links from your account.
* ✅ **Generate New Links** – Generate new gift links for unclaimed Nitro gifts.
* ✅ **Mass Link Regeneration** – Regenerate all active links at once.
* ✅ **Single Link Regeneration** – Regenerate a specific gift link.
* ✅ **Proxy Support** – Use proxies for requests or run in proxyless mode.
* ✅ **Rate-Limit Aware** – Automatically handles HTTP 429 rate limits.
* ✅ **Clean CLI Interface** – Displays codes, names, and expiration times neatly.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/imlittledoo/discord-regen-tool.git
cd discord-regen-tool
```

2. Create a `config.json` in the root directory:

```json
{
  "TOKEN": "YOUR_DISCORD_TOKEN",
  "proxyless": true
}
```

* `TOKEN` – Your Discord account token.
* `proxyless` – Set to `true` to run without proxies.

3. Optional: Add proxies to `input/proxies.txt` (one per line) if you want to use proxy mode.

---

## Usage

Run the tool with Python:

```bash
python main.py
```

You will be presented with a menu:

```
[1] - Link Fetcher
[2] - Generate New Links
[3] - Mass Link Regeneration
[4] - Single Link Regeneration
[5] - Exit
```

* **1 – Link Fetcher**: Fetch all active links from your account and save them to `output/Link Fetcher/`.
* **2 – Generate New Links**: Generate unclaimed gift links for your entitlements and save them to `output/Newly Generated Links/`.
* **3 – Mass Link Regeneration**: Regenerate all active links at once.
* **4 – Single Link Regeneration**: Regenerate a single link by entering its code.
* **5 – Exit**: Close the tool.

---

## Output Structure

The tool saves gift links in organized directories:

* **Link Fetcher**:

  * `links.txt` – Shortened URLs.
  * `full_links.txt` – Full information including name and expiration.

* **Newly Generated Links**:

  * `links.txt` – Shortened URLs of newly generated codes.
  * `full_links.txt` – Full information including name.

* **Single Link Regenerator**:

  * `links.txt` – Regenerated code.
  * `full_links.txt` – Full information including name.

---

## Notes

* **KeyAuth License**: Make sure you have a valid KeyAuth license to run this tool.
* **Discord Token**: Using your token responsibly is your responsibility. Avoid sharing your token.
* **Rate Limits**: The tool automatically waits when Discord rate-limits requests. Do not spam requests manually.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for bug fixes, improvements, or new features.

---

## Disclaimer

This tool is intended for personal use. Misuse of Discord accounts, tokens, or services may result in bans or violations of Discord's Terms of Service. Use responsibly.

---

## Author

Made by Andrew AL ACHKAR – Version 1.0

---

I can also create a **minimal badges + GIF banner version** for a more polished GitHub repo homepage if you want it to look extra professional.

Do you want me to do that?
