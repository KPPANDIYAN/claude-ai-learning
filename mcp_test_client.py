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

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()


            # --------------------------------------------------
            # DISCOVER MCP TOOLS
            # --------------------------------------------------

            tools_result = await session.list_tools()


            # --------------------------------------------------
            # CONVERT MCP TOOL DEFINITIONS
            # INTO ANTHROPIC TOOL FORMAT
            # --------------------------------------------------

            claude_tools = []

            for tool in tools_result.tools:

                claude_tools.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema
                    }
                )


            print("Tools provided to Claude:")

            for tool in claude_tools:
                print(tool["name"])


            # --------------------------------------------------
            # USER GOAL
            # --------------------------------------------------

            messages = [
                {
                    "role": "user",
                    "content": (
                        "Investigate test case TC-102. "
                        "Determine its current status and owner. "
                        "If it failed, find the failure reason. "
                        "Then provide a concise investigation summary."
                    )
                }
            ]


            # --------------------------------------------------
            # ASK CLAUDE TO DECIDE WHICH TOOLS ARE NEEDED
            # --------------------------------------------------

            response = claude.messages.create(
                model=MODEL_NAME,
                max_tokens=500,
                tools=claude_tools,
                messages=messages
            )


            print("\nClaude stop reason:")
            print(response.stop_reason)

            print("\nClaude response:")
            print(response.content)


if __name__ == "__main__":
    asyncio.run(main())