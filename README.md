# A matrix bot that automatically replies with a link to alternative frontends

**Fully vibe coded**

A Matrix bot that sanitises and substitutes share links in Matrix rooms with lightweight, privacy-respecting proxy frontend alternatives.

When in a room, the bot will listen for messages containing links. If a supported link (e.g., Twitter, YouTube) is detected, it will post a reply with a link to an alternative frontend (e.g., Nitter, Invidious).

Supported services are configurable via `services.json`, and the alternative frontends are defined in `alts.json`.

## Features

- Replaces links (e.g., Twitter/X, YouTube, Instagram, Reddit) with privacy-focused alternatives (e.g., Nitter, Invidious). URL detection is case-insensitive.
- Recognizes `x.com` as an alias for `twitter.com`. (It's recommended to also add `x.com` to the `alt_domains` list for `twitter.com` in your `services.json` for full clarity, though the bot attempts to handle this).
- Configurable list of supported services and alternative frontends via `services.json` and `alts.json`.
- **Session Persistence**: Remembers its Matrix session (access token, device ID) across restarts, avoiding the need for password login every time, by storing data in a specified directory.
- Operates only in rooms it is already a member of (manual addition to rooms required).
- Dockerized for easy deployment.

## Prerequisites

- A Matrix user account for the bot (register on your chosen homeserver).
- Python >= 3.11.
- Docker and Docker Compose (for Docker-based deployment).

## Configuration

The Matrix bot is configured using environment variables. Create a `.env` file in the root of the project by copying `.env.example` and fill in the details:

```env
# .env file for Matrix Bot
HOMESERVER="https://matrix-client.matrix.org"  # Your bot's homeserver URL
USER_ID="@yourbotusername:matrix.org"        # Full Matrix User ID of the bot
# PASSWORD="yourbotpassword"                 # Bot's account password. Required for first login or if session store is invalid. Can be removed after first successful login if session is persisted.
# DEVICE_ID="linkmatrixbot"                  # Optional: A friendly name for the bot's device/session, used on first login.
MATRIX_BOT_STORE_PATH="/app/store"           # Path inside the container for storing session data. E.g., /app/store (for Docker) or ./matrix_bot_data/store (for local)

# Optional: Custom paths for alts and services JSON files
# If not set, defaults to sample.config/alts.json and sample.config/services.json relative to the script
# MATRIX_BOT_ALTS_JSON_PATH="/path/to/your/alts.json"
# MATRIX_BOT_SERVICES_JSON_PATH="/path/to/your/services.json"
```

- `HOMESERVER`: The URL of the Matrix homeserver your bot is registered on.
- `USER_ID`: The bot's full Matrix ID (e.g., `@botname:yourserver.org`).
- `PASSWORD` (Optional after first login): The password for the bot's Matrix account. Needed for the very first login, or if the session data in `MATRIX_BOT_STORE_PATH` becomes invalid. Can be removed from the `.env` file once the bot has successfully logged in and created a session store.
- `DEVICE_ID` (Optional): A descriptive name for the bot's device/session, primarily used during the initial login if no session store exists.
- `MATRIX_BOT_STORE_PATH`: **Required for session persistence.** Path to a directory where the bot will store its session data (access token, device ID, sync token). This allows the bot to resume its session on restart without needing the password.
    - When using Docker, this path should correspond to the container-side path of a mounted volume (e.g., `/app/store` which is mapped from `./matrix_bot_data/store` on the host in `docker-compose.yml`).
    - When running directly with Python, choose a writable path (e.g., `./matrix_bot_data/store`).
- `MATRIX_BOT_ALTS_JSON_PATH` (Optional): Specifies a custom path to the `alts.json` file.
- `MATRIX_BOT_SERVICES_JSON_PATH` (Optional): Specifies a custom path to the `services.json` file.
- `LOG_LEVEL` (Optional): Sets the logging level for the bot.

The `alts.json` and `services.json` files define the link substitution rules. By default, the bot expects these to be in the `sample.config/` directory.

## Running the Bot

The bot needs to be manually invited or added to the Matrix rooms where it should operate. It will not automatically accept invitations.

### 1. Directly with Python (for development or simple deployments)

#### Installation

1.  Clone the repository.
2.  Install Python dependencies: `pip install matrix-nio python-dotenv`.
3.  Create and configure your `.env` file, ensuring `MATRIX_BOT_STORE_PATH` points to a writable directory (e.g., `./matrix_bot_data/store`).
4.  Ensure `sample.config/alts.json` and `sample.config/services.json` exist (or your custom paths are configured).

#### Usage

1.  Run the bot: `python matrix_bot.py`.
    *   On the first run, ensure `PASSWORD` is set in `.env` for initial login. The bot will create session files in `MATRIX_BOT_STORE_PATH`.
    *   On subsequent runs, the bot will attempt to use the stored session.
2.  Manually add/invite the bot to the desired Matrix rooms.
3.  Test: Send a message containing a supported link.

### 2. Using Docker (Recommended for most deployments)

#### Prerequisites (Docker)

- Docker and Docker Compose installed.

#### Running with Docker Compose

Use the template docker-compose file, make sure to set the required variables
