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

            # ----------------------------------------------
            # PRINT ACTUAL RESOURCE TEXT
            # ----------------------------------------------

            if resource_result.contents:

                print("\nActual Resource Content:")

                print(
                    resource_result.contents[0].text
                )

            # ----------------------------------------------
            # DISCOVER MCP RESOURCE TEMPLATES
            # ----------------------------------------------

            templates_result = (
                await session.list_resource_templates()
            )

            print("\nAvailable MCP resource templates:")

            for template in templates_result.resource_templates:

                print("\nName:")
                print(template.name)

                print("URI Template:")
                print(template.uri_template)

                print("Description:")
                print(template.description)

                print("MIME Type:")
                print(template.mime_type)

            # ----------------------------------------------
            # READ RESOURCE FROM TEMPLATE
            # ----------------------------------------------

            test_report_result = await session.read_resource(
                "test-report://TC-102"
            )

            print("\nTest report resource result:")
            print(test_report_result)

            if test_report_result.contents:

                print("\nActual Test Report Content:")

                print(
                    test_report_result.contents[0].text
                )


if __name__ == "__main__":
    asyncio.run(main())