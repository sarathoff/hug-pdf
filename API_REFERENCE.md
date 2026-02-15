# HugPDF API Reference

Complete API documentation for programmatic PDF generation.

## Base URL

```
https://your-backend-url.com/api
```

## Authentication

All API requests require authentication using an API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Generate PDF

Generate a PDF document from a text prompt.

**Endpoint:** `POST /v1/generate`

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body:**

```json
{
  "prompt": "Create a professional resume for John Doe",
  "mode": "normal"
}
```

**Parameters:**

| Parameter | Type   | Required | Description                                                          |
| --------- | ------ | -------- | -------------------------------------------------------------------- |
| `prompt`  | string | Yes      | Text description of the PDF to generate                              |
| `mode`    | string | No       | Generation mode: `normal`, `research`, or `ebook`. Default: `normal` |

**Response:**

Returns a PDF file (binary) with the following headers:

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="document_20260215_123456.pdf"
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 2026-02-15T12:35:00Z
```

**Example Request (cURL):**

```bash
curl -X POST https://your-backend-url.com/api/v1/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a professional resume for John Doe", "mode": "normal"}' \
  --output document.pdf
```

**Example Request (Python):**

```python
import requests

response = requests.post(
    "https://your-backend-url.com/api/v1/generate",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "prompt": "Create a professional resume for John Doe",
        "mode": "normal"
    }
)

if response.status_code == 200:
    with open("document.pdf", "wb") as f:
        f.write(response.content)
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

---

### Create API Key

Generate a new API key for your account.

**Endpoint:** `POST /v1/keys`

**Headers:**

```
Authorization: Bearer SUPABASE_JWT_TOKEN
Content-Type: application/json
```

**Request Body:**

```json
{
  "name": "My Application",
  "tier": "free"
}
```

**Parameters:**

| Parameter | Type   | Required | Description                                  |
| --------- | ------ | -------- | -------------------------------------------- |
| `name`    | string | Yes      | Friendly name for the API key                |
| `tier`    | string | No       | Tier level: `free` or `pro`. Default: `free` |

**Response:**

```json
{
  "success": true,
  "api_key": "pdf_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "key_id": "uuid",
  "name": "My Application",
  "tier": "free",
  "prefix": "pdf_live_xxxxxxxx..."
}
```

> **Important:** The `api_key` field is only shown once. Save it immediately!

---

### List API Keys

Get all API keys for your account.

**Endpoint:** `GET /v1/keys`

**Headers:**

```
Authorization: Bearer SUPABASE_JWT_TOKEN
```

**Response:**

```json
{
  "keys": [
    {
      "id": "uuid",
      "name": "My Application",
      "key_prefix": "pdf_live_xxxxxxxx...",
      "tier": "free",
      "is_active": true,
      "created_at": "2026-02-15T12:00:00Z",
      "last_used_at": "2026-02-15T12:30:00Z",
      "requests_count": 42,
      "requests_limit": 1000
    }
  ]
}
```

---

### Revoke API Key

Revoke an API key.

**Endpoint:** `DELETE /v1/keys/{key_id}`

**Headers:**

```
Authorization: Bearer SUPABASE_JWT_TOKEN
```

**Response:**

```json
{
  "success": true,
  "message": "API key revoked"
}
```

---

## Generation Modes

### Normal Mode

Standard PDF generation for documents up to 5 pages.

**Use cases:**

- Resumes
- Invoices
- Letters
- Forms
- Certificates

**Example:**

```json
{
  "prompt": "Create a professional invoice for ABC Company for $1,500",
  "mode": "normal"
}
```

### Research Mode

Generate research papers with citations and references.

**Use cases:**

- Academic papers
- Research reports
- Literature reviews
- Technical documentation

**Features:**

- Web research integration
- Automatic citations
- Bibliography generation
- 10-15 pages

**Example:**

```json
{
  "prompt": "Write a research paper on the impact of AI on healthcare",
  "mode": "research"
}
```

### E-book Mode

