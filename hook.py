from plugins.standa.app.api import StandaApi
from plugins.standa.app.service import StandaService

name = 'Standa'
description = 'A plugin that auto-generates stand-alone agents from selected adversary profile, enabling agents to operate independently from the Caldera C2 server.'
address = '/plugin/standa/gui'


async def enable(services):
    app = services.get('app_svc').application
    fetcher = StandaApi(services)
    app.router.add_route('*', '/plugin/standa/gui', fetcher.splash)  
    app.router.add_route('GET', '/plugin/standa/download', fetcher.download)
    
    plugin_svc = StandaService(services)
    await plugin_svc.get_parser_modules()
    await plugin_svc.get_requirements_modules()