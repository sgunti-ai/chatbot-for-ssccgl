# Frontend Integration Summary

## Changes Made

### 1. **API Service Update** (`frontend/src/services/api.js`)
- ✅ Added `parseText(text)` export
- Calls `POST /parse-text` with raw text
- Returns response data with shape: `{ status, questions[], total }`

### 2. **New Hook** (`frontend/src/hooks/useParseAPI.js`)
- ✅ Created React hook for parse endpoint consumption
- Provides: `parseText`, `loading`, `error`, `results`, `clearResults`
- Mirrors the existing `useSSCAPI` hook pattern for consistency
- Handles loading/error states automatically

### 3. **API Schema Documentation** (`frontend/src/API_SCHEMA.md`)
- ✅ Documents the new `/parse-text` endpoint
- Shows request/response examples
- Details the `ParseTextResponse` and `ParsedQuestion` schemas
- Includes hook usage examples
- Compares `/parse-text` vs `/query` endpoints

## Usage Example

```javascript
import { useParseAPI } from '../hooks/useParseAPI';

export const TextParserComponent = () => {
  const { parseText, loading, error, results } = useParseAPI();
  const [textInput, setTextInput] = useState('');

  const handleParse = async () => {
    await parseText(textInput);
  };

  if (loading) return <div>Parsing...</div>;
  if (error) return <div>Error: {error}</div>;
  if (results) {
    return (
      <div>
        <p>Extracted {results.total} questions</p>
        {results.questions.map(q => (
          <div key={q.question_id}>
            <p><strong>{q.text}</strong></p>
            <ul>
              {q.options.map((opt, i) => (
                <li key={i}>{opt}</li>
              ))}
            </ul>
            <p>Answer: {q.correct_answer}</p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <textarea 
      value={textInput}
      onChange={e => setTextInput(e.target.value)}
      placeholder="Paste question text here..."
    />
  );
};
```

## Response Schema

### ParseTextResponse (HTTP 200)
```json
{
  "status": "success",
  "questions": [
    {
      "question_id": "q_abc123...",
      "text": "Question text",
      "options": ["option1", "option2", ...],
      "correct_answer": "option1",
      "subject": "Quantitative"
    }
  ],
  "total": 1
}
```

## Backend Verification

The `/parse-text` endpoint in `backend/app/main.py`:
- ✅ Returns `ParseTextResponse` model
- ✅ Has OpenAPI schema documented
- ✅ Includes explicit responses decorator
- ✅ Passes all unit tests (3/3)
- ✅ Passes quality gates (flake8: 0 errors, pytest: all passing)

## Frontend Compatibility

- ✅ Service layer updated to expose `parseText()`
- ✅ Hook layer provides React integration pattern
- ✅ Uses same error handling as existing hooks
- ✅ Consistent with frontend architecture

## Next Steps (Optional)

1. **Create a parse component**: Build a new React component that uses `useParseAPI` for text parsing UI
2. **Add to UploadPanel**: Integrate text parsing into the upload workflow
3. **Add tests**: Create Jest tests for the new hook
4. **Update UploadPanel.jsx**: Can now optionally use `/parse-text` for fast text parsing without ML
