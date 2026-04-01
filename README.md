# bonus-cli

CLI tool for interacting with Bónus grocery store (Iceland).

## Setup

```
uv run bonus stores                              # find your store ID
uv run bonus login <CARD_ID> <STORE_ID>          # configure
```

Your Bónus loyalty card ID can be found inside the Gripið og greitt app (starts with `BON`).

### Example

```
uv run bonus login BON12444421495010426 07       # card + Grandi store
uv run bonus search "pylsur"                      # search products with prices
uv run bonus product 25331                        # product details
```

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search products with prices |
| `product <id>` | Show product details |
| `stores` | List all Bónus locations |
| `offers` | List current offers/deals |
| `points` | Show loyalty point rate |
| `login <card> <store>` | Configure card and store |
| `logout` | Clear config |
| `config-show` | Show current config |
| `ping` | Check API status |

All commands support `-j` for JSON output.

## Store IDs

Run `bonus stores` for the full list. Some common ones:

| ID | Location |
|----|----------|
| 07 | Fiskislóð / Grandi |
| 17 | Kringlan |
| 05 | Kópavogur |
| 04 | Hafnarfjörður |
| 02 | Faxafen |
| 09 | Grafarvogur |
