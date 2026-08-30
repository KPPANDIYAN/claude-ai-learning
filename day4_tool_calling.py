from anthropic import Anthropic

client = Anthropic()


# --------------------------------------------------
# Actual Python tool
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


# --------------------------------------------------
# Tool definition shown to Claude
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

            "required": [
                "test_case_id"
            ]
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
            "What is the current status of test case TC-102?"
        )
    }
]


# --------------------------------------------------
# First Claude call
# --------------------------------------------------

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    tools=tools,
    messages=messages
)


print("Claude stop reason:")
print(response.stop_reason)

print("\nClaude response content:")
print(response.content)


# --------------------------------------------------
# Store Claude's tool request in conversation history
# --------------------------------------------------

messages.append(
    {
        "role": "assistant",
        "content": response.content
    }
)


# --------------------------------------------------
# Execute requested tool
# --------------------------------------------------

if response.stop_reason == "tool_use":

    for content_block in response.content:

        if content_block.type == "tool_use":

            print("\nSelected tool:")
            print(content_block.name)

            print("\nGenerated input:")
            print(content_block.input)

            if content_block.name == "get_test_status":

                test_case_id = (
                    content_block.input["test_case_id"]
                )

                tool_result = get_test_status(
                    test_case_id
                )

                print("\nTool result:")
                print(tool_result)


                # --------------------------------------
                # Add tool result to conversation
                # --------------------------------------

                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": str(tool_result)
                            }
                        ]
                    }
                )


# --------------------------------------------------
# Second Claude call
# --------------------------------------------------

second_response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    tools=tools,
    messages=messages
)


print("\nClaude second stop reason:")
print(second_response.stop_reason)

print("\nClaude final answer:")

for content_block in second_response.content:

    if content_block.type == "text":
        print(content_block.text)