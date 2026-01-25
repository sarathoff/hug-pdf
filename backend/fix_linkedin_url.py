# Fix LinkedIn URL format for Firecrawl - remove trailing slash

with open('services/linkedin_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add URL cleaning before the extract call
old_extract = '''            # Use Firecrawl's extract feature with schema
            result = self.client.extract(
                urls=[linkedin_url],
                schema=schema
            )'''

new_extract = '''            # Clean URL - remove trailing slash and ensure proper format
            clean_url = linkedin_url.rstrip('/')
            
            # Use Firecrawl's extract feature with schema
            result = self.client.extract(
                urls=[clean_url],
                schema=schema
            )'''

content = content.replace(old_extract, new_extract)

with open('services/linkedin_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed LinkedIn URL format!")
