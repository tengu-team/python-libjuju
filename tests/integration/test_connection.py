import pytest

from juju.client.connection import Connection
from juju.client import client
from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_connect_current(event_loop):
    async with base.CleanModel():
        conn = await Connection.connect_current()

        assert isinstance(conn, Connection)
        await conn.close()


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor(event_loop):

    async with base.CleanModel():
        conn = await Connection.connect_current()

        assert conn.monitor.status == 'connected'
        await conn.close()

        assert conn.monitor.status == 'disconnected'


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor_catches_error(event_loop):

    async with base.CleanModel():
        conn = await Connection.connect_current()

        assert conn.monitor.status == 'connected'
        await conn.ws.close()

        assert conn.monitor.status == 'error'

        await conn.close()


@base.bootstrapped
@pytest.mark.asyncio
async def test_full_status(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        c = client.ClientFacade.from_connection(model.connection)

        status = await c.FullStatus(None)
