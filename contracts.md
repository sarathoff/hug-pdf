# API Contracts & Integration Plan

## Overview
Backend will integrate Gemini LLM for generating HTML/CSS content and provide PDF export functionality.

## API Endpoints

### 1. POST /api/generate-initial
**Purpose**: Generate initial HTML content from user prompt
**Request Body**:
```json
{
  "prompt": "string",
  "session_id": "string (optional)"
}
```
**Response**:
```json
{
  "session_id": "string",
  "html_content": "string",
  "message": "string"
}
```

### 2. POST /api/chat
**Purpose**: Handle follow-up chat messages to modify HTML
**Request Body**:
```json
{
  "session_id": "string",
  "message": "string",
  "current_html": "string"
}
```
**Response**:
```json
{
  "html_content": "string",
  "message": "string"
}
```

### 3. POST /api/download-pdf
**Purpose**: Convert HTML to PDF and return download URL or file
**Request Body**:
```json
{
  "html_content": "string",
  "filename": "string (optional)"
}
```
**Response**: PDF file download

## MongoDB Collections

### sessions
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "created_at": "datetime",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "datetime"
    }
  ],
  "current_html": "string"
}
```

## Mock Data to Replace

### Frontend: /app/frontend/src/utils/mockData.js
- `mockGeneratePDF()` → Replace with API call to `/api/generate-initial`
- `mockChatResponse()` → Replace with API call to `/api/chat`

### Frontend: /app/frontend/src/pages/EditorPage.jsx
- `handleInitialGeneration()` → Call real API endpoint
- `handleSendMessage()` → Call real API endpoint
- `handleDownloadPDF()` → Call real PDF download endpoint

## Gemini Integration

### Prompt Engineering
1. **Initial Generation**: Ask Gemini to generate complete HTML with inline CSS using DM Sans font
2. **Modifications**: Provide current HTML + modification request, ask Gemini to return updated HTML
3. **Template**: Ensure HTML includes proper structure, styling, and is PDF-ready

### API Key Storage
- Store in `/app/backend/.env` as `GEMINI_API_KEY`
- Use `google-generativeai` Python package

## PDF Generation
- Use `weasyprint` or `pdfkit` library to convert HTML to PDF
- Ensure proper CSS rendering for print media
- Handle fonts and styling correctly

## Frontend Integration Steps
1. Remove mock data imports
2. Add axios calls to backend endpoints
3. Handle loading states and errors
4. Update download to fetch PDF from backend
