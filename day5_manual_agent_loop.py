from anthropic import Anthropic

client = Anthropic()


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
            "Get the execution status of a test case. "
            "Use this when you need to know whether "
            "a test passed, failed, or is still in progress."
        ),

        "input_schema": {
            "type": "object",

            "properties": {
                "test_case_id": {
                    "type": "string"
                }
            },

            "required": [
                "test_case_id"
            ]
        }
    },

    {
        "name": "get_failure_log",

        "description": (
            "Get the failure log for a failed test case. "
            "Use this when you need to understand why "
            "a test failed."
        ),

        "input_schema": {
            "type": "object",

            "properties": {
                "test_case_id": {
                    "type": "string"
                }
            },

            "required": [
                "test_case_id"
            ]
        }
    },

    {
        "name": "get_test_owner",

        "description": (
            "Get the owner responsible for a test case. "
            "Use this when you need to know who owns "
            "or maintains a test case."
        ),

        "input_schema": {
            "type": "object",

            "properties": {
                "test_case_id": {
                    "type": "string"
                }
            },

            "required": [
                "test_case_id"
            ]
        }
    }
]


# --------------------------------------------------
# AGENT GOAL
# --------------------------------------------------

goal = (
    "Investigate test case TC-102. "
    "Determine its current status and owner. "
    "If it failed, retrieve the failure evidence "
    "and explain the likely cause."
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

while True:

    print("\n==================================")


    # --------------------------------------------------
    # DECIDE
    # --------------------------------------------------

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        tools=tools,
        messages=messages
    )


    print("Agent stop reason:")
    print(response.stop_reason)

    print("\nAgent response:")
    print(response.content)


    # Store Claude's decision in agent state

    messages.append(
        {
            "role": "assistant",
            "content": response.content
        }
    )


    # --------------------------------------------------
    # STOP
    # --------------------------------------------------

    if response.stop_reason == "end_turn":

        print("\nAgent final answer:")

        for content_block in response.content:

            if content_block.type == "text":
                print(content_block.text)

        break


    # --------------------------------------------------
    # ACT
    # --------------------------------------------------

    if response.stop_reason == "tool_use":

        tool_results = []

        for content_block in response.content:

            if content_block.type != "tool_use":
                continue


            print("\nAgent decided to use tool:")
            print(content_block.name)

            print("\nTool input:")
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


            elif content_block.name == "get_test_owner":

                tool_result = get_test_owner(
                    test_case_id
                )


            else:

                tool_result = "Unknown tool requested"


            # --------------------------------------------------
            # OBSERVATION
            # --------------------------------------------------

            print("\nObservation from tool:")
            print(tool_result)


            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": str(tool_result)
                }
            )


        # --------------------------------------------------
        # UPDATE AGENT STATE
        # --------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )


        # Agent decides again using updated state
        continue


    print(
        "\nAgent stopped unexpectedly:",
        response.stop_reason
    )

    break