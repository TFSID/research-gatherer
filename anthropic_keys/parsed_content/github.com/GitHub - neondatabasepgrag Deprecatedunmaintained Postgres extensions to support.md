---
source: https://github.com/neondatabase/pgrag
parsed_date: 2026-06-27 01:28:27
domain: github.com
---

Title: GitHub - neondatabase/pgrag: Deprecated/unmaintained Postgres extensions to support end-to-end Retrieval-Augmented Generation (RAG) pipelines

URL Source: https://github.com/neondatabase/pgrag

Markdown Content:
## pgrag —~~EXPERIMENTAL~~ DEPRECATED

[](https://github.com/neondatabase/pgrag#pgrag-experimental-deprecated)
**Please note: these extensions are no longer developed or maintained.**

Experimental Postgres extensions to support end-to-end Retrieval-Augmented Generation (RAG) pipelines.

These currently provide:

### Text extraction and conversion

[](https://github.com/neondatabase/pgrag#text-extraction-and-conversion)
*   Simple text extraction from PDF documents (using [pdf-extract](https://github.com/jrmuizel/pdf-extract)). Currently no OCR and no support for complex layout or formatting.

*   Simple text extraction from .docx documents (using [docx-rs](https://github.com/cstkingkey/docx-rs)).

*   HTML conversion to Markdown (using [htmd](https://github.com/letmutex/htmd)).

### Text chunking

[](https://github.com/neondatabase/pgrag#text-chunking)
*   Text chunking by character count (using [text-splitter](https://github.com/benbrandt/text-splitter)).

*   Text chunking by token count (also using [text-splitter](https://github.com/benbrandt/text-splitter)).

### Local embedding and reranking models

[](https://github.com/neondatabase/pgrag#local-embedding-and-reranking-models)
These models run locally on the Postgres server's CPU or GPU. They are packaged as separate extensions, because they are large (>100MB) and because we may want to add others in future.

*   Local tokenising + embedding generation with 33M parameter model [bge-small-en-v1.5](https://huggingface.co/Xenova/bge-small-en-v1.5) (using [ort](https://github.com/pykeio/ort) via [fastembed](https://github.com/Anush008/fastembed-rs)).

*   Local tokenising + reranking with 33M parameter model [jina-reranker-v1-tiny-en](https://huggingface.co/jinaai/jina-reranker-v1-tiny-en) (also using [ort](https://github.com/pykeio/ort) via [fastembed](https://github.com/Anush008/fastembed-rs)).

### Remote embedding and chat models

[](https://github.com/neondatabase/pgrag#remote-embedding-and-chat-models)
The extension calls out to these models over HTTPS/JSON APIs.

*   OpenAI API for embeddings (e.g. `text-embedding-3-small`) and chat completions (e.g. `gpt-4o-mini`).

*   Anthropic API for chat completions (e.g. `claude-3-haiku-20240307`).

*   Fireworks.ai API for embeddings (e.g. `nomic-ai/nomic-embed-text-v1.5`) and chat completions (e.g. `llama-v3p1-8b-instruct`).

*   Voyage AI API for embeddings (e.g. `voyage-multilingual-2`) and reranking (e.g. `rerank-2-lite`).

## Installation

[](https://github.com/neondatabase/pgrag#installation)
First, you'll need to install `pgvector`. For example:

wget https://github.com/pgvector/pgvector/archive/refs/tags/v0.7.4.tar.gz -O pgvector-0.7.4.tar.gz
tar xzf pgvector-0.7.4.tar.gz
cd pgvector-0.7.4
export PG_CONFIG=/path/to/pg_config  # not just a path: should actually end with `pg_config`
make
make install  #may need sudo

Next, download the extensions source, and (if you are building the embedding or reranking extensions with baked-in model data) extract the relevant model files:

cd lib/bge_small_en_v15 && tar xzf model.onnx.tar.gz && cd ../..
cd lib/jina_reranker_v1_tiny_en && tar xzf model.onnx.tar.gz && cd ../..

Then (with up-to-date Rust installed):

cargo install --locked cargo-pgrx@0.14.1

Finally, inside each of the three folders inside `exts`:

PG_CONFIG=/path/to/pg_config cargo pgrx install --release

The extension has been tested on Linux and macOS. pgrx does not currently support Windows.

### Embedding and reranking extensions

[](https://github.com/neondatabase/pgrag#embedding-and-reranking-extensions)
#### Background worker process

[](https://github.com/neondatabase/pgrag#background-worker-process)
To avoid requiring excessive memory when reranking or generating embeddings in multiple Postgres processes, each of these tasks is done by a multi-threaded background worker (the worker is started when Postgres starts, but the models are lazy-loaded on first use).

For `rag_bge_small_en_v15` and `rag_jina_reranker_v1_tiny_en`, you'll therefore need to edit `postgresql.conf` to add a `shared_preload_libraries` configuration:

```
shared_preload_libraries = 'rag_bge_small_en_v15.so,rag_jina_reranker_v1_tiny_en.so'
```

On macOS, replace `.so` with `.dylib` in these library names.

When using `cargo pgrx run` with Postgres instances installed by pgrx, `postgresql.conf` is located in `~/.pgrx/data-N` (where N is the relevant Postgres version).

When using `cargo pgrx test`, `postgresql.conf` is inside the `target` directory of your extension, e.g. `~/path/to/myext/target/test-pgdata/N` (where N is the relevant Postgres version).

#### ORT and ONNX installation

[](https://github.com/neondatabase/pgrag#ort-and-onnx-installation)
The `ort` and `ort-sys` crates are currently supplied in patched form in `vendor`, otherwise `ort` and `ort-sys` versions end up mismatched, and that leads to build failures. We stick at `2.0.0-rc.4` (by keeping `fastembed` at `=3.14.1`) because this is the last version using the ONNX Runtime at `1.18`, and `1.19` has build problems on some platforms at the time of writing.

The `ort` package supplies precompiled binaries for the ONNX runtime (currently v1.18). On some platforms, this may give rise to `undefined symbol` errors. In that case, you'll need to compile the ONNX runtime yourself and provide the build location to `cargo pgrx install` in the `ORT_LIB_LOCATION` environment variable. An example for Ubuntu 24.04 is provided in [COMPILE.sh](https://github.com/neondatabase/pgrag/blob/main/COMPILE.sh).

#### Remote ONNX model file

[](https://github.com/neondatabase/pgrag#remote-onnx-model-file)
By default, the embedding and reranking model data are embedded within the extension, using Rust's `include_bytes!()` macro. Alternatively, it's possible to have the `.onnx` files downloaded on first use (since the last Postgres restart). This is enabled by the `remote_onnx` crate feature, and the download URL is specified via the `REMOTE_ONNX_URL` build-time environment variable. For example:

REMOTE_ONNX_URL=http://example.com/path/model.onnx cargo pgrx install --release --features remote_onnx

The `REMOTE_ONNX_URL` variable defaults to a HuggingFace URL, but it is strongly recommended to change this to a location you control.

## Usage

[](https://github.com/neondatabase/pgrag#usage)

create extension if not exists rag cascade;
create extension if not exists rag_bge_small_en_v15 cascade; 
create extension if not exists rag_jina_reranker_v1_tiny_en cascade; 

The three extensions have no dependencies on each other, but all are dependent on pgvector. Specify `cascade` to ensure pgvector is installed alongside them.

#### `markdown_from_html(text) -> text`

[](https://github.com/neondatabase/pgrag#markdown_from_htmltext---text)
Locally convert HTML to Markdown:

select rag.markdown_from_html('<html><body><h1>Title</h1><p>A <i>very</i> short paragraph</p><p>Another paragraph</p></body></html>');
-- '# Title\n\nA _very_ short paragraph\n\nAnother paragraph'

#### `text_from_pdf(bytea) -> text`

[](https://github.com/neondatabase/pgrag#text_from_pdfbytea---text)
Locally extract text from a PDF:

\set contents `base64 < /path/to/your.pdf`
select rag.text_from_pdf(decode(:'contents', 'base64'));
-- 'Text content of PDF'

#### `text_from_docx(bytea) -> text`

[](https://github.com/neondatabase/pgrag#text_from_docxbytea---text)
Locally extract text from a .docx file:

\set contents `base64 < /path/to/your.docx`
select rag.text_from_docx(decode(:'contents', 'base64'));
-- 'Text content of .docx'

#### `chunks_by_character_count(text, max_characters integer, max_overlap_characters integer) -> text[]`

[](https://github.com/neondatabase/pgrag#chunks_by_character_counttext-max_characters-integer-max_overlap_characters-integer---text)
Locally chunk text using character count, with max and overlap:

select rag.chunks_by_character_count('The quick brown fox jumps over the lazy dog', 20, 4);
-- {"The quick brown fox","fox jumps over the","the lazy dog"}

#### `chunks_by_token_count(text, max_tokens integer, max_overlap_tokens integer) -> text[]`

[](https://github.com/neondatabase/pgrag#chunks_by_token_counttext-max_tokens-integer-max_overlap_tokens-integer---text)
Locally chunk text using token count for specific embedding model, with max and overlap:

select rag_bge_small_en_v15.chunks_by_token_count('The quick brown fox jumps over the lazy dog', 4, 1);
-- {"The quick brown fox","fox jumps over the","the lazy dog"}

#### `embedding_for_passage(text) -> vector(384)`

[](https://github.com/neondatabase/pgrag#embedding_for_passagetext---vector384)
#### `embedding_for_query(text) -> vector(384)`

[](https://github.com/neondatabase/pgrag#embedding_for_querytext---vector384)
Locally tokenize + generate embeddings using a small (33M param) model:

select rag_bge_small_en_v15.embedding_for_passage('The quick brown fox jumps over the lazy dog');
-- [-0.1047543,-0.02242211,-0.0126493685, ...]
select rag_bge_small_en_v15.embedding_for_query('What did the quick brown fox jump over?');
-- [-0.09328926,-0.030567117,-0.027558783, ...]

#### `rerank_score(text, text) -> real`

[](https://github.com/neondatabase/pgrag#rerank_scoretext-text---real)
#### `rerank_score(text, text[]) -> real[]`

[](https://github.com/neondatabase/pgrag#rerank_scoretext-text---real-1)
#### `rerank_distance(text, text) -> real`

[](https://github.com/neondatabase/pgrag#rerank_distancetext-text---real)
#### `rerank_distance(text, text[]) -> real[]`

[](https://github.com/neondatabase/pgrag#rerank_distancetext-text---real-1)
Locally tokenize + calculate reranking scores for original texts using a small (33M param) model.

In each case `distance` is equal to `-score`. If multiple texts are provided in the second argument, scores or distances are returned in matching order.

select rag_jina_reranker_v1_tiny_en.rerank_distance('The quick brown fox jumps over the lazy dog', 'What did the quick brown fox jump over?');
-- -1.1093962

select rag_jina_reranker_v1_tiny_en.rerank_distance('The quick brown fox jumps over the lazy dog', 'Never Eat Shredded Wheat');
-- 1.4725753

#### `openai_set_api_key(text)`

[](https://github.com/neondatabase/pgrag#openai_set_api_keytext)
#### `openai_get_api_key() -> text`

[](https://github.com/neondatabase/pgrag#openai_get_api_key---text)
Store and retrieve your OpenAI API key:

select rag.openai_set_api_key('sk-proj-...');
select rag.openai_get_api_key();
-- 'sk-proj-...'

#### `openai_text_embedding(model text, text) -> vector`

[](https://github.com/neondatabase/pgrag#openai_text_embeddingmodel-text-text---vector)
#### `openai_text_embedding_3_small(text) -> vector(1536)`

[](https://github.com/neondatabase/pgrag#openai_text_embedding_3_smalltext---vector1536)
#### `openai_text_embedding_3_large(text) -> vector(3072)`

[](https://github.com/neondatabase/pgrag#openai_text_embedding_3_largetext---vector3072)
#### `openai_text_embedding_ada_002(text) -> vector(1536)`

[](https://github.com/neondatabase/pgrag#openai_text_embedding_ada_002text---vector1536)
Call out to OpenAI embeddings API (making network request):

select rag.openai_text_embedding_3_small('The quick brown fox jumps over the lazy dog');
-- [-0.020836005,-0.016921125,-0.00450666, ...]

#### `openai_chat_completion(json) -> json`

[](https://github.com/neondatabase/pgrag#openai_chat_completionjson---json)
Call out to OpenAI chat/completions API (making network request):

select rag.openai_chat_completion('{
 "model": "gpt-4o-mini",
 "messages":[
 {"role": "system", "content": "you are a helpful assistant"},
 {"role": "user", "content": "hi!"}
 ]
}'::json);
-- {"id": "chatcmpl-...", "model": "gpt-4o-mini-2024-07-18", "usage": {"total_tokens": 27, "prompt_tokens": 18, "completion_tokens": 9}, "object": "chat.completion", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello! How can I assist you today?", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "created": 1724765541, "system_fingerprint": "fp_..."}

#### `anthropic_set_api_key(text)`

[](https://github.com/neondatabase/pgrag#anthropic_set_api_keytext)
#### `anthropic_get_api_key() -> text`

[](https://github.com/neondatabase/pgrag#anthropic_get_api_key---text)
Store and retrieve your Anthropic API key:

select rag.anthropic_set_api_key('sk-ant-api...');
select rag.anthropic_get_api_key();
-- 'sk-ant-api...'

#### `anthropic_messages(version text, body json) -> json`

[](https://github.com/neondatabase/pgrag#anthropic_messagesversion-text-body-json---json)
Call out to Anthropic messages (i.e. chat/completions) API (making network request):

select rag.anthropic_messages('2023-06-01', '{
 "model": "claude-3-haiku-20240307",
 "max_tokens": 64,
 "system": "you are a helpful assistant",
 "messages":[
 {
 "role": "user",
 "content": "hi!"
 }
 ]
}'::json);
-- {"content":[{"text":"Hello! How can I assist you today?","type":"text"}],"id":"msg_...","model":"claude-3-haiku-20240307","role":"assistant","stop_reason":"end_turn","stop_sequence":null,"type":"message","usage":{"input_tokens":14,"output_tokens":19}}

#### `fireworks_set_api_key(text)`

[](https://github.com/neondatabase/pgrag#fireworks_set_api_keytext)
#### `fireworks_get_api_key() -> text`

[](https://github.com/neondatabase/pgrag#fireworks_get_api_key---text)
Store and retrieve your Fireworks.ai API key:

select rag.fireworks_set_api_key('fw_...');
select rag.fireworks_get_api_key();
-- 'fw_...'

#### `fireworks_nomic_embed_text_v15(text) -> vector(768)`

[](https://github.com/neondatabase/pgrag#fireworks_nomic_embed_text_v15text---vector768)
#### `fireworks_nomic_embed_text_v1(text) -> vector(768)`

[](https://github.com/neondatabase/pgrag#fireworks_nomic_embed_text_v1text---vector768)
#### `fireworks_text_embedding_whereisai_uae_large_v1(text) -> vector(1024)`

[](https://github.com/neondatabase/pgrag#fireworks_text_embedding_whereisai_uae_large_v1text---vector1024)
#### `fireworks_text_embedding_thenlper_gte_large(text) -> vector(1024)`

[](https://github.com/neondatabase/pgrag#fireworks_text_embedding_thenlper_gte_largetext---vector1024)
#### `fireworks_text_embedding_thenlper_gte_base(text) -> vector(768)`

[](https://github.com/neondatabase/pgrag#fireworks_text_embedding_thenlper_gte_basetext---vector768)
#### `fireworks_text_embedding(model text, input text) -> vector`

[](https://github.com/neondatabase/pgrag#fireworks_text_embeddingmodel-text-input-text---vector)
Call out to Fireworks.ai embeddings API (making network request):

select rag.fireworks_nomic_embed_text_v15('The quick brown fox jumps over the lazy dog');
-- [-0.012481689,0.026031494,-0.15270996, ...]

#### `fireworks_chat_completion(json) -> json`

[](https://github.com/neondatabase/pgrag#fireworks_chat_completionjson---json)
Call out to Fireworks.ai chat/completions API (makes network request):

select rag.fireworks_chat_completion('{
 "model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
 "messages":[
 {"role": "system", "content": "you are a helpful assistant"},
 {"role": "user", "content": "hi!"}
 ]
}'::json);
-- {"choices":[{"finish_reason":"stop","index":0,"message":{"content":"Hi! How can I assist you today?","role":"assistant"}}],"created":1725362940,"id":"...","model":"accounts/fireworks/models/llama-v3p1-8b-instruct","object":"chat.completion","usage":{"completion_tokens":10,"prompt_tokens":23,"total_tokens":33}}

#### `voyageai_set_api_key(text)`

[](https://github.com/neondatabase/pgrag#voyageai_set_api_keytext)
#### `voyageai_get_api_key() -> text`

[](https://github.com/neondatabase/pgrag#voyageai_get_api_key---text)
Store and retrieve your Voyage AI API key:

select rag.voyageai_set_api_key('pa-...');
select rag.voyageai_get_api_key();
-- 'pa-...'

#### `voyageai_embedding(model text, input_type, text) -> vector`

[](https://github.com/neondatabase/pgrag#voyageai_embeddingmodel-text-input_type-text---vector)
#### `voyageai_embedding_3(input_type, text) -> vector(1024)`

[](https://github.com/neondatabase/pgrag#voyageai_embedding_3input_type-text---vector1024)
#### `voyageai_embedding_3_lite(input_type, text) -> vector(512)`

[](https://github.com/neondatabase/pgrag#voyageai_embedding_3_liteinput_type-text---vector512)
#### `voyageai_embedding_code_2(input_type, text) -> vector(1536)`

[](https://github.com/neondatabase/pgrag#voyageai_embedding_code_2input_type-text---vector1536)
#### `voyageai_embedding_finance_2(input_type, text) -> vector(1024)`

[](https://github.com/neondatabase/pgrag#voyageai_embedding_finance_2input_type-text---vector1024)
#### `voyageai_embedding_law_2(input_type, text) -> vector(1024)`

[](https://github.com/neondatabase/pgrag#voyageai_embedding_law_2input_type-text---vector1024)
#### `voyageai_embedding_multilingual_2(input_type, text) -> vector(1024)`

[](https://github.com/neondatabase/pgrag#voyageai_embedding_multilingual_2input_type-text---vector1024)
Call out to Voyage AI embeddings API (making network request).

`input_type` may be `'query'` or `'document'` (or `NULL`):

select rag.voyageai_embedding_3_lite('document', 'the cat sat on the mat');
-- [-0.033761546,0.01360899,0.0832813, ...]

#### `voyageai_rerank_score(model text, query text, document text) -> real`

[](https://github.com/neondatabase/pgrag#voyageai_rerank_scoremodel-text-query-text-document-text---real)
#### `voyageai_rerank_score(model text, query text, documents text[]) -> real[]`

[](https://github.com/neondatabase/pgrag#voyageai_rerank_scoremodel-text-query-text-documents-text---real)
#### `voyageai_rerank_distance(model text, query text, document text) -> real`

[](https://github.com/neondatabase/pgrag#voyageai_rerank_distancemodel-text-query-text-document-text---real)
#### `voyageai_rerank_distance(model text, query text, documents text[]) -> real[]`

[](https://github.com/neondatabase/pgrag#voyageai_rerank_distancemodel-text-query-text-documents-text---real)
Call out to Voyage AI reranking model (making network request).

In each case `distance` is equal to `-score`. If multiple texts are provided in the second argument, scores or distances are returned in matching order.

select rag.voyageai_rerank_distance('rerank-2-lite', 'the cat sat on the mat', ARRAY['the baboon played with the balloon', 'how much wood would a woodchuck chuck?']);
-- {-0.5,-0.4609375}

## End-to-end RAG example

[](https://github.com/neondatabase/pgrag#end-to-end-rag-example)
Setup: create a `docs` table and ingest some PDF documents as text.

drop table docs cascade;
create table docs
( id int primary key generated always as identity
, name text not null
, fulltext text not null
);

\set contents `base64 < /path/to/first.pdf`
insert into docs (name, fulltext)
values ('first.pdf', rag.text_from_pdf(decode(:'contents','base64')));

\set contents `base64 < /path/to/second.pdf`
insert into docs (name, fulltext)
values ('second.pdf', rag.text_from_pdf(decode(:'contents','base64')));

\set contents `base64 < /path/to/third.pdf`
insert into docs (name, fulltext)
values ('third.pdf', rag.text_from_pdf(decode(:'contents','base64'))));

Now we create an `embeddings` table, chunk the text, and generate embeddings for the chunks (this is all done locally).

drop table embeddings;
create table embeddings
( id int primary key generated always as identity
, doc_id int not null references docs(id)
, chunk text not null
, embedding vector(384) not null
);

create index on embeddings using hnsw (embedding vector_cosine_ops);

with chunks as (
  select id, unnest(rag_bge_small_en_v15.chunks_by_token_count(fulltext, 192, 8)) as chunk
  from docs
)
insert into embeddings (doc_id, chunk, embedding) (
  select id, chunk, rag_bge_small_en_v15.embedding_for_passage(chunk) from chunks
);

Let's query the embeddings and rerank the results (still all done locally).

\set query 'what is [...]? how does it work?'

with ranked as (
  select
    id, doc_id, chunk, embedding <=> rag_bge_small_en_v15.embedding_for_query(:'query') as cosine_distance
  from embeddings
  order by cosine_distance
  limit 10
)
select *, rag_jina_reranker_v1_tiny_en.rerank_distance(:'query', chunk)
from ranked
order by rerank_distance;

Building on that, now we can also feed the query and top chunks to remote ChatGPT to complete the RAG pipeline.

\set query 'what is [...]? how does it work?'

with ranked as (
  select
    id, doc_id, chunk, embedding <=> rag_bge_small_en_v15.embedding_for_query(:'query') as cosine_distance
  from embeddings
  order by cosine_distance limit 10
),
reranked as (
  select *, rag_jina_reranker_v1_tiny_en.rerank_distance(:'query', chunk)
  from ranked
  order by rerank_distance limit 5
)
select rag.openai_chat_completion(json_object(
  'model': 'gpt-4o-mini',
  'messages': json_array(
    json_object(
      'role': 'system',
      'content': E'The user is [...].\n\n Try to answer the user''s QUESTION using only the provided CONTEXT.\n\n The CONTEXT represents extracts from [...] which have been selected as most relevant to this question.\n\n If the context is not relevant or complete enough to confidently answer the question, your best response is: "I''m afraid I don''t have the information to answer that question".'
    ),
    json_object(
      'role': 'user',
      'content': E'# CONTEXT\n\n```\n' || string_agg(chunk, E'\n\n') || E'\n```\n\n# QUESTION\n\n```\n' || :'query' || E'```'
    )
  )
)) -> 'choices' -> 0 -> 'message' -> 'content' as answer
from reranked;

## License

[](https://github.com/neondatabase/pgrag#license)
This software is released under the [Apache 2.0 license](https://github.com/neondatabase/pgrag/blob/main/LICENSE). Third-party code and data are provided under their respective licenses.
