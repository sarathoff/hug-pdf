"""
Example: Modified gemini_service.py with Context Caching

This file shows how to integrate the CacheService into your existing GeminiService.
Key changes:
1. Import and initialize CacheService
2. Cache base instructions and mode-specific prompts
3. Use cached content in API calls
4. Cache research content for reuse
"""

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

class GeminiServiceWithCache:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.perplexity_service = PerplexityService()
        self.web_scraper = WebScraperService()
        self.pexels_service = PexelsService()

        # Initialize cache service
        self.cache_service = CacheService()

        # Cache version - increment when you change prompts
        self.CACHE_VERSION = "v1"

    def _get_base_instructions(self) -> str:
        """Base instructions used across all modes - perfect for caching"""
        return """
CRITICAL:
1. Use \\usepackage{lmodern} and \\usepackage[margin=1in]{geometry}.
2. NO 'beramono', 'fvm', 'libertine' fonts.
3. Use \\vspace{1em} between sections.

IMAGES:
1. Use \\usepackage{graphicx}.
2. Use \\includegraphics[width=0.8\\textwidth]{URL} for [URL:...] tags.
"""

    def _get_mode_system_prompt(self, mode: str, **kwargs) -> str:
        """Get mode-specific system prompt"""
        base_instructions = self._get_base_instructions()

        if mode == 'ebook':
            ebook_images_section = kwargs.get('ebook_images_section', '')
            return f"""
Act as an expert eBook author. Create a professional 20+ page LaTeX eBook.

REQUIREMENTS:
1. Class: \\documentclass[11pt]{{report}}.
2. Structure: Title Page, TOC, 5+ Chapters, Conclusion.
3. Content: detailed, informative, ~20 pages.
4. Format: \\usepackage{{fancyhdr}}, \\pagenumbering{{arabic}}.

{base_instructions}

{ebook_images_section}

Generate ONLY the LaTeX code.
"""
        elif mode == 'research':
            research_section = kwargs.get('research_section', '')
            citations_section = kwargs.get('citations_section', '')

            return f"""
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

Generate ONLY the LaTeX code.
"""
        else:  # normal mode
            return f"""
Act as a fast LaTeX document generator. Create a clean, professional document.

REQUIREMENTS:
1. Class: \\documentclass{{article}}.
2. Layout: Clean, use \\section and \\subsection.
3. Speed: Be concise but effective. Focus on clear formatting.

{base_instructions}

Generate ONLY the LaTeX code.
"""

    def generate_latex_from_prompt_cached(
        self,
        prompt: str,
        mode: str = 'normal',
        research_context: Optional[str] = None,
        citations: Optional[list] = None
    ) -> str:
        """Generate LaTeX document using context caching"""

        # Prepare mode-specific content
        kwargs = {}

        if mode == 'ebook':
            # Fetch images for ebook
            ebook_images_section = ""
            try:
                search_query = prompt[:50]
                pexels_result = self.pexels_service.search_images_sync(search_query, per_page=3)

                if pexels_result and 'photos' in pexels_result:
                    image_urls = [photo['src']['large'] for photo in pexels_result['photos'][:3]]
                    if image_urls:
                        ebook_images_section = "\n\nAVAILABLE IMAGES (Insert these throughout your eBook):\n"
                        for i, url in enumerate(image_urls):
                            ebook_images_section += f"Image {i+1}: {url}\n"
                        ebook_images_section += "\nINSTRUCTIONS: Use \\includegraphics[width=0.7\\textwidth]{{{url}}} to insert images in relevant chapters.\n"
            except Exception as e:
                logger.warning(f"Failed to fetch images for E-book: {e}")

            kwargs['ebook_images_section'] = ebook_images_section

        elif mode == 'research':
            research_section = ""
            citations_section = ""

            if research_context:
                research_section = f"\nPERPLEXITY SUMMARY:\n{research_context}\n"

            # DEEP RESEARCH: Scrape citations and cache them
            deep_content = ""
            if citations:
                logger.info("Starting Deep Research Scraping...")

                # Create a cache key based on citations
                citations_hash = self.cache_service._hash_content(''.join(citations[:4]))
                research_cache_key = f"research_content_{citations_hash}_{self.CACHE_VERSION}"

                # Try to get cached research content
                cached_research = self.cache_service.get_cache(research_cache_key)

                if not cached_research:
                    # Scrape and cache the content
                    deep_content = "\nFULL SOURCE CONTENT (Use this for deep analysis):\n"

                    for i, url in enumerate(citations[:4]):
                        try:
                            scraped_text = self.web_scraper.scrape_url(url)
                            if scraped_text:
                                deep_content += f"\n--- SOURCE {i+1}: {url} ---\n{scraped_text}\n"
                        except Exception as e:
                            logger.warning(f"Failed to scrape {url}: {e}")

                    # Cache the scraped content (30 min TTL for freshness)
                    if deep_content:
                        self.cache_service.create_cache(
                            cache_key=research_cache_key,
                            system_instruction=deep_content,
                            ttl_seconds=1800  # 30 minutes
                        )
                else:
                    logger.info(f"Using cached research content: {research_cache_key}")

                research_section += "\n" + deep_content

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

            kwargs['research_section'] = research_section
            kwargs['citations_section'] = citations_section

        # Get system prompt for this mode
        system_prompt_base = self._get_mode_system_prompt(mode, **kwargs)

        # Create cache key for this mode's system prompt
        mode_cache_key = f"{mode}_mode_{self.CACHE_VERSION}"

        # Get or create cached system prompt (1 hour TTL)
        cached_prompt_name = self.cache_service.get_or_create_cache(
            cache_key=mode_cache_key,
            system_instruction=system_prompt_base,
            ttl_seconds=3600  # 1 hour
        )

        try:
            model_name = 'gemini-1.5-flash'

            # Generate content using cached system prompt
            if cached_prompt_name:
                # Use cached content
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=f"User request: {prompt}",
                    cached_content=cached_prompt_name  # Use cached system instructions
                )
                logger.info(f"Generated with cached prompt: {mode_cache_key}")
            else:
                # Fallback to non-cached generation
                full_prompt = system_prompt_base + f"\n\nUser request: {prompt}"
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                logger.warning(f"Cache miss, generated without cache for mode: {mode}")

            latex_content = response.text.strip()

            # Clean up markdown formatting
            if latex_content.startswith('```latex') or latex_content.startswith('```tex'):
                latex_content = latex_content.split('\n', 1)[1] if '\n' in latex_content else latex_content[7:]
            if latex_content.startswith('```'):
                latex_content = latex_content[3:]
            if latex_content.endswith('```'):
                latex_content = latex_content[:-3]

            latex_content = latex_content.strip()

            # Log cache statistics
            stats = self.cache_service.get_stats()
            logger.info(f"Cache stats: {stats}")

            return latex_content

        except Exception as e:
            logger.error(f"Error generating LaTeX: {str(e)}")
            raise

    def get_cache_statistics(self) -> dict:
        """Get cache performance statistics"""
        return self.cache_service.get_stats()
