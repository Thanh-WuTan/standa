from plugins.standa.app.api import StandaApi

name = 'Abilities'
description = 'A sample plugin for demonstration purposes'
address = '/plugin/standa/gui'


async def enable(services):
    app = services.get('app_svc').application
    fetcher = StandaApi(services)
    app.router.add_route('*', '/plugin/standa/gui', fetcher.splash) 
    app.router.add_route('GET', '/plugin/standa/download/adversary_profile/{adversary_id}', fetcher.download_adversary_profile) 
    app.router.add_route('GET', '/plugin/standa/download/atomic_ordering/{adversary_id}', fetcher.download_atomic_ordering)
    app.router.add_route('GET', '/plugin/standa/something', fetcher.something)
    app.router.add_route('GET', '/plugin/standa/get_all_payloads', fetcher.get_payloads)