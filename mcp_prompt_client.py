import asyncio

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


claude = Anthropic()

MODEL_NAME = "claude-haiku-4-5-20251001"


async def main():

    server_params = StdioServerParameters(
        command="mcp",
        args=["run", "mcp_test_server.py"]
    )

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            await session.initialize()

            # ----------------------------------------------
            # DISCOVER MCP PROMPTS
            # ----------------------------------------------

            prompts_result = (
                await session.list_prompts()
            )

            print("Available MCP prompts:")

            for prompt in prompts_result.prompts:

                print("\nName:")
                print(prompt.name)

                print("Description:")
                print(prompt.description)

                print("Arguments:")
                print(prompt.arguments)

            # ----------------------------------------------
            # GET / RENDER MCP PROMPT
            # ----------------------------------------------

            prompt_result = await session.get_prompt(
                "investigate_test_failure",
                arguments={
                    "test_case_id": "TC-102"
                }
            )

            print("\nRendered MCP prompt:")
            print(prompt_result)

            # ----------------------------------------------
            # CONVERT MCP PROMPT MESSAGE
            # TO CLAUDE MESSAGE FORMAT
            # ----------------------------------------------

            claude_messages = []

            for prompt_message in prompt_result.messages:

                if prompt_message.content.type != "text":
                    continue

                claude_messages.append(
                    {
                        "role": prompt_message.role,
                        "content": prompt_message.content.text
                    }
                )

            print("\nMessages prepared for Claude:")
            print(claude_messages)

            # ----------------------------------------------
            # SEND MCP PROMPT TO CLAUDE
            # ----------------------------------------------

            claude_response = claude.messages.create(
                model=MODEL_NAME,
                max_tokens=600,
                messages=claude_messages
            )

            print("\nClaude stop reason:")
            print(claude_response.stop_reason)

            print("\nClaude response:")

            for block in claude_response.content:

                if block.type == "text":
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(main())