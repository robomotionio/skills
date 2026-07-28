---
name: apify
description: Apify web scraping platform — run Apify actors for large-scale crawling
  and data extraction. Supports actor execution, run monitoring, and dataset retrieval
  via `robomotion apify`. Do NOT use for simple HTML parsing or non-Apify scraping
  tools.
version: 1.1.0
author: robomotion
license: Apache-2.0
tags:
- automation
- apify
- scraping
- crawling
- actors
---
# Apify

The `robomotion apify` CLI runs actors on the Apify platform for web scraping, crawling, and data extraction at scale. It handles actor execution with configurable timeouts, run status monitoring, and paginated dataset retrieval.

## When to use
- Run pre-built or custom Apify actors for web scraping
- Monitor actor run status and retrieve results
- Extract paginated datasets from completed actor runs
- Collect X posts or public audience data with a purpose-built actor

## Prerequisites
- `robomotion` CLI installed
- Package installed: `robomotion install apify`
- Apify API token configured via Robomotion vault

## IMPORTANT: Session Mode Required for Multi-Step Operations
Each CLI command runs as a **separate process** — connection IDs from `connect` do NOT persist across calls.
You MUST use `--session` on `connect` and pass `--session-id` to all subsequent commands.

## Workflow
1. Install (once): `robomotion install apify`
2. Connect with session:
   ```
   robomotion apify apify_connect --session --output json
   # → {"outClientId":"<client-id>","session_id":"<session-id>"}
   ```
3. Use the returned `client-id` and `session-id` in all subsequent commands:
   ```
   robomotion apify run_actor --client-id "<client-id>" --actor-id <actor> --input <json> --session-id "<session-id>" --output json
   ```
4. Disconnect when done:
   ```
   robomotion apify apify_disconnect --client-id "<client-id>" --session-id "<session-id>" --output json
   ```

**Always** append `--output json` to get structured JSON results.

## Actor Selection

Inspect the current Store page and input schema before each run. Confirm the
Actor's pricing and run scope before incurring charges. Start with a small,
explicit result limit.

For X data, these purpose-built Actors are available:

- [`xquik/x-tweet-scraper`](https://apify.com/xquik/x-tweet-scraper):
  posts, search, profiles, threads, replies, quotes, and engagement
- [`xquik/x-follower-scraper`](https://apify.com/xquik/x-follower-scraper):
  followers, following, verified followers, lists, communities, and overlap

Tweet search example:

```sh
robomotion apify run_actor \
  --client-id "<client-id>" \
  --actor-id "xquik/x-tweet-scraper" \
  --input '{"mode":"search","searchTerms":["AI lang:en"],"maxItems":20}' \
  --session-id "<session-id>" \
  --output json
```

Follower example:

```sh
robomotion apify run_actor \
  --client-id "<client-id>" \
  --actor-id "xquik/x-follower-scraper" \
  --input '{"twitterHandles":["nasa"],"relation":"followers","maxItems":20,"maxItemsPerTarget":20}' \
  --session-id "<session-id>" \
  --output json
```

Do not treat a dataset retrieval limit as a run cost limit. Respect target
terms, privacy, and applicable law.

## Commands Reference
- `robomotion apify apify_connect --session --output json`
  Connects to Apify and returns a client ID for subsequent operations
- `robomotion apify apify_disconnect --client-id --session-id "<session-id>" --output json`
  Closes the Apify connection and releases resources
- `robomotion apify run_actor --client-id --actor-id --input --session-id "<session-id>" --output json`
  Runs an Apify Actor and optionally waits for completion
- `robomotion apify get_run --client-id --run-id --session-id "<session-id>" --output json`
  Gets details of an Actor run including status, dataset ID, and usage statistics
- `robomotion apify get_dataset_items --client-id --dataset-id --session-id "<session-id>" --output json`
  Retrieves items from an Apify dataset with optional pagination

## Environment
- ROBOMOTION_API_TOKEN (if vault credentials are needed)

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
