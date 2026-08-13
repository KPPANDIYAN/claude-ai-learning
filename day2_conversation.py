import time
import anthropic
from anthropic import Anthropic

client = Anthropic()

messages = []

MODEL_NAME = "claude-haiku-4-5-20251001"
MAX_TOKENS = 500
SYSTEM_PROMPT = "You are an experienced automation testing engineer."

CONTINUE_PROMPT = (
    "Continue exactly from where your previous response ended. "
    "Do not repeat any heading, explanation, code, or content that "
    "you already provided. Start immediately with the missing continuation."
)


def get_claude_response(messages):
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages
    )

    return response


def add_message(messages, role, content):
    messages.append({
        "role": role,
        "content": content
    })


def call_claude_safely(messages):

    try:
        return get_claude_response(messages)

    except anthropic.NotFoundError as e:
        print("\nModel or resource not found:")
        print(e)

    except anthropic.AuthenticationError:
        print("\nAuthentication failed.")
        print("Please check whether ANTHROPIC_API_KEY is set correctly.")

    except anthropic.RateLimitError:
        print("\nRate limit reached.")
        print("Waiting 5 seconds before retrying...")

        time.sleep(5)

        try:
            return get_claude_response(messages)

        except Exception as retry_error:
            print("\nRetry also failed:")
            print(retry_error)

    except anthropic.APIConnectionError as e:
        print("\nUnable to connect to Anthropic API:")
        print(e)

    except anthropic.APIStatusError as e:
        print("\nAnthropic API returned an error:")
        print(e)

    return None


def handle_continuation(response, claude_answer, messages):

    while response.stop_reason == "max_tokens":

        print("\nClaude reached the maximum output token limit.")

        continue_choice = input(
            "Type 'continue' if you want Claude to continue, "
            "press Enter to stop continuing, or type 'exit' to quit: "
        )

        if continue_choice.lower() == "exit":
            print("Exiting chat...")
            exit()

        if continue_choice.lower() != "continue":
            break

        add_message(messages, "assistant", claude_answer)
        add_message(messages, "user", CONTINUE_PROMPT)

        response = call_claude_safely(messages)

        if response is None:
            return None, claude_answer

        claude_answer = response.content[0].text

        print("\nClaude continued response:")
        print(claude_answer)

    return response, claude_answer


while True:

    user_question = input("\nYou: ")

    if user_question.lower() == "exit":
        print("Exiting chat...")
        break

    add_message(messages, "user", user_question)

    response = call_claude_safely(messages)

    if response is None:
        break

    print("\nInput tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)

    claude_answer = response.content[0].text

    print("\nClaude:")
    print(claude_answer)

    response, claude_answer = handle_continuation(
        response,
        claude_answer,
        messages
    )

    if response is None:
        break

    add_message(messages, "assistant", claude_answer)