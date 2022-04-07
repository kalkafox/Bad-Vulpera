from discord import Webhook, AsyncWebhookAdapter
from aiohttp import web, ClientSession
from rich.console import Console



class BuildStatus():
    l = Console()

    app = web.Application()
    routes = web.RouteTableDef()

    def __init__(self, token):
        self.app.add_routes(self.routes)
        try:
            web.run_app(self.app)
        except KeyboardInterrupt:
            pass

    @routes.post('/github')
    async def github(self, request):
        self.l.log("[green] Got GitHub response.")
        return web.Response(text="OK!")


def main():
    bs = BuildStatus('token')

main()




