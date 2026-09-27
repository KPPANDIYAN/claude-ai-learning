import asyncio

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import MAX_ITERATIONS


claude = Anthropic()

MODEL_NAME = "claude-haiku-4-5-20251001"
MAX_TOKENS = 700

SYSTEM_PROMPT = """
You are an AI Test Failure Investigator.

Your job is to investigate automated test failures using only the available tools.

Rules:
- Use tool results as factual evidence.
- Clearly separate observed facts from possible causes.
- Do not present assumptions as confirmed facts.
- Only request tools when they are useful.
- Avoid repeating the same tool call with the same arguments unless there is a valid reason.
- When enough evidence is available, stop using tools and provide the final report.

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

    server_params = StdioServerParameters(
        command="mcp",
        args=["run", "mcp_test_server.py"]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            tools_result = await session.list_tools()

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

            iteration = 0
            executed_calls = set()

            while iteration < MAX_ITERATIONS:

                iteration += 1

                print(f"\n--- Agent iteration {iteration} ---")

                response = claude.messages.create(
                    model=MODEL_NAME,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM_PROMPT,
                    tools=claude_tools,
                    messages=messages
                )

                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content
                    }
                )

                print("Stop reason:")
                print(response.stop_reason)

                if response.stop_reason == "end_turn":

                    print("\nFinal investigation:")

                    for block in response.content:
                        if block.type == "text":
                            print(block.text)

                    break

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

                        call_key = (
                            block.name,
                            str(block.input)
                        )

                        if call_key in executed_calls:

                            result_value = (
                                f"Repeated tool call blocked: "
                                f"{block.name} with {block.input}"
                            )

                        else:

                            executed_calls.add(call_key)

                            try:

                                mcp_result = (
                                    await session.call_tool(
                                        block.name,
                                        block.input
                                    )
                                )

                                if mcp_result.is_error:

                                    result_value = (
                                        "MCP tool returned an error"
                                    )

                                elif (
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

                            except Exception as e:

                                result_value = (
                                    f"Tool execution failed: "
                                    f"{str(e)}"
                                )

                        print(
                            f"MCP result: {result_value}"
                        )

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result_value)
                            }
                        )

                    messages.append(
                        {
                            "role": "user",
                            "content": tool_results
                        }
                    )

                    continue

                print(
                    "\nAgent stopped because an "
                    "unexpected stop reason was returned:"
                )

                print(response.stop_reason)

                break

            else:

                print(
                    "\nAgent stopped because the maximum "
                    "iteration limit was reached."
                )

if __name__ == "__main__":
    asyncio.run(main())