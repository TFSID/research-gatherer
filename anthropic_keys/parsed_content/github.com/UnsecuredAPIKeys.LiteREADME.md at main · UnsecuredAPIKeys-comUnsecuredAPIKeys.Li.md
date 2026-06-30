---
source: https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md
parsed_date: 2026-06-27 01:29:24
domain: github.com
---

Title: UnsecuredAPIKeys.Lite/README.md at main · UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite

URL Source: https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md

Markdown Content:
[![Image 1: GitHub Stars](https://camo.githubusercontent.com/60bef96c65e9a859796a8884c6bae546f3d17012ba70923a88ef423966b7ee4f/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f73746172732f54534361727465724a722f556e736563757265644150494b6579732d4f70656e536f757263653f7374796c653d736f6369616c)](https://github.com/TSCarterJr/UnsecuredAPIKeys-OpenSource)[![Image 2: .NET 10](https://camo.githubusercontent.com/c83663d94fc6f4a1007e259b8a836de817b868787d826347900d4690a1b124c3/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2e4e45542d31302e302d353132424434)](https://dotnet.microsoft.com/download/dotnet/10.0)[![Image 3: License](https://camo.githubusercontent.com/0c3de1245f0e4d6dc7bb486218b8d01e3f0108e659386fec30ec3d6c777cfa3a/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d437573746f6d2d626c7565)](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/LICENSE)[![Image 4: CodeRabbit Pull Request Reviews](https://camo.githubusercontent.com/38af605c06b1dbfe58035b6d613c5f3a0961c12cfa95013563a3d74e3d90a3ae/68747470733a2f2f696d672e736869656c64732e696f2f636f64657261626269742f7072732f6769746875622f54534361727465724a722f556e736563757265644150494b6579732d4f70656e536f757263653f75746d5f736f757263653d6f73732675746d5f6d656469756d3d6769746875622675746d5f63616d706169676e3d54534361727465724a72253246556e736563757265644150494b6579732d4f70656e536f75726365266c6162656c436f6c6f723d31373137313726636f6c6f723d464635373041266c696e6b3d6874747073253341253246253246636f64657261626269742e6169266c6162656c3d436f64655261626269742b52657669657773)](https://camo.githubusercontent.com/38af605c06b1dbfe58035b6d613c5f3a0961c12cfa95013563a3d74e3d90a3ae/68747470733a2f2f696d672e736869656c64732e696f2f636f64657261626269742f7072732f6769746875622f54534361727465724a722f556e736563757265644150494b6579732d4f70656e536f757263653f75746d5f736f757263653d6f73732675746d5f6d656469756d3d6769746875622675746d5f63616d706169676e3d54534361727465724a72253246556e736563757265644150494b6579732d4f70656e536f75726365266c6162656c436f6c6f723d31373137313726636f6c6f723d464635373041266c696e6b3d6874747073253341253246253246636f64657261626269742e6169266c6162656c3d436f64655261626269742b52657669657773)

> **Thank you to everyone who has starred this project!** Your support helps raise awareness about API key security and encourages responsible disclosure practices.

> **Full Version Available:**[www.UnsecuredAPIKeys.com](https://www.unsecuredapikeys.com/)
> 
> 
> The full version offers: Web UI, all API providers, community features, and more.

A command-line tool for discovering and validating exposed API keys on GitHub. This lite version focuses on educational and security awareness purposes.

## Lite Version Limits

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#lite-version-limits)
| Feature | Lite (This Repo) | Full Version |
| --- | --- | --- |
| Search Provider | GitHub only | GitHub, GitLab, SourceGraph |
| API Providers | OpenAI, Anthropic, Google | 15+ providers |
| Valid Key Cap | 50 keys | Higher limits |
| Interface | CLI | Web UI + API |
| Database | SQLite (local) | PostgreSQL |

## ⚠️ Educational Purpose Only

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#%EF%B8%8F-educational-purpose-only)
This tool is for **educational and security awareness purposes only**.

*   **Learn** how API keys get exposed in public repositories
*   **Understand** the importance of secret management
*   **Report** exposed keys responsibly to repository owners
*   **Never** use discovered keys for unauthorized access

**Do NOT publish your database or results publicly.** This would expose working API keys to malicious actors.

## Quick Start

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#quick-start)
### 1. Download

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#1-download)
Download the latest release for your platform from [**Releases**](https://github.com/TSCarterJr/UnsecuredAPIKeys-OpenSource/releases):

| Platform | File |
| --- | --- |
| Windows | `unsecuredapikeys-win-x64.exe` |
| Linux | `unsecuredapikeys-linux-x64` |

**No .NET runtime required** - these are self-contained executables.

### 2. Run

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#2-run)
**Windows:**

.\unsecuredapikeys-win-x64.exe

**Linux:**

chmod +x unsecuredapikeys-linux-x64
./unsecuredapikeys-linux-x64

### 3. Configure GitHub Token

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#3-configure-github-token)
On first run, go to **Configure Settings**>**Set GitHub Token**.

Create a token at: [https://github.com/settings/tokens](https://github.com/settings/tokens) Required scope: `public_repo`

### 4. Start Searching

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#4-start-searching)
*   **Start Scraper**: Searches GitHub for exposed API keys (runs continuously)
*   **Start Verifier**: Maintains up to 50 valid keys (re-checks as needed)
*   **View Status**: Shows current statistics
*   **Export Keys**: Export to JSON or CSV

### Building from Source (Optional)

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#building-from-source-optional)
If you prefer to build from source:

git clone https://github.com/TSCarterJr/UnsecuredAPIKeys-OpenSource.git
cd UnsecuredAPIKeys-OpenSource
dotnet build
cd UnsecuredAPIKeys.CLI
dotnet run

## How It Works

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#how-it-works)
### Scraper

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#scraper)
1.   Uses your GitHub token to search for common API key patterns
2.   Extracts potential keys using regex patterns for OpenAI, Anthropic, and Google
3.   Stores discovered keys in a local SQLite database

### Verifier

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#verifier)
1.   Validates discovered keys against the actual provider APIs
2.   Maintains exactly 50 valid keys (lite limit)
3.   Re-checks existing valid keys periodically
4.   When a key becomes invalid, verifies new ones until back to 50

## Project Structure

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#project-structure)

```
UnsecuredAPIKeys-OpenSource/
├── UnsecuredAPIKeys.CLI/         # Main CLI application
├── UnsecuredAPIKeys.Data/        # SQLite database layer
├── UnsecuredAPIKeys.Providers/   # API validation providers
├── unsecuredapikeys.db           # SQLite database (auto-created)
└── README.md
```

## Prerequisites

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#prerequisites)
*   **.NET 10 SDK** - [Download here](https://dotnet.microsoft.com/download/dotnet/10.0)
*   **GitHub Personal Access Token** - [Create here](https://github.com/settings/tokens)
*   **Platform**: Windows, macOS, or Linux

## Supported Providers (Lite)

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#supported-providers-lite)
| Provider | Pattern Examples |
| --- | --- |
| OpenAI | `sk-proj-*`, `sk-or-v1-*` |
| Anthropic | `sk-ant-api*` |
| Google AI | `AIzaSy*` |

## Configuration

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#configuration)
Copy `appsettings.example.json` to `appsettings.json` and configure:

{
  "GitHub": {
    "Token": "ghp_YOUR_TOKEN"
  },
  "Database": {
    "Path": "unsecuredapikeys.db"
  }
}

Or configure directly via the CLI menu.

## Database

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#database)
The SQLite database (`unsecuredapikeys.db`) is auto-created on first run in the working directory.

| Action | How |
| --- | --- |
| **Location** | Same folder as the executable |
| **Reset** | Delete `unsecuredapikeys.db` and restart |
| **Backup** | Copy the `.db` file |
| **View data** | Use any SQLite browser (e.g., DB Browser for SQLite) |

## Search Queries

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#search-queries)
On first run, default search queries are automatically seeded:

*   `sk-proj-`, `sk-or-v1-`, `OPENAI_API_KEY` (OpenAI)
*   `sk-ant-api`, `ANTHROPIC_API_KEY` (Anthropic)
*   `AIzaSy`, `GOOGLE_API_KEY` (Google)

The scraper rotates through these queries automatically.

## Rate Limiting

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#rate-limiting)
Built-in delays prevent API abuse:

| Operation | Delay |
| --- | --- |
| Between searches | 5 seconds |
| Between verifications | 1 second |
| Batch size | 10 keys |

GitHub's API allows ~30 searches/minute with authentication.

## Troubleshooting

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#troubleshooting)
| Issue | Solution |
| --- | --- |
| "No GitHub token configured" | Go to Configure Settings > Set GitHub Token |
| "Rate limit exceeded" | Wait 60 seconds, or use a different token |
| Build fails | Ensure .NET 10 SDK is installed: `dotnet --version` |
| No keys found | Check your token has `public_repo` scope |
| Database locked | Close other apps using the .db file |

## Legal & Ethical Use

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#legal--ethical-use)
*   **Educational Purpose**: This tool demonstrates API security vulnerabilities
*   **Responsible Use**: Only use for legitimate security research
*   **No Abuse**: Do not use discovered keys for unauthorized access
*   **Compliance**: Follow all applicable laws and terms of service

## License

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#license)
This project uses a **custom attribution-required license** based on MIT.

### Attribution Required

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#attribution-required)
Any use of this code requires visible attribution:

*   Display: "Based on UnsecuredAPIKeys Open Source"
*   Link to: [https://github.com/TSCarterJr/UnsecuredAPIKeys-OpenSource](https://github.com/TSCarterJr/UnsecuredAPIKeys-OpenSource)
*   Must be visible in UI/documentation

See [LICENSE](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/LICENSE) for full details.

## Legacy UI Version

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#legacy-ui-version)
Looking for the original Web UI + WebAPI architecture? Check the [`legacy_ui`](https://github.com/TSCarterJr/UnsecuredAPIKeys-OpenSource/tree/legacy_ui) branch.

> **Note**: The legacy branch is no longer actively maintained. For the full-featured web experience, use [www.UnsecuredAPIKeys.com](https://www.unsecuredapikeys.com/).

## Full Version

[](https://github.com/UnsecuredAPIKeys-com/UnsecuredAPIKeys.Lite/blob/main/README.md#full-version)
For higher limits, more providers, web interface, and community features:

**[www.UnsecuredAPIKeys.com](https://www.unsecuredapikeys.com/)**

* * *

**Remember**: Use responsibly and in accordance with applicable laws.
