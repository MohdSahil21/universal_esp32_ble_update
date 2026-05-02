from bleak import BleakClient, BleakScanner

async def find_devices(target_names):
    devices = await BleakScanner.discover()
    return [d for d in devices if d.name in target_names]