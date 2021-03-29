linkchanbot(1)

# NAME

*linkchanbot* -
A Telegram Bot which sanitises and substitutes share links
with lightweight, privacy respecting proxy frontend alternatives.

# SYNOPSIS

*linkchanbot* [-h] [-v] [-l LOGFILE]

# DESCRIPTION

*linkchanbot* is a Telegram bot utility that transforms share links from common
social media services to links which point to alternative lightweight, privacy
respecting frontends, like Nitter, Invidious, Bibliogram, and Teddit.
*linkchanbot* can substitute links in chat, inline mode, and group chats.

# USAGE

\-h, --help
	show help and exit

\-v, --version
	print version and exit

\-l _LOGFILE_, --logfile _LOGFILE_
	specify the log file

# CONFIGURATION

*linkchanbot* adheres to the XDG Base Directory System,
and sources configuration files
from _$XDG_CONFIG_HOME/linkchan_ (defaults to _$HOME/.config/linkchan_).
*linkchanbot* will copy missing configuration files
from _/etc/local/share/linkchanbot_.

_bot.cfg_
	Defines the _token_ and _admin_ variables.

	_token_
		Required. The Telegram bot token. Visit @botfather.
	_admin_
		Optional. A Telegram username
		to whom the bot will provide the special
		_/restart_ and _/shutdown_ commands.

_alts.json_
	Defines the alternative services (proxies or otherwise)
	available as a substitute.
	An alt's _service_ value should exist
	and have a corresponding a key in _services.json_
	else it won't be recognised as available.

_services.json_
	Defines the domains and subdomains of common services to be
	recognised and replaced.

_queries.json_
	Defines whitelists of queries to be left untouched during substitution.

# TELEGRAM USAGE

Send _/start_ on Telegram. *linkchanbot* will present help.

Additionally, if _admin_ is specified in configuration, the Telegram user
with the username _admin_ will be provided with the following commands:

_/restart_
	Restart the bot. Reads new configuration.

_/shutdown_
	Shutdown the bot.

