import asyncio

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


claude = Anthropic()

MODEL_NAME = "claude-haiku-4-5-20251001"
MAX_TOKENS = 700
MAX_ITERATIONS = 5


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are an AI Test Failure Investigator.

Your job is to investigate automated test failures
using only the available tools.

Rules:
- Use tool results as factual evidence.
- Clearly separate observed facts from possible causes.
- Do not present assumptions as confirmed facts.
- Only request tools when they are useful.
- Avoid repeating the same tool call with the same
  arguments unless there is a valid reason.
- When enough evidence is available, stop using tools
  and provide the final report.

Final report must contain:
1. Test case
2. Status
3. Owner
4. Observed failure evidence
5. Likely root cause
6. Confidence
7. Recommended next action
"""


async def main():

    # --------------------------------------------------
    # MCP SERVER CONFIGURATION
    # --------------------------------------------------

    server_params = StdioServerParameters(
        command="mcp",
        args=["run", "mcp_test_server.py"]
    )


    # --------------------------------------------------
    # STDIO TRANSPORT
    # --------------------------------------------------

    async with stdio_client(
        server_params
    ) as (read, write):


        # --------------------------------------------------
        # MCP CLIENT SESSION
        # --------------------------------------------------

        async with ClientSession(
            read,
            write
        ) as session:


            # --------------------------------------------------
            # INITIALIZE MCP
            # --------------------------------------------------

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
            # AGENT GOAL / INITIAL STATE
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
            # AGENT CONTROL STATE
            # --------------------------------------------------

            iteration = 0
            executed_calls = set()


            # --------------------------------------------------
            # GUARDED MCP-POWERED AGENT LOOP
            # --------------------------------------------------

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
                    system=SYSTEM_PROMPT,
                    tools=claude_tools,
                    messages=messages
                )


                # ----------------------------------------------
                # PRESERVE CLAUDE DECISION IN STATE
                # ----------------------------------------------

                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content
                    }
                )


                print("Stop reason:")
                print(response.stop_reason)


                # ----------------------------------------------
                # CLAUDE FINISHED
                # ----------------------------------------------

                if response.stop_reason == "end_turn":

                    print("\nFinal investigation:")

                    for block in response.content:

                        if block.type == "text":
                            print(block.text)

                    break


                # ----------------------------------------------
                # CLAUDE REQUESTED TOOLS
                # ----------------------------------------------

                if response.stop_reason == "tool_use":

                    tool_results = []


                    for block in response.content:


                        # --------------------------------------
                        # IGNORE NON-TOOL BLOCKS
                        # --------------------------------------

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
                        # CREATE DUPLICATE-CALL KEY
                        # --------------------------------------

                        call_key = (
                            block.name,
                            str(block.input)
                        )


                        # --------------------------------------
                        # DUPLICATE-CALL GUARD
                        # --------------------------------------

                        if call_key in executed_calls:

                            result_value = (
                                f"Repeated tool call blocked: "
                                f"{block.name} "
                                f"with {block.input}"
                            )


                        else:

                            executed_calls.add(
                                call_key
                            )


                            # ----------------------------------
                            # MCP EXECUTION SAFETY BOUNDARY
                            # ----------------------------------

                            try:

                                mcp_result = (
                                    await session.call_tool(
                                        block.name,
                                        block.input
                                    )
                                )


                                # ------------------------------
                                # MCP RETURNED AN ERROR
                                # ------------------------------

                                if mcp_result.is_error:

                                    result_value = (
                                        "MCP tool returned "
                                        "an error"
                                    )


                                # ------------------------------
                                # PREFERRED STRUCTURED RESULT
                                # ------------------------------

                                elif (
                                    mcp_result.structured_content
                                    and "result"
                                    in mcp_result.structured_content
                                ):

                                    result_value = (
                                        mcp_result
                                        .structured_content[
                                            "result"
                                        ]
                                    )


                                # ------------------------------
                                # FALLBACK TEXT CONTENT
                                # ------------------------------

                                elif mcp_result.content:

                                    result_value = (
                                        mcp_result
                                        .content[0]
                                        .text
                                    )


                                # ------------------------------
                                # EMPTY RESULT
                                # ------------------------------

                                else:

                                    result_value = (
                                        "No result returned"
                                    )


                            # ----------------------------------
                            # PYTHON / RUNTIME FAILURE
                            # ----------------------------------

                            except Exception as e:

                                result_value = (
                                    "Tool execution failed: "
                                    f"{str(e)}"
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
                                "content": str(
                                    result_value
                                )
                            }
                        )


                    # ------------------------------------------
                    # UPDATE AGENT STATE
                    # ------------------------------------------

                    messages.append(
                        {
                            "role": "user",
                            "content": tool_results
                        }
                    )


                    # ------------------------------------------
                    # NEXT CLAUDE DECISION
                    # ------------------------------------------

                    continue


                # ----------------------------------------------
                # UNEXPECTED STOP REASON
                # ----------------------------------------------

                print(
                    "\nAgent stopped because an "
                    "unexpected stop reason "
                    "was returned:"
                )

                print(
                    response.stop_reason
                )

                break


            # --------------------------------------------------
            # MAX ITERATIONS EXHAUSTED
            # --------------------------------------------------

            else:

                print(
                    "\nAgent stopped because the "
                    "maximum iteration limit "
                    "was reached."
                )


if __name__ == "__main__":
    asyncio.run(main())