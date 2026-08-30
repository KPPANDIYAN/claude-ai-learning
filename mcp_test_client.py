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
            # CONVERT MCP TOOLS FOR CLAUDE
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
            # CONVERSATION STATE
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
            # FIRST CLAUDE DECISION
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


            # --------------------------------------------------
            # STORE CLAUDE'S TOOL REQUEST
            # --------------------------------------------------

            messages.append(
                {
                    "role": "assistant",
                    "content": response.content
                }
            )


            # --------------------------------------------------
            # EXECUTE CLAUDE-REQUESTED MCP TOOLS
            # --------------------------------------------------

            if response.stop_reason == "tool_use":

                tool_results = []

                for block in response.content:

                    if block.type != "tool_use":
                        continue


                    print("\nClaude requested tool:")
                    print(block.name)

                    print("\nInput:")
                    print(block.input)


                    # ------------------------------------------
                    # DYNAMIC MCP TOOL INVOCATION
                    # ------------------------------------------

                    mcp_result = await session.call_tool(
                        block.name,
                        block.input
                    )


                    # ------------------------------------------
                    # EXTRACT RESULT
                    # ------------------------------------------

                    if (
                        mcp_result.structured_content
                        and "result"
                        in mcp_result.structured_content
                    ):

                        result_value = (
                            mcp_result
                            .structured_content["result"]
                        )

                    elif mcp_result.content:

                        result_value = (
                            mcp_result.content[0].text
                        )

                    else:

                        result_value = "No result returned"


                    print("\nMCP result:")
                    print(result_value)


                    # ------------------------------------------
                    # PREPARE RESULT FOR CLAUDE
                    # ------------------------------------------

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result_value)
                        }
                    )


                # ----------------------------------------------
                # STORE TOOL OBSERVATIONS
                # ----------------------------------------------

                messages.append(
                    {
                        "role": "user",
                        "content": tool_results
                    }
                )


            # --------------------------------------------------
            # SECOND CLAUDE DECISION
            # --------------------------------------------------

            second_response = claude.messages.create(
                model=MODEL_NAME,
                max_tokens=500,
                tools=claude_tools,
                messages=messages
            )


            print("\nClaude second stop reason:")
            print(second_response.stop_reason)

            print("\nClaude second response:")
            print(second_response.content)


if __name__ == "__main__":
    asyncio.run(main())