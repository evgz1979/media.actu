"""Keep old comparison links working inside the main workspace."""
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse
from nicegui import app


def register_comparison_page(request, format_bytes, format_date):
    @app.get('/compare', include_in_schema=False)
    async def comparison_redirect(source: str = '', path: str = '', job: str = ''):
        params = {key: value for key, value in {'source': source, 'path': path, 'job': job}.items() if value}
        return RedirectResponse('/' + ('?' + urlencode(params) if params else ''), status_code=307)
