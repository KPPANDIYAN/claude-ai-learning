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
    Represents authentication failures.

    These failures should NOT normally be retried.
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

    @param test_case_id: Test case identifier to validate.
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

def execute_with_retry(operation):
    """
    Execute a backend operation and retry only
    temporary/transient backend failures.

    Validation and authentication errors are
    intentionally not retried.

    @param operation: Callable backend operation.
    @return: Result returned by the backend operation.
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
    Simulate reading test status from an
    external test-management backend.

    In a real system, this method could contain:
    - REST API call
    - database query
    - Jira/TestRail call
    - TetraScience request

    @param test_case_id: Test case identifier.
    @return: Current test execution status.
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
    2. Authenticate
    3. Execute backend read
    4. Retry only transient backend failures

    @param test_case_id: Test case identifier.
    @return: Current test execution status.
    """

    validate_test_case_id(
        test_case_id
    )

    authenticate()

    def backend_operation():

        return read_test_status_from_backend(
            test_case_id
        )

    return execute_with_retry(
        backend_operation
    )