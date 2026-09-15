import os
import re


# --------------------------------------------------
# SIMULATED EXTERNAL TEST MANAGEMENT BACKEND
# --------------------------------------------------

EXPECTED_API_KEY = "test-backend-demo-key"

TEST_CASE_ID_PATTERN = re.compile(
    r"^TC-\d{3}$"
)


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
        raise RuntimeError(
            "TEST_BACKEND_API_KEY is not configured"
        )

    if api_key != EXPECTED_API_KEY:
        raise PermissionError(
            "Invalid backend API key"
        )


# --------------------------------------------------
# INPUT VALIDATION
# --------------------------------------------------

def validate_test_case_id(
    test_case_id: str
) -> None:
    """
    Validate the test-case identifier.

    Expected format:
    TC- followed by exactly three digits.

    Examples:
    TC-101
    TC-102
    TC-999
    """

    if not test_case_id:
        raise ValueError(
            "Test case ID cannot be empty"
        )

    if not isinstance(
        test_case_id,
        str
    ):
        raise TypeError(
            "Test case ID must be a string"
        )

    if not TEST_CASE_ID_PATTERN.fullmatch(
        test_case_id
    ):
        raise ValueError(
            "Invalid test case ID format. "
            "Expected format: TC-123"
        )


# --------------------------------------------------
# BACKEND OPERATION
# --------------------------------------------------

def get_test_status(
    test_case_id: str
) -> str:
    """
    Retrieve test status from the simulated backend.
    """

    validate_test_case_id(
        test_case_id
    )

    authenticate()

    test_data = {
        "TC-101": "Passed",
        "TC-102": "Failed",
        "TC-103": "In Progress"
    }

    return test_data.get(
        test_case_id,
        "Test case not found"
    )