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

### Prerequisites

- A Telegram bot token (visit [@botfather](https://t.me/botfather)).

### Dependencies

- [scdoc](https://sr.ht/~sircmpwn/scdoc) (build dep.)
- Python >= 3.9
- PyPI: python-telegram-bot >= 13

### Install

	$ git clone https://git.sr.ht/~torresjrjr/linkchanbot
	$ cd linkchanbot
	$ python -m pip install -r requirements.txt
	# make install

To start serving, linkchanbot needs further configuration.


Configuration
-------------

### Telegram

- Visit [@botfather](https://t.me/botfather).
- Create a new bot (or select an existing one).
- Save the bot API token.
- Disable "Group Privacy mode".
- Enable "Inline mode".
- Set the "inline placeholder" to "Paste link...".
- Optionally set "inline feedback" to "100%" for logging.
- Set the bot commands: `/start`, `/help`, and `/about`.

### Server

Add the required bot token (and optionally an admin username)
either in `bot.cfg` in the linkchan config directory
(`$XDG_CONFIG_HOME/linkchan` or `$HOME/.config/linkchan`):

	[auth]
	# required
	token = 123:ABC...
	# optional, provides /restart and /shutdown
	admin = username

Or by environment variable:

	$ export LINKCHAN_TOKEN='123:ABC...'
	$ export LINKCHAN_ADMIN='admin_username'

Your bot should now be ready.

### Advanced configuration

See `linkchanbot(1)`


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

See `linkchanbot(1)` or `linkchanbot --help`.


Resources
---------

- License: GNU Affero General Public License
- Project page: <https://sr.ht/~torresjrjr/linkchanbot>
- Mailing list: <~torresjrjr/linkchanbot@lists.sr.ht> (patches & discussion)

