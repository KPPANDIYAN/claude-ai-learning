import time
import anthropic
from anthropic import Anthropic

client = Anthropic()

messages = []

CONTINUE_PROMPT = (
    "Continue exactly from where your previous response ended. "
    "Do not repeat any heading, explanation, code, or content that "
    "you already provided. Start immediately with the missing continuation."
)


def get_claude_response(messages):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system="You are an experienced automation testing engineer.",
        messages=messages
    )

    return response


def add_message(messages, role, content):
    messages.append({
        "role": role,
        "content": content
    })


def handle_continuation(response, claude_answer, messages):

    while response.stop_reason == "max_tokens":

        print("\nClaude reached the maximum output token limit.")

        continue_choice = input(
            "Type 'continue' if you want Claude to continue, "
            "otherwise press Enter: "
        )

        if continue_choice.lower() == "exit":
            print("Exiting chat...")
            exit()

        if continue_choice.lower() != "continue":
            break

        add_message(messages, "assistant", claude_answer)
        add_message(messages, "user", CONTINUE_PROMPT)

        response = get_claude_response(messages)

        claude_answer = response.content[0].text

        print("\nClaude continued response:")
        print(claude_answer)

    return response, claude_answer


while True:

    user_question = input("\nYou: ")

    if user_question.lower() == "exit":
        break

    add_message(messages, "user", user_question)

    try:
        response = get_claude_response(messages)

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
            response = get_claude_response(messages)

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

    response, claude_answer = handle_continuation(
        response,
        claude_answer,
        messages
    )

    add_message(messages, "assistant", claude_answer)