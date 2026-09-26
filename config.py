# --------------------------------------------------
# CENTRAL RUNTIME CONFIGURATION
# --------------------------------------------------
# All settings are read from environment variables.
# A local .env file (see .env.example) is loaded first
# for convenience. Values are read once, at import time.

import os

from dotenv import load_dotenv


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

# Loads key=value pairs from the .env file into the
# process environment.
# Variables that are already set in the shell / OS
# take priority and are NOT overwritten by .env.
load_dotenv()


# --------------------------------------------------
# ANTHROPIC CONFIGURATION
# --------------------------------------------------

# API key for the Claude Messages API.
# Default: "" (not configured).
# Currently not imported directly by the Claude client scripts.
# Anthropic() reads ANTHROPIC_API_KEY from the process environment.
ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY",
    ""
)


# --------------------------------------------------
# BACKEND SECURITY CONFIGURATION
# --------------------------------------------------

# API key used by test_management_backend.authenticate().
# Default: "" (not configured).
# - Empty value -> BackendAuthenticationError
#   ("TEST_BACKEND_API_KEY is not configured")
# - Wrong value -> BackendAuthenticationError
#   ("Invalid backend API key")
TEST_BACKEND_API_KEY = os.getenv(
    "TEST_BACKEND_API_KEY",
    ""
)

# Permissions granted to the backend identity.
# Format: comma-separated list; spaces around each
# scope are ignored.
# Example: read:test_status,read:test_owner
# Default: "" (no scopes -> every protected call
# raises PermissionError).
# get_test_status requires: read:test_status
TEST_BACKEND_SCOPES = os.getenv(
    "TEST_BACKEND_SCOPES",
    ""
)


# --------------------------------------------------
# RESILIENCY CONFIGURATION
# --------------------------------------------------

# Total number of attempts for a backend operation,
# INCLUDING the first attempt (not "extra" retries).
# Example: 3 -> 1 initial attempt + up to 2 retries.
# Only BackendTransientError is retried; validation,
# authentication and authorization errors fail at once.
# Must be a whole number >= 1. Default: 3.
MAX_RETRIES = int(
    os.getenv(
        "MAX_RETRIES",
        "3"
    )
)

# Fixed wait, in seconds, between retry attempts
# (no exponential backoff). Decimals are allowed,
# e.g. 0.5. Default: 1.
RETRY_DELAY_SECONDS = float(
    os.getenv(
        "RETRY_DELAY_SECONDS",
        "1"
    )
)