Generate long-form content (20+ pages).

**Use cases:**

- E-books
- Guides
- Manuals
- Tutorials
- Comprehensive reports

**Features:**

- Chapter organization
- Table of contents
- Images integration
- 20-50 pages

**Example:**

```json
{
  "prompt": "Create an e-book about Python programming for beginners",
  "mode": "ebook"
}
```

---

## Rate Limits

### Free Tier

- **10 requests per minute**
- **1,000 requests per month**
- Access to normal mode only

### Pro Tier

- **100 requests per minute**
- **10,000 requests per month**
- Access to all modes

### Rate Limit Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 2026-02-15T12:35:00Z
```

### Handling Rate Limits

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

**Best practices:**

- Monitor the `X-RateLimit-Remaining` header
- Implement exponential backoff
- Cache responses when possible
- Upgrade to Pro tier for higher limits

---

## Error Codes

| Status Code | Description                                   |
| ----------- | --------------------------------------------- |
| `200`       | Success - PDF generated                       |
| `400`       | Bad Request - Invalid parameters              |
| `401`       | Unauthorized - Invalid or missing API key     |
| `429`       | Too Many Requests - Rate limit exceeded       |
| `500`       | Internal Server Error - PDF generation failed |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

#### 401 Unauthorized

```json
{
  "detail": "Invalid or inactive API key"
}
```

**Solution:** Check your API key is correct and hasn't been revoked.

#### 400 Bad Request

```json
{
  "detail": "Missing 'prompt' in request body"
}
```

**Solution:** Ensure all required parameters are included.

#### 429 Rate Limit Exceeded

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

**Solution:** Wait for the rate limit to reset or upgrade your tier.

#### 500 Internal Server Error

```json
{
  "detail": "PDF generation failed: LaTeX compilation error"
}
```

**Solution:** Simplify your prompt or contact support.

---

## Best Practices

### Security

1. **Never expose API keys**
   - Don't commit to version control
   - Use environment variables
   - Rotate keys regularly

2. **Use HTTPS only**
   - All API requests must use HTTPS
   - Never send keys over HTTP

3. **Validate input**
   - Sanitize user input
   - Set length limits
   - Prevent injection attacks

### Performance

1. **Cache responses**
   - Cache generated PDFs when possible
   - Use CDN for frequently accessed documents

2. **Batch requests**
   - Queue multiple requests
   - Respect rate limits
   - Use async processing

3. **Monitor usage**
   - Track API calls
   - Set up alerts
   - Optimize prompts

### Error Handling

Always implement proper error handling:

```python
import requests
import time

def generate_pdf_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"prompt": prompt},
                timeout=30
            )

            if response.status_code == 200:
                return response.content
            elif response.status_code == 429:
                # Rate limit - wait and retry
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
            else:
                response.raise_for_status()

        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    raise Exception("Max retries exceeded")
```

---

## Webhooks (Coming Soon)

Async PDF generation with webhook notifications.

**Endpoint:** `POST /v1/generate/async`

**Request:**

```json
{
  "prompt": "Create a comprehensive e-book",
  "mode": "ebook",
  "webhook_url": "https://your-app.com/webhook"
}
```

**Response:**

```json
{
  "job_id": "uuid",
  "status": "pending"
}
```

**Webhook Payload:**

```json
{
  "job_id": "uuid",
  "status": "completed",
  "pdf_url": "https://cdn.hugpdf.com/documents/xxx.pdf"
}
```

---

## SDKs

Official SDKs coming soon:

- Python SDK
- JavaScript/TypeScript SDK
- Go SDK
- Ruby SDK

---

## Support

- **Documentation:** https://hugpdf.com/developer
- **Email:** support@hugpdf.com
- **GitHub:** https://github.com/hugpdf/api-issues
- **Discord:** https://discord.gg/hugpdf

---

## Changelog

### v1.0.0 (2026-02-15)

- Initial API release
- PDF generation endpoint
- API key management
- Rate limiting
- Three generation modes (normal, research, ebook)
