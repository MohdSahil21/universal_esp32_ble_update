import argparse
import asyncio
import yaml
from bleak import BleakClient

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from ota.ble import find_devices
from ota.updater import perform_ota
from ota.logger import log_update, get_last_updates
from ota.utils import load_device_list


console = Console()


# ---------------- CONFIG ---------------- #

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ---------------- HISTORY ---------------- #

def show_history(file_path, limit):
    data = get_last_updates(file_path, limit)

    table = Table(title=f"Last {limit} OTA Updates")

    table.add_column("Time", style="cyan")
    table.add_column("Device", style="green")
    table.add_column("Version", style="magenta")

    for row in data:
        if len(row) == 3:
            table.add_row(*row)

    console.print(table)


# ---------------- OTA RUNNER ---------------- #

async def update_device(dev, config, progress):
    firmware_path = config["ota"]["firmware_path"]
    version = config["ota"]["version"]

    task_id = progress.add_task(f"[yellow]{dev.name}", total=100)

    try:
        async with BleakClient(dev) as client:
            progress.update(task_id, advance=10, description=f"[cyan]Connecting {dev.name}")

            success = await perform_ota(
                client,
                config,
                firmware_path
            )

            if success:
                progress.update(task_id, completed=100, description=f"[green]✔ {dev.name}")
                log_update(
                    config["logging"]["history_file"],
                    dev.name,
                    version
                )
                return (dev.name, "SUCCESS")
            else:
                progress.update(task_id, completed=100, description=f"[red]✖ {dev.name}")
                return (dev.name, "FAILED")

    except Exception as e:
        progress.update(task_id, completed=100, description=f"[red]ERROR {dev.name}")
        return (dev.name, f"ERROR: {str(e)}")


# ---------------- MAIN RUN ---------------- #

async def run(args):
    config = load_config(args.config)

    # Show history mode
    if args.history is not None:
        limit = min(args.history, 20)
        show_history(config["logging"]["history_file"], limit)
        return

    # Load devices
    devices = load_device_list(args.devices)

    console.print(f"\n[bold cyan]🔍 Searching for devices...[/bold cyan]")
    found = await find_devices(devices)

    if not found:
        console.print("[red]No devices found.[/red]")
        return

    console.print(f"[green]Found {len(found)} device(s)[/green]\n")

    results = []

    # Progress UI
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        for dev in found:
            result = await update_device(dev, config, progress)
            results.append(result)

    # ---------------- SUMMARY ---------------- #

    console.print("\n[bold]📊 OTA Summary[/bold]\n")

    table = Table()

    table.add_column("Device", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")

    success_count = 0

    for name, status in results:
        if status == "SUCCESS":
            table.add_row(name, "[green]SUCCESS[/green]")
            success_count += 1
        elif "ERROR" in status:
            table.add_row(name, f"[red]{status}[/red]")
        else:
            table.add_row(name, "[red]FAILED[/red]")

    console.print(table)

    console.print(
        f"\n[bold]Result:[/bold] "
        f"[green]{success_count} success[/green], "
        f"[red]{len(results) - success_count} failed[/red]\n"
    )


# ---------------- ENTRY ---------------- #

def main():
    parser = argparse.ArgumentParser(description="ESP32 BLE OTA CLI")

    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--devices", help="Device file or comma-separated names")
    parser.add_argument("--firmware", help="Override firmware path")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--history", nargs="?", const=5, type=int,
                        help="Show last OTA updates (default=5, max=20)")

    args = parser.parse_args()

    asyncio.run(run(args))


if __name__ == "__main__":
    main()