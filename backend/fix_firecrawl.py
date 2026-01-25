# Fix Firecrawl API method in linkedin_service.py

with open('services/linkedin_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace scrape_url with scrape
content = content.replace('self.client.scrape_url(', 'self.client.scrape(')

with open('services/linkedin_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Firecrawl API method!")
