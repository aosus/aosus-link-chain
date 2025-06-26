# Matrix Link Replacer Bot

A Matrix bot that sanitises and substitutes share links in Matrix rooms with lightweight, privacy-respecting proxy frontend alternatives.

When invited to a room by an authorized user, the bot will listen for messages containing links. If a supported link (e.g., Twitter, YouTube) is detected, it will post a reply with a link to an alternative frontend (e.g., Nitter, Invidious).

Supported services are configurable via `services.json`, and the alternative frontends are defined in `alts.json`.

## Features

- Replaces links (e.g., Twitter/X, YouTube, Instagram, Reddit) with privacy-focused alternatives (e.g., Nitter, Invidious). URL detection is case-insensitive.
- Recognizes `x.com` as an alias for `twitter.com`. (It's recommended to also add `x.com` to the `alt_domains` list for `twitter.com` in your `services.json` for full clarity, though the bot attempts to handle this).
- Configurable list of supported services and alternative frontends via `services.json` and `alts.json`.
- Secure: Only joins rooms when invited by a pre-configured authorized Matrix User ID.
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
PASSWORD="yourbotpassword"                   # Bot's account password
# DEVICE_ID="linkmatrixbot"                  # Optional: A friendly name for the bot's device/session
ALLOWED_INVITER_USER_ID="@adminuser:matrix.org" # Full Matrix User ID of the person allowed to invite the bot

# Optional: Custom paths for alts and services JSON files
# If not set, defaults to sample.config/alts.json and sample.config/services.json relative to the script
# MATRIX_BOT_ALTS_JSON_PATH="/path/to/your/alts.json"
# MATRIX_BOT_SERVICES_JSON_PATH="/path/to/your/services.json"
```

- `HOMESERVER`: The URL of the Matrix homeserver your bot is registered on.
- `USER_ID`: The bot's full Matrix ID (e.g., `@botname:yourserver.org`).
- `PASSWORD`: The password for the bot's Matrix account.
- `DEVICE_ID` (Optional): A descriptive name for the bot's session.
- `ALLOWED_INVITER_USER_ID`: Crucial for security. This is the full Matrix ID of the user who has permission to invite the bot into rooms. The bot will ignore invites from anyone else.
- `MATRIX_BOT_ALTS_JSON_PATH` (Optional): Specifies a custom path to the `alts.json` file. If not set, the bot defaults to looking for `sample.config/alts.json` relative to the `matrix_bot.py` script (or `/app/sample.config/alts.json` inside Docker).
- `MATRIX_BOT_SERVICES_JSON_PATH` (Optional): Specifies a custom path to the `services.json` file. If not set, the bot defaults to looking for `sample.config/services.json` relative to the `matrix_bot.py` script (or `/app/sample.config/services.json` inside Docker).

The `alts.json` and `services.json` files define the link substitution rules. By default, the bot expects these to be in the `sample.config/` directory. You can customize their location using the environment variables above. Sample files are provided in `sample.config/`.

## Running the Bot

There are two main ways to run the bot:

### 1. Directly with Python (for development or simple deployments)

#### Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd matrix-link-replacer-bot # Or your chosen directory name
    ```
2.  Install Python dependencies:
    ```bash
    pip install matrix-nio python-dotenv
    ```
3.  Ensure your `.env` file is configured as described above.
4.  Make sure `sample.config/alts.json` and `sample.config/services.json` exist (or your custom paths are configured).

#### Usage

1.  Run the bot:
    ```bash
    python matrix_bot.py
    ```
2.  Invite the bot: From the Matrix account specified as `ALLOWED_INVITER_USER_ID`, invite the bot (e.g., `@yourbotusername:matrix.org`) to a room. The bot should automatically join.
3.  Test: Send a message containing a supported link (e.g., a Twitter or YouTube link) in the room. The bot should reply with the substituted version.

The Matrix bot will print logging information to the console.

### 2. Using Docker (Recommended for most deployments)

The Matrix bot can be run as a Docker container using Docker Compose.

#### Prerequisites (Docker)

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop, or can be installed separately [Install Docker Compose](https://docs.docker.com/compose/install/))

#### Building and Running with Docker Compose

1.  **Ensure Configuration is Ready**:
    *   Make sure you have a `.env` file in the root of the project, correctly filled out as described in the "Configuration" section. Docker Compose will use this file to provide environment variables to the container.
    *   The default `Dockerfile` copies the `sample.config/` directory into the image. If you want to use custom `alts.json` or `services.json` files from your host machine:
        *   **Option 1 (Recommended for custom files):** Place your `alts.json` and `services.json` in a directory on your host machine (e.g., `./my_matrix_config/`). Then, in your `.env` file, set the paths to point within the container, for example:
            ```env
            MATRIX_BOT_ALTS_JSON_PATH=/app/user_config/alts.json
            MATRIX_BOT_SERVICES_JSON_PATH=/app/user_config/services.json
            ```
            And uncomment/adjust the volume mounts in `docker-compose.yml` to map your host directory to `/app/user_config` in the container:
            ```yaml
            # In docker-compose.yml:
            # services:
            #   matrix-link-replacer:
            #     volumes:
            #       - ./my_matrix_config:/app/user_config:ro
            ```
            (Note: The `docker-compose.yml` provided has a placeholder for volumes, you might need to uncomment and adjust it.)
        *   **Option 2 (Using default sample.config from image):** If you're using the `sample.config` files included in the repository (and thus in the Docker image), ensure `MATRIX_BOT_ALTS_JSON_PATH` and `MATRIX_BOT_SERVICES_JSON_PATH` are unset in your `.env` file so the bot uses the defaults within the container (i.e., `/app/sample.config/alts.json` and `/app/sample.config/services.json`).

2.  **Build and Run the Container**:
    Open a terminal in the root of the project directory (where `docker-compose.yml` is located) and run:
    ```bash
    docker-compose up --build -d
    ```
    - `--build`: Forces Docker Compose to build the image (e.g., if you've changed `Dockerfile` or files it copies).
    - `-d`: Runs the container in detached mode (in the background).

3.  **Viewing Logs**:
    To view the logs of the running container:
    ```bash
    docker-compose logs -f matrix-link-replacer
    ```

4.  **Stopping the Container**:
    To stop the container:
    ```bash
    docker-compose down
    ```

#### Notes on Docker Configuration

- **Environment Variables**: The `docker-compose.yml` uses `env_file: .env` to load variables from a `.env` file located in the project root. This is a convenience for local development with Docker Compose. The Python script itself (`matrix_bot.py`) reads standard environment variables. Therefore, when deploying outside of Docker Compose (e.g., with `docker run` or in orchestrated environments like Kubernetes), you should provide environment variables directly to the container. These externally provided variables will be used by the application. If a `.env` file is not present inside the container's working directory or if variables are already set in the environment, `python-dotenv` (used in the script) will not override them.
- The bot inside the Docker container will behave the same way as running it directly, respecting the `ALLOWED_INVITER_USER_ID` and other configurations provided via environment variables.

## Automated Docker Image Publishing

This project uses GitHub Actions to automatically build and publish the Docker image to the GitHub Container Registry (GHCR).

- **On every push to the `main` branch**: The Docker image is built and pushed to `ghcr.io/<OWNER>/<REPOSITORY_NAME>:latest` and `ghcr.io/<OWNER>/<REPOSITORY_NAME>:sha-<commit_sha>`. Replace `<OWNER>` and `<REPOSITORY_NAME>` with your GitHub username/organization and repository name respectively (these are typically automatically lowercased by GHCR).
- **On every pull request to the `main` branch**: The Docker image is built as a test to ensure the Dockerfile is valid and the application can be packaged, but it is not pushed.

You can find the workflow definition in `.github/workflows/docker-publish.yml`.

### Workflow Status

[![Docker Build and Publish](https://github.com/OWNER/REPOSITORY_NAME/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/OWNER/REPOSITORY_NAME/actions/workflows/docker-publish.yml)

*(Please replace `OWNER/REPOSITORY_NAME` in the badge URL above with your actual GitHub repository owner and name after the initial commit for the badge to work correctly.)*

### Using the Published Image

Once published, you can pull the image using:
```bash
docker pull ghcr.io/<owner>/<repository_name>:latest
```
And use it in your Docker Compose file by referencing this image name instead of using the `build:` context, or in other Docker environments. Remember to replace `<owner>` and `<repository_name>` with the actual values (usually lowercase).

## License

This project is based on the original linkchanbot and is likely under the GNU Affero General Public License. Please check the `LICENSE` file for details. (Note: Original `LICENSE` file might need review if project has significantly diverged or if new components have different licenses).
