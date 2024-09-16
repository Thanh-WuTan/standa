from plugins.myplugin.app.api import MypluginApi

name = 'Abilities'
description = 'A sample plugin for demonstration purposes'
address = '/plugin/myplugin/gui'


async def enable(services):
    app = services.get('app_svc').application
    fetcher = MypluginApi(services)
    app.router.add_route('*', '/plugin/myplugin/gui', fetcher.splash) 
    app.router.add_route('GET', '/plugin/myplugin/download/adversary_profile/{adversary_id}', fetcher.download_adversary_profile) 
    app.router.add_route('GET', '/plugin/myplugin/download/atomic_ordering/{adversary_id}', fetcher.download_atomic_ordering)
    app.router.add_route('GET', '/plugin/myplugin/something', fetcher.something)
    app.router.add_route('GET', '/plugin/myplugin/get_all_payloads', fetcher.get_payloads)