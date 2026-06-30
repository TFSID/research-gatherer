---
source: https://github.com/olafurjohannsson/kjarni
parsed_date: 2026-06-27 01:28:28
domain: github.com
---

Title: GitHub - olafurjohannsson/kjarni: Native and Private ML inference engine, embeddings, classification, reranking, search, and text generation. Rust core with C# bindings. No Python, no ONNX, no CUDA.

URL Source: https://github.com/olafurjohannsson/kjarni

Markdown Content:
A native library for running machine learning models.

Kjarni compiles to a single shared library and runs locally, without Python, containers, external services, or GPU requirements. It also ships as a command-line tool that reads from stdin, writes JSON, and pipes like any UNIX tool.

C# bindings are available via [NuGet](https://www.nuget.org/packages/Kjarni). Go bindings are available at [kjarni-go](https://github.com/olafurjohannsson/kjarni-go). The CLI is available as a [binary download](https://github.com/olafurjohannsson/kjarni/releases).

The name is Icelandic [ˈkʰjartnɪ]. It means "core."

## Install

[](https://github.com/olafurjohannsson/kjarni#install)
**C# / .NET:**

dotnet add package Kjarni

**Go:**

go get github.com/olafurjohannsson/kjarni-go@latest

**CLI (Linux x64):**

curl -fsSL https://kjarni.ai/install.sh | sh

## Quick Start

[](https://github.com/olafurjohannsson/kjarni#quick-start)
**C#:**

using Kjarni;

using var classifier = new Classifier("distilbert-sentiment");
Console.WriteLine(classifier.Classify("I love this product!"));
// POSITIVE (100.0%)

**Go:**

import "github.com/olafurjohannsson/kjarni-go"

c, _ := kjarni.NewClassifier("distilbert-sentiment")
defer c.Close()

result, _ := c.Classify("I love this product!")
fmt.Printf("%s: %.1f%%\n", result.Label, result.Score*100)
// POSITIVE: 100.0%

**CLI:**

$ kjarni classify "I love this product!"
  ✓       POSITIVE  ████████████████████  100.0%
          NEGATIVE  ░░░░░░░░░░░░░░░░░░░░    0.0%

$ echo "Terrible quality" | kjarni classify
  ✓       NEGATIVE  ████████████████████  100.0%
          POSITIVE  ░░░░░░░░░░░░░░░░░░░░    0.0%

Models download on first use and are cached locally. No setup or configuration required.

## CLI

[](https://github.com/olafurjohannsson/kjarni#cli)
The CLI supports the same capabilities as the C# and Go libraries. It reads from arguments or stdin, and outputs human-readable tables or JSON.

# Sentiment analysis
$ kjarni classify "Best purchase ever"
  ✓       POSITIVE  ████████████████████  100.0%
          NEGATIVE  ░░░░░░░░░░░░░░░░░░░░    0.0%

# Toxicity detection
$ kjarni classify "You are the worst cook ever" --model toxic-bert
  ✓          toxic  ███████████████████░   92.8%
            insult  ██████████████░░░░░░   72.3%
           obscene  ██░░░░░░░░░░░░░░░░░░    7.6%
     identity_hate  ░░░░░░░░░░░░░░░░░░░░    0.5%
      severe_toxic  ░░░░░░░░░░░░░░░░░░░░    0.3%

# Pipe from stdin
$ echo "I hate mondays" | kjarni classify
  ✓       NEGATIVE  ████████████████████  100.0%
          POSITIVE  ░░░░░░░░░░░░░░░░░░░░    0.0%

# JSON output for scripting
$ echo "Great service" | kjarni classify --format json | jq '.label'
"POSITIVE"

# Semantic similarity
$ kjarni similarity "doctor" "physician"
  █████████████████░░░   86.0%  highly similar
  ↔ "doctor"
  ↔ "physician"

# Index a folder and search it
$ kjarni index create my-docs docs/*
✓ Indexed 15 documents (39.52 KB)

$ kjarni search my-docs "keeping data safe" --top-k 3
  1. cryptocraphy.txt
     ████████████████████  100.0%
     "Symmetric and asymmetric cryptography protect digital communications by…"

  2. tcpip.txt
     ██████████░░░░░░░░░░   49.2%
     "TCP/IP is a layered protocol suite that enables reliable data transmiss…"

  3. neuralnetworks.txt
     ░░░░░░░░░░░░░░░░░░░░    0.0%
     "Neural networks consist of interconnected layers of artificial neurons …"

# Search with reranking
$ kjarni search my-docs "keeping data safe" --top-k 3 --rerank-model minilm-l6-v2-cross-encoder

# Generate embeddings
$ kjarni embed "hello world" --format json | head -n 5
{
  "dim": 384,
  "embedding": [
    0.17644444,
    0.03936597,

## Examples

[](https://github.com/olafurjohannsson/kjarni#examples)
### Sentiment Analysis

[](https://github.com/olafurjohannsson/kjarni#sentiment-analysis)
**C#:**

using var classifier = new Classifier("distilbert-sentiment");
Console.WriteLine(classifier.Classify("Best purchase I've ever made!"));
// POSITIVE (100.0%)

**Go:**

c, _ := kjarni.NewClassifier("distilbert-sentiment")
defer c.Close()

result, _ := c.Classify("Best purchase I've ever made!")
fmt.Printf("%s: %.1f%%\n", result.Label, result.Score*100)
// POSITIVE: 100.0%

### Toxicity Detection

[](https://github.com/olafurjohannsson/kjarni#toxicity-detection)
**C#:**

using var classifier = new Classifier("toxic-bert");
Console.WriteLine(classifier.Classify("You are an idiot").ToDetailedString());

**Go:**

c, _ := kjarni.NewClassifier("toxic-bert")
defer c.Close()

result, _ := c.Classify("You are an idiot")
for _, s := range result.AllScores {
    fmt.Printf(" %s: %.2f%%\n", s.Label, s.Score*100)
}

```
✓          toxic  ███████████████████░   92.8%
            insult  ██████████████░░░░░░   72.3%
           obscene  ██░░░░░░░░░░░░░░░░░░    7.6%
     identity_hate  ░░░░░░░░░░░░░░░░░░░░    0.5%
      severe_toxic  ░░░░░░░░░░░░░░░░░░░░    0.3%
```

### Embeddings

[](https://github.com/olafurjohannsson/kjarni#embeddings)
**C#:**

using var embedder = new Embedder("minilm-l6-v2");
float[] vector = embedder.Encode("Hello world");
Console.WriteLine(string.Join(", ", vector[..5]));
// -0.034477282, 0.03102318, 0.006734989, 0.02610899, -0.03936202

**Go:**

e, _ := kjarni.NewEmbedder("minilm-l6-v2")
defer e.Close()

vector, _ := e.Embed("Hello world")
fmt.Printf("Dimensions: %d\n", len(vector))
fmt.Printf("First 5: %v\n", vector[:5])

### Semantic Similarity

[](https://github.com/olafurjohannsson/kjarni#semantic-similarity)
**C#:**

using var embedder = new Embedder("minilm-l6-v2");
Console.WriteLine(embedder.Similarity("doctor", "physician"));
// 0.8598132

**Go:**

e, _ := kjarni.NewEmbedder("minilm-l6-v2")
defer e.Close()

sim, _ := e.Similarity("doctor", "physician")
fmt.Printf("Similarity: %.1f%%\n", sim*100)
// Similarity: 86.0%

### Index & Search

[](https://github.com/olafurjohannsson/kjarni#index--search)
**C#:**

using var indexer = new Indexer(model: "minilm-l6-v2", quiet: true);
indexer.Create("my_index", new[] { "docs/" });

using var searcher = new Searcher(
    model: "minilm-l6-v2",
    rerankerModel: "minilm-l6-v2-cross-encoder");

var results = searcher.Search("my_index", "how do returns work?",
    mode: SearchMode.Hybrid);

foreach (var r in results)
    Console.WriteLine($" {r.Score:F4}: {r.Text}");

**Go:**

idx, _ := kjarni.NewIndexer("minilm-l6-v2")
defer idx.Close()
idx.Create("./my-index", []string{"./docs"})

s, _ := kjarni.NewSearcher("minilm-l6-v2", "minilm-l6-v2-cross-encoder")
defer s.Close()
results, _ := s.Search("./my-index", "how do returns work?", kjarni.Hybrid)

for _, r := range results {
    fmt.Printf("%.3f: %s\n", r.Score, r.Text)
}

Search modes: `Semantic` (vector similarity), `Keyword` (BM25), `Hybrid` (both).

## Models

[](https://github.com/olafurjohannsson/kjarni#models)
| Task | Model | Size |
| --- | --- | --- |
| Sentiment (3-class) | `roberta-sentiment` | 125MB |
| Sentiment (multilingual) | `bert-sentiment-multilingual` | 168MB |
| Sentiment (binary) | `distilbert-sentiment` | 66MB |
| Emotion (7-class) | `distilroberta-emotion` | 82MB |
| Emotion (28-class) | `roberta-emotions` | 125MB |
| Toxicity | `toxic-bert` | 110MB |
| Embeddings | `minilm-l6-v2` | 90MB |
| Embeddings | `mpnet-base-v2` | 420MB |
| Reranking | `minilm-l6-v2-cross-encoder` | 90MB |

Models download on first use. The engine also supports Llama, Qwen2, Mistral, Phi-3, T5, BART, and Whisper.

Bindings and APIs for these models are intentionally not exposed in the initial release and will ship in a future version.

## Configuration

[](https://github.com/olafurjohannsson/kjarni#configuration)
### Cache Directory

[](https://github.com/olafurjohannsson/kjarni#cache-directory)
Default locations:

*   **Linux:**`~/.cache/kjarni`
*   **Windows:**`%LOCALAPPDATA%\kjarni`

Override with `KJARNI_CACHE_DIR` or the constructor parameter:

using var embedder = new Embedder("minilm-l6-v2", cacheDir: "/my/models");

### HuggingFace Token

[](https://github.com/olafurjohannsson/kjarni#huggingface-token)
For gated models:

export HF_TOKEN=hf_your_token_here

### Quiet Mode

[](https://github.com/olafurjohannsson/kjarni#quiet-mode)

using var embedder = new Embedder("minilm-l6-v2", quiet: true);

## Platform Support

[](https://github.com/olafurjohannsson/kjarni#platform-support)
| Platform | CPU | GPU |
| --- | --- | --- |
| Linux x64 | Yes | Yes (Vulkan) |
| Windows x64 | Yes | Yes (DX12/Vulkan) |
| macOS ARM64 | Planned | Planned (Metal) |

GPU inference uses WebGPU. CUDA is not required.

using var embedder = new Embedder("minilm-l6-v2", device: "gpu");

## How It Works

[](https://github.com/olafurjohannsson/kjarni#how-it-works)
Kjarni does not wrap ONNX, LibTorch, or any external inference engine. The runtime is written in Rust. The only system dependency is glibc 2.17.

*   Hand-tuned SIMD kernels (AVX2/FMA, NEON)
*   Custom WGSL compute shaders for GPU
*   Zero-copy model loading via mmap
*   BF16 compute path
*   Quantization: Q4, Q6, Q8

## Why

[](https://github.com/olafurjohannsson/kjarni#why)
Adding machine learning to an application usually means Python, CUDA, containers, or an external service. Kjarni is a single `.so` or `.dll` that runs as part of your application, with predictable behavior and no external infrastructure.

## Project Structure

[](https://github.com/olafurjohannsson/kjarni#project-structure)

```
crates/
├── kjarni/              # High-level API
├── kjarni-transformers/  # Engine — models, kernels, GPU shaders
├── kjarni-ffi/          # C ABI + language bindings
│   └── bindings/
│       ├── csharp/      # NuGet package
│       └── go/          # Go module (published to kjarni-go)
├── kjarni-cli/          # Command-line tool
└── kjarni-examples/     # Rust examples
```

The Go module is auto-published from this monorepo to [kjarni-go](https://github.com/olafurjohannsson/kjarni-go) via CI.

## Building from Source

[](https://github.com/olafurjohannsson/kjarni#building-from-source)

cargo build --release -p kjarni-ffi
cargo build --release -p kjarni-cli
cargo test

## License

[](https://github.com/olafurjohannsson/kjarni#license)
MIT or Apache-2.0, at your option.
