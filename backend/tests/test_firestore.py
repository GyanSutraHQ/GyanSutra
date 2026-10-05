from unittest.mock import AsyncMock, Mock

from gyansutra.firestore import ScriptureStore


async def test_close_awaits_grpc_transport_and_is_idempotent():
    store = ScriptureStore()
    client = Mock()
    client._firestore_api_internal.transport.close = AsyncMock()
    store._client = client
    await store.close()
    await store.close()
    client._firestore_api_internal.transport.close.assert_awaited_once()
    client.close.assert_called_once()
    assert store._client is None
