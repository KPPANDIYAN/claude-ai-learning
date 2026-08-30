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
# Ask Claude a question that requires the tool
# --------------------------------------------------

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": (
                "What is the current status of test case TC-102?"
            )
        }
    ]
)


# --------------------------------------------------
# Inspect Claude's decision
# --------------------------------------------------

print("Claude stop reason:")
print(response.stop_reason)

print("\nClaude response content:")
print(response.content)