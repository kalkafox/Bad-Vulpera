from discord import Webhook, AsyncWebhookAdapter
from aiohttp import web, ClientSession
from rich.console import Console



class BuildStatus():
    l = Console()

    app = web.Application()
    routes = web.RouteTableDef()

    def __init__(self, token):
        self.app.add_routes(self.routes)
        web.run_app(self.app)

    @routes.get('/github')
    async def github(self, request):
        return web.Response(text="OK!")


def main():
    bs = BuildStatus()

main()




