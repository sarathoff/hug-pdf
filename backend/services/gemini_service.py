from google import genai
from google.genai import types
import os
from typing import Dict, Optional, List
import logging
from services.perplexity_service import PerplexityService
from services.web_scraper_service import WebScraperService
from services.pexels_service import PexelsService
from services.cache_service import CacheService
from backend.prompts import latex_prompts
from backend.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.perplexity_service = PerplexityService()
        self.web_scraper = WebScraperService()
        self.pexels_service = PexelsService()
        self.cache_service = CacheService()
        self.CACHE_VERSION = "v1"
        
    def generate_latex_from_prompt(self, prompt: str, mode: str = 'normal', tier: str = 'pro', research_context: Optional[str] = None, citations: Optional[list] = None) -> str:
        """Generate LaTeX document from user prompt with mode and tier support"""
        
        # Prepare context sections
        images_section = ""
        research_section = ""
        citations_section = ""
        
        # 1. Handle Images
        try:
            if mode == 'ebook':
                logger.info("Fetching relevant images for E-book Mode...")
                pexels_result = self.pexels_service.search_images(prompt[:50], per_page=3)
                if pexels_result and 'photos' in pexels_result:
                    image_urls = [photo['src']['large'] for photo in pexels_result['photos']]
                    if image_urls:
                        images_section = "\n\nAVAILABLE IMAGES (Insert these throughout your eBook):\n"
                        for i, url in enumerate(image_urls):
                            images_section += f"Image {i+1}: {url}\n"
                        images_section += "\nINSTRUCTIONS: Use \\includegraphics[width=0.7\\textwidth]{{{url}}} to insert images.\n"
            
            elif mode == 'research' and citations:
                logger.info("Fetching relevant images for Research Mode...")
                pexels_result = self.pexels_service.search_images(prompt[:50], per_page=2)
                if pexels_result and 'photos' in pexels_result:
                    image_urls = [photo['src']['large'] for photo in pexels_result['photos']]
                    if image_urls:
                        images_section = "\n\nAVAILABLE IMAGES:\n"
                        for i, url in enumerate(image_urls):
                            images_section += f"Image {i+1}: {url}\n"
                        images_section += "\nINSTRUCTIONS: Use \\includegraphics[width=0.7\\textwidth]{{{url}}}.\n"
                        
            elif mode == 'normal':
                logger.info("Fetching relevant image for Normal Mode...")
                pexels_result = self.pexels_service.search_images(prompt[:50], per_page=1)
                if pexels_result and 'photos' in pexels_result:
                    if pexels_result['photos']:
                        url = pexels_result['photos'][0]['src']['large']
                        images_section = f"\n\nAVAILABLE IMAGE: {url}\nINSTRUCTIONS: Use \\includegraphics[width=0.7\\textwidth]{{{url}}} if relevant.\n"
        except Exception as e:
            logger.warning(f"Failed to fetch images: {e}")

        # 2. Handle Research Context
        if mode == 'research':
            if research_context:
                research_section = f"PERPLEXITY SUMMARY:\n{research_context}\n"
            
            if citations:
                # Deep Scrape top citations
                deep_content = ""
                for i, url in enumerate(citations[:4]):
                    try:
                        text = self.web_scraper.scrape_url(url)
                        if text:
                            deep_content += f"\n--- SOURCE {i+1}: {url} ---\n{text[:2000]}...\n"
                    except Exception as e:
                        logger.warning(f"Failed to scrape {url}: {e}")
                
                if deep_content:
                    research_section += f"\nFULL SOURCE CONTENT:\n{deep_content}"
                
                citations_list = "\\n".join([f"[{i+1}] {cite}" for i, cite in enumerate(citations)])
                citations_section = f"AVAILABLE CITATIONS:\n{citations_list}\n"

        # 3. Select System Prompt
        if mode == 'ebook':
            system_prompt = latex_prompts.EBOOK_SYSTEM_PROMPT.format(
                base_instructions=latex_prompts.BASE_INSTRUCTIONS,
                images_section=images_section,
                prompt=prompt
            )
        elif mode == 'research':
            system_prompt = latex_prompts.RESEARCH_SYSTEM_PROMPT.format(
                base_instructions=latex_prompts.BASE_INSTRUCTIONS,
                research_section=research_section,
                citations_section=citations_section,
                prompt=prompt
            )
        else:
            system_prompt = latex_prompts.NORMAL_SYSTEM_PROMPT.format(
                base_instructions=latex_prompts.BASE_INSTRUCTIONS,
                images_section=images_section,
                prompt=prompt
            )

        try:
            # Model Selection with Fallback
            model_name = settings.GEMINI_MODEL_STARTER if tier == 'starter' else settings.GEMINI_MODEL_PRO
            
            # Cache Strategy
            cache_key = f"{mode}_{tier}_{self.CACHE_VERSION}"
            cached_prompt_name = self.cache_service.get_or_create_cache(
                cache_key=cache_key,
                system_instruction=system_prompt,
                model=model_name, # Pass correct model
                ttl_seconds=3600
            )
            
            generate_config = None
            if cached_prompt_name:
                # If using cache, we might need a specific way to call it depending on SDK
                # For now, following the pattern of passing cached_content
                # Note: 'contents' should be just the user prompt if system prompt is cached, 
                # but here our system prompt IS the task.
                # So we send an empty user prompt or verification trigger?
                # Actually, in this design the "system prompt" contains the user request {prompt} formatted in.
                # So caching it is tricky because the PROMPT changes every time.
                # FIX: We should only cache the BASE INSTRUCTIONS, not the user prompt.
                # But for this immediate fix, we will skip caching if it causes issues, 
                # or acknowledge that we are caching the *template* (if we could).
                
                # Sinc we formatted the prompt INTO the system prompt, the cache key is constant but content allows changes?
                # No. create_cache takes specific content.
                # If we cache the whole thing, we can't change the prompt.
                # We should disable cache for this specific logic unless we separate system instruction from user prompt.
                pass

            # Proceed with direct generation for now to ensure stability
            response = self.client.models.generate_content(
                model=model_name,
                contents=system_prompt
            )
            
            latex_content = self._clean_latex(response.text)
            
            # Fallback for Research References
            if mode == 'research' and citations and 'References' not in latex_content and 'bibliography' not in latex_content:
                logger.warning("Appending missing references...")
                refs = "\n\n\\section*{References}\n\\begin{enumerate}\n" + \
                       "\n".join([f"    \\item {c}" for c in citations]) + \
                       "\n\\end{enumerate}\n"
                if '\\end{document}' in latex_content:
                    latex_content = latex_content.replace('\\end{document}', refs + '\\end{document}')
                else:
                    latex_content += refs
            
            return latex_content

        except Exception as e:
            logger.error(f"Error generating LaTeX: {str(e)}")
            # Try fallback model if 404
            if "404" in str(e) or "not found" in str(e).lower():
                logger.warning("Primary model failed, trying fallback gemini-1.5-flash...")
                try:
                    response = self.client.models.generate_content(
                        model=settings.GEMINI_MODEL_STARTER,
                        contents=system_prompt
                    )
                    return self._clean_latex(response.text)
                except Exception as e2:
                    logger.error(f"Fallback failed: {e2}")
            raise

    def modify_latex(self, current_latex: str, modification_request: str, mode: str = 'normal') -> str:
        """Modify LaTeX based on request"""
        
        if mode == 'ppt':
             system_prompt = latex_prompts.PPT_MODIFY_SYSTEM_PROMPT.format(
                current_latex=current_latex,
                modification_request=modification_request
            )
        else:
            system_prompt = latex_prompts.MODIFY_SYSTEM_PROMPT.format(
                current_latex=current_latex,
                modification_request=modification_request
            )
        
        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL_PRO,
                contents=system_prompt
            )
            return self._clean_latex(response.text)
        except Exception as e:
            logger.error(f"Error modifying LaTeX: {e}")
            raise

    def generate_html_from_prompt(self, prompt: str, mode: str = 'normal', tier: str = 'pro') -> Dict[str, str]:
        """Orchestrator for generation"""
        research_context = None
        citations = []
        
        if mode == 'research':
            logger.info(f"Researching: {prompt[:50]}...")
            res = self.perplexity_service.research_query(prompt)
            if res:
                research_context = res.get('content', '')
                citations = res.get('citations', [])
        
        latex = self.generate_latex_from_prompt(prompt, mode, tier, research_context, citations)
        
        msgs = {
            'ebook': "I've generated your e-book! Check the chapters.",
            'research': "I've created your research paper with citations.",
            'normal': "I've generated your document."
        }
        
        return {
            "html": latex,
            "latex": latex,
            "message": msgs.get(mode, msgs['normal']),
            "mode": mode
        }

    def modify_html(self, current_html: str, modification_request: str, current_latex: str = None, mode: str = 'normal') -> Dict[str, str]:
        target = current_latex if current_latex else current_html
        if mode == 'research' and ('research' in modification_request or 'find' in modification_request):
             res = self.perplexity_service.research_query(modification_request)
             if res:
                 modification_request += f"\n\nContext: {res.get('content')}"
        
        new_latex = self.modify_latex(target, modification_request, mode)
        return {
            "html": new_latex,
            "latex": new_latex,
            "message": "Updated document.",
            "mode": mode
        }

    def _clean_latex(self, text: str) -> str:
        text = text.strip()
        if text.startswith('```latex'): return text[8:-3].strip() if text.endswith('```') else text[8:].strip()
        if text.startswith('```tex'): return text[6:-3].strip() if text.endswith('```') else text[6:].strip()
        if text.startswith('```'): return text[3:-3].strip() if text.endswith('```') else text[3:].strip()
        return text

    # ... keep other methods like format_content_for_pdf if needed, or stub them
    def format_content_for_pdf(self, markdown: str, conversion_type: str, metadata: Dict, options: Dict) -> str:
         # Simplified version reusing logic
         return self.generate_latex_from_prompt(f"Convert this markdown to {conversion_type}: {markdown[:1000]}...", mode='normal')

    def extract_json_from_markdown(self, prompt: str, schema: Dict) -> Dict:
        import json
        try:
            # Use structured output if available in SDK
            # We use the prompt directly to generate the JSON
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
            
            # Switch to FLASH model for better stability/availability
            # Use settings constant which now points to the valid 2.5 model
            # OPTIMIZATION: Use STARTER (Flash) for JSON extraction to improve speed
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL_STARTER, 
                contents=prompt,
                config=config
            )
            
            # Additional safety: handle if response is null or text is empty
            if not response.text:
                raise ValueError("Empty response from AI")
                
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            # Detailed logging to help user debug
            logger.warning("Attempting fallback to standard JSON parsing explicitly...")
            try:
                # Fallback: simplified prompt
                fallback_prompt = f"{prompt}\n\nRETURN ONLY RAW JSON. NO MARKDOWN."
                response = self.client.models.generate_content(
                    model=settings.GEMINI_MODEL_STARTER, # Use valid model from settings
                    contents=fallback_prompt
                )
                text = self._clean_latex(response.text) # Reusing clean method to strip markdown
                if text.startswith('json'): text = text[4:].strip()
                return json.loads(text)
            except Exception as e2:
                 logger.error(f"Fallback JSON failed: {e2}")
                 raise e
