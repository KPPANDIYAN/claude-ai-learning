from mcp.server import MCPServer


# --------------------------------------------------
# CREATE MCP SERVER
# --------------------------------------------------

mcp = MCPServer("Testing MCP Server")


# --------------------------------------------------
# FIRST MCP TOOL
# --------------------------------------------------

@mcp.tool()
def get_test_status(test_case_id: str) -> str:
    """
    Get the current execution status of a test case.
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