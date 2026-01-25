from google import genai
from google.genai import types
import os
from typing import Dict, Optional
import logging
from services.perplexity_service import PerplexityService
from services.web_scraper_service import WebScraperService
from services.pexels_service import PexelsService
from services.cache_service import CacheService

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.perplexity_service = PerplexityService()
        self.web_scraper = WebScraperService()
        self.pexels_service = PexelsService()
        self.cache_service = CacheService()
        self.CACHE_VERSION = "v1"  # Increment when changing prompts
        
    def generate_latex_from_prompt(self, prompt: str, mode: str = 'normal', tier: str = 'pro', research_context: Optional[str] = None, citations: Optional[list] = None) -> str:
        """Generate LaTeX document from user prompt with mode and tier support"""
        
        # Base instructions common to all modes
        base_instructions = """
CRITICAL:
1. Use \\usepackage{lmodern} and \\usepackage[margin=1in]{geometry}.
2. NO 'beramono', 'fvm', 'libertine' fonts.
3. Use \\vspace{1em} between sections.

IMAGES:
1. Use \\usepackage{graphicx}.
2. Use \\includegraphics[width=0.8\\textwidth]{URL} for [URL:...] tags.
"""
        
        # Mode-specific prompts
        if mode == 'ebook':
            # AUTO-IMAGE INSERTION for E-book: Fetch 3 images
            ebook_images_section = ""
            logger.info("Fetching relevant images for E-book Mode...")
            try:
                search_query = prompt[:50]
                pexels_result = self.pexels_service.search_images(search_query, per_page=3)
                
                if pexels_result and 'photos' in pexels_result:
                    image_urls = [photo['src']['large'] for photo in pexels_result['photos'][:3]]
                    if image_urls:
                        ebook_images_section = "\n\nAVAILABLE IMAGES (Insert these throughout your eBook):\n"
                        for i, url in enumerate(image_urls):
                            ebook_images_section += f"Image {i+1}: {url}\n"
                        ebook_images_section += "\nINSTRUCTIONS: Use \\includegraphics[width=0.7\\textwidth]{{{url}}} to insert images in relevant chapters.\n"
            except Exception as e:
                logger.warning(f"Failed to fetch images for E-book: {e}")
            
            system_prompt = f"""
Act as an expert eBook author. Create a professional 20+ page LaTeX eBook.

REQUIREMENTS:
1. Class: \\documentclass[11pt]{{report}}.
2. Structure: Title Page, TOC, 5+ Chapters, Conclusion.
3. Content: detailed, informative, ~20 pages.
4. Format: \\usepackage{{fancyhdr}}, \\pagenumbering{{arabic}}.

{base_instructions}

{ebook_images_section}

User request: {prompt}

Generate ONLY the LaTeX code.
"""
        elif mode == 'research':
            research_section = ""
            citations_section = ""
            
            if research_context:
                research_section = f"""
PERPLEXITY SUMMARY:
{research_context}
"""

            # DEEP RESEARCH: Scrape the citations
            deep_content = ""
            if citations:
                logger.info("Starting Deep Research Scraping...")
                deep_content = "\nFULL SOURCE CONTENT (Use this for deep analysis):\n"
                
                # Limit to top 4 citations to balance speed/coverage
                for i, url in enumerate(citations[:4]): 
                    try:
                        scraped_text = self.web_scraper.scrape_url(url)
                        if scraped_text:
                            deep_content += f"\n--- SOURCE {i+1}: {url} ---\n{scraped_text}\n"
                    except Exception as e:
                        logger.warning(f"Failed to scrape {url}: {e}")
                
                research_section += "\n" + deep_content

            # AUTO-IMAGE INSERTION: Fetch relevant images
            images_section = ""
            if citations:  # Only add images if we have research data
                logger.info("Fetching relevant images for Research Mode...")
                try:
                    # Use the prompt as search query (first 50 chars for relevance)
                    search_query = prompt[:50]
                    pexels_result = self.pexels_service.search_images(search_query, per_page=2)
                    
                    if pexels_result and 'photos' in pexels_result:
                        image_urls = [photo['src']['large'] for photo in pexels_result['photos'][:2]]
                        if image_urls:
                            images_section = "\n\nAVAILABLE IMAGES (Insert these in your document):\n"
                            for i, url in enumerate(image_urls):
                                images_section += f"Image {i+1}: {url}\n"
                            images_section += "\nINSTRUCTIONS: Use \\includegraphics[width=0.7\\textwidth]{{{url}}} to insert images at relevant sections.\n"
                            research_section += images_section
                except Exception as e:
                    logger.warning(f"Failed to fetch images: {e}")

            
            if citations:
                citations_list = "\\n".join([f"[{i+1}] {cite}" for i, cite in enumerate(citations)])
                citations_section = f"""
AVAILABLE CITATIONS:
{citations_list}

CITATION INSTRUCTIONS:
1. You MUST use the provided citations in your text as [1], [2], etc. where appropriate.
2. You MUST include a 'References' section at the end of the document.
3. The References section MUST list the citations exactly as provided above.
4. Do NOT make up new citations. Use ONLY the provided ones.
"""

            system_prompt = f"""
Act as an academic researcher. Create a cited LaTeX research paper based STRICTLY on the provided research data and citations.

REQUIREMENTS:
1. Class: \\documentclass[12pt]{{article}}.
2. Sections: Abstract, Introduction, Key Findings (Bulleted), Analysis, Discussion, Conclusion, References.
3. Tone: Formal, objective, academic.
4. Content: Synthesize the provided RESEARCH DATA. Do not just copy it.
5. Citations: deeply integrate the provided citations [1], [2] etc. into the text.
6. Length: Comprehensive (aim for 1000+ words).
7. Formatting: Use \\textbf{{..}} for key terms. Use \\begin{{itemize}} for lists.
8. Analysis: Provide critical insights and comparisons, not just summary.

{base_instructions}

{research_section}

{citations_section}

User request: {prompt}

Generate ONLY the LaTeX code.
"""
        else:  # normal mode
            # AUTO-IMAGE INSERTION for Normal Mode: Fetch 1 image for documentation/reports
            normal_images_section = ""
            logger.info("Fetching relevant image for Normal Mode...")
            try:
                # Use the prompt as search query (first 50 chars for relevance)
                search_query = prompt[:50]
                pexels_result = self.pexels_service.search_images(search_query, per_page=1)
                
                if pexels_result and 'photos' in pexels_result:
                    image_urls = [photo['src']['large'] for photo in pexels_result['photos'][:1]]
                    if image_urls:
                        normal_images_section = "\n\nAVAILABLE IMAGE (Insert this in your document if relevant):\n"
                        normal_images_section += f"Image: {image_urls[0]}\n"
                        normal_images_section += "\nINSTRUCTIONS: Use \\includegraphics[width=0.7\\textwidth]{{{url}}} to insert the image at a relevant section if appropriate for the document type.\n"
            except Exception as e:
                logger.warning(f"Failed to fetch image for Normal mode: {e}")
            
            system_prompt = f"""
Act as a fast LaTeX document generator. Create a clean, professional document.

REQUIREMENTS:
1. Class: \\documentclass{{article}}.
2. Layout: Clean, use \\section and \\subsection.
3. Speed: Be concise but effective. Focus on clear formatting.

{base_instructions}

{normal_images_section}

User request: {prompt}

Generate ONLY the LaTeX code.
"""
        
        try:
            # Use tier-based model selection
            # Starter: Flash-8B (cheapest, ~10x cheaper than Flash 2.0)
            # Pro/Power: Flash 2.0 (best quality)
            model_name = 'gemini-1.5-flash-8b' if tier == 'starter' else 'gemini-2.0-flash-exp'
            
            # Create cache key for this mode and tier
            cache_key = f"{mode}_{tier}_{self.CACHE_VERSION}"
            
            # Get or create cached system prompt (1 hour TTL)
            cached_prompt_name = self.cache_service.get_or_create_cache(
                cache_key=cache_key,
                system_instruction=system_prompt,
                model=model_name,
                ttl_seconds=3600  # 1 hour
            )
            
            # Generate content using cached system prompt
            if cached_prompt_name:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=system_prompt,  # Full prompt for now, will optimize later
                    cached_content=cached_prompt_name
                )
                logger.info(f"Generated with cached prompt: {cache_key}")
            else:
                # Fallback to non-cached generation
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=system_prompt
                )
                logger.warning(f"Cache miss, generated without cache for mode: {mode}, tier: {tier}")
            
            latex_content = response.text.strip()
            
            # Clean up potential markdown formatting
            if latex_content.startswith('```latex') or latex_content.startswith('```tex'):
                latex_content = latex_content.split('\n', 1)[1] if '\n' in latex_content else latex_content[7:]
            if latex_content.startswith('```'):
                latex_content = latex_content[3:]
            if latex_content.endswith('```'):
                latex_content = latex_content[:-3]
            
            latex_content = latex_content.strip()

            # FALLBACK: Ensure citations are present in Research Mode
            if mode == 'research' and citations:
                # Check if References section exists (heuristics)
                has_references = '\\section*{References}' in latex_content or '\\bibliography' in latex_content or '\\begin{thebibliography}' in latex_content
                
                if not has_references:
                    logger.warning("Gemini failed to generate References section. Appending manually.")
                    
                    # Create the References section manually
                    references_latex = "\n\n\\section*{References}\n\\begin{enumerate}\n"
                    for cite in citations:
                        # Escape special LaTeX characters in citations if needed, mostly clean text expected
                        references_latex += f"    \\item {cite}\n"
                    references_latex += "\\end{enumerate}\n"
                    
                    # Insert before \end{document}
                    if '\\end{document}' in latex_content:
                        latex_content = latex_content.replace('\\end{document}', references_latex + '\\end{document}')
                    else:
                        latex_content += references_latex
            
            logger.info(f"Generated LaTeX document ({mode} mode) for prompt: {prompt[:50]}...")
            return latex_content
        except Exception as e:
            logger.error(f"Error generating LaTeX: {str(e)}")
            raise
    
    def generate_html_from_prompt(self, prompt: str, mode: str = 'normal', tier: str = 'pro') -> Dict[str, str]:
        """Generate LaTeX document from user prompt with mode and tier support"""
        
        # For research mode, get research context from Perplexity
        research_context = None
        citations = []
        
        if mode == 'research':
            logger.info(f"Research mode: Querying Perplexity for: {prompt[:50]}...")
            research_result = self.perplexity_service.research_query(prompt)
            
            if research_result:
                research_context = research_result.get('content', '')
                citations = research_result.get('citations', [])
                logger.info(f"Research completed with {len(citations)} citations")
            else:
                logger.warning("Perplexity research failed, falling back to normal mode")
                mode = 'normal'
        
        latex_content = self.generate_latex_from_prompt(prompt, mode=mode, tier=tier, research_context=research_context, citations=citations)
        

        
        # Mode-specific messages
        if mode == 'ebook':
            message = "I've generated your e-book in LaTeX! This is a comprehensive document with chapters and sections. Feel free to ask me to modify anything!"
        elif mode == 'research':
            message = "I've generated your research document with citations! Check the References section at the end. Feel free to ask me to modify anything!"
        else:
            message = "I've generated your document in LaTeX. You can see the code on the right. Feel free to ask me to modify anything!"
        
        logger.info(f"Generated LaTeX ({mode} mode) for prompt: {prompt[:50]}...")
        return {
            "html": latex_content,
            "latex": latex_content,
            "message": message,
            "mode": mode
        }
    
    def modify_latex(self, current_latex: str, modification_request: str, mode: str = 'normal') -> str:
        """Modify existing LaTeX based on user request"""
        
        # Default system prompt for normal documents
        system_prompt = f"""
You are an expert at modifying LaTeX documents. The user has an existing LaTeX document and wants to make changes.

Current LaTeX:
{current_latex}

User's modification request: {modification_request}

IMPORTANT:
1. Return the COMPLETE modified LaTeX document
2. Keep the same overall structure but apply the requested changes
3. Ensure all changes are properly integrated
4. Keep it professional and well-formatted

CRITICAL FONT & PACKAGE INSTRUCTIONS:
1. If the user asks to fix fonts/errors: REMOVE 'beramono', 'libertine', 'newtxmath'. REPLACE with \\usepackage{{lmodern}}.
2. Ensure no conflicting packages (e.g. amssymb vs newtxmath).
3. Stick to standard, safe LaTeX packages.

SPACING & LAYOUT QUALITY INSTRUCTIONS (PREVENT OVERLAPPING):
1. Maintain proper spacing between sections: \\vspace{{0.5em}} or \\medskip
2. Ensure adequate whitespace between elements
3. Use \\hfill or tabular for headers with dates to prevent overlap
4. Avoid negative vspace unless necessary
5. Keep reasonable margins and paragraph spacing

IMAGE HANDLING INSTRUCTIONS:
1. If adding images, ALWAYS include \\usepackage{{graphicx}} in the preamble
2. When user provides an image URL (in brackets like [URL: ...]), use \\includegraphics{{URL}}
3. Use appropriate width: \\includegraphics[width=0.5\\textwidth]{{URL}}
4. Center images: \\begin{{center}} ... \\end{{center}}
5. Add captions if appropriate: \\begin{{figure}}[h] \\centering \\includegraphics... \\caption{{...}} \\end{{figure}}

Generate ONLY the complete modified LaTeX code, nothing else. No explanations, no markdown code blocks, just the raw LaTeX.
"""

        # PPT / Beamer Specific Prompt
        if mode == 'ppt':
            system_prompt = f"""
You are an expert at creating and observing LaTeX Beamer presentations. The user has an existing presentation and wants to modify it.

Current LaTeX (Beamer):
{current_latex}

User's modification request: {modification_request}

IMPORTANT:
1. Return the COMPLETE modified LaTeX document.
2. MODIFY the existing content based on the request. Do NOT generate a random new presentation.
3. If the request is vague (e.g. "improve this"), improve the language and formatting of the CURRENT slides.
2. MUST maintain \\documentclass{{beamer}} and the slide structure using \\begin{{frame}}...\\end{{frame}}.
3. Do NOT convert this into a normal article/report. KEEP IT AS SLIDES.
4. CONTENT QUALITY: Ensure professional, detailed, and high-quality content. Avoid generic placeholders.

IMAGE HANDLING FOR SLIDES (CRITICAL):
1. When user provides an image URL (e.g. [URL: ...]) or asks to add an image:
   - If the slide has text, use \\begin{{columns}}:
     \\begin{{columns}}[T]
     \\column{{0.5\\textwidth}}
     (Bullet points here)
     \\column{{0.5\\textwidth}}
     \\begin{{figure}}
     \\centering
     \\includegraphics[width=\\textwidth]{{URL}}
     \\end{{figure}}
     \\end{{columns}}
   - If the slide is empty or image-only, use:
     \\begin{{figure}}
     \\centering
     \\includegraphics[width=0.8\\textwidth]{{URL}}
     \\end{{figure}}
2. Ensure \\usepackage{{graphicx}} is present.

CONTENT INSTRUCTIONS:
1. Keep text concise (bullet points).
2. Avoid long paragraphs.
3. Use \\frametitle{{...}} for slide titles.
4. If asked to "improve" or "detail", EXPAND on the EXISTING slides. Do NOT create a new presentation from scratch.
5. PRESERVE EXISTING STRUCTURE unless asked otherwise.

Generate ONLY the complete modified LaTeX code (Beamer), nothing else. No explanations, no markdown code blocks.
"""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=system_prompt
            )
            latex_content = response.text.strip()
            
            # Clean up potential markdown formatting with Regex for robustness
            import re
            
            # Pattern: Extract content inside triple backticks (latex/tex optional)
            # If no backticks, assume the whole content is LaTeX (or contains it)
            code_block_match = re.search(r'```(?:latex|tex)?\s*(.*?)\s*```', latex_content, re.DOTALL)
            
            if code_block_match:
                latex_content = code_block_match.group(1).strip()
            else:
                # Fallback: if no code blocks, look for \documentclass...
                if "\\documentclass" in latex_content:
                    start = latex_content.find("\\documentclass")
                    latex_content = latex_content[start:]
                
                latex_content = latex_content.strip()
            
            logger.info(f"Modified LaTeX based on request: {modification_request[:50]}...")
            return latex_content
        except Exception as e:
            logger.error(f"Error modifying LaTeX: {str(e)}")
            raise
    
    def modify_html(self, current_html: str, modification_request: str, current_latex: str = None, mode: str = 'normal') -> Dict[str, str]:
        """Modify existing LaTeX based on user request with mode support"""
        # Use current_latex if provided, otherwise use current_html (which is actually LaTeX)
        latex_to_modify = current_latex if current_latex else current_html
        
        # For research mode modifications, optionally get new research
        if mode == 'research' and ('research' in modification_request.lower() or 'find' in modification_request.lower()):
            logger.info(f"Research mode modification: Querying Perplexity...")
            research_result = self.perplexity_service.research_query(modification_request)
            
            if research_result:
                research_context = research_result.get('content', '')
                # Add research context to modification request
                modification_request += f"\n\nAdditional research context: {research_context}"
        
        # Pass the mode to modify_latex so it knows if it's PPT or Doc
        latex_content = self.modify_latex(latex_to_modify, modification_request, mode=mode)
        
        result = {
            "html": latex_content,
            "latex": latex_content,
            "message": "I've updated the document based on your request.",
            "mode": mode
        }
        
        logger.info(f"Modified LaTeX ({mode} mode) based on request: {modification_request[:50]}...")
        return result
    def extract_json_from_markdown(self, markdown: str, schema: Dict) -> Dict:
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

    def format_content_for_pdf(self, markdown: str, conversion_type: str, metadata: Dict, options: Dict) -> str:
        """
        Convert markdown content to LaTeX based on conversion type
        
        Args:
            markdown: Raw markdown content
            conversion_type: Type of conversion (blog, article, website, resume, docs)
            metadata: Metadata from scraping (title, author, date, etc.)
            options: Additional formatting options
            
        Returns:
            LaTeX content ready for PDF generation
        """
        logger.info(f"Formatting content as {conversion_type}")
        
        # Build type-specific prompt
        type_prompts = {
            'blog': """
Convert this blog post to a professional LaTeX article format.

REQUIREMENTS:
- Clean, readable article layout
- Include title, author (if available), and date
- Preserve headings, lists, and formatting
- Include images with captions if present
- Use a modern, blog-friendly style
""",
            'article': """
Convert this article to an academic/professional LaTeX format.

REQUIREMENTS:
- Formal article structure with abstract (if present)
- Proper heading hierarchy
- Include citations and references if present
- Professional typography
- Include tables and figures properly
""",
            'website': """
Convert this website content to a comprehensive LaTeX document.

REQUIREMENTS:
- Preserve the full content structure
- Include all sections and subsections
- Maintain navigation structure as table of contents
- Include images and media references
- Clean, organized layout
""",
            'resume': """
Convert this content to a professional resume/CV LaTeX format.

REQUIREMENTS:
- Professional CV layout
- Clear sections: Experience, Education, Skills
- Clean typography optimized for ATS systems
- Proper spacing and formatting
- Modern, professional design
""",
            'docs': """
Convert this documentation to a technical LaTeX document.

REQUIREMENTS:
- Technical documentation format
- Code blocks with syntax highlighting
- Clear API/function documentation
- Table of contents
- Professional technical styling
"""
        }
        
        base_prompt = type_prompts.get(conversion_type, type_prompts['article'])
        
        # Extract metadata
        title = metadata.get('title', 'Untitled Document')
        author = metadata.get('author', '')
        date = metadata.get('publishedTime', '')
        
        full_prompt = f"""
{base_prompt}

METADATA:
Title: {title}
Author: {author}
Date: {date}

CONTENT (Markdown):
{markdown[:15000]}

CRITICAL LATEX REQUIREMENTS:
1. Use \\usepackage{{lmodern}} and \\usepackage[margin=1in]{{geometry}}
2. NO 'beramono', 'fvm', 'libertine' fonts
3. Use \\vspace{{1em}} between sections
4. For images, use \\usepackage{{graphicx}} and \\includegraphics[width=0.8\\textwidth]{{URL}}
5. Return ONLY the complete LaTeX document, no explanations

Generate the complete LaTeX document now:
"""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=full_prompt
            )
            
            latex_content = response.text.strip()
            
            # Clean markdown code blocks if present
            if latex_content.startswith('```latex'):
                latex_content = latex_content[8:]
            elif latex_content.startswith('```'):
                latex_content = latex_content[3:]
            if latex_content.endswith('```'):
                latex_content = latex_content[:-3]
                
            return latex_content.strip()
            
        except Exception as e:
            logger.error(f"Error formatting content for PDF: {str(e)}")
            raise

