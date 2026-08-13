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
    - Keep the answer under 300 words.
    - Use simple beginner-friendly language.
    - Avoid unnecessary advanced details.

    Output Format:
    Use these sections:
    1. What Selenium is
    2. Why Selenium is used
    3. Main Selenium components
    4. One simple Java example
"""

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": USER_PROMPT
        }
    ]
)

print("Claude response:")
print(response.content[0].text)