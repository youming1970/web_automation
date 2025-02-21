# test_async.py
import pytest
import asyncio

async def test_async_simple():
    await asyncio.sleep(0.1)
    assert True