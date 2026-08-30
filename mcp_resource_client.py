import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


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
            # DISCOVER MCP RESOURCES
            # ----------------------------------------------

            resources_result = (
                await session.list_resources()
            )

            print("Available MCP resources:")

            for resource in resources_result.resources:

                print("\nName:")
                print(resource.name)

                print("URI:")
                print(resource.uri)

                print("Description:")
                print(resource.description)

                print("MIME Type:")
                print(resource.mime_type)

            # ----------------------------------------------
            # READ MCP RESOURCE
            # ----------------------------------------------

            resource_result = await session.read_resource(
                "test-environment://qa"
            )

            print("\nResource read result:")
            print(resource_result)


if __name__ == "__main__":
    asyncio.run(main())