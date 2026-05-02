# ota/updater.py

import asyncio
from ota.protocol import *

async def perform_ota(client, config, firmware_path):
    queue = asyncio.Queue()

    async def handler(sender, data):
        if data == OTA_CONTROL_REQUEST_ACK:
            await queue.put("ack")
        elif data == OTA_CONTROL_REQUEST_NAK:
            await queue.put("nak")
        elif data == OTA_CONTROL_DONE_ACK:
            await queue.put("done_ack")
        elif data == OTA_CONTROL_DONE_NAK:
            await queue.put("done_nak")

    await client.start_notify(config["ota"]["control_uuid"], handler)

    packet_size = client.mtu_size - 3

    await client.write_gatt_char(
        config["ota"]["data_uuid"],
        packet_size.to_bytes(2, "little"),
        response=True
    )

    # stream instead of storing all
    await client.write_gatt_char(
        config["ota"]["control_uuid"],
        OTA_CONTROL_REQUEST
    )

    try:
        status = await asyncio.wait_for(queue.get(), timeout=5)
    except asyncio.TimeoutError:
        return False

    if status != "ack":
        return False

    with open(firmware_path, "rb") as f:
        while chunk := f.read(packet_size):
            await client.write_gatt_char(
                config["ota"]["data_uuid"],
                chunk,
                response=True
            )

    await client.write_gatt_char(
        config["ota"]["control_uuid"],
        OTA_CONTROL_DONE
    )

    try:
        status = await asyncio.wait_for(queue.get(), timeout=5)
    except asyncio.TimeoutError:
        return False

    return status == "done_ack"