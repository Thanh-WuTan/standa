import json
from aiohttp_jinja2 import template, web 
from app.service.auth_svc import check_authorization
from plugins.standa.app.service import StandaService

class StandaApi:
    def __init__(self, services):
        self.services = services
        self.auth_svc = services.get('auth_svc')
        self.myplugin_svc = StandaService(services)

    @check_authorization
    async def download(self, request):
        try:
            adversary_id = request.query.get('adversary')
            source_id = request.query.get('source')
            platform = request.query.get('platform')
            if not adversary_id or not source_id or not platform:
                return web.HTTPBadRequest(reason="Missing required query parameters")
            zip_path = await self.myplugin_svc.download_standalone_agent(adversary_id, source_id, platform)
            if not zip_path:
                return web.Response(text='Agent not found', status=404)
            return web.FileResponse(zip_path, headers={
                'Content-Disposition': f'attachment; filename="{adversary_id}.zip"'
            })
        except Exception as e:
            print("Error: ", e)
            return web.Response(text=str(e), status=500)

    @check_authorization
    @template('standa.html')
    async def splash(self, request):
        adversaries = [a.display for a in await self.services.get('data_svc').locate('adversaries')]
        sources = [s.display for s in await self.services.get('data_svc').locate('sources')]

        return dict(adversaries=adversaries, sources=sources)
        