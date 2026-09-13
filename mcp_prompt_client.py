import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    # --------------------------------------------------
    # MCP SERVER CONFIGURATION
    # --------------------------------------------------

    server_params = StdioServerParameters(
        command="mcp",
        args=["run", "mcp_test_server.py"]
    )


    # --------------------------------------------------
    # CONNECT TO MCP SERVER USING STDIO
    # --------------------------------------------------

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            # ----------------------------------------------
            # INITIALIZE MCP SESSION
            # ----------------------------------------------

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


if __name__ == "__main__":
    asyncio.run(main())