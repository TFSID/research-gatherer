---
source: https://github.com/tmcqueen/ngraphify
parsed_date: 2026-06-27 01:28:27
domain: github.com
---

Title: GitHub - tmcqueen/ngraphify: Reimplement the graphify Python application in C# .NET 10 with a native Leiden clustering wrapper, covering AST extraction for 9 languages, graph building, deduplication, clustering, analysis, caching, and report generation.

URL Source: https://github.com/tmcqueen/ngraphify

Markdown Content:
## Graphiphy

[](https://github.com/tmcqueen/ngraphify#graphiphy)
A .NET 10 codebase analysis tool that builds knowledge graphs from source code using TreeSitter extraction and graph clustering. Analyze repositories, discover dependencies, and ask LLM questions about your codebase architecture.

## What It Does

[](https://github.com/tmcqueen/ngraphify#what-it-does)
Graphiphy parses source files in **9 languages** (C#, Java, Python, JavaScript, TypeScript, Go, Rust, C++, C) via TreeSitter, builds a **knowledge graph** using QuikGraph with Leiden clustering, and exposes analysis through:

*   **CLI commands** — analyze, report, query, and serve
*   **MCP server** — integrate with Claude and other AI clients
*   **MSBuild integration** — automatically analyze during .NET builds

## Features

[](https://github.com/tmcqueen/ngraphify#features)
*   **AST Extraction** — 9 languages, respects `.gitignore`, blocks sensitive files
*   **Knowledge Graph** — nodes (entities), edges (relationships), Leiden clustering (optional)
*   **Graph Analysis** — god nodes (highly connected), surprising connections, community detection
*   **LLM Integration** — 5 providers (Anthropic, OpenAI, Ollama, Copilot, A2A)
*   **MCP Server** — use with Claude Desktop, Cursor, and other MCP clients
*   **Caching** — incremental analysis, `.graphiphy-cache/` directory
*   **Markdown Reports** — detailed codebase summaries and visualizations

## Quick Start

[](https://github.com/tmcqueen/ngraphify#quick-start)
### Installation

[](https://github.com/tmcqueen/ngraphify#installation)
Install the CLI globally:

dotnet tool install -g Graphiphy.Cli

Or build from source:

git clone https://github.com/timm/ngraphify
cd ngraphify
dotnet build src/Graphiphy.Cli

### First Command

[](https://github.com/tmcqueen/ngraphify#first-command)
Analyze a repository:

graphiphy-cli analyze /path/to/repo

Output:

```
Metric                Value
─────────────────────────────
Files detected        42
Nodes (entities)      156
Edges (relations)     284
Top entity            UserService (Services/UserService.cs)
```

Generate a Markdown report:

graphiphy-cli report /path/to/repo --out analysis.md

Query with an LLM (requires API key):

export ANTHROPIC_API_KEY=sk-ant-...
graphiphy-cli query /path/to/repo "What are the main dependencies in this codebase?"

Start the MCP server:

graphiphy-cli serve /path/to/repo

Then add to Claude Desktop (`claude_desktop_config.json`):

{
  "mcpServers": {
    "graphiphy": {
      "command": "/path/to/graphiphy-cli",
      "args": ["serve", "/path/to/repo"]
    }
  }
}

## Requirements

[](https://github.com/tmcqueen/ngraphify#requirements)
*   **.NET 10 runtime** — [download](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)
*   **TreeSitter native libraries** — included in distribution
*   **LLM API key** (optional) — for the `query` command

## Installation Methods

[](https://github.com/tmcqueen/ngraphify#installation-methods)
### 1. Global .NET Tool

[](https://github.com/tmcqueen/ngraphify#1-global-net-tool)
Fastest and recommended:

dotnet tool install -g Graphiphy.Cli

Update:

dotnet tool update -g Graphiphy.Cli

Uninstall:

dotnet tool uninstall -g Graphiphy.Cli

### 2. Local Tool (via dotnet-tools.json)

[](https://github.com/tmcqueen/ngraphify#2-local-tool-via-dotnet-toolsjson)
In your repository root:

dotnet new tool-manifest  # if not already created
dotnet tool install Graphiphy.Cli

Run:

dotnet tool run graphiphy-cli analyze .

### 3. Build from Source

[](https://github.com/tmcqueen/ngraphify#3-build-from-source)

git clone https://github.com/timm/ngraphify
cd ngraphify
dotnet publish src/Graphiphy.Cli -c Release -o ./dist
./dist/graphiphy-cli analyze /path/to/repo

### 4. NuGet Package (MSBuild Integration)

[](https://github.com/tmcqueen/ngraphify#4-nuget-package-msbuild-integration)
Install in any .NET project:

dotnet add package Graphiphy.MSBuild

This enables automatic analysis during builds. See [MSBuild Integration](https://github.com/tmcqueen/ngraphify/blob/main/docs/MSBuild-Integration.md).

## CLI Commands

[](https://github.com/tmcqueen/ngraphify#cli-commands)
### analyze

[](https://github.com/tmcqueen/ngraphify#analyze)
Get repository statistics and extract the graph.

graphiphy-cli analyze <path> [options]

Options:

*   `--out, -o <file>` — Write Markdown report to file
*   `--cache <dir>` — Cache directory (default: `<path>/.graphiphy-cache`)

Example:

graphiphy-cli analyze /path/to/repo --out report.md

### report

[](https://github.com/tmcqueen/ngraphify#report)
Generate a detailed Markdown analysis report.

graphiphy-cli report <path> [options]

Options:

*   `--out, -o <file>` — Write to file (prints to stdout if omitted)
*   `--cache <dir>` — Cache directory (default: `<path>/.graphiphy-cache`)

Example:

graphiphy-cli report /path/to/repo --out analysis.md
cat analysis.md | less

### query

[](https://github.com/tmcqueen/ngraphify#query)
Ask an LLM a question about the codebase.

graphiphy-cli query <path> <question> [options]

Options:

*   `--provider <name>` — `anthropic` (default), `openai`, `ollama`, `copilot`, `a2a`
*   `--key <apiKey>` — API key (falls back to env vars)
*   `--model <name>` — Model name
*   `--agent-url <url>` — Remote agent URL (A2A only)
*   `--cache <dir>` — Cache directory

Examples:

# Using Anthropic (default)
export ANTHROPIC_API_KEY=sk-ant-...
graphiphy-cli query /path/to/repo "What is the main entry point?"

# Using OpenAI
export OPENAI_API_KEY=sk-...
graphiphy-cli query /path/to/repo "Summarize the architecture" --provider openai --model gpt-4o

# Using Ollama (local)
graphiphy-cli query /path/to/repo "Find security issues" --provider ollama --model llama3.2

# Using GitHub Copilot
graphiphy-cli query /path/to/repo "List all services" --provider copilot

# Using remote A2A agent
graphiphy-cli query /path/to/repo "Explain this codebase" --provider a2a --agent-url http://agent.example.com

### serve

[](https://github.com/tmcqueen/ngraphify#serve)
Start an MCP (Model Context Protocol) server on stdio.

graphiphy-cli serve [path] [options]

Arguments:

*   `[path]` — Repository root (default: current directory)

Options:

*   `--cache <dir>` — Cache directory

Example:

graphiphy-cli serve /path/to/repo

Diagnostics go to stderr; stdout is reserved for MCP JSON-RPC protocol.

## MCP Server Tools

[](https://github.com/tmcqueen/ngraphify#mcp-server-tools)
When running as an MCP server, the following tools are available to AI clients:

| Tool | Description | Parameters |
| --- | --- | --- |
| `get_god_nodes` | Most connected entities in the graph | `topN` (optional, default: 5) |
| `get_surprising_connections` | Cross-file dependencies and ambiguous edges | `topN` (optional, default: 5) |
| `get_summary_stats` | Node count, edge count, community count, top files | — |
| `search_nodes` | Find nodes by label substring | `query` (required) |
| `get_report` | Full Markdown analysis report | — |

### Example Claude Prompts

[](https://github.com/tmcqueen/ngraphify#example-claude-prompts)
With the server running in Claude Desktop:

> "What are the most connected classes in this repository?"

> "Are there any surprising dependencies between modules?"

> "Show me everything that depends on the Router class."

> "Generate a full analysis report for this codebase."

## Configuration

[](https://github.com/tmcqueen/ngraphify#configuration)
### Cache Directory

[](https://github.com/tmcqueen/ngraphify#cache-directory)
By default, analysis is cached in `.graphiphy-cache/` at the repository root. To use a custom location:

graphiphy-cli analyze /path/to/repo --cache /tmp/ngraph-cache

Or in MSBuild:

<PropertyGroup>
  <GraphiphyCacheDir>$(MSBuildProjectDirectory)/.graphiphy-cache</GraphiphyCacheDir>
</PropertyGroup>

### .gitignore Handling

[](https://github.com/tmcqueen/ngraphify#gitignore-handling)
Graphiphy respects `.gitignore` files at any depth in your repository. Files matching `.gitignore` patterns are automatically excluded.

Additionally, sensitive files are **always blocked**:

*   Private keys (`.pem`, `.key`, `.p8`, etc.)
*   Credentials (`.env`, `config.local.*`, credentials files)
*   Lock files (some)

### Environment Variables

[](https://github.com/tmcqueen/ngraphify#environment-variables)
#### For API Keys

[](https://github.com/tmcqueen/ngraphify#for-api-keys)

export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GITHUB_TOKEN=ghp_...  # For Copilot provider

#### For Build Integration

[](https://github.com/tmcqueen/ngraphify#for-build-integration)

export GRAPHIPHY_ANALYZING=1  # Prevents recursive analysis during MSBuild

## Architecture

[](https://github.com/tmcqueen/ngraphify#architecture)
### Pipeline

[](https://github.com/tmcqueen/ngraphify#pipeline)

```
Source Files
    ↓
TreeSitter Extraction (9 languages)
    ↓
Entity Deduplication
    ↓
Graph Construction (QuikGraph)
    ↓
Leiden Clustering (optional)
    ↓
Analysis & Reporting
```

### Graph Model

[](https://github.com/tmcqueen/ngraphify#graph-model)
*   **Vertices (Nodes)** — Classes, functions, methods, modules, types
*   **Edges** — Dependencies, calls, imports, inheritance
*   **Communities** — Groups of related entities (Leiden algorithm)

### Components

[](https://github.com/tmcqueen/ngraphify#components)
*   `Graphiphy` — Core: extraction, graph building, dedup, clustering, analysis, reporting, caching
*   `Graphiphy.Llm` — LLM integration (MAF 1.5.0 agent, 5 providers)
*   `Graphiphy.Pipeline` — Orchestration (`RepositoryAnalysis.RunAsync`)
*   `Graphiphy.Cli` — Command-line interface and MCP server
*   `Graphiphy.MSBuild` — MSBuild integration targets

## Supported Languages

[](https://github.com/tmcqueen/ngraphify#supported-languages)
Graphiphy extracts and analyzes code in these languages:

| Language | Extensions |
| --- | --- |
| C# | `.cs` |
| Java | `.java` |
| Python | `.py` |
| JavaScript | `.js`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Go | `.go` |
| Rust | `.rs` |
| C++ | `.cpp`, `.cc`, `.h`, `.hpp` |
| C | `.c`, `.h` |

## Troubleshooting

[](https://github.com/tmcqueen/ngraphify#troubleshooting)
### "graphiphy-cli not found"

[](https://github.com/tmcqueen/ngraphify#graphiphy-cli-not-found)
Ensure the tool is installed:

dotnet tool list -g

If not listed, install it:

dotnet tool install -g Graphiphy.Cli

### "Leiden clustering library not found"

[](https://github.com/tmcqueen/ngraphify#leiden-clustering-library-not-found)
Leiden clustering is optional. If the native library is unavailable, analysis continues with a graceful warning. This is non-fatal.

To resolve:

*   Ensure TreeSitter native libraries are present in your `.NET` runtime folder
*   On Linux: `sudo apt-get install tree-sitter`
*   On macOS: `brew install tree-sitter`
*   On Windows: Use the pre-built distribution

### "pass binary not installed" or secret resolution warning

[](https://github.com/tmcqueen/ngraphify#pass-binary-not-installed-or-secret-resolution-warning)
If the `pass` password manager is not installed, the CLI will warn at startup but continue normally. Commands that require secrets (e.g., `query` with LLM provider) will fail with a clear error message only if the secret is actually needed. You can:

1.   Install `pass` if using secret providers: `sudo apt-get install pass` (Linux) or `brew install pass` (macOS)
2.   Provide secrets via environment variables instead: `export ANTHROPIC_API_KEY=sk-ant-...`

### "API key required but not provided"

[](https://github.com/tmcqueen/ngraphify#api-key-required-but-not-provided)
For the `query` command, provide an API key via:

1.   Environment variable: `export ANTHROPIC_API_KEY=...`
2.   Command-line flag: `--key sk-ant-...`
3.   Default fallback: `ANTHROPIC_API_KEY` (Anthropic), `OPENAI_API_KEY` (OpenAI)

### Performance Issues

[](https://github.com/tmcqueen/ngraphify#performance-issues)
*   **First run** — Full extraction uses all available CPU cores for parallel processing. Subsequent runs use cache.
*   **Large repos** — For repos with 1000+ files, incremental builds are faster. Parallel file extraction significantly speeds up analysis of large codebases.
*   **Memory** — Disable Leiden clustering if memory is constrained: set `<GraphiphyEnabled>false</GraphiphyEnabled>` in MSBuild.

### Build Integration Not Running

[](https://github.com/tmcqueen/ngraphify#build-integration-not-running)
1.   Check that source files have been modified since last build:

rm .graphiphy-cache/.msbuild-stamp
dotnet build 
2.   Verify `graphiphy-cli` is installed:

graphiphy-cli analyze . > /dev/null && echo "OK" || echo "Not found" 
3.   Disable and re-enable in the project:

<PropertyGroup>
  <GraphiphyEnabled>true</GraphiphyEnabled>
</PropertyGroup> 

## Documentation

[](https://github.com/tmcqueen/ngraphify#documentation)
*   [MSBuild Integration](https://github.com/tmcqueen/ngraphify/blob/main/docs/MSBuild-Integration.md) — Automate analysis in .NET builds
*   [MCP Configuration](https://github.com/tmcqueen/ngraphify/blob/main/docs/mcp-config.md) — Setup with Claude Desktop
*   [Usage Guide](https://github.com/tmcqueen/ngraphify/blob/main/docs/Usage.md) — Detailed command reference and workflows

## Contributing

[](https://github.com/tmcqueen/ngraphify#contributing)
Contributions are welcome. The codebase follows:

*   .NET conventions (C#, async/await, nullable reference types)
*   TUnit for testing (`tests/` directory)
*   Spectre.Console for CLI output

To build and test:

dotnet build
dotnet test

## License

[](https://github.com/tmcqueen/ngraphify#license)
See [LICENSE](https://github.com/tmcqueen/ngraphify/blob/main/LICENSE) for details.

## About

[](https://github.com/tmcqueen/ngraphify#about)
Graphiphy is a .NET reimplementation of the Python `graphify` project, providing fast, integrated codebase analysis for .NET development workflows.
