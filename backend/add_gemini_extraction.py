# Add extract_json_from_markdown to GeminiService

with open('services/gemini_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_method = '''    def extract_json_from_markdown(self, markdown: str, schema: Dict) -> Dict:
        """Extract structured data from markdown content using Gemini
        
        Args:
            markdown: Raw markdown content from Firecrawl
            schema: Expected JSON schema for extraction
            
        Returns:
            Dictionary containing extracted structured data
        """
        import json
        
        schema_str = json.dumps(schema, indent=2)
        
        system_prompt = f"""
You are an expert data extraction assistant. Your task is to extract structured information from the provided markdown content according to the specified JSON schema.

MARKDOWN CONTENT:
{markdown[:20000]}  # Limit content length to avoid context limits

TARGET JSON SCHEMA:
{schema_str}

INSTRUCTIONS:
1. Extract all relevant information that matches the schema
2. Return ONLY valid JSON
3. Do not include markdown formatting like ```json ... ```
4. If a field is missing, omit it or use null (unless required)
5. Infer logical values where appropriate (e.g. current role = True if no end date)

Analyze the content carefully and provide the highly accurate extraction.
"""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=system_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            result_text = response.text.strip()
            
            # Clean potential markdown
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
                
            return json.loads(result_text.strip())
            
        except Exception as e:
            logger.error(f"Error extracting JSON from markdown: {str(e)}")
            return {}

'''

# Append the new method to the class
content = content + "\n" + new_method

with open('services/gemini_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added extract_json_from_markdown extraction method to GeminiService!")
