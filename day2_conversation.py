import time
import anthropic
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

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system="You are an experienced automation testing engineer.",
            messages=messages
        )

    except anthropic.NotFoundError as e:
        print("\nModel or resource not found:")
        print(e)
        break

    except anthropic.AuthenticationError:
        print("\nAuthentication failed.")
        print("Please check whether ANTHROPIC_API_KEY is set correctly.")
        break

    except anthropic.RateLimitError:
        print("\nRate limit reached.")
        print("Waiting 5 seconds before retrying...")

        time.sleep(5)

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system="You are an experienced automation testing engineer.",
                messages=messages
            )

        except Exception as retry_error:
            print("\nRetry also failed:")
            print(retry_error)
            break

    except anthropic.APIConnectionError as e:
        print("\nUnable to connect to Anthropic API:")
        print(e)
        break

    except anthropic.APIStatusError as e:
        print("\nAnthropic API returned an error:")
        print(e)
        break

    print("\nInput tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)
    print("Stop reason:", response.stop_reason)

    claude_answer = response.content[0].text

    print("\nClaude:")
    print(claude_answer)

    if response.stop_reason == "max_tokens":
        print("\nClaude reached the maximum output token limit.")

    messages.append({
        "role": "assistant",
        "content": claude_answer
    })