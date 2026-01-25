"""
PPT Generator Service
Generates professional presentations using LaTeX Beamer with AI-powered content and images
"""

import logging
from typing import Optional, Dict, List
import re

logger = logging.getLogger(__name__)

class PPTGeneratorService:
    """Service for generating professional presentations"""
    
    def __init__(self, gemini_service, pexels_service):
        """
        Initialize PPT Generator Service
        
        Args:
            gemini_service: Service for AI content generation
            pexels_service: Service for fetching presentation images
        """
        self.gemini_service = gemini_service
        self.pexels_service = pexels_service
        logger.info("PPTGeneratorService initialized")
    
    async def generate_presentation(
        self,
        topic: Optional[str] = None,
        content: Optional[str] = None,
        num_slides: int = 10,
        style: str = "minimal",
        user_name: Optional[str] = None
    ) -> Dict:
        """
        Generate a professional presentation
        
        Args:
            topic: Topic to generate presentation about
            content: Existing content to convert to slides
            num_slides: Number of slides to generate (5-30)
            style: Presentation style (minimal, default, elegant)
            user_name: Name to display as author
            
        Returns:
            Dict with latex_content, slide_count, images_used, message
        """
        try:
            logger.info(f"Generating presentation: topic={topic}, content_length={len(content) if content else 0}, slides={num_slides}, style={style}")
            
            # Validate inputs
            if not topic and not content:
                raise ValueError("Either topic or content must be provided")
            
            if num_slides < 5 or num_slides > 30:
                raise ValueError("Number of slides must be between 5 and 30")
            
            # Generate presentation outline and content
            if topic:
                presentation_data = await self._generate_from_topic(topic, num_slides)
            else:
                presentation_data = await self._generate_from_content(content, num_slides)
            
            # Fetch images for slides
            images_used = await self._fetch_slide_images(presentation_data['slides'])
            
            # Generate LaTeX
            latex_content = self._generate_beamer_latex(
                presentation_data,
                images_used,
                style,
                user_name or "Created with HugPDF"
            )
            
            # Count slides
            slide_count = latex_content.count(r'\begin{frame}')
            
            logger.info(f"Presentation generated successfully: {slide_count} slides, {len(images_used)} images")
            
            return {
                'latex_content': latex_content,
                'slide_count': slide_count,
                'images_used': images_used,
                'message': f'Professional presentation created with {slide_count} slides!'
            }
            
        except Exception as e:
            logger.error(f"Error generating presentation: {str(e)}")
            raise
    
    async def _generate_from_topic(self, topic: str, num_slides: int) -> Dict:
        """Generate presentation content from a topic using AI"""
        
        prompt = f"""Create a professional presentation outline for the topic: "{topic}"

Generate exactly {num_slides} slides (including title and conclusion).

For each slide, provide:
1. Slide title
2. 3-5 concise bullet points
3. A brief image search query (what image would best represent this slide)

Make the presentation engaging, professional, and well-structured with a clear flow.
Include an introduction slide and a conclusion/summary slide.
"""
        
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "subtitle": {"type": "string"},
                "slides": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "title": {"type": "string"},
                            "points": {"type": "array", "items": {"type": "string"}},
                            "image_query": {"type": "string"}
                        },
                        "required": ["title", "points", "image_query"]
                    }
                }
            },
            "required": ["title", "slides"]
        }
        
        response = self.gemini_service.extract_json_from_markdown(prompt, schema)
        return response
    
    async def _generate_from_content(self, content: str, num_slides: int) -> Dict:
        """Convert existing content into presentation slides"""
        
        prompt = f"""Convert the following content into a professional presentation with {num_slides} slides.

Content:
{content}

Structure the content into clear, concise slides with:
1. A compelling title slide
2. An outline/agenda slide
3. Content slides with 3-5 bullet points each
4. A conclusion/summary slide

For each slide, suggest a relevant image search query.
"""
        
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "subtitle": {"type": "string"},
                "slides": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "title": {"type": "string"},
                            "points": {"type": "array", "items": {"type": "string"}},
                            "image_query": {"type": "string"}
                        },
                        "required": ["title", "points", "image_query"]
                    }
                }
            },
            "required": ["title", "slides"]
        }
        
        response = self.gemini_service.extract_json_from_markdown(prompt, schema)
        return response
    
    async def _fetch_slide_images(self, slides: List[Dict]) -> List[str]:
        """Fetch relevant images for slides from Pexels"""
        images = []
        
        for slide in slides:
            if 'image_query' in slide and slide['image_query']:
                try:
                    # Fetch one image per slide
                    result = await self.pexels_service.search_images(
                        query=slide['image_query'],
                        per_page=1
                    )
                    
                    if result and 'photos' in result and len(result['photos']) > 0:
                        # Get medium-sized image URL
                        image_url = result['photos'][0]['src']['large']
                        images.append(image_url)
                        logger.info(f"Fetched image for '{slide['image_query']}': {image_url}")
                    else:
                        images.append(None)
                        logger.warning(f"No image found for query: {slide['image_query']}")
                        
                except Exception as e:
                    logger.error(f"Error fetching image for '{slide.get('image_query')}': {str(e)}")
                    images.append(None)
            else:
                images.append(None)
        
        return images
    
    def _generate_beamer_latex(
        self,
        presentation_data: Dict,
        images: List[str],
        style: str,
        author: str
    ) -> str:
        """Generate Beamer LaTeX code for the presentation"""
        
        title = presentation_data.get('title', 'Presentation')
        subtitle = presentation_data.get('subtitle', '')
        slides = presentation_data.get('slides', [])
        
        # Start with document class and packages
        latex = r"""\documentclass{beamer}

\usepackage[english]{babel}
\usepackage[utf8x]{inputenc}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}

"""
        
        # Add theme based on style
        if style == "elegant":
            latex += r"""\mode<presentation>
{
\usetheme{Madrid}
\usecolortheme{seahorse}
\usefonttheme{serif}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{caption}[numbered]
}
"""
        elif style == "default":
            latex += r"""\mode<presentation>
{
\usetheme{default}
\usecolortheme{default}
\usefonttheme{default}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{caption}[numbered]
}
"""
        else:  # minimal
            latex += r"""\mode<presentation>
{
\usetheme{default}
\usecolortheme{default}
\usefonttheme{default}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{caption}[numbered]
}
"""
        
        # Add title, author, date
        latex += f"""
\\title{{{self._escape_latex(title)}}}
"""
        
        if subtitle:
            latex += f"\\subtitle{{{self._escape_latex(subtitle)}}}\n"
        
        latex += f"""\\author{{{self._escape_latex(author)}}}
\\date{{\\today}}

\\begin{{document}}

% Title slide
\\begin{{frame}}
\\titlepage
\\end{{frame}}

"""
        
        # Add outline slide if there are sections
        has_sections = any(slide.get('type') == 'section' for slide in slides)
        if has_sections or len(slides) > 5:
            latex += r"""% Outline
\begin{frame}{Outline}
\tableofcontents
\end{frame}

"""
        
        # Generate content slides
        current_section = None
        
        for i, slide in enumerate(slides):
            slide_type = slide.get('type', 'content')
            slide_title = slide.get('title', f'Slide {i+1}')
            points = slide.get('points', [])
            image_url = images[i] if i < len(images) else None
            
            # Add section if this is a new section
            if slide_type == 'section':
                latex += f"\\section{{{self._escape_latex(slide_title)}}}\n\n"
                current_section = slide_title
                continue
            
            # Start frame
            latex += f"\\begin{{frame}}{{{self._escape_latex(slide_title)}}}\n\n"
            
            # If we have both image and content, use two columns
            if image_url and points:
                latex += r"""\begin{columns}[T]
\column{0.5\textwidth}
"""
                # Add image
                latex += f"""\\begin{{figure}}
\\centering
\\includegraphics[width=\\textwidth]{{{image_url}}}
\\end{{figure}}

\\column{{0.5\\textwidth}}
"""
                # Add bullet points
                if points:
                    latex += "\\begin{itemize}\n"
                    for point in points:
                        latex += f"\\item {self._escape_latex(point)}\n"
                    latex += "\\end{itemize}\n"
                
                latex += "\\end{columns}\n"
                
            elif image_url:
                # Image only
                latex += f"""\\begin{{figure}}
\\centering
\\includegraphics[width=0.8\\textwidth]{{{image_url}}}
\\end{{figure}}
"""
            elif points:
                # Bullet points only
                latex += "\\begin{itemize}\n"
                for point in points:
                    latex += f"\\item {self._escape_latex(point)}\n"
                latex += "\\end{itemize}\n"
            
            # End frame
            latex += "\\end{frame}\n\n"
        
        # End document
        latex += "\\end{document}\n"
        
        return latex
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # Replace special characters
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
