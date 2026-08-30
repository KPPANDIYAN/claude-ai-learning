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
            "Get the current execution status of a test case. "
            "Use this when the user wants to know whether "
            "a test case passed, failed, or is still in progress."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "test_case_id": {
                    "type": "string",
                    "description": (
                        "The test case ID, for example TC-102."
                    )
                }
            },
            "required": ["test_case_id"]
        }
    },

    {
        "name": "get_failure_log",
        "description": (
            "Get the failure or exception log for a failed test case. "
            "Use this when the user wants to understand why "
            "a test case failed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "test_case_id": {
                    "type": "string",
                    "description": (
                        "The failed test case ID, for example TC-102."
                    )
                }
            },
            "required": ["test_case_id"]
        }
    }
]


# --------------------------------------------------
# Conversation history
# --------------------------------------------------

messages = [
    {
        "role": "user",
        "content": (
            "Tell me the current status of TC-102. "
            "If it failed, explain why it failed."
        )
    }
]


# --------------------------------------------------
# Reusable Claude tool loop
# --------------------------------------------------

while True:

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        tools=tools,
        messages=messages
    )

    print("\n----------------------------------")
    print("Claude stop reason:")
    print(response.stop_reason)

    print("\nClaude response content:")
    print(response.content)


    # --------------------------------------------------
    # Preserve Claude's response in conversation history
    # --------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": response.content
        }
    )


    # --------------------------------------------------
    # Claude has finished
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

            if content_block.type != "tool_use":
                continue

            print("\nSelected tool:")
            print(content_block.name)

            print("\nGenerated input:")
            print(content_block.input)

            test_case_id = (
                content_block.input["test_case_id"]
            )


            if content_block.name == "get_test_status":

                tool_result = get_test_status(
                    test_case_id
                )


            elif content_block.name == "get_failure_log":

                tool_result = get_failure_log(
                    test_case_id
                )


            else:

                tool_result = "Unknown tool requested"


            print("\nTool result:")
            print(tool_result)


            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": str(tool_result)
                }
            )


        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )


        # Start the next Claude decision cycle
        continue


    # --------------------------------------------------
    # Unexpected stop reason
    # --------------------------------------------------

    print(
        "\nClaude stopped for an unexpected reason:",
        response.stop_reason
    )

    break