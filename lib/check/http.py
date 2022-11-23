import logging
from libprobe.asset import Asset


async def check_http(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict:
    ...
