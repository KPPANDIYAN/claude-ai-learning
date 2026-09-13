import os


# --------------------------------------------------
# SIMULATED EXTERNAL TEST MANAGEMENT BACKEND
# --------------------------------------------------

EXPECTED_API_KEY = "test-backend-demo-key"


def authenticate() -> None:
    """
    Validate that the backend API key is available
    and matches the expected value.
    """

    api_key = os.getenv("TEST_BACKEND_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TEST_BACKEND_API_KEY is not configured"
        )

    if api_key != EXPECTED_API_KEY:
        raise PermissionError(
            "Invalid backend API key"
        )


def get_test_status(test_case_id: str) -> str:
    """
    Retrieve test status from the simulated backend.
    """

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