import asyncio
import os
import json
import functools
import pathlib
import re
import logging # Added for improved logging
import time # Added for timestamping
from urllib.parse import urlparse, urlencode, parse_qs

from dotenv import load_dotenv
from nio import AsyncClient, LoginError, RoomMessageText, MatrixRoom, RoomMemberEvent

# Configure logging
# Log level will be set based on environment variable LOG_LEVEL
log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO) # Fallback to INFO if invalid

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.info(f"Logging level set to: {logging.getLevelName(logger.getEffectiveLevel())}")


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
    logger.debug(f"mk_newlinks: Processing link: {link}")
    if not ALTS or not SERVICES:
        logger.warning("mk_newlinks: ALTS or SERVICES not loaded. Link substitution will not work.")
        return [False]

    original_link = link # Keep original for logging
    # Prepare and parse link string
    if not link.startswith("https://") and not link.startswith("http://"):
        link = "https://" + link

    try:
        url = urlparse(link)
    except ValueError:
        logger.warning(f"mk_newlinks: Invalid URL '{original_link}' resulted in ValueError during parsing.")
        return [False] # Invalid URL

    # Enforce HTTPS
    url = url._replace(scheme="https")
    parsed_netloc_lower = url.netloc.lower() # Normalize netloc to lowercase for matching

    # Recognise service
    service_key_matched = None # This will store the canonical key from SERVICES dict
    if parsed_netloc_lower in SERVICES:
        service_key_matched = parsed_netloc_lower # Direct match with a primary service domain (already lowercase)
    else:
        # Iterate through services and their alt_domains (also lowercased for comparison)
        for main_domain, service_data in SERVICES.items():
            # Ensure alt_domains are treated as lowercase for matching
            alt_domains_lower = [ad.lower() for ad in service_data.get("alt_domains", [])]
            if parsed_netloc_lower in alt_domains_lower:
                service_key_matched = main_domain # Matched an alt_domain, use its main_domain key
                break

    if not service_key_matched:
        logger.debug(f"mk_newlinks: Service not recognized for domain '{url.netloc}' (normalized: '{parsed_netloc_lower}') from link '{original_link}'.")
        return [False]

    logger.debug(f"mk_newlinks: Recognized link '{original_link}' as service '{service_key_matched}' (matched on '{parsed_netloc_lower}').")

    # Keep only allowed URL queries (path, query, fragment should retain original casing from url object)
    allowed_queries = SERVICES[service_key_matched].get("query_whitelist", [])
    old_queries = parse_qs(url.query, keep_blank_values=True)
    new_queries = {
        query: v for (query, v) in old_queries.items() if query in allowed_queries
    }
    # Create a new URL object for modification that only has scheme, queries, path, etc. from original,
    # but netloc will be replaced by alt domains.
    # The original url object still has original casing for path/query.
    url_to_substitute = url._replace(query=urlencode(new_queries, doseq=True))


    # Find alts for replacing `service_key_matched`
    applicable_alts = {
        altsite: alt_data for (altsite, alt_data) in ALTS.items() if alt_data.get("service", "").lower() == service_key_matched
    }
    logger.debug(f"mk_newlinks: Found applicable_alts: {list(applicable_alts.keys())} for service '{service_key_matched}'.")

    if not applicable_alts:
        logger.debug(f"mk_newlinks: No applicable alts found for service '{service_key_matched}' from link '{original_link}'.")
        return [False]

    # Make new substitutes
    # When substituting, we use the altsite (which should be a domain) as the new netloc.
    # The path, query (now sanitized), and fragment are taken from url_to_substitute.
    newlinks = list(
        map(
            lambda new_alt_domain: url_to_substitute._replace(netloc=new_alt_domain).geturl(),
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

    # Dynamically add x.com as an alias for twitter.com if twitter.com service exists
    if "twitter.com" in SERVICES:
        if "alt_domains" not in SERVICES["twitter.com"]:
            SERVICES["twitter.com"]["alt_domains"] = []
        if "x.com" not in SERVICES["twitter.com"]["alt_domains"]:
            SERVICES["twitter.com"]["alt_domains"].append("x.com")
            logger.info("Dynamically added 'x.com' as an alt_domain for 'twitter.com' service.")


def find_links_in_text(text):
    """Finds URLs in a given text string.
    Attempts to find URLs with or without http(s):// prefix.
    """
    # This regex looks for:
    # 1. Optional http:// or https://
    # 2. Optional www.
    # 3. A domain name part (sequence of subdomain.domain.tld)
    # 4. A path part (anything after / that's not whitespace)
    # It's not perfect and might match things like "file.py" if not careful,
    # but it's more inclusive. We rely on mk_newlinks to validate if it's a known service.
    url_pattern = re.compile(
        r'(?:(?:http[s]?://|ftp://|www\.)|(?:(?!(?:http[s]?|ftp)://|www\.))(?=[a-zA-Z0-9]))'  # Scheme or www, or start of domain
        r'(?:[a-zA-Z0-9\-]+\.)+(?:[a-zA-Z]{2,})'  # domain.tld
        r'(?::[0-9]+)?'  # Optional port
        r'(?:/[^\s]*)?'  # Optional path
        r'(?=\b|[\s"\'<>]|$)', # Ensure it's a boundary or end of string to avoid matching parts of words
        re.IGNORECASE  # Make matching case-insensitive
    )
    # Previous simpler regex for http(s) only:
    # url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.findall(text)


async def main():
    load_dotenv()
    load_config_data()

    homeserver = os.environ["HOMESERVER"]
    user_id = os.environ["USER_ID"]
    password = os.environ["PASSWORD"]
    device_id = os.environ.get("DEVICE_ID", "linkmatrixbot")

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

    # Initialize bot_startup_time here. It will be set properly before sync_forever.
    bot_startup_time = 0

    # Define callbacks as regular async functions
    async def on_room_invite_callback(room: MatrixRoom, event: RoomMemberEvent):
        logger.debug("on_room_invite_callback: Entered function.")
        if event.membership != "invite" or event.state_key != client.user_id:
            logger.debug(
                f"on_room_invite_callback: Ignoring event, not an invite for us. "
                f"Membership: {event.membership}, State Key: {event.state_key} (our user_id: {client.user_id})"
            )
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
        # This callback reads bot_startup_time from the enclosing main() scope
        logger.debug(
            f"Message received in room {room.room_id} ({room.display_name}) | Sender: {event.sender} | Body: {event.body}"
        )

        if event.server_timestamp <= bot_startup_time: # Uses bot_startup_time from main's scope
            logger.debug(f"Ignoring old message from {event.sender} with timestamp {event.server_timestamp} (startup: {bot_startup_time})")
            return

        if event.sender == client.user_id: # Don't reply to our own messages
            logger.debug("Message is from self, ignoring.")
            return

        found_links = find_links_in_text(event.body)
        if not found_links:
            logger.debug("No links found in message.")
            return

        logger.debug(f"Found links: {found_links}")

        replies = []
        for link in found_links:
            logger.debug(f"Processing link for substitution: {link}")
            new_links = mk_newlinks(link) # This function now has more logging
            if new_links and new_links[0] is not False: # Check explicitly for not False
                substituted_link = new_links[0]
                logger.debug(f"Substituted link {link} -> {substituted_link}")
                reply_text = substituted_link # Changed to only send the new link
                replies.append(reply_text)
            else:
                logger.debug(f"No substitution found or mk_newlinks failed for {link}")

        if replies:
            full_reply = "\n".join(replies)
            logger.info(f"Sending reply to room {room.room_id}: {full_reply}")
            try:
                await client.room_send(
                    room_id=room.room_id,
                    message_type="m.room.message",
                    content={"msgtype": "m.text", "body": full_reply},
                )
            except Exception as e:
                logger.error(f"Failed to send message to room {room.room_id}: {e}", exc_info=True)
        else:
            logger.debug(f"No replies generated for message from {event.sender} in room {room.room_id}.")

    # Register callbacks explicitly after client login and before starting sync loop
    logger.info("Registering event callbacks...")
    client.add_event_callback(on_room_invite_callback, RoomMemberEvent)
    client.add_event_callback(message_handler_callback, RoomMessageText)
    logger.info("Event callbacks registered.")

    # Set the actual startup timestamp *before* starting the sync loop that uses it.
    bot_startup_time = int(time.time() * 1000)
    logger.info(f"Bot startup timestamp set to: {bot_startup_time}")

    logger.info("Starting sync_forever with server (full_state=True for initial sync)...")
    try:
        # full_state=True on the first run of sync_forever will get initial room states.
        # nio handles the transition from initial sync to subsequent incremental syncs.
        await client.sync_forever(timeout=30000, full_state=True)
    except Exception as e:
        logger.error(f"Error during sync_forever: {e}", exc_info=True)
    finally:
        logger.info("Closing client...")
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
