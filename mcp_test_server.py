from mcp.server import MCPServer
mcp = MCPServer("Testing MCP Server")

@mcp.tool()
def get_test_status(test_case_id: str) -> str:
    """
    Get the current execution status of a test case.
    """

    test_data={
        "TC-101": "Passed",
        "TC-102": "Failed",
        "TC-103": "In Progress"
    }

    return test_data.get(test_case_id, "Test case not found")

@mcp.tool()
def get_failure_log(test_case_id: str) -> str:
    """
    Get the latest failure log for a test case.
    """

    failure_logs = {
        "TC-101": "No failure. Test passed.",
        "TC-102": (
            "NoSuchElementException: "
            "Unable to locate element with id 'login-button'"
        ),
        "TC-103": "Test is still in progress."
    }

    return failure_logs.get(
        test_case_id,
        "Failure log not found"
    )


@mcp.tool()
def get_test_owner(test_case_id: str) -> str:
    """
    Get the owner of a test case.
    """

    owner_data = {
        "TC-101": "Anita",
        "TC-102": "Ravi",
        "TC-103": "Kumar"
    }

    return owner_data.get(
        test_case_id,
        "Owner not found"
    )

# --------------------------------------------------
# MCP RESOURCE 1
# --------------------------------------------------

@mcp.resource(
    "test-environment://qa",
    name="qa_test_environment",
    description="Read the QA automation test environment configuration.",
    mime_type="text/plain"
)
def get_qa_test_environment() -> str:

    return """
    Application: SauceDemo
    Environment: QA
    Browser: Chrome
    Automation Framework: Selenium
    Execution Type: Automated UI Testing
    """
# --------------------------------------------------
# MCP RESOURCE TEMPLATE
# --------------------------------------------------

@mcp.resource(
    "test-report://{test_case_id}",
    name="test_report",
    description="Read the execution report for a test case.",
    mime_type="text/plain"
)
def get_test_report(test_case_id: str) -> str:

    report_data = {
                "TC-101": """
        Test Case: TC-101
        Status: Passed
        Owner: Anitha
        Failure Evidence: None
        """,
                "TC-102": """
        Test Case: TC-102
        Status: Failed
        Owner: Ravi
        Failure Evidence:
        NoSuchElementException:
        Unable to locate element with id 'login-button'
        """,
                "TC-103": """
        Test Case: TC-103
        Status: In Progress
        Owner: Kumar
        Failure Evidence: Not available yet
        """
            }

    return report_data.get(
        test_case_id,
        f"No report found for {test_case_id}"
    )