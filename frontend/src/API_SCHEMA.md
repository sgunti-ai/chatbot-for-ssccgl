# Frontend API Integration Guide

## Parse Text Endpoint (`/parse-text`)

The `/parse-text` endpoint extracts questions from raw text and returns a structured response.

### Request
```javascript
POST /parse-text
Content-Type: application/json

{
  "text": "Section : Quantitative\nQ.1 What is 2+2?\n1. 3\n2. 4\nAns 2"
}
```

### Response (`ParseTextResponse`)
```json
{
  "status": "success",
  "questions": [
    {
      "question_id": "q_abc123...",
      "text": "What is 2+2?",
      "options": ["3", "4"],
      "correct_answer": "4",
      "subject": "Quantitative"
    }
  ],
  "total": 1
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | "success" or "error" |
| `questions` | `ParsedQuestion[]` | Extracted questions |
| `total` | `number` | Total questions extracted |

### ParsedQuestion Fields

| Field | Type | Description |
|-------|------|-------------|
| `question_id` | `string` | Unique ID (format: `q_<hash>`) |
| `text` | `string` | Question text |
| `options` | `string[]` | Answer options |
| `correct_answer` | `string` | Correct answer (may be null) |
| `subject` | `string` | Subject category |

## Frontend Hook: `useParseAPI`

```javascript
import { useParseAPI } from '../hooks/useParseAPI';

export const MyComponent = () => {
  const { parseText, loading, error, results, clearResults } = useParseAPI();

  const handleParse = async (textContent) => {
    const response = await parseText(textContent);
    if (response) {
      console.log(`Extracted ${response.total} questions`);
      console.log(response.questions);
    }
  };

  return (
    <div>
      <button onClick={() => handleParse(myText)}>Parse</button>
      {loading && <p>Parsing...</p>}
      {error && <p>Error: {error}</p>}
      {results && <p>Found {results.total} questions</p>}
    </div>
  );
};
```

## Difference from `/query` Endpoint

| Aspect | `/query` | `/parse-text` |
|--------|---------|---------------|
| Purpose | Semantic search | Text parsing |
| Requires DB | Yes (ChromaDB) | No |
| ML Model | Uses embeddings | Regex-based |
| Input | Question/keyword | Raw text |
| Output | Matching questions | Extracted questions |
| Use Case | Find similar questions | Extract from PDF/text |

## Notes

- **Debug Mode**: Set `SSC_DEBUG=1` environment variable to enable debug logging
- **Parsing**: Uses regex heuristics to split text into question blocks
- **Question IDs**: Automatically generated using MD5 hash of question text
- **Subjects**: Extracted from text sections (e.g., "Section : Quantitative" → "Quantitative")
