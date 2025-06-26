import asyncio
import os
import json
import functools
import pathlib
import re
import logging # Added for improved logging
from urllib.parse import urlparse, urlencode, parse_qs

from dotenv import load_dotenv
from nio import AsyncClient, LoginError, RoomMessageText, MatrixRoom, RoomMemberEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global ALTS and SERVICES dictionaries
ALTS = {}
SERVICES = {}

# Constants
TEMPLATE = """
{new}
<a href="{old}">source</a>
""" # This is HTML, Matrix uses Markdown or HTML subset. Will need adjustment.

# Utility functions from linkchanbot (oneline is still used)
@functools.cache
def oneline(s: str) -> str:
    """
    Converts newlines and tabs to ASCII representations.
    """
    s = s.replace("\\", "\\\\")
    return s.replace("\n", "\\n").replace("\t", "\\t")

@functools.cache
def mk_newlinks(link):
    """
    The core logic of link substitution.
    Given a link, returns either:
        [str...]    A list of new links.
        [False]     A list with a single False element.
    """
    if not ALTS or not SERVICES:
        logger.warning("ALTS or SERVICES not loaded. Link substitution will not work.")
        return [False]

    # Prepare and parse link string
    if not link.startswith("https://") and not link.startswith("http://"):
        link = "https://" + link

    try:
        url = urlparse(link)
    except ValueError:
        return [False] # Invalid URL

    # Enforce HTTPS
    url = url._replace(scheme="https")

    # Recognise service
    if url.netloc in SERVICES.keys():
        service = url.netloc
    else:
        for main_domain, service_data in SERVICES.items():
            if url.netloc in service_data.get("alt_domains", []):
                service = main_domain
                break
        else:
            # Fail if service is unrecognised
            return [False]

    # Keep only allowed URL queries
    allowed_queries = SERVICES[service].get("query_whitelist") or []
    old_queries = parse_qs(url.query, keep_blank_values=True)
    new_queries = {
        query: v for (query, v) in old_queries.items() if query in allowed_queries
    }
    url = url._replace(query=urlencode(new_queries, doseq=True))

    # Find alts for replacing `service`
    applicable_alts = {
        altsite: alt for (altsite, alt) in ALTS.items() if alt.get("service") == service
    }

    if not applicable_alts:
        return [False]

    # Make new substitutes
    newlinks = list(
        map(
            lambda newdomain: url._replace(netloc=newdomain).geturl(),
            applicable_alts.keys(),
        )
    )
    return newlinks


def load_config_data():
    """Loads alts.json and services.json."""
    global ALTS, SERVICES

    script_dir = pathlib.Path(__file__).parent
    default_alts_path = script_dir / "sample.config" / "alts.json"
    default_services_path = script_dir / "sample.config" / "services.json"

    alts_json_path_str = os.environ.get("MATRIX_BOT_ALTS_JSON_PATH")
    services_json_path_str = os.environ.get("MATRIX_BOT_SERVICES_JSON_PATH")

    alts_path = pathlib.Path(alts_json_path_str) if alts_json_path_str else default_alts_path
    services_path = pathlib.Path(services_json_path_str) if services_json_path_str else default_services_path

    try:
        with open(alts_path, "r") as f:
            ALTS = json.load(f)
        logger.info(f"Successfully loaded ALTS from {alts_path}")
    except FileNotFoundError:
        logger.error(f"ALTS file not found at {alts_path}. Link substitution for some services might not work.")
        ALTS = {} # Ensure ALTS is an empty dict if file not found
    except json.decoder.JSONDecodeError as e:
        logger.error(f"JSON syntax error in {alts_path}: {e}")
        ALTS = {}

    try:
        with open(services_path, "r") as f:
            SERVICES = json.load(f)
        logger.info(f"Successfully loaded SERVICES from {services_path}")
    except FileNotFoundError:
        logger.error(f"SERVICES file not found at {services_path}. Link substitution will likely not work.")
        SERVICES = {} # Ensure SERVICES is an empty dict if file not found
    except json.decoder.JSONDecodeError as e:
        logger.error(f"JSON syntax error in {services_path}: {e}")
        SERVICES = {}

    # Validate ALTS (optional, but good practice)
    if ALTS:
        for altsite, alt in ALTS.items():
            if "service" not in alt:
                logger.warning(f"alts.json: '{altsite}' has no 'service' value, it might be ignored or cause issues.")


