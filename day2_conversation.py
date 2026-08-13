from anthropic import Anthropic

client = Anthropic()

messages = []

while True:

    user_question = input("\nYou: ")

    if user_question.lower() == "exit":
        break

    messages.append({
        "role": "user",
        "content": user_question
    })

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system="You are an experienced automation testing engineer.",
        messages=messages
    )

    print("\nInput tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)
    print("Stop reason:", response.stop_reason)

    claude_answer = response.content[0].text

    print("\nClaude:")
    print(claude_answer)

    messages.append({
        "role": "assistant",
        "content": claude_answer
    })