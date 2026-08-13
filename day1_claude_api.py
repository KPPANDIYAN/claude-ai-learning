from anthropic import Anthropic

client = Anthropic()

messages = []

# First user question
user_question = input("You: ")

messages.append({
    "role": "user",
    "content": user_question
})

# First Claude call
response1 = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    system="You are an experienced automation testing engineer.",
    messages=messages
)

first_answer = response1.content[0].text

print("Claude first response:")
print(first_answer)

# Store Claude's actual response
messages.append({
    "role": "assistant",
    "content": first_answer
})

# Second user question
second_question = input("\nYou: ")

messages.append({
    "role": "user",
    "content": second_question
})

# Second Claude call
response2 = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=400,
    system="You are an experienced automation testing engineer.",
    messages=messages
)

print("\nClaude second response:")
print(response2.content[0].text)
print("\nStop reason:", response2.stop_reason)