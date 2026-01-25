# Fix Firecrawl API to use extract method instead of scrape

with open('services/linkedin_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the scrape call with extract
old_code = '''            # Use Firecrawl's extract feature with schema
            result = self.client.scrape(
                linkedin_url,
                params={
                    'formats': ['extract'],
                    'extract': {
                        'schema': schema
                    }
                }
            )'''

new_code = '''            # Use Firecrawl's extract feature with schema
            result = self.client.extract(
                urls=[linkedin_url],
                schema=schema
            )'''

content = content.replace(old_code, new_code)

# Also update the result checking
content = content.replace(
    "if result and 'extract' in result:\n                extracted_data = result['extract']",
    "if result and 'data' in result and result['data']:\n                extracted_data = result['data'][0]"
)

with open('services/linkedin_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Firecrawl API to use extract method!")
