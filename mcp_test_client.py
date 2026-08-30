import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command="mcp",
        args=["run", "mcp_test_server.py"]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            tools_result = await session.list_tools()

            print("Available tools:")

            for tool in tools_result.tools:
                print(tool.name)


            # --------------------------------------------------
            # COLLECT MULTIPLE MCP OBSERVATIONS
            # --------------------------------------------------

            observations = {}


            status_result = await session.call_tool(
                "get_test_status",
                {
                    "test_case_id": "TC-102"
                }
            )

            observations["status"] = (
                status_result
                .structured_content["result"]
            )


            failure_result = await session.call_tool(
                "get_failure_log",
                {
                    "test_case_id": "TC-102"
                }
            )

            observations["failure_log"] = (
                failure_result
                .structured_content["result"]
            )


            owner_result = await session.call_tool(
                "get_test_owner",
                {
                    "test_case_id": "TC-102"
                }
            )

            observations["owner"] = (
                owner_result
                .structured_content["result"]
            )


            print("\nCollected observations:")
            print(observations)


if __name__ == "__main__":
    asyncio.run(main())