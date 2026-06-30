---
source: https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode
parsed_date: 2026-06-27 01:29:22
domain: github.com
---

Title: GitHub - JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode: A Semantic Kernel connector that bridges your local Claude Code OAuth session into Microsoft Semantic Kernel — no manual API key management needed.

URL Source: https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode

Markdown Content:
[![Image 1: NuGet](https://camo.githubusercontent.com/4dab51884c4716f8ba2c2dff1a7649a5fbae438ac241002a384a85c161b1f068/68747470733a2f2f696d672e736869656c64732e696f2f6e756765742f762f4a442e53656d616e7469634b65726e656c2e436f6e6e6563746f72732e436c61756465436f64652e737667)](https://www.nuget.org/packages/JD.SemanticKernel.Connectors.ClaudeCode)[![Image 2: NuGet Downloads](https://camo.githubusercontent.com/70e141cfa8a482af46999ac8703c4a20e7d4d0221ed766f6912fae113c5e2865/68747470733a2f2f696d672e736869656c64732e696f2f6e756765742f64742f4a442e53656d616e7469634b65726e656c2e436f6e6e6563746f72732e436c61756465436f64652e737667)](https://www.nuget.org/packages/JD.SemanticKernel.Connectors.ClaudeCode)[![Image 3: CI](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/actions/workflows/ci.yml/badge.svg)](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/actions/workflows/ci.yml)[![Image 4: CodeQL](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/actions/workflows/codeql-analysis.yml)[![Image 5: codecov](https://camo.githubusercontent.com/eed7bed19dc085cae9a9bc034acb941548047d5c244c2ae11ca35f4683ffa840/68747470733a2f2f636f6465636f762e696f2f67682f4a65727265747444617669732f4a442e53656d616e7469634b65726e656c2e436f6e6e6563746f72732e436c61756465436f64652f67726170682f62616467652e737667)](https://codecov.io/gh/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode)[![Image 6: License: MIT](https://camo.githubusercontent.com/fdf2982b9f5d7489dcf44570e714e3a15fce6253e0cc6b5aa61a075aac2ff71b/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d79656c6c6f772e737667)](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/LICENSE)

A **Semantic Kernel connector** for Anthropic models with API-key-first authentication and optional local Claude Code OAuth support.

## Features

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#features)
*   **API-key-first authentication** — supports `sk-ant-api*` via options or `ANTHROPIC_API_KEY`
*   **Optional local OAuth support** — `sk-ant-oat*` is opt-in and interactive-only
*   **Multi-source credential resolution** — options/env API key first, then local OAuth sources
*   **Full Semantic Kernel integration** — `IKernelBuilder.UseClaudeCodeChatCompletion()` one-liner
*   **DI-friendly** — `IServiceCollection.AddClaudeCodeAuthentication()` for ASP.NET Core / Generic Host
*   **Broad TFM support** — `netstandard2.0`, `net8.0`, `net10.0`

## Compliance Defaults

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#compliance-defaults)
*   OAuth token support is **disabled by default**.
*   OAuth usage requires `EnableOAuthTokenSupport = true` and an interactive session.
*   Unattended or automated OAuth workflows are intentionally blocked.
*   For service, CI, or unattended usage, use Anthropic API keys (`sk-ant-api*`).
*   Anthropic Consumer Terms (effective October 8, 2025) apply to consumer-service usage: [https://www.anthropic.com/legal/consumer-terms](https://www.anthropic.com/legal/consumer-terms)
*   Anthropic API keys are governed by Anthropic Commercial Terms: [https://www.anthropic.com/legal/commercial-terms](https://www.anthropic.com/legal/commercial-terms)

## Quick Start

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#quick-start)
### Install

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#install)

dotnet add package JD.SemanticKernel.Connectors.ClaudeCode

### Kernel Builder (Recommended)

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#kernel-builder-recommended)

using JD.SemanticKernel.Connectors.ClaudeCode;

var builder = Kernel.CreateBuilder();
builder.UseClaudeCodeChatCompletion(apiKey: "sk-ant-api..."); // defaults to ClaudeModels.Default (Sonnet)
var kernel = builder.Build();

var result = await kernel.InvokePromptAsync("Hello, Claude!");
Console.WriteLine(result);

### Service Collection (ASP.NET Core)

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#service-collection-aspnet-core)

builder.Services.AddClaudeCodeAuthentication(options =>
{
    options.CredentialsPath = "/custom/path/.credentials.json"; // optional
    options.EnableOAuthTokenSupport = true; // only for local interactive OAuth use
});

### Configuration Binding

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#configuration-binding)

{
  "ClaudeSession": {
    "ApiKey": null,
    "OAuthToken": null,
    "EnableOAuthTokenSupport": false,
    "CredentialsPath": null
  }
}

builder.Services.AddClaudeCodeAuthentication(builder.Configuration);

## Credential Resolution Order

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#credential-resolution-order)
| Priority | Source | Description |
| --- | --- | --- |
| 1 | `ClaudeSession:ApiKey` | Explicit API key in options/config |
| 2 | `ANTHROPIC_API_KEY` env var | Environment variable |
| 3 | `ClaudeSession:OAuthToken` | Explicit OAuth token (requires `EnableOAuthTokenSupport = true`) |
| 4 | `~/.claude/.credentials.json` | Local Claude Code session (requires `EnableOAuthTokenSupport = true`) |

## Sample CLI Tools

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#sample-cli-tools)
[![Image 7: CLI tools demo](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/raw/main/docs/images/cli-help.png)](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/images/cli-help.png)

This repo includes sample projects demonstrating agentic workflows with Semantic Kernel:

| Tool | Command | Description |
| --- | --- | --- |
| **Gherkin Generator** | `jdgerkinator` | Converts acceptance criteria into Gherkin/Reqnroll specs |
| **PR Review Agent** | `jdpr` | Multi-provider PR review (GitHub, Azure DevOps, GitLab) |
| **Codebase Explorer** | `jdxplr` | Profiles codebases into structured knowledgebases |
| **Todo Extractor** | _(library demo)_ | Extracts structured todos from natural language |

Install the CLI tools as global tools:

dotnet tool install -g JD.Tools.GherkinGenerator
dotnet tool install -g JD.Tools.PullRequestReviewer
dotnet tool install -g JD.Tools.CodebaseExplorer

## Models

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#models)
Well-known model constants are available via `ClaudeModels`:

builder.UseClaudeCodeChatCompletion(ClaudeModels.Opus);   // claude-opus-4-6
builder.UseClaudeCodeChatCompletion(ClaudeModels.Sonnet);  // claude-sonnet-4-6 (default)
builder.UseClaudeCodeChatCompletion(ClaudeModels.Haiku);   // claude-haiku-4-5

## Documentation

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#documentation)
Full documentation is available at the [DocFX site](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs) including:

*   [Getting Started](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/articles/getting-started.md)
*   [Credential Resolution](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/articles/credential-resolution.md)
*   [Kernel Builder Integration](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/articles/kernel-builder-integration.md)
*   [Service Collection Integration](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/articles/service-collection-integration.md)
*   [HttpClientFactory](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/articles/http-client-factory.md)
*   [Configuration Reference](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/articles/configuration-reference.md)
*   [Sample Tools Guide](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/docs/samples/index.md)

## Building

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#building)

dotnet build
dotnet test

### Build Documentation

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#build-documentation)

cd docs
dotnet tool restore
dotnet docfx docfx.json

## Shared Abstractions

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#shared-abstractions)
This connector implements the **JD.SemanticKernel.Connectors.Abstractions** interfaces, enabling multi-provider bridging:

| Interface | Implementation |
| --- | --- |
| `ISessionProvider` | `ClaudeCodeSessionProvider` — credential resolution with `IsAuthenticatedAsync()` |
| `IModelDiscoveryProvider` | `ClaudeModelDiscovery` — returns known Claude model catalogue |
| `SessionOptionsBase` | `ClaudeCodeSessionOptions` — inherits `DangerouslyDisableSslValidation`, `CustomEndpoint` |

Use the same abstractions across providers:

ISessionProvider provider = isClaudeCode
    ? claudeCodeProvider
    : copilotProvider;

var creds = await provider.GetCredentialsAsync();

### Related Projects

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#related-projects)
*   **[JD.SemanticKernel.Connectors.GitHubCopilot](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.GitHubCopilot)** — Same pattern for GitHub Copilot subscriptions
*   **[JD.SemanticKernel.Extensions](https://github.com/JerrettDavis/JD.SemanticKernel.Extensions)** — SK extensions for skills, hooks, plugins, compaction, and semantic memory

## License

[](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode#license)
[MIT](https://github.com/JerrettDavis/JD.SemanticKernel.Connectors.ClaudeCode/blob/main/LICENSE)
