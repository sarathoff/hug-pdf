# API Setup Guide

Welcome to the HugPDF API! This guide will help you get started with programmatic PDF generation.

## Quick Start

### 1. Create an Account

1. Visit [HugPDF](https://hugpdf.com) and click "Sign up"
2. Create an account using email/password or Google OAuth
3. Verify your email (if required)

### 2. Generate an API Key

1. Log in to your account
2. Click on your profile icon in the top right
3. Select "Developer" from the dropdown menu
4. Click "Create New API Key"
5. Give your key a descriptive name (e.g., "My Application")
6. **Important:** Copy and save your API key immediately - it won't be shown again!

### 3. Make Your First API Call

#### Using cURL

```bash
curl -X POST https://your-backend-url.com/api/v1/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a professional resume for John Doe"}' \
  --output document.pdf
```

#### Using Python

```python
import requests

response = requests.post(
    "https://your-backend-url.com/api/v1/generate",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={"prompt": "Create a professional resume for John Doe"}
)

with open("document.pdf", "wb") as f:
    f.write(response.content)

print("PDF generated successfully!")
```

#### Using JavaScript (Node.js)

```javascript
const axios = require("axios");
const fs = require("fs");

axios
  .post(
    "https://your-backend-url.com/api/v1/generate",
    {
      prompt: "Create a professional resume for John Doe",
    },
    {
      headers: { Authorization: "Bearer YOUR_API_KEY" },
      responseType: "arraybuffer",
    },
  )
  .then((response) => {
    fs.writeFileSync("document.pdf", response.data);
    console.log("PDF generated successfully!");
  })
  .catch((error) => {
    console.error("Error:", error.response?.data || error.message);
  });
```

## Common Use Cases

### 1. Automated Document Generation

Generate invoices, reports, or certificates automatically:

```python
def generate_invoice(customer_name, amount):
    prompt = f"Create a professional invoice for {customer_name} for ${amount}"
    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": prompt}
    )
    return response.content
```

### 2. Research Papers

Generate comprehensive research documents:

```python
response = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "prompt": "Write a research paper on climate change",
        "mode": "research"  # Uses research mode with citations
    }
)
```

### 3. E-books

Create long-form content:

```python
response = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "prompt": "Create an e-book about Python programming",
        "mode": "ebook"  # Generates 20+ pages
    }
)
```

## Rate Limits

### Free Tier

- **10 requests per minute**
- **1,000 requests per month**
- Access to normal mode

### Pro Tier

- **100 requests per minute**
- **10,000 requests per month**
- Access to all modes (normal, research, ebook)

Rate limit information is included in response headers:

- `X-RateLimit-Limit`: Your rate limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: When the limit resets

## Error Handling

Always handle errors gracefully:

```python
try:
    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()  # Raises HTTPError for bad responses

    with open("document.pdf", "wb") as f:
        f.write(response.content)

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    elif e.response.status_code == 400:
        print("Bad request:", e.response.json())
    else:
        print(f"HTTP error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Store API Keys Securely**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly

2. **Handle Rate Limits**
   - Implement exponential backoff
   - Cache responses when possible
   - Monitor usage in the Developer Portal

3. **Validate Input**
   - Sanitize user input before sending to API
   - Set reasonable prompt length limits
   - Validate file sizes

4. **Monitor Usage**
   - Check the Developer Portal regularly
   - Set up alerts for high usage
   - Track costs and optimize

## Integration Examples

### Telegram Bot

```python
from telegram import Update
from telegram.ext import Application, CommandHandler

async def generate_pdf(update: Update, context):
    prompt = ' '.join(context.args)

    response = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": prompt}
    )

    await update.message.reply_document(
        document=response.content,
        filename="document.pdf"
    )

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("pdf", generate_pdf))
app.run_polling()
```

### Zapier/Make.com Webhook

1. Create a webhook trigger
2. Use HTTP POST action
3. Set URL: `https://your-backend-url.com/api/v1/generate`
4. Add header: `Authorization: Bearer YOUR_API_KEY`
5. Set body: `{"prompt": "{{your_prompt}}"}`
6. Save PDF to Google Drive/Dropbox

## Troubleshooting

### "Invalid or inactive API key"

- Check that you're using the correct API key
- Ensure the key hasn't been revoked
- Verify the Authorization header format

### "Rate limit exceeded"

- Wait for the rate limit to reset
- Upgrade to Pro tier for higher limits
- Implement request queuing

### "PDF generation failed"

- Check your prompt is valid
- Ensure you're not exceeding length limits
- Try a simpler prompt first

## Support

Need help? Contact us:

- Email: support@hugpdf.com
- Documentation: https://hugpdf.com/developer
- GitHub Issues: https://github.com/hugpdf/api-issues

## Next Steps

- Explore the [API Reference](API_REFERENCE.md) for detailed endpoint documentation
- Check out more [integration examples](https://hugpdf.com/examples)
- Join our [Discord community](https://discord.gg/hugpdf)
