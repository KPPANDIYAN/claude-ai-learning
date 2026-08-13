from anthropic import Anthropic

client = Anthropic()

SYSTEM_PROMPT = (
    "You are an experienced automation testing engineer "
    "who explains technical concepts clearly to beginners."
)

USER_PROMPT = """
Explain Selenium to someone who knows Java but is new to automation.

Cover:
1. What Selenium is
2. Why it is used
3. Main components
4. One simple example

Constraints:
- Keep the answer under 300 words.
- Use simple language.
- Use clear headings.
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