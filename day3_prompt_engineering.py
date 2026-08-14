import json
from anthropic import Anthropic

client = Anthropic()

SYSTEM_PROMPT = (
    "You are an experienced automation testing engineer "
    "who explains technical concepts clearly to beginners."
)

USER_PROMPT = """
Task:
Explain Selenium.

Context:
The reader knows Java but is new to automation testing.

Constraints:
- Use simple beginner-friendly language.
- Keep each explanation short.
- Return only valid JSON.
- Do not add Markdown.
- Do not add any text before or after the JSON.

Output Format:
{
  "what_is_selenium": "<answer>",
  "why_it_is_used": "<answer>",
  "main_components": "<answer>",
  "simple_java_example": "<answer>"     
}
"""

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=600,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": USER_PROMPT
        }
    ]
)

# ----------------------------------
# Check how Claude stopped
# ----------------------------------

print("\nStop reason:", response.stop_reason)
print("Output tokens:", response.usage.output_tokens)

# ----------------------------------
# Extract Claude response
# ----------------------------------

claude_text = response.content[0].text

print("\nRaw Claude response:")
print(claude_text)

# ----------------------------------
# Clean Markdown code fences
# ----------------------------------

claude_text = claude_text.strip()

if claude_text.startswith("```json"):
    claude_text = claude_text.removeprefix("```json")

if claude_text.endswith("```"):
    claude_text = claude_text.removesuffix("```")

claude_text = claude_text.strip()

# ----------------------------------
# Parse JSON
# ----------------------------------

try:

    data = json.loads(claude_text)

    print("\nParsed Python object:")
    print(data)

    # ----------------------------------
    # Validate required fields
    # ----------------------------------

    required_fields = [
        "what_is_selenium",
        "why_it_is_used",
        "main_components",
        "simple_java_example"
    ]

    missing_fields = []

    for field in required_fields:

        if field not in data:
            missing_fields.append(field)

    # ----------------------------------
    # Validation result
    # ----------------------------------

    if missing_fields:

        print("\nValidation failed.")
        print("Missing fields:", missing_fields)

    else:

        print("\nValidation successful.")
        print("All required fields are available.")

        # ----------------------------------
        # Access individual values safely
        # ----------------------------------

        print("\nWhat is Selenium:")
        print(data.get("what_is_selenium"))

        print("\nWhy it is used:")
        print(data.get("why_it_is_used"))

        print("\nMain components:")
        print(data.get("main_components"))

        print("\nSimple Java example:")
        print(data.get("simple_java_example"))

    # ----------------------------------
    # Deliberately test a missing key
    # ----------------------------------

    print("\nTesting missing key:")
    print(
        data.get(
            "browser_support",
            "Field not available"
        )
    )

# ----------------------------------
# Handle invalid JSON
# ----------------------------------

except json.JSONDecodeError as e:

    print("\nInvalid JSON received from Claude.")
    print("JSON parsing error:", e)

    if response.stop_reason == "max_tokens":

        print(
            "The response was probably truncated because Claude "
            "reached the maximum output token limit."
        )