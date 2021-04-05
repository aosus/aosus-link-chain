linkchanbot(1)

# NAME

*linkchanbot* -
A Telegram Bot which sanitises and substitutes share links
with lightweight, privacy respecting proxy frontend alternatives.

# SYNOPSIS

*linkchanbot* [-h] [-v] [-l _LOGFILE_]

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
	Defines the *token* and *admin* variables.

	*token*
		Required. The Telegram bot token. Visit @botfather.
	*admin*
		Optional. A Telegram username
		to whom the bot will provide the special
		*/restart* and */shutdown* commands.

_alts.json_
	Defines the alternative services (proxies or otherwise)
	available as a substitute.
	An alt's *service* value should exist
	and have a corresponding a key in _services.json_,
	else it will be ignored.

_services.json_
	Defines common services to be recognised and replaced.
	For each domain, defines the alternate domains and whitelists
	of queries to be left untouched during substitution.

# TELEGRAM USAGE

Send */start* on Telegram. *linkchanbot* will present usage information.

Additionally, if *admin* is specified in configuration, the Telegram user
with the username *admin* will be provided with the following commands:

*/restart*
	Restart the bot. Reads new configuration.

*/shutdown*
	Shutdown the bot.

