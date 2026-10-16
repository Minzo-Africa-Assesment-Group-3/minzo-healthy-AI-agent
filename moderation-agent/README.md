# Review Moderation API

AI-powered moderation service for healthcare reviews.

The service uses FastAPI, LangChain, and OpenAI to determine whether a healthcare review is acceptable, abusive, or spam.

## Endpoint

### POST `/moderate`

Request:

```json
{
  "comment": "The doctor was professional and explained everything clearly."
}
```

## Successful response

### Allowed review

```json
{
  "allowed": true,
  "category": "allowed",
  "reason": "The review is respectful and relevant.",
  "suggestion": ""
}
```

### Abusive review

```json
{
  "allowed": false,
  "category": "abusive",
  "reason": "The review contains abusive or harassing language.",
  "suggestion": "Please rewrite your review using respectful language."
}
```

### Spam

```json
{
  "allowed": false,
  "category": "spam",
  "reason": "The review contains promotional or spam content.",
  "suggestion": "Please remove promotional content and describe your healthcare experience."
}
```

## Validation

The `comment` field:

- Cannot be empty.
- Must contain at least 1 character.
- Cannot exceed 2,000 characters.

Invalid requests return HTTP `422`.

## Service errors

If the moderation/AI service is unavailable, the API returns:

```json
{
  "detail": "The moderation service is temporarily unavailable. Please try again later."
}
```

with HTTP status `503`.

Internal OpenAI or application errors are not exposed to users.

## Integration flow

The Node.js backend should call this service before saving a review.

```text
User submits review
        ↓
Node.js backend
        ↓
POST /moderate
        ↓
Moderation API
        ↓
allowed?
   /          \
 yes           no
  ↓             ↓
Save review   Return suggestion
```

If `allowed` is `true`, the Node.js backend can save the review.

If `allowed` is `false`, the Node.js backend should not save the review and should return the `suggestion` to the user.

## Local development

Start the FastAPI service with:

```bash
uvicorn app.main:app --reload
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Run tests with:

```bash
pytest
```


## Local Setup

### Prerequisites

Make sure Python 3.10+ is installed.

You can check your Python version with:

```bash
python --version
```

### 1. Navigate to the moderation agent

From the project root:

```bash
cd moderation-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows (Git Bash):**

```bash
source venv/Scripts/activate
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

Once activated, you should see `(venv)` at the beginning of your terminal prompt.

### 4. Install the dependencies

All required Python packages are listed in `requirements.txt`.

Run:

```bash
pip install -r requirements.txt
```

This installs the dependencies required by the moderation service, including:

- FastAPI
- Uvicorn
- LangChain
- LangChain OpenAI integration
- Pydantic
- Python dotenv

### 5. Configure the environment variables

Create a `.env` file inside the `moderation-agent` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your OpenAI API key.

**Do not commit the `.env` file to Git.** It is already included in `.gitignore`.

### 6. Start the API

From the `moderation-agent` directory:

```bash
uvicorn app.main:app --reload
```

The API should now be available at:

```text
http://127.0.0.1:8000
```

### 7. Open the API documentation

FastAPI automatically provides interactive documentation at:

```text
http://127.0.0.1:8000/docs
```

You can use the `/moderate` endpoint from the Swagger interface to test the API.

### 8. Run the tests

Install the test dependency if it is not already included in `requirements.txt`:

```bash
pip install pytest
```

Then run:

```bash
pytest
```

The tests mock the AI moderation function, so they can run without making OpenAI API calls.

### Quick Setup

For someone who already has Python installed, the basic setup is:

```bash
cd moderation-agent
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Then create `.env`, add the `OPENAI_API_KEY`, and start the server:

```bash
uvicorn app.main:app --reload
```