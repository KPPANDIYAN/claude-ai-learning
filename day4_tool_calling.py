from anthropic import Anthropic

client = Anthropic()


# --------------------------------------------------
# Actual Python tools
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


# --------------------------------------------------
# Tool definitions shown to Claude
# --------------------------------------------------

tools = [
    {
        "name": "get_test_status",
        "description": (
            "Get the current execution status of one or more test cases. "
            "Use this when the user wants to know whether test cases "
            "passed, failed, or are still in progress."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "test_case_ids": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": (
                        "One or more test case IDs, "
                        "for example TC-101, TC-102."
                    )
                }
            },
            "required": ["test_case_ids"]
        }
    },

    {
        "name": "get_failure_log",
        "description": (
            "Get the failure or exception log for one or more failed "
            "test cases. Use this when the user wants to understand "
            "why test cases failed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "test_case_ids": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": (
                        "One or more test case IDs, "
                        "for example TC-102."
                    )
                }
            },
            "required": ["test_case_ids"]
        }
    }
]


# --------------------------------------------------
# Helper function that executes whichever tool
# Claude requested
# --------------------------------------------------

def execute_tool(tool_name, tool_input):

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

        else:

            results[test_case_id] = (
                "Unknown tool requested"
            )

    return results


# --------------------------------------------------
# Conversation
# --------------------------------------------------

messages = [
    {
        "role": "user",
        "content": (
            "Tell me the status of TC-101 and TC-102, "
            "and explain why any failed test failed."
        )
    }
]


# --------------------------------------------------
# Reusable Claude tool loop
# --------------------------------------------------

while True:

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        tools=tools,
        messages=messages
    )

    print("\n----------------------------------")
    print("Claude stop reason:")
    print(response.stop_reason)

    print("\nClaude response content:")
    print(response.content)

    # --------------------------------------------------
    # Store Claude's complete response in history
    # --------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": response.content
        }
    )

    # --------------------------------------------------
    # If Claude is finished, print final text and stop
    # --------------------------------------------------

    if response.stop_reason == "end_turn":

        print("\nClaude final answer:")

        for content_block in response.content:

            if content_block.type == "text":
                print(content_block.text)

        break

    # --------------------------------------------------
    # Claude wants one or more tools
    # --------------------------------------------------

    if response.stop_reason == "tool_use":

        tool_results = []

        for content_block in response.content:

            if content_block.type == "tool_use":

                print("\nSelected tool:")
                print(content_block.name)

                print("\nGenerated input:")
                print(content_block.input)

                # --------------------------------------
                # Execute selected tool dynamically
                # --------------------------------------

                tool_result = execute_tool(
                    content_block.name,
                    content_block.input
                )

                print("\nTool result:")
                print(tool_result)

                # --------------------------------------
                # Prepare result for this specific
                # tool request
                # --------------------------------------

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": str(tool_result)
                    }
                )

        # --------------------------------------------------
        # Send ALL tool results back to Claude
        # --------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )

        # Go back to top of while loop.
        # Claude receives the results and decides
        # whether it needs another tool or can finish.

        continue

    # --------------------------------------------------
    # Unexpected stop reason
    # --------------------------------------------------

    print(
        "\nClaude stopped for an unexpected reason:",
        response.stop_reason
    )

    break