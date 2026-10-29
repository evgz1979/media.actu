import unittest
from unittest.mock import patch

import httpx


class UIConnectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_core_polling_reuses_a_connection_pool_and_closes_it_on_shutdown(self):
        import ui as frontend
        client_type = httpx.AsyncClient
        requests, clients = [], []

        def response(request):
            requests.append(str(request.url))
            return httpx.Response(200, json={'ok': True})

        def create(**kwargs):
            client = client_type(transport=httpx.MockTransport(response), **kwargs)
            clients.append(client)
            return client

        await frontend.close_core_client()
        with patch.object(frontend.httpx, 'AsyncClient', side_effect=create):
            try:
                self.assertEqual(await frontend.core_request('GET', '/health', timeout=2), {'ok': True})
                await frontend.core_request('GET', '/health', timeout=3)
                self.assertEqual(len(clients), 1)
                self.assertEqual(len(requests), 2)
            finally:
                await frontend.close_core_client()
        self.assertTrue(clients[0].is_closed)
