---
source: https://github.com/kcaldas/genie
parsed_date: 2026-06-27 01:31:37
domain: github.com
---

Title: GitHub - kcaldas/genie: 🧞 Powerful AI assistant for your command line - Built with Go and Gemini AI

URL Source: https://github.com/kcaldas/genie

Markdown Content:
[![Image 1: Go Version](https://camo.githubusercontent.com/6342720489483aacc0024e551fafe10b8808df34847ea759ebf3375b0c8b87f5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f676f2d312e32332b2d626c75652e737667)](https://golang.org/)[![Image 2: License: MIT](https://camo.githubusercontent.com/fdf2982b9f5d7489dcf44570e714e3a15fce6253e0cc6b5aa61a075aac2ff71b/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d79656c6c6f772e737667)](https://opensource.org/licenses/MIT)[![Image 3: Docker](https://camo.githubusercontent.com/9b20b6131e402a89533d97d464e35a6948e0b0ab798b91b1c31a119c6cfbc7e0/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f636b65722d72656164792d627269676874677265656e2e737667)](https://github.com/kcaldas/genie/pkgs/container/genie)[![Image 4: Beta](https://camo.githubusercontent.com/716bfc39105776d292464f3d0a131e324a87c2ef5a038742f6447fceb8d5e378/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f7374617475732d626574612d6f72616e67652e737667)](https://github.com/kcaldas/genie/releases)

Transform your terminal into an AI-powered workspace. Born from a developer's need for control and transparency in AI assistance.

Quick demo:

[![Image 5: asciicast](https://camo.githubusercontent.com/d614342f2e9d6a473820ee1562d5bec94cd14fd69e452fedf174a76da8f903d0/68747470733a2f2f61736369696e656d612e6f72672f612f61734d59494c376956727045636b3243654c4149337350714e2e737667)](https://asciinema.org/a/asMYIL7iVrpEck2CeLAI3sPqN)

Theming demo: [![Image 6: asciicast](https://camo.githubusercontent.com/604ad8ed486a9da63f9a062b1ea253e57af8349fe5bffd1e10466b170ca80404/68747470733a2f2f61736369696e656d612e6f72672f612f526c5836764f67685752325a496147306765764147354376702e737667)](https://asciinema.org/a/RlX6vOghWR2ZIaG0gevAG5Cvp)

## 🚀 Quick Start

[](https://github.com/kcaldas/genie#-quick-start)
### Installation

[](https://github.com/kcaldas/genie#installation)
#### macOS (Homebrew)

[](https://github.com/kcaldas/genie#macos-homebrew)

brew tap kcaldas/genie
brew install genie

#### Direct Download

[](https://github.com/kcaldas/genie#direct-download)

# Download latest release
curl -L https://github.com/kcaldas/genie/releases/latest/download/genie_$(uname -s)_$(uname -m).tar.gz | tar xz
sudo mv genie /usr/local/bin/

#### Docker

[](https://github.com/kcaldas/genie#docker)

docker run --rm -it ghcr.io/kcaldas/genie:latest

#### Build from Source

[](https://github.com/kcaldas/genie#build-from-source)

go install github.com/kcaldas/genie/cmd/genie@latest

### Configuration

[](https://github.com/kcaldas/genie#configuration)
Genie ships with Gemini enabled by default. To get started:

1.   Generate a key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2.   Set it as an environment variable:

export GEMINI_API_KEY="YOUR_API_KEY"
genie ask "hello world"              # CLI mode
git diff | genie ask "commit msg?"   # Unix pipes
genie                                # Interactive TUI mode

> **💡 Tip:** The Gemini API provides 100 free requests per day with Gemini 2.5 Pro. Upgrade to a paid plan for higher rate limits.

Prefer OpenAI? Switch providers with two environment variables:

export GENIE_LLM_PROVIDER="openai"
export OPENAI_API_KEY="sk-your-api-key"
genie ask "summarize README.md"

Optionally set `OPENAI_BASE_URL` or `OPENAI_ORG_ID` if you use a custom endpoint.

Prefer Anthropic? Use the Claude models instead:

export GENIE_LLM_PROVIDER="anthropic"
export ANTHROPIC_API_KEY="sk-ant-api-key"
genie ask "explain retrieval augmented generation"

Set `ANTHROPIC_SHOW_THINKING=true` if you want Claude's thinking blocks streamed as notifications.

**📖 Full setup guide:**[docs/INSTALLATION.md](https://github.com/kcaldas/genie/blob/main/docs/INSTALLATION.md)

## 🎭 Personas

[](https://github.com/kcaldas/genie#-personas)
Genie supports different personas for specialized tasks:

# Use specific personas
genie --persona engineer ask "review this code"
genie --persona product-owner ask "plan this feature"

Each persona can pin its own `model_name` and `llm_provider` inside `prompt.yaml`, while `GENIE_MODEL_NAME` and `GENIE_LLM_PROVIDER` remain global fallbacks.

**📖 Learn more:**[docs/personas.md](https://github.com/kcaldas/genie/blob/main/docs/personas.md)

## 💡 Philosophy

[](https://github.com/kcaldas/genie#-philosophy)
Inspired by [Lazygit](https://github.com/jesseduffield/lazygit), [Claude Code](https://claude.ai/code), and [Aider](https://github.com/paul-gauthier/aider), and built for the Unix philosophy: composable, transparent, and adaptable.

**Core beliefs:**

*   **Give you control** - Understand what's happening, not just trust a black box, and is infinitely hackable
*   **Integrate naturally** - Work with your existing tools, don't replace them
*   **Respect the terminal** - Embrace the power and flexibility of the command line
*   **Stay composable** - Pipe, redirect, script, and automate freely

Whether you're coding, managing projects, taking notes, or automating workflows, Genie adapts to your needs.

## 📚 Documentation

[](https://github.com/kcaldas/genie#-documentation)
*   **[Installation & Setup](https://github.com/kcaldas/genie/blob/main/docs/INSTALLATION.md)** - Complete installation guide
*   **[TUI Guide](https://github.com/kcaldas/genie/blob/main/docs/TUI.md)** - Interactive interface features
*   **[CLI Usage](https://github.com/kcaldas/genie/blob/main/docs/CLI.md)** - Command line examples
*   **[Configuration](https://github.com/kcaldas/genie/blob/main/docs/CONFIGURATION.md)** - Customization options
*   **[Personas](https://github.com/kcaldas/genie/blob/main/docs/personas.md)** - AI personality system
*   **[Docker Usage](https://github.com/kcaldas/genie/blob/main/docs/DOCKER.md)** - Container setup
*   **[Architecture](https://github.com/kcaldas/genie/blob/main/docs/ARCHITECTURE.md)** - How Genie works
*   **[Contributing](https://github.com/kcaldas/genie/blob/main/CONTRIBUTING.md)** - Join the project

## 🔗 Ecosystem

[](https://github.com/kcaldas/genie#-ecosystem)
*   [kcaldas/genie.nvim](https://github.com/kcaldas/genie.nvim) - Neovim companion plugin

## 🙏 Acknowledgments

[](https://github.com/kcaldas/genie#-acknowledgments)
Built with [Google Gemini AI](https://ai.google.dev/) • [gocui](https://github.com/awesome-gocui/gocui) • [GoReleaser](https://goreleaser.com/)

* * *

Made with ❤️ for developers who love the command line
