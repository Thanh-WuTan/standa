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
    async def download_adversary_profile(self, request):
        try:
            adversary_id = request.match_info.get('adversary_id')
            profile = await self.myplugin_svc.get_adversary_profile(adversary_id)
        except Exception as e:
            print("Error: ", e)
            return web.Response(text=str(e), status=500)
        
        if not profile:
            return web.Response(text='Adversary not found', status=404)
        
        content = f"Adversary ID: {profile['adversary_id']}\nName: {profile['name']}\nDescription: {profile['description']}\nObjective: {profile['objective']}\nPlugin: {profile['plugin']}\nAtomic ordering: {profile['atomic_ordering']}"

        return web.Response(
            text=content,
            headers={
                'Content-Disposition': f'attachment; filename="{profile["name"]}.txt"'
            }
        )
        
    @check_authorization
    async def download_atomic_ordering(self, request): 
        try:
            adversary_id = request.match_info.get('adversary_id')
            atomic_ordering = await self.myplugin_svc.get_atomic_ordering(adversary_id)
            
            if not atomic_ordering:
                return web.Response(text='Atomic ordering not found', status=404)
            
            zip_path = await self.myplugin_svc.create_zip_containing_abilities(atomic_ordering)
             
            return web.FileResponse(zip_path, headers={
                'Content-Disposition': f'attachment; filename="{adversary_id}_abilities.zip"'
            })
        
        except Exception as e:
            print("Error: ", e)
            return web.Response(text=str(e), status=500)

    @check_authorization
    async def something(self, request):
        try:
            something = await self.myplugin_svc.do_something()
            return web.Response(text=json.dumps(something), content_type='application/json')
        except Exception as e:
            print("Error: ", e)
            return web.Response(text=str(e), status=500)

    @check_authorization
    async def get_parsers(self, request):
        try:
            parsers = await self.myplugin_svc.get_all_parsers()
            return web.Response(text=json.dumps(parsers), content_type='application/json')
        except Exception as e:
            print("Error: ", e)
            return web.Response(text=str(e), status=500)

    @check_authorization
    @template('standa.html')
    async def splash(self, request):
        adversaries = await self.services.get('data_svc').locate('adversaries')
        return(dict(adversaries=[a.display for a in adversaries]))
    
    