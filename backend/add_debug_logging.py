# Add debug logging to see Firecrawl response structure

with open('services/linkedin_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add logging before the if statement
old_check = '''            
            if result and 'data' in result and result['data']:
                extracted_data = result['data'][0]'''

new_check = '''            
            # Debug: Log the actual response structure
            logger.info(f"Firecrawl response type: {type(result)}")
            logger.info(f"Firecrawl response keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            logger.info(f"Firecrawl response: {str(result)[:500]}")
            
            # Try different response structures
            extracted_data = None
            if result:
                # Try direct data access
                if isinstance(result, dict):
                    if 'data' in result and result['data']:
                        extracted_data = result['data'][0] if isinstance(result['data'], list) else result['data']
                    elif 'extract' in result:
                        extracted_data = result['extract']
                    else:
                        # Maybe the result itself is the data
                        extracted_data = result
                elif isinstance(result, list) and result:
                    extracted_data = result[0]
            
            if extracted_data and 'name' in extracted_data:'''

content = content.replace(old_check, new_check)

# Update the success message
content = content.replace(
    "logger.info(f\"Successfully extracted LinkedIn data for: {extracted_data.get('name', 'Unknown')}\")\n                return extracted_data",
    "logger.info(f\"Successfully extracted LinkedIn data for: {extracted_data.get('name', 'Unknown')}\")\n                return extracted_data"
)

# Update the else clause
content = content.replace(
    "else:\n                logger.error(\"Failed to extract structured data from LinkedIn profile\")\n                return None",
    "else:\n                logger.error(f\"Failed to extract structured data. Result structure: {type(result)}\")\n                return None"
)

with open('services/linkedin_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added debug logging to LinkedIn service!")