def find_links_in_text(text):
    """Finds URLs in a given text string."""
    # Basic URL regex, can be improved for more complex cases
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.findall(text)


async def main():
    load_dotenv()
    load_config_data()

    homeserver = os.environ["HOMESERVER"]
    user_id = os.environ["USER_ID"]
    password = os.environ["PASSWORD"]
    device_id = os.environ.get("DEVICE_ID", "linkmatrixbot")
    # room_id is removed, bot will auto-join rooms it's invited to by the admin

    client = AsyncClient(homeserver, user_id, device_id=device_id)

    logger.info(f"Attempting to login as {user_id} on {homeserver}...")
    try:
        login_response = await client.login(password, device_name=device_id)
        if isinstance(login_response, LoginError):
            logger.error(f"Failed to login: {login_response.message}")
            return
    except Exception as e:
        logger.error(f"Login exception: {e}", exc_info=True)
        return

    logger.info("Login successful!")

    allowed_inviter_user_id = os.environ.get("ALLOWED_INVITER_USER_ID")
    if not allowed_inviter_user_id:
        logger.warning("ALLOWED_INVITER_USER_ID not set. Bot will not accept any invites.")

    # Define callbacks first
    async def on_room_invite_callback(room: MatrixRoom, event: RoomMemberEvent):
        if event.membership != "invite" or event.state_key != client.user_id:
            return # Not an invite for us

        logger.info(f"Received invite to room {room.room_id} ({room.display_name}) from {event.sender}")

        if allowed_inviter_user_id and event.sender == allowed_inviter_user_id:
            logger.info(f"Inviter {event.sender} is authorized. Joining room {room.room_id}")
            try:
                await client.join(room.room_id)
                logger.info(f"Successfully joined room {room.room_id}")
            except Exception as e:
                logger.error(f"Failed to join room {room.room_id}: {e}", exc_info=True)
        else:
            logger.info(f"Inviter {event.sender} is not authorized. Rejecting invite for room {room.room_id}")
            try:
                await client.room_leave(room.room_id)
                logger.info(f"Successfully rejected (left) room {room.room_id}")
            except Exception as e:
                logger.error(f"Failed to leave (reject) room {room.room_id}: {e}", exc_info=True)

    async def message_handler_callback(room: MatrixRoom, event: RoomMessageText):
        logger.debug(
            f"Message received in room {room.room_id} ({room.display_name}) | Sender: {event.sender} | Body: {event.body}"
        )

        if event.sender == client.user_id: # Don't reply to our own messages
            return

        found_links = find_links_in_text(event.body)
        if not found_links:
            return

        replies = []
        for link in found_links:
            new_links = mk_newlinks(link)
            if new_links and new_links[0]: # mk_newlinks returns [False] on failure
                substituted_link = new_links[0]
                reply_text = f"{substituted_link} (source: {link})"
                replies.append(reply_text)

        if replies:
            full_reply = "\n".join(replies)
            try:
                await client.room_send(
                    room_id=room.room_id,
                    message_type="m.room.message",
                    content={"msgtype": "m.text", "body": full_reply},
                )
            except Exception as e:
                logger.error(f"Failed to send message to room {room.room_id}: {e}", exc_info=True)

    # Perform an initial sync to ensure client is ready
    logger.info("Performing initial sync with server...")
    try:
        await client.sync(timeout=30000, full_state=True)
        logger.info("Initial sync complete.")
    except Exception as e:
        logger.error(f"Error during initial sync: {e}", exc_info=True)
        await client.close()
        return

    # Register callbacks after initial sync
    logger.info("Registering event callbacks...")
    client.add_event_callback(on_room_invite_callback, RoomMemberEvent)
    client.add_event_callback(message_handler_callback, RoomMessageText)
    logger.info("Event callbacks registered.")

    logger.info("Starting continuous sync with server...")
    try:
        await client.sync_forever(timeout=30000, full_state=False)  # full_state=False for subsequent syncs
    except Exception as e:
        logger.error(f"Error during sync_forever: {e}", exc_info=True)
    finally:
        logger.info("Closing client...")
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
