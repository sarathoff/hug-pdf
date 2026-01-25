# Fix Firecrawl scrape method call to use explicit arguments instead of params dict

with open('services/linkedin_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the incorrect scrape call
old_call = '''            # Use scrape_url which returns markdown by default or specified format
            # Note: Checking API method vs SDK version. 
            # If scrape_url is not available (as seen in previous errors), we use scrape method
            
            try:
                # Try scrape_url first (older SDK)
                scrape_result = self.client.scrape_url(
                    clean_url,
                    params={'formats': ['markdown']}
                )
            except AttributeError:
                # Fallback to newer SDK 'scrape' method
                scrape_result = self.client.scrape(
                    clean_url,
                    params={'formats': ['markdown']}
                )'''

new_call = '''            # Use Firecrawl scrape method with explicit keyword arguments
            # The v2 SDK expects arguments directly, not in a params dict
            
            try:
                # Try cleaner v2 scrape method directly
                scrape_result = self.client.scrape(
                    clean_url,
                    formats=['markdown']
                )
            except TypeError as e:
                # Fallback if params dict is expected (older versions)
                logger.warning(f"Standard scrape failed ({e}), trying with params dict...")
                try:
                    scrape_result = self.client.scrape(
                        clean_url,
                        params={'formats': ['markdown']}
                    )
                except AttributeError:
                     # Very old SDK
                     scrape_result = self.client.scrape_url(
                        clean_url,
                        params={'formats': ['markdown']}
                     )'''

content = content.replace(old_call, new_call)

with open('services/linkedin_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Firecrawl scrape method signature!")
