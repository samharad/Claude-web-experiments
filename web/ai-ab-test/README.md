# AI A/B Test

A web tool for conducting AI-powered A/B comparisons. Use multiple AI models to evaluate two options and visualize the aggregate results.

## Features

### Multi-Model Comparison
- **Claude** (Anthropic): Sonnet 4, Opus 4
- **GPT** (OpenAI): GPT-4o, GPT-4o Mini
- **Gemini** (Google): 2.5 Pro, 2.0 Flash

### Input Options
- Text input for each option
- File attachments via drag-and-drop (images, PDFs, text files)
- Custom evaluation question/criteria

### Position Bias Mitigation
Half of queries present Option A first, half present Option B first. The content is swapped under the labels to test if models have position bias. Results are mapped back to the original options.

### Reasoning & Rationales
Models provide brief reasoning (2-3 sentences) before their final answer. Click on the result boxes (Option A, Option B, Refused) to view all rationales for that choice in a modal.

### Execution
- Parallel execution across providers (Anthropic, OpenAI, Google run simultaneously)
- Sequential within each provider to respect rate limits
- Automatic retry with exponential backoff on rate limit errors (2s, 4s, 8s, 16s, 32s)
- Cancel button to abort running experiments

### Cost Tracking
- Estimated cost shown before running
- Actual cost displayed after completion
- Based on current API pricing per 1M tokens

### Results Visualization
- Summary boxes showing total A/B/Refused counts
- Bar chart comparing results across models
- Pie chart showing overall distribution
- Click any summary box to see the reasoning behind those choices

### Experiment History
- Automatically saves completed experiments to localStorage
- Side panel shows past experiments with date, question preview, and results
- Click to restore any previous experiment (inputs, results, rationales)
- Delete individual experiments or clear all history
- Keeps last 50 experiments

### API Key Management
- Keys stored locally in browser localStorage
- Never sent anywhere except respective API endpoints
- Links to get API keys from each provider
- Set/clear keys from the UI

## Usage

1. Enter text and/or attach files for Option A and Option B
2. Write your evaluation question/criteria
3. Select which AI models to use (collapsible section)
4. Set the number of queries per model (default 10)
5. Click "Run Experiment"
6. View results and click result boxes to see rationales
7. Access past experiments from the history panel

## API Keys

You'll need API keys from the providers you want to use:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Google**: https://aistudio.google.com/app/apikey

## Supported File Types

- **Images**: PNG, JPG, GIF, WebP (all providers)
- **PDFs**: Supported by Claude and Gemini; OpenAI support varies
- **Text files**: .txt, .md, .json, .csv

## Cost Estimates

Approximate pricing per 1M tokens (as of early 2025):

| Model | Input | Output |
|-------|-------|--------|
| Claude Sonnet 4 | $3 | $15 |
| Claude Opus 4 | $15 | $75 |
| GPT-4o | $2.50 | $10 |
| GPT-4o-mini | $0.15 | $0.60 |
| Gemini 2.5 Pro | $1.25 | $10 |
| Gemini 2.0 Flash | $0.10 | $0.40 |

## Technical Notes

- Single HTML file with inline CSS/JS
- Uses Chart.js for visualizations (loaded from CDN)
- All data stored in browser localStorage
- No server-side component - API calls made directly from browser
