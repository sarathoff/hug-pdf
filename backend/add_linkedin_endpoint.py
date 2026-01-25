# Script to add LinkedIn endpoint to server.py

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

endpoint_code = '''
@api_router.post("/linkedin-to-resume", response_model=LinkedInToResumeResponse)
async def linkedin_to_resume(
    request: LinkedInToResumeRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Convert LinkedIn profile to professional resume"""
    try:
        # Validate LinkedIn URL
        if not linkedin_service.validate_linkedin_url(request.linkedin_url):
            raise HTTPException(
                status_code=400,
                detail="Invalid LinkedIn URL. Please provide a valid LinkedIn profile URL (e.g., https://www.linkedin.com/in/username)"
            )
        
        # Scrape LinkedIn profile
        logger.info(f"Scraping LinkedIn profile: {request.linkedin_url}")
        linkedin_data = linkedin_service.scrape_linkedin_profile(request.linkedin_url)
        
        if not linkedin_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to scrape LinkedIn profile. Please ensure the profile is public and the URL is correct."
            )
        
        # Generate resume from LinkedIn data
        logger.info(f"Generating resume for: {linkedin_data.get('name', 'Unknown')}")
        result = resume_generator.generate_resume_from_linkedin(linkedin_data)
        
        return LinkedInToResumeResponse(
            latex_content=result['latex'],
            message=result['message'],
            name=linkedin_data.get('name')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in linkedin_to_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

'''

# Insert before rephrasy endpoint
new_content = content.replace(
    '@api_router.post("/rephrasy/detect", response_model=RephrasyDetectResponse)',
    endpoint_code + '@api_router.post("/rephrasy/detect", response_model=RephrasyDetectResponse)'
)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("LinkedIn endpoint added successfully!")
