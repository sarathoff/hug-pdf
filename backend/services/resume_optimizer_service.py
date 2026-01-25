import os
import logging
from typing import Dict, Optional
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ResumeOptimizerService:
    """Service for optimizing resumes for ATS compatibility"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def optimize_resume(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Optimize resume for ATS compatibility
        
        Args:
            resume_text: Extracted text from resume PDF
            job_description: Optional job description for role-specific optimization
            
        Returns:
            Dictionary with optimized LaTeX, ATS score, and improvements
        """
        try:
            logger.info(f"Optimizing resume ({len(resume_text)} chars)")
            
            # Build optimization prompt
            if job_description:
                prompt = self._build_job_specific_prompt(resume_text, job_description)
            else:
                prompt = self._build_general_optimization_prompt(resume_text)
            
            # Generate optimized resume using Gemini
            response = self.gemini_service.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            latex_content = response.text.strip()
            
            # Clean markdown code blocks if present
            if latex_content.startswith('```latex'):
                latex_content = latex_content[8:]
            elif latex_content.startswith('```'):
                latex_content = latex_content[3:]
            if latex_content.endswith('```'):
                latex_content = latex_content[:-3]
            
            # Calculate ATS score
            ats_score = self._calculate_ats_score(resume_text, job_description, latex_content)
            
            # Extract improvements made
            improvements = self._extract_improvements(resume_text, latex_content, job_description)
            
            return {
                'latex': latex_content.strip(),
                'ats_score': ats_score,
                'improvements': improvements,
                'message': 'Resume optimized successfully for ATS compatibility'
            }
            
        except Exception as e:
            logger.error(f"Error optimizing resume: {str(e)}")
            return None
    
    def _build_job_specific_prompt(self, resume_text: str, job_description: str) -> str:
        """Build prompt for job-specific optimization"""
        return f"""
You are an expert resume writer and ATS optimization specialist. Optimize this resume for the following job description.

JOB DESCRIPTION:
{job_description[:3000]}

CURRENT RESUME:
{resume_text[:10000]}

OPTIMIZATION REQUIREMENTS:
1. **Keyword Matching**: Extract key skills, technologies, and requirements from the job description and naturally incorporate them into the resume
2. **Quantify Achievements**: Add metrics and numbers to achievements (e.g., "Increased sales by 30%", "Managed team of 5")
3. **ATS-Friendly Formatting**: Use clean, simple LaTeX formatting that ATS systems can parse
4. **Action Verbs**: Start bullet points with strong action verbs (Led, Developed, Implemented, Achieved)
5. **Relevance**: Highlight experience and skills most relevant to the job description
6. **Remove Irrelevant**: Remove or minimize information not relevant to the role
7. **Standard Sections**: Use standard section headers (Experience, Education, Skills, etc.)

CRITICAL LATEX REQUIREMENTS:
1. Use \\usepackage{{lmodern}} and \\usepackage[margin=1in]{{geometry}}
2. NO graphics, tables, or complex formatting (ATS-unfriendly)
3. Use simple \\section{{}} and \\subsection{{}} commands
4. Use \\textbf{{}} for emphasis, not fancy fonts
5. Return ONLY the complete LaTeX document, no explanations

Generate an ATS-optimized professional resume in LaTeX format:
"""
    
    def _build_general_optimization_prompt(self, resume_text: str) -> str:
        """Build prompt for general ATS optimization"""
        return f"""
You are an expert resume writer and ATS optimization specialist. Optimize this resume for maximum ATS compatibility.

CURRENT RESUME:
{resume_text[:10000]}

OPTIMIZATION REQUIREMENTS:
1. **ATS-Friendly Formatting**: Use clean, simple LaTeX formatting that ATS systems can parse
2. **Quantify Achievements**: Add metrics and numbers to achievements where possible
3. **Action Verbs**: Start bullet points with strong action verbs
4. **Standard Sections**: Use standard section headers (Experience, Education, Skills, Certifications)
5. **Keywords**: Ensure industry-standard keywords are present
6. **Clean Structure**: Clear hierarchy and organization
7. **Professional Tone**: Maintain professional language throughout

CRITICAL LATEX REQUIREMENTS:
1. Use \\usepackage{{lmodern}} and \\usepackage[margin=1in]{{geometry}}
2. NO graphics, tables, or complex formatting (ATS-unfriendly)
3. Use simple \\section{{}} and \\subsection{{}} commands
4. Use \\textbf{{}} for emphasis, not fancy fonts
5. Return ONLY the complete LaTeX document, no explanations

Generate an ATS-optimized professional resume in LaTeX format:
"""
    
    def _calculate_ats_score(
        self, 
        original_text: str, 
        job_description: Optional[str],
        optimized_latex: str
    ) -> int:
        """
        Calculate ATS compatibility score (0-100)
        
        Scoring factors:
        - Keyword match (if job description provided): 30%
        - Formatting quality: 25%
        - Completeness: 20%
        - Quantification: 15%
        - Relevance: 10%
        """
        score = 0
        
        # Base score for having content
        score += 40
        
        # Check for quantified achievements (numbers/percentages)
        import re
        numbers = re.findall(r'\d+%|\d+\+', optimized_latex)
        if len(numbers) >= 3:
            score += 15
        elif len(numbers) >= 1:
            score += 10
        
        # Check for standard sections
        standard_sections = ['Experience', 'Education', 'Skills']
        sections_found = sum(1 for section in standard_sections if section.lower() in optimized_latex.lower())
        score += sections_found * 5
        
        # Check for action verbs
        action_verbs = ['Led', 'Developed', 'Implemented', 'Managed', 'Created', 'Designed', 'Achieved']
        verbs_found = sum(1 for verb in action_verbs if verb in optimized_latex)
        score += min(verbs_found * 2, 10)
        
        # Keyword matching bonus if job description provided
        if job_description:
            # Simple keyword matching
            job_keywords = set(job_description.lower().split())
            resume_keywords = set(optimized_latex.lower().split())
            match_ratio = len(job_keywords & resume_keywords) / max(len(job_keywords), 1)
            score += int(match_ratio * 20)
        
        return min(score, 100)
    
    def _extract_improvements(
        self,
        original_text: str,
        optimized_latex: str,
        job_description: Optional[str]
    ) -> list:
        """Extract list of improvements made"""
        improvements = []
        
        import re
        
        # Check for quantification
        original_numbers = re.findall(r'\d+%|\d+\+', original_text)
        optimized_numbers = re.findall(r'\d+%|\d+\+', optimized_latex)
        if len(optimized_numbers) > len(original_numbers):
            improvements.append("Added quantified achievements with metrics")
        
        # Check for ATS-friendly formatting
        if '\\section{' in optimized_latex:
            improvements.append("Improved formatting for ATS compatibility")
        
        # Check for job-specific optimization
        if job_description:
            improvements.append("Tailored content to match job requirements")
            improvements.append("Added relevant keywords from job description")
        
        # Check for action verbs
        action_verbs = ['Led', 'Developed', 'Implemented', 'Managed', 'Created']
        if any(verb in optimized_latex for verb in action_verbs):
            improvements.append("Enhanced bullet points with strong action verbs")
        
        if not improvements:
            improvements.append("Optimized overall structure and formatting")
        
        return improvements
