import os
import re
import time


# --------------------------------------------------
# SIMULATED EXTERNAL TEST MANAGEMENT BACKEND
# --------------------------------------------------

EXPECTED_API_KEY = "test-backend-demo-key"

TEST_CASE_ID_PATTERN = re.compile(
    r"^TC-\d{3}$"
)

REQUIRED_STATUS_SCOPE = "read:test_status"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1


# --------------------------------------------------
# CUSTOM BACKEND EXCEPTIONS
# --------------------------------------------------

class BackendTransientError(Exception):
    """
    Represents a temporary backend failure.

    Examples:
    - temporary network issue
    - HTTP 502
    - HTTP 503
    - connection reset

    These failures may be retried.
    """
    pass


class BackendAuthenticationError(Exception):
    """
    Represents backend authentication failures.

    These failures should not normally be retried.
    """
    pass


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

def authenticate() -> None:
    """
    Validate that the backend API key exists
    and matches the expected demo credential.
    """

    api_key = os.getenv(
        "TEST_BACKEND_API_KEY"
    )

    if not api_key:
        raise BackendAuthenticationError(
            "TEST_BACKEND_API_KEY is not configured"
        )

    if api_key != EXPECTED_API_KEY:
        raise BackendAuthenticationError(
            "Invalid backend API key"
        )


# --------------------------------------------------
# AUTHORIZATION
# --------------------------------------------------

def authorize(
    required_scope: str
) -> None:
    """
    Verify that the authenticated backend identity
    has the required permission.

    Example environment value:

    TEST_BACKEND_SCOPES=read:test_status

    Multiple scopes can be comma-separated.

    Example:

    TEST_BACKEND_SCOPES=
    read:test_status,read:test_owner
    """

    configured_scopes = os.getenv(
        "TEST_BACKEND_SCOPES",
        ""
    )

    allowed_scopes = {
        scope.strip()
        for scope in configured_scopes.split(",")
        if scope.strip()
    }

    if required_scope not in allowed_scopes:
        raise PermissionError(
            f"Missing required scope: {required_scope}"
        )


# --------------------------------------------------
# INPUT VALIDATION
# --------------------------------------------------

def validate_test_case_id(
    test_case_id: str
) -> None:
    """
    Validate the test case identifier.

    Expected format:
    TC- followed by exactly three digits.

    Examples:
    TC-101
    TC-102
    TC-999
    """

    if not isinstance(
        test_case_id,
        str
    ):
        raise TypeError(
            "Test case ID must be a string"
        )

    if not test_case_id:
        raise ValueError(
            "Test case ID cannot be empty"
        )

    if not TEST_CASE_ID_PATTERN.fullmatch(
        test_case_id
    ):
        raise ValueError(
            "Invalid test case ID format. "
            "Expected format: TC-123"
        )


# --------------------------------------------------
# RETRY HANDLER
# --------------------------------------------------

def execute_with_retry(
    operation
):
    """
    Execute a backend operation and retry only
    transient backend failures.

    Authentication, authorization and validation
    failures are intentionally not retried.
    """

    last_error = None

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:
            return operation()

        except BackendTransientError as error:

            last_error = error

            print(
                f"Transient backend failure. "
                f"Attempt {attempt}/{MAX_RETRIES}"
            )

            if attempt == MAX_RETRIES:
                raise

            time.sleep(
                RETRY_DELAY_SECONDS
            )

    raise last_error


# --------------------------------------------------
# SIMULATED BACKEND READ
# --------------------------------------------------

def read_test_status_from_backend(
    test_case_id: str
) -> str:
    """
    Simulate reading test status from an external
    test-management system.

    In a real system this could contain:
    - REST API call
    - database query
    - Jira/TestRail call
    - TetraScience request
    """

    test_data = {
        "TC-101": "Passed",
        "TC-102": "Failed",
        "TC-103": "In Progress"
    }

    return test_data.get(
        test_case_id,
        "Test case not found"
    )


# --------------------------------------------------
# PUBLIC BACKEND OPERATION
# --------------------------------------------------

def get_test_status(
    test_case_id: str
) -> str:
    """
    Retrieve test status from the simulated backend.

    Processing order:

    1. Validate input
    2. Authenticate caller
    3. Authorize required capability
    4. Execute backend operation
    5. Retry only transient failures
    """

    validate_test_case_id(
        test_case_id
    )

    authenticate()

    authorize(
        REQUIRED_STATUS_SCOPE
    )

    def backend_operation():

        return read_test_status_from_backend(
            test_case_id
        )

    return execute_with_retry(
        backend_operation
    )