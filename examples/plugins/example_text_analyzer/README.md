# Text Analyzer Plugin

Advanced text analysis with NLP capabilities for comprehensive document insights.

## Features

- **Statistics** - Word count, character count, readability metrics
- **Keyword Extraction** - Identify most important terms
- **Sentiment Analysis** - Detect positive/negative/neutral sentiment
- **Readability Scores** - Flesch Reading Ease, grade level
- **Pattern Detection** - Find emails, URLs, phone numbers, dates

## Usage

### Basic Analysis

```python
result = await plugin.process(text_file, context)
# Returns statistics, keywords, and sentiment
```

### Custom Operations

```python
result = await plugin.process(
    text_file,
    context,
    operations=['stats', 'keywords', 'sentiment', 'readability', 'patterns']
)
```

## Output Example

```json
{
  "success": true,
  "statistics": {
    "words": 1523,
    "unique_words": 487,
    "sentences": 89,
    "paragraphs": 12,
    "lexical_diversity": "32.00%",
    "avg_word_length": "4.73",
    "avg_words_per_sentence": "17.11"
  },
  "keywords": {
    "top_keywords": [
      {"word": "processing", "count": 45},
      {"word": "file", "count": 38},
      {"word": "system", "count": 27}
    ]
  },
  "sentiment": {
    "sentiment": "positive",
    "score": "0.35",
    "positive_words": 12,
    "negative_words": 3
  },
  "readability": {
    "flesch_reading_ease": "67.3",
    "difficulty": "Standard",
    "grade_level": "8.2"
  }
}
```

## Configuration

```json
{
  "min_word_length": 3,
  "top_keywords": 10
}
```

## Supported Formats

- `.txt` - Plain text
- `.md` - Markdown
- `.log` - Log files
- `.csv` - CSV (text analysis)
- `.json` - JSON (text content)

## Use Cases

1. **Document Analysis** - Understand document complexity
2. **Content Review** - Assess readability for target audience
3. **SEO Optimization** - Extract keywords
4. **Sentiment Monitoring** - Track document sentiment
5. **Data Extraction** - Find patterns (emails, URLs, dates)

## License

MIT
