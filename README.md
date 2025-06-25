linkchanbot
===========

> Note: This is a fork from <https://sr.ht/~torresjrjr/linkchanbot>

A Telegram Bot which sanitises and substitutes share links
with lightweight, privacy respecting proxy frontend alternatives.

- Main instance: [@linkchanbot](https://t.me/linkchanbot)
- Aosus instance: [@aosuslinkchainbot](https://t.me/aosuslinkchainbot)
- User updates: [@linkchan\_updates](https://t.me/linkchan_updates)

![screenshot](https://i.imgur.com/WnbOD5c.jpg)

Supported services (configurable):

- twitter.com => Nitter
- youtube.com => Inividious, CloudTube
- instagram.com => Bibliogram
- reddit.com => Teddit, Libreddit, Old Reddit


Installation
------------

This repository now contains two bots: the original Telegram bot and a new Matrix bot.

### Original Telegram Bot (linkchanbot)

#### Prerequisites

- A Telegram bot token (visit [@botfather](https://t.me/botfather)).

#### Dependencies

- [scdoc](https://sr.ht/~sircmpwn/scdoc) (build dep.)
- Python >= 3.9
- PyPI: python-telegram-bot >= 13 (see `requirements.txt`)

#### Install

	$ git clone https://git.sr.ht/~torresjrjr/linkchanbot # Or your fork's URL
	$ cd linkchanbot
	$ python -m pip install -r requirements.txt
	# make install # For system-wide installation of the Telegram bot

To start serving the Telegram bot, it needs further configuration.

### New Matrix Bot (matrix_bot.py)

#### Prerequisites

- A Matrix user account for the bot (register on your chosen homeserver).
- The Matrix User ID (e.g., `@yourbot:matrix.org`) and password for this account.
- The Matrix User ID of an "admin" user who will be allowed to invite the bot to rooms.

#### Dependencies

- Python >= 3.9 (same as Telegram bot)
- PyPI: `matrix-nio`, `python-dotenv` (install via `pip install matrix-nio python-dotenv`)

#### Install

1. Clone the repository:
   ```bash
   $ git clone https://git.sr.ht/~torresjrjr/linkchanbot # Or your fork's URL
   $ cd linkchanbot
   ```
2. Install Python dependencies:
   ```bash
   $ python -m pip install matrix-nio python-dotenv
   ```
   (If you also intend to run the Telegram bot, ensure `requirements.txt` is also installed, e.g., `pip install -r requirements.txt matrix-nio python-dotenv`)

The `matrix_bot.py` script is run directly with Python and does not use the `Makefile` for installation.

Configuration
-------------

### Original Telegram Bot

- Visit [@botfather](https://t.me/botfather).
- Create a new bot (or select an existing one).
- Save the bot API token.
- Disable "Group Privacy mode".
- Enable "Inline mode".
- Set the "inline placeholder" to "Paste link...".
- Optionally set "inline feedback" to "100%" for logging.
- Set the bot commands: `/start`, `/help`, and `/about`.

#### Server (Telegram Bot)

Add the required bot token (and optionally an admin username)
either in `bot.cfg` in the linkchan config directory
(`$XDG_CONFIG_HOME/linkchan` or `$HOME/.config/linkchan`):

	[auth]
	# required
	token = 123:ABC...
	# optional, provides /restart and /shutdown
	admin = username

Or by environment variable (see `.env.example` for `LINKCHAN_TOKEN`, `LINKCHAN_ADMIN`).

Your Telegram bot should now be ready.

### Advanced configuration (Telegram Bot)

See `linkchanbot(1)` (man page for the Telegram bot).

### New Matrix Bot

The Matrix bot is configured using environment variables. Create a `.env` file in the root of the project (you can copy `.env.example`) and fill in the details:

```env
# .env file for Matrix Bot
HOMESERVER="https://matrix-client.matrix.org"  # Your bot's homeserver URL
USER_ID="@yourbotusername:matrix.org"        # Full Matrix User ID of the bot
PASSWORD="yourbotpassword"                   # Bot's account password
# DEVICE_ID="linkmatrixbot"                  # Optional: A friendly name for the bot's device/session
ALLOWED_INVITER_USER_ID="@adminuser:matrix.org" # Full Matrix User ID of the person allowed to invite the bot

# Optional: Custom paths for alts and services JSON files
# If not set, defaults to sample.config/alts.json and sample.config/services.json
# MATRIX_BOT_ALTS_JSON_PATH="/path/to/your/alts.json"
# MATRIX_BOT_SERVICES_JSON_PATH="/path/to/your/services.json"
```

- `HOMESERVER`: The URL of the Matrix homeserver your bot is registered on.
- `USER_ID`: The bot's full Matrix ID (e.g., `@botname:yourserver.org`).
- `PASSWORD`: The password for the bot's Matrix account.
- `DEVICE_ID` (Optional): A descriptive name for the bot's session. If not provided, one might be generated or a default used by the library.
- `ALLOWED_INVITER_USER_ID`: Crucial for security. This is the full Matrix ID of the user who has permission to invite the bot into rooms. The bot will ignore invites from anyone else.
- `MATRIX_BOT_ALTS_JSON_PATH` (Optional): Specifies a custom path to the `alts.json` file. If not set, the bot defaults to looking for `sample.config/alts.json` relative to the `matrix_bot.py` script.
- `MATRIX_BOT_SERVICES_JSON_PATH` (Optional): Specifies a custom path to the `services.json` file. If not set, the bot defaults to looking for `sample.config/services.json` relative to the `matrix_bot.py` script.

The `alts.json` and `services.json` files define the link substitution rules. By default, the bot expects these to be in the `sample.config/` directory. You can customize their location using the `MATRIX_BOT_ALTS_JSON_PATH` and `MATRIX_BOT_SERVICES_JSON_PATH` environment variables if you prefer to store your configurations elsewhere.


Updating
--------

linkchanbot comes with a preconfigured list of 'alts' (proxies) and
other configuration data. This data is updated with new commits. On
start-up, linkchanbot copies this data in the absence of locally
configured data to `XDG_CONFIG_HOME/linkchan` (`bot.cfg` is untouched).

To fully update linkchanbot and its configuration data, perform a normal
installtion with the latest commit, then remove (and backup) the local
configuration files and restart linkchanbot.

	shell:
		$ rm ~/.config/linkchan/alts.json
		$ rm ~/.config/linkchan/services.json
	Telegram:
		/restart  (or manaully in the shell)


Usage
-----

### Original Telegram Bot

See `linkchanbot(1)` (man page) or run `linkchanbot --help`.

### New Matrix Bot

1.  **Ensure configuration is complete**: You need a registered Matrix account for the bot and a `.env` file with its credentials and the `ALLOWED_INVITER_USER_ID` (see Configuration section above).
2.  **Make sure `sample.config/alts.json` and `sample.config/services.json` exist** and are configured as they contain the link substitution rules.
3.  **Run the bot**:
    ```bash
    python matrix_bot.py
    ```
4.  **Invite the bot**: From the Matrix account specified as `ALLOWED_INVITER_USER_ID`, invite the bot (e.g., `@yourbotusername:matrix.org`) to a room. The bot should automatically join.
5.  **Test**: Send a message containing a supported link (e.g., a Twitter or YouTube link) in the room. The bot should reply with the substituted version.

The Matrix bot will print logging information to the console.


Resources
---------

- License: GNU Affero General Public License
- Project page: <https://sr.ht/~torresjrjr/linkchanbot>
- Mailing list: <~torresjrjr/linkchanbot@lists.sr.ht> (patches & discussion)

