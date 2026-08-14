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