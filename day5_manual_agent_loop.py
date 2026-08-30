from anthropic import Anthropic

client = Anthropic()

SYSTEM_PROMPT = """
You are an AI Test Failure Investigator.

Your job is to investigate automated test failures using the available tools.

Rules:
- Use tool results as factual evidence.
- Clearly distinguish observed facts from possible causes.
- Do not present assumptions as confirmed facts.
- Only request tools when they are useful for completing the investigation.
- Once enough information is available, provide the final investigation report.

Final report must contain:
1. Test case
2. Status
3. Owner
4. Observed failure evidence
5. Likely root cause
6. Confidence
7. Recommended next action
"""


# --------------------------------------------------
# TOOL IMPLEMENTATIONS
# --------------------------------------------------

def get_test_status(test_case_id):

    test_data = {
        "TC-101": "Passed",
        "TC-102": "Failed",
        "TC-103": "In Progress"
    }

    return test_data.get(
        test_case_id,
        "Test case not found"
    )


def get_failure_log(test_case_id):

    failure_logs = {
        "TC-102": (
            "NoSuchElementException: "
            "Unable to locate element with id 'login-button'"
        )
    }

    return failure_logs.get(
        test_case_id,
        "No failure log found"
    )

def get_test_owner(test_case_id):

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
# TOOL DEFINITIONS FOR CLAUDE
# --------------------------------------------------

tools = [
    {
        "name": "get_test_status",
        "description": (
            "Get the execution status of one or more test cases. "
            "Use this when you need to know whether a test passed, "
            "failed, or is still in progress."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "test_case_ids": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["test_case_ids"]
        }
    },

    {
        "name": "get_failure_log",
        "description": (
            "Get the failure log for one or more failed test cases. "
            "Use this when you need to understand why a test failed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "test_case_ids": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["test_case_ids"]
        }
    },

    {
    "name": "get_test_owner",
    "description": (
        "Get the owner responsible for one or more test cases. "
        "Use this when the user wants to know who owns or maintains "
        "a test case."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "test_case_ids": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["test_case_ids"]
    }
}

]


# --------------------------------------------------
# EXECUTE TOOL
# --------------------------------------------------

def execute_tool(tool_name, tool_input):

    try:

        test_case_ids = tool_input["test_case_ids"]

        results = {}

        for test_case_id in test_case_ids:

            if tool_name == "get_test_status":

                results[test_case_id] = get_test_status(
                    test_case_id
                )

            elif tool_name == "get_failure_log":

                results[test_case_id] = get_failure_log(
                    test_case_id
                )

            elif tool_name == "get_test_owner":

                results[test_case_id] = get_test_owner(
                    test_case_id
                )

            else:

                return {
                    "error": f"Unknown tool: {tool_name}"
                }

        return results

    except KeyError as e:

        return {
            "error": f"Missing required input: {e}"
        }

    except Exception as e:

        return {
            "error": f"Tool execution failed: {str(e)}"
        }


# --------------------------------------------------
# AGENT GOAL
# --------------------------------------------------

goal = (
    "Investigate test case TC-102. "
    "Determine its current status and owner. "
    "If it failed, retrieve the failure evidence. "
    "Analyze the likely root cause based only on the available evidence. "
    "Provide a confidence level and recommend the next action."
)


# --------------------------------------------------
# AGENT STATE
# --------------------------------------------------

messages = [
    {
        "role": "user",
        "content": goal
    }
]


# --------------------------------------------------
# MANUAL AGENT LOOP
# --------------------------------------------------

MAX_ITERATIONS = 5
iteration = 0

while iteration < MAX_ITERATIONS:

    iteration += 1

    print(
        f"\nAgent iteration: "
        f"{iteration}/{MAX_ITERATIONS}"
    )

    # ----------------------------------------------
    # DECIDE
    # ----------------------------------------------

    response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=700,
    system=SYSTEM_PROMPT,
    tools=tools,
    messages=messages
    )

    print("\n==================================")
    print("Agent stop reason:")
    print(response.stop_reason)

    print("\nAgent response:")
    print(response.content)

    # Store Claude's decision in state
    messages.append(
        {
            "role": "assistant",
            "content": response.content
        }
    )

    # ----------------------------------------------
    # STOP
    # ----------------------------------------------

    if response.stop_reason == "end_turn":

        print("\nAgent final answer:")

        for content_block in response.content:

            if content_block.type == "text":
                print(content_block.text)

        break

    # ----------------------------------------------
    # ACT
    # ----------------------------------------------

    if response.stop_reason == "tool_use":

        tool_results = []

        for content_block in response.content:

            if content_block.type == "tool_use":

                print("\nAgent decided to use tool:")
                print(content_block.name)

                print("\nTool input:")
                print(content_block.input)

                tool_result = execute_tool(
                    content_block.name,
                    content_block.input
                )

                print("\nObservation from tool:")
                print(tool_result)

                # ----------------------------------
                # OBSERVE
                # ----------------------------------

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": str(tool_result)
                    }
                )

        # Store observations in state
        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )

        # Agent will decide again
        continue

    print(
        "\nAgent stopped unexpectedly:",
        response.stop_reason
    )

    break
else:

    print(
        "\nAgent stopped because the maximum "
        "iteration limit was reached."
    )