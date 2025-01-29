import aiohttp
from aiohttp import web
from yarl import URL


async def proxy_handler(request: web.Request) -> web.Response:
    """
    Check request contains http url in query args:
        /fetch?url=http%3A%2F%2Fexample.com%2F
    and trying to fetch it and return body with http status.
    If url passed without scheme or is invalid raise 400 Bad request.
    On failure raise 502 Bad gateway.
    :param request: aiohttp.web.Request to handle
    :return: aiohttp.web.Response
    """
    url_param = request.query.get('url')
    if not url_param:
        raise web.HTTPBadRequest(reason="No url to fetch")

    try:
        url = URL(url_param)
    except Exception:
        raise web.HTTPBadRequest(reason="Empty url scheme")

    if not url.is_absolute():
        raise web.HTTPBadRequest(reason="URL must be absolute")

    session = request.app['session']
    try:
        async with session.get(url) as response:
            body = await response.text()
            return web.Response(text=body, status=response.status)
    except aiohttp.ClientError:
        raise web.HTTPBadGateway(reason="Failed to fetch the URL")


async def setup_application(app: web.Application) -> None:
    """
    Setup application routes and aiohttp session for fetching
    :param app: app to apply settings with
    """
    app['session'] = aiohttp.ClientSession()
    app.router.add_get('/fetch', proxy_handler)


async def teardown_application(app: web.Application) -> None:
    """
    Application with aiohttp session for tearing down
    :param app: app for tearing down
    """
    await app['session'].close()


if __name__ == '__main__':
    app = web.Application()
    app.on_startup.append(setup_application)
    app.on_cleanup.append(teardown_application)
    web.run_app(app)