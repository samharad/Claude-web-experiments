# AI A/B Test

A web tool for conducting AI-powered A/B comparisons. Use multiple AI models to evaluate two options and visualize the aggregate results.

## Features

- **Multi-model comparison**: Run tests across Claude (Sonnet/Opus), GPT-4o (standard/mini), and Gemini (Pro/Flash)
- **Position bias mitigation**: Automatically randomizes the order of options across queries to eliminate position bias
- **File attachments**: Drag-and-drop support for images, PDFs, and text files
- **Cost tracking**: Shows estimated cost before running and actual cost after completion
- **Visual results**: Bar chart per model and overall pie chart distribution
- **Local API key storage**: Keys stored in browser localStorage, never sent anywhere except the respective AI provider

## Usage

1. Enter text and/or attach files for Option A and Option B
2. Write your evaluation question/criteria
3. Select which AI models to use
4. Set the number of queries per model (default 10)
5. Click "Run Experiment"
6. View results showing preference distribution across models

## API Keys

You'll need API keys from the providers you want to use:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Google**: https://aistudio.google.com/app/apikey

Keys are stored locally in your browser and only sent to their respective API endpoints.

## Position Bias Mitigation

To ensure fair comparison, the tool presents options in both orders:
- Half the queries show "Option A" first, "Option B" second
- Half show "Option B" first, "Option A" second

Responses are mapped back to the original A/B designation for consistent results.

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
