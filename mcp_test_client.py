import asyncio

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


claude = Anthropic()

MODEL_NAME = "claude-haiku-4-5-20251001"
MAX_TOKENS = 700
MAX_ITERATIONS = 5


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
            # AGENT GOAL / STATE
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
            # GUARDED AGENT LOOP
            # --------------------------------------------------

            iteration = 0

            while iteration < MAX_ITERATIONS:

                iteration += 1

                print(
                    f"\n--- Agent iteration "
                    f"{iteration} ---"
                )


                # ----------------------------------------------
                # CLAUDE DECIDES
                # ----------------------------------------------

                response = claude.messages.create(
                    model=MODEL_NAME,
                    max_tokens=MAX_TOKENS,
                    tools=claude_tools,
                    messages=messages
                )


                print("Stop reason:")
                print(response.stop_reason)


                # ----------------------------------------------
                # PRESERVE CLAUDE DECISION IN STATE
                # ----------------------------------------------

                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content
                    }
                )


                # ----------------------------------------------
                # FINAL ANSWER
                # ----------------------------------------------

                if response.stop_reason == "end_turn":

                    print("\nFinal investigation:")

                    for block in response.content:

                        if block.type == "text":
                            print(block.text)

                    break


                # ----------------------------------------------
                # CLAUDE REQUESTED MCP TOOLS
                # ----------------------------------------------

                if response.stop_reason == "tool_use":

                    tool_results = []


                    for block in response.content:

                        if block.type != "tool_use":
                            continue


                        print(
                            f"\nClaude requested tool: "
                            f"{block.name}"
                        )

                        print(
                            f"Input: {block.input}"
                        )


                        # --------------------------------------
                        # INVOKE MCP TOOL DYNAMICALLY
                        # --------------------------------------

                        mcp_result = await session.call_tool(
                            block.name,
                            block.input
                        )


                        # --------------------------------------
                        # EXTRACT TOOL RESULT
                        # --------------------------------------

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

                            result_value = (
                                "No result returned"
                            )


                        print(
                            f"MCP result: "
                            f"{result_value}"
                        )


                        # --------------------------------------
                        # PREPARE OBSERVATION FOR CLAUDE
                        # --------------------------------------

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result_value)
                            }
                        )


                    # ------------------------------------------
                    # UPDATE AGENT STATE WITH OBSERVATIONS
                    # ------------------------------------------

                    messages.append(
                        {
                            "role": "user",
                            "content": tool_results
                        }
                    )


                    # ------------------------------------------
                    # GO TO NEXT AGENT DECISION
                    # ------------------------------------------

                    continue


                # ----------------------------------------------
                # UNEXPECTED STOP REASON
                # ----------------------------------------------

                print(
                    "\nAgent stopped because an "
                    "unexpected stop reason was returned:"
                )

                print(response.stop_reason)

                break


            # --------------------------------------------------
            # MAX ITERATION LIMIT REACHED
            # --------------------------------------------------

            else:

                print(
                    "\nAgent stopped because the maximum "
                    "iteration limit was reached."
                )


if __name__ == "__main__":
    asyncio.run(main())