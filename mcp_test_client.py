import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    # --------------------------------------------------
    # HOW TO START THE MCP SERVER
    # --------------------------------------------------

    server_params = StdioServerParameters(
        command="mcp",
        args=["run", "mcp_test_server.py"]
    )


    # --------------------------------------------------
    # CREATE STDIO TRANSPORT
    # --------------------------------------------------

    async with stdio_client(
        server_params
    ) as (read, write):


        # --------------------------------------------------
        # CREATE MCP CLIENT SESSION
        # --------------------------------------------------

        async with ClientSession(
            read,
            write
        ) as session:


            # --------------------------------------------------
            # INITIALIZE MCP CONNECTION
            # --------------------------------------------------

            await session.initialize()


            # --------------------------------------------------
            # DISCOVER TOOLS FROM SERVER
            # --------------------------------------------------

            tools_result = await session.list_tools()


            print("Available tools:")

            for tool in tools_result.tools:
                print(tool.name)


if __name__ == "__main__":
    asyncio.run(main())