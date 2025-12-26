# Debate Agent REST API

A comprehensive REST API for the AI-powered debate system, providing endpoints for affirmative agents, negative agents, and referee agents.

## Quick Start

### Installation

First, install the required dependencies:

```bash
pip install -r ../requirements.txt
```

### Running the API

Start the API server:

```bash
python debate_api.py
```

Or using uvicorn directly:

```bash
uvicorn debate_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check

#### `GET /`
Root endpoint - API health check

**Response:**
```json
{
  "status": "healthy",
  "message": "Debate Agent API is running",
  "version": "1.0.0"
}
```

#### `GET /health`
Detailed health check endpoint

---

### Topic Generation

#### `POST /api/topics/generate`
Generate both affirmative and negative team options for a debate topic.

**Request Body:**
```json
{
  "topic": "Should artificial intelligence be regulated by governments?"
}
```

**Response:**
```json
{
  "affirmative_option": "Government regulation ensures AI safety...",
  "negative_option": "Free market innovation drives responsible AI...",
  "status": "success"
}
```

#### `POST /api/topics/affirmative`
Generate only the affirmative team option.

**Request Body:**
```json
{
  "topic": "Should artificial intelligence be regulated by governments?"
}
```

**Response:**
```json
{
  "statement": "Government regulation ensures AI safety...",
  "status": "success"
}
```

#### `POST /api/topics/negative`
Generate only the negative team option.

---

### Affirmative Team Endpoints

#### `POST /api/affirmative/statement`
Generate an affirmative team statement.

**Request Body:**
```json
{
  "topic": "Should artificial intelligence be regulated by governments?",
  "aff_options": "Government regulation ensures AI safety and ethical use",
  "neg_options": "Free market innovation drives responsible AI development",
  "affirmative_statements": ["Previous affirmative argument 1", "Previous affirmative argument 2"],
  "negative_statements": ["Previous negative argument 1"],
  "context": "Opening statement"
}
```

**Response:**
```json
{
  "statement": "The affirmative team argues that...",
  "status": "success"
}
```

#### `POST /api/affirmative/rebuttal`
Generate an affirmative team rebuttal.

**Request Body:**
```json
{
  "topic": "Should artificial intelligence be regulated by governments?",
  "opponent_argument": "Market forces naturally regulate AI development",
  "team_position": "Government oversight is essential for public safety"
}
```

**Response:**
```json
{
  "statement": "While market forces play a role, history shows...",
  "status": "success"
}
```

#### `POST /api/affirmative/closing`
Generate an affirmative team closing argument.

**Request Body:**
```json
{
  "topic": "Should artificial intelligence be regulated by governments?",
  "aff_options": "Government regulation ensures AI safety",
  "neg_options": "Free market innovation drives responsible AI",
  "team_statements": ["Argument 1", "Argument 2", "Argument 3"],
  "opponent_statements": ["Counter 1", "Counter 2", "Counter 3"]
}
```

**Response:**
```json
{
  "statement": "In conclusion, we have demonstrated that...",
  "status": "success"
}
```

---

### Negative Team Endpoints

#### `POST /api/negative/statement`
Generate a negative team statement.

**Request Body:**
```json
{
  "topic": "Should artificial intelligence be regulated by governments?",
  "aff_options": "Government regulation ensures AI safety",
  "neg_options": "Free market innovation drives responsible AI development",
  "affirmative_statements": ["Previous affirmative argument 1"],
  "negative_statements": ["Previous negative argument 1", "Previous negative argument 2"],
  "context": "Rebuttal round"
}
```

**Response:**
```json
{
  "statement": "The negative team contends that...",
  "status": "success"
}
```

#### `POST /api/negative/rebuttal`
Generate a negative team rebuttal.

#### `POST /api/negative/closing`
Generate a negative team closing argument.

---

### Referee/Judge Endpoints

#### `POST /api/judge/debate`
Judge a complete debate and return a decision.

**Request Body:**
```json
{
  "topic": "Should artificial intelligence be regulated by governments?",
  "aff_options": "Government regulation ensures AI safety",
  "neg_options": "Free market innovation drives responsible AI",
  "affirmative_statements": [
    "Opening statement from affirmative",
    "Rebuttal from affirmative",
    "Second argument from affirmative"
  ],
  "negative_statements": [
    "Opening statement from negative",
    "Rebuttal from negative",
    "Second argument from negative"
  ],
  "aff_final": "Affirmative closing argument summarizing key points...",
  "neg_final": "Negative closing argument summarizing key points..."
}
```

**Response:**
```json
{
  "result": "{\"winner\": \"affirmative\", \"reason\": \"The affirmative team...\", \"affirmative_score\": 85, \"negative_score\": 78}",
  "status": "success"
}
```

---

### Configuration Endpoints

#### `GET /api/config/temperature`
Get the current temperature setting for AI generation.

**Response:**
```json
{
  "temperature": 0.7
}
```

#### `POST /api/config/temperature`
Set the temperature for AI generation (0.0 to 2.0).

**Request Body:**
```json
{
  "temperature": 0.8
}
```

**Response:**
```json
{
  "message": "Temperature updated successfully",
  "temperature": 0.8
}
```

---

## Example Usage

### Using cURL

```bash
# Generate debate topics
curl -X POST "http://localhost:8000/api/topics/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Should social media be regulated?"}'

# Generate affirmative statement
curl -X POST "http://localhost:8000/api/affirmative/statement" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Should social media be regulated?",
    "aff_options": "Regulation protects users from harm",
    "neg_options": "Free speech should not be restricted",
    "affirmative_statements": [],
    "negative_statements": [],
    "context": "Opening statement"
  }'

# Judge a debate
curl -X POST "http://localhost:8000/api/judge/debate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Should social media be regulated?",
    "aff_options": "Regulation protects users",
    "neg_options": "Free speech is paramount",
    "affirmative_statements": ["Statement 1", "Statement 2"],
    "negative_statements": ["Counter 1", "Counter 2"],
    "aff_final": "Final affirmative argument",
    "neg_final": "Final negative argument"
  }'
```

### Using Python Requests

```python
import requests

API_BASE = "http://localhost:8000"

# Generate topics
response = requests.post(
    f"{API_BASE}/api/topics/generate",
    json={"topic": "Should AI be regulated?"}
)
topics = response.json()
print(f"Affirmative: {topics['affirmative_option']}")
print(f"Negative: {topics['negative_option']}")

# Generate affirmative statement
response = requests.post(
    f"{API_BASE}/api/affirmative/statement",
    json={
        "topic": "Should AI be regulated?",
        "aff_options": topics['affirmative_option'],
        "neg_options": topics['negative_option'],
        "affirmative_statements": [],
        "negative_statements": [],
        "context": "Opening statement"
    }
)
statement = response.json()
print(f"Statement: {statement['statement']}")
```

### Using JavaScript/Fetch

```javascript
// Generate topics
const response = await fetch('http://localhost:8000/api/topics/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    topic: 'Should AI be regulated?'
  })
});

const topics = await response.json();
console.log('Affirmative:', topics.affirmative_option);
console.log('Negative:', topics.negative_option);

// Generate affirmative statement
const statementResponse = await fetch('http://localhost:8000/api/affirmative/statement', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    topic: 'Should AI be regulated?',
    aff_options: topics.affirmative_option,
    neg_options: topics.negative_option,
    affirmative_statements: [],
    negative_statements: [],
    context: 'Opening statement'
  })
});

const statement = await statementResponse.json();
console.log('Statement:', statement.statement);
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# API Server Configuration (optional)
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input parameters
- `500 Internal Server Error`: Server-side error

Error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## CORS Configuration

The API is configured to accept requests from any origin (`*`). For production use, update the CORS settings in `debate_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Development

### Auto-reload

The API runs with auto-reload enabled by default during development. Any changes to the code will automatically restart the server.

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: Visit `http://localhost:8000/docs` to test endpoints interactively
- **ReDoc**: Visit `http://localhost:8000/redoc` for alternative documentation

### Testing

You can test all endpoints directly from the Swagger UI at `/docs` without writing any code.

---

## Production Deployment

For production deployment, consider:

1. **Use a production ASGI server** (uvicorn with workers or gunicorn)
2. **Set up proper CORS** restrictions
3. **Add authentication** if needed
4. **Use environment variables** for configuration
5. **Set up logging** and monitoring
6. **Use HTTPS** with proper SSL certificates

Example production command:

```bash
uvicorn debate_api:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## License

Same as the main DebateAgent project.
