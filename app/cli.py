import json
import os
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from app import config
from app.client import BonusClient

console = Console()


def get_client() -> BonusClient:
    token = os.environ.get("BONUS_TOKEN") or config.get_token() or ""
    card_id = os.environ.get("BONUS_CARD_ID") or config.get_card_id() or ""
    store_id = os.environ.get("BONUS_STORE_ID") or config.get_store_id() or ""
    return BonusClient(token, card_id, store_id)


def _format_price(amount: Any) -> str:
    if amount is None or amount == "" or amount == 0:
        return "-"
    try:
        return f"{int(float(str(amount))):,} kr"
    except (ValueError, TypeError):
        return str(amount)


@click.group()
def main() -> None:
    """Bónus CLI - Interact with Bónus grocery store (Iceland)."""


# === System ===


@main.command()
def ping() -> None:
    """Ping the Bónus API server."""
    with get_client() as client:
        result = client.ping()
        console.print(f"[green]{result}[/green]")


# === Products ===


@main.command()
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Max results")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def search(query: str, limit: int, json_output: bool) -> None:
    """Search for products."""
    with get_client() as client:
        items = client.search_items(query, limit)
        if json_output:
            console.print(json.dumps(items, indent=2, default=str))
            return
        if not items:
            console.print("[dim]No products found[/dim]")
            return
        table = Table(title=f"Products matching '{query}' ({len(items)} results)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Price", style="yellow", justify="right")
        table.add_column("Unit", style="dim")
        for item in items:
            price = item.get("Price", "")
            if isinstance(price, dict):
                price = price.get("Amount", price.get("Amt", ""))
            prices = item.get("Prices", [])
            if not price and prices:
                price = prices[0].get("Amt", prices[0].get("Amount", ""))
            table.add_row(
                str(item.get("Id", "")),
                str(item.get("Description", ""))[:50],
                _format_price(price),
                str(item.get("SalesUomId", "")),
            )
        console.print(table)


@main.command("product")
@click.argument("item_id")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def product_show(item_id: str, json_output: bool) -> None:
    """Show product details by ID."""
    with get_client() as client:
        item = client.get_item(item_id)
        if json_output:
            console.print(json.dumps(item, indent=2, default=str))
            return
        if not item:
            console.print("[red]Product not found[/red]")
            return
        console.print(f"[bold cyan]{item.get('Description', '')}[/bold cyan]")
        console.print(f"[bold]ID:[/bold] {item.get('Id', '')}")
        price = item.get("Price", "")
        if isinstance(price, dict):
            console.print(f"[bold]Price:[/bold] {_format_price(price.get('Amount', ''))}")
        else:
            console.print(f"[bold]Price:[/bold] {_format_price(price)}")
        console.print(f"[bold]Category:[/bold] {item.get('ItemCategoryCode', '')}")
        console.print(f"[bold]Unit:[/bold] {item.get('SalesUomId', '')}")
        if item.get("Details"):
            console.print(f"[bold]Details:[/bold] {item['Details']}")
        images = item.get("Images", [])
        if images:
            console.print(f"[bold]Image:[/bold] {images[0].get('StreamURL', '')}")
        uoms = item.get("UnitOfMeasures", [])
        if uoms:
            console.print(f"[bold]Units:[/bold] {', '.join(u.get('Description', '') for u in uoms)}")


# === Stores ===


@main.command("stores")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def stores(json_output: bool) -> None:
    """List all Bónus store locations."""
    with get_client() as client:
        store_list = client.get_stores()
        if json_output:
            console.print(json.dumps(store_list, indent=2, default=str))
            return
        if not store_list:
            console.print("[dim]No stores found[/dim]")
            return
        table = Table(title=f"Bónus Stores ({len(store_list)})")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Address", style="dim")
        table.add_column("City", style="yellow")
        table.add_column("PostCode", style="dim")
        for store in store_list:
            addr = store.get("Address", {})
            table.add_row(
                str(store.get("Id", "")),
                str(store.get("Description", store.get("Name", ""))),
                str(addr.get("Address1", "")),
                str(addr.get("City", "")),
                str(addr.get("PostCode", "")),
            )
        console.print(table)


# === Offers ===


@main.command("offers")
@click.option("--card-id", "-c", default="", help="Loyalty card ID")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def offers(card_id: str, json_output: bool) -> None:
    """List published offers/deals."""
    with get_client() as client:
        offer_list = client.get_published_offers(card_id)
        if json_output:
            console.print(json.dumps(offer_list, indent=2, default=str))
            return
        if not offer_list:
            console.print("[dim]No offers found[/dim]")
            return
        table = Table(title=f"Offers ({len(offer_list)})")
        table.add_column("ID", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Details", style="dim", max_width=40)
        for offer in offer_list:
            table.add_row(
                str(offer.get("Id", "")),
                str(offer.get("Description", ""))[:40],
                str(offer.get("Type", offer.get("OfferType", ""))),
                str(offer.get("Details", ""))[:40],
            )
        console.print(table)


# === Loyalty ===


@main.command("points")
def points() -> None:
    """Show loyalty point rate."""
    with get_client() as client:
        rate = client.get_point_rate()
        console.print(f"[bold]Point rate:[/bold] {rate}")


@main.command("profile")
@click.option("--card-id", "-c", default="", help="Loyalty card ID")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def profile(card_id: str, json_output: bool) -> None:
    """Show member profile by card ID."""
    with get_client() as client:
        contact = client.contact_get_by_card_id(card_id)
        if json_output:
            console.print(json.dumps(contact, indent=2, default=str))
            return
        if not contact:
            console.print("[dim]No profile found[/dim]")
            return
        console.print(f"[bold cyan]Member Profile[/bold cyan]")
        for key in ("Id", "FirstName", "LastName", "Email", "Phone", "MobilePhone", "CardId"):
            val = contact.get(key, "")
            if val:
                console.print(f"[bold]{key}:[/bold] {val}")
        accounts = contact.get("Account", {})
        if accounts:
            console.print(f"[bold]Points:[/bold] {accounts.get('PointBalance', 0)}")


# === Auth ===


@main.command()
@click.argument("card_id")
@click.argument("store_id")
def login(card_id: str, store_id: str) -> None:
    """Configure card and store. Run 'bonus stores' to find your store ID.

    \b
    Examples:
      bonus login BON12232321234010426 07
    """
    config.set_card_id(card_id)
    config.set_store_id(store_id)
    console.print(f"[green]Card ID:[/green] {card_id}")
    console.print(f"[green]Store ID:[/green] {store_id}")
    console.print(f"Config saved to {config.CONFIG_FILE}")


@main.command()
def logout() -> None:
    """Clear saved credentials."""
    config.clear_config()
    console.print("[green]Logged out - credentials cleared[/green]")


@main.command("config-show")
def config_show() -> None:
    """Show current configuration."""
    console.print(f"[bold]Config file:[/bold] {config.CONFIG_FILE}")
    card_id = config.get_card_id()
    console.print(f"[bold]Card ID:[/bold] {card_id or '[dim]not set[/dim]'}")
    store_id = config.get_store_id()
    console.print(f"[bold]Store ID:[/bold] {store_id or '[dim]not set[/dim]'}")
    card_id = config.get_card_id()
    console.print(f"[bold]Card ID:[/bold] {card_id or '[dim]not set[/dim]'}")


if __name__ == "__main__":
    main()
