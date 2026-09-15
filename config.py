import os

from dotenv import load_dotenv


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# ANTHROPIC CONFIGURATION
# --------------------------------------------------

ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY",
    ""
)


# --------------------------------------------------
# BACKEND SECURITY CONFIGURATION
# --------------------------------------------------

TEST_BACKEND_API_KEY = os.getenv(
    "TEST_BACKEND_API_KEY",
    ""
)

TEST_BACKEND_SCOPES = os.getenv(
    "TEST_BACKEND_SCOPES",
    ""
)


# --------------------------------------------------
# RESILIENCY CONFIGURATION
# --------------------------------------------------

MAX_RETRIES = int(
    os.getenv(
        "MAX_RETRIES",
        "3"
    )
)

RETRY_DELAY_SECONDS = float(
    os.getenv(
        "RETRY_DELAY_SECONDS",
        "1"
    )
)