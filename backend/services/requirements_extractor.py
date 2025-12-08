"""
Requirements Extractor Module
==============================
Extracts functional and non-functional requirements from raw text
using Google Gemini API.

This is STEP 1 in the BA workflow:
Input Text → Extract Requirements
"""

import google.generativeai as genai
from backend.core.config import APIConfig
from utils.prompts import PromptTemplates
import re


class RequirementsExtractor:
    """Extract requirements from raw text using AI"""
    
    def __init__(self):
        """Initialize Gemini API"""
        self.api_configured = False
        
        try:
            # Configure Gemini API
            genai.configure(api_key=APIConfig.GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=APIConfig.GEMINI_MODEL,
                generation_config=APIConfig.GEMINI_CONFIG
            )
            
            self.api_configured = True
        
        except Exception as e:
            print(f"Gemini API configuration error: {str(e)}")
    
    
    def extract(self, raw_text, project_type="General", industry="General"):
        """
        Extract requirements from raw text
    
        Args:
            raw_text: Meeting transcript or document text
            project_type: Type of project (Web, Mobile, Desktop, etc.)
            industry: Industry domain (Finance, Healthcare, etc.)
        
        Returns:
            Dictionary with extracted requirements
        """
        if not self.api_configured:
            raise Exception("Gemini API not configured. Please add API key to api_config.py")
    
        import time
        max_retries = 3
        retry_delay = 2  # seconds
    
        for attempt in range(max_retries):
            try:
                # Generate prompt
                prompt = PromptTemplates.requirements_extractor(raw_text, project_type, industry)
            
                # Call Gemini API
                print(f"Calling Gemini API (attempt {attempt + 1}/{max_retries})...")
                response = self.model.generate_content(prompt)
                raw_output = response.text
                print(f"Got response from Gemini: {len(raw_output)} characters")
            
                # Parse the response
                requirements = self._parse_requirements(raw_output)
                requirements['raw_output'] = raw_output
            
                # If parsing failed, try alternative parsing
                if requirements['total_count'] == 0:
                    print("Warning: Standard parsing found no requirements. Trying alternative parsing...")
                    requirements = self._alternative_parse(raw_output)
            
                return requirements
        
            except Exception as e:
                error_msg = str(e)
            
                # Check if it's a 503 overload error
                if "503" in error_msg or "overloaded" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                        print(f"Model overloaded. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("Max retries reached. Model is still overloaded.")
                        raise Exception("Gemini API is currently overloaded. Please try again in a few minutes.")
                else:
                    # Different error, don't retry
                    print(f"Requirements extraction error: {error_msg}")
                    raise Exception(f"Requirements extraction error: {error_msg}")
    
        raise Exception("Failed to extract requirements after multiple retries")
    
    def _parse_requirements(self, text):
        """
        Parse AI output into structured requirements
        
        Args:
            text: Raw AI response text
            
        Returns:
            Dictionary with functional and non-functional requirements
        """
        functional = []
        non_functional = []
        
        # Split text into sections
        sections = text.split('##')
        
        for section in sections:
            section = section.strip()
            
            # Check if this is functional requirements section
            if 'Functional Requirements' in section or 'FUNCTIONAL REQUIREMENTS' in section:
                functional = self._extract_requirement_items(section, 'FR')
            
            # Check if this is non-functional requirements section
            elif 'Non-Functional Requirements' in section or 'NON-FUNCTIONAL REQUIREMENTS' in section or 'Non Functional Requirements' in section:
                non_functional = self._extract_requirement_items(section, 'NFR')
        
        return {
            'functional': functional,
            'non_functional': non_functional,
            'total_count': len(functional) + len(non_functional)
        }
    
    
    def _extract_requirement_items(self, section_text, req_prefix):
        """
        Extract individual requirement items from a section
        
        Args:
            section_text: Text containing requirements
            req_prefix: Requirement prefix (FR or NFR)
            
        Returns:
            List of requirement dictionaries
        """
        requirements = []
        
        # Try multiple regex patterns
        patterns = [
            # Pattern 1: - FR-001: Description
            rf'[-*•]\s*({req_prefix}-\d+):\s*(.+?)(?=\n[-*•]\s*{req_prefix}-\d+:|\n##|\Z)',
            # Pattern 2: FR-001: Description (without bullet)
            rf'\n({req_prefix}-\d+):\s*(.+?)(?=\n{req_prefix}-\d+:|\n##|\Z)',
            # Pattern 3: **FR-001**: Description
            rf'\*\*({req_prefix}-\d+)\*\*:\s*(.+?)(?=\n\*\*{req_prefix}-\d+|\n##|\Z)',
        ]
        
        matches = []
        for pattern in patterns:
            matches = re.findall(pattern, section_text, re.MULTILINE | re.DOTALL)
            if matches:
                print(f"Found {len(matches)} requirements with pattern")
                break
        
        # If no matches found, try line-by-line parsing
        if not matches:
            print(f"No matches found with regex, trying line-by-line for {req_prefix}")
            lines = section_text.split('\n')
            for line in lines:
                line = line.strip()
                # Look for lines containing requirement codes
                if req_prefix in line and ':' in line:
                    match = re.search(rf'({req_prefix}-?\d+)[:.\s]+(.+)', line)
                    if match:
                        matches.append((match.group(1), match.group(2)))
        
        # Process all matches
        for idx, match in enumerate(matches, 1):
            try:
                if len(match) >= 2:
                    req_code = match[0].strip()
                    description = match[1].strip()
                    
                    # Ensure req_code has proper format
                    if '-' not in req_code:
                        req_code = f"{req_prefix}-{req_code}"
                    
                    # Clean up description
                    description = ' '.join(description.split())
                    
                    # Only add if description is meaningful
                    if description and len(description) > 10:
                        requirements.append({
                            'req_code': req_code,
                            'req_type': 'Functional' if req_prefix == 'FR' else 'Non-Functional',
                            'description': description
                        })
            except (IndexError, AttributeError) as e:
                print(f"Error processing match {idx}: {e}")
                continue
        
        return requirements
    
    
    def _alternative_parse(self, text):
        """
        Alternative parsing method if standard parsing fails
        
        Args:
            text: Raw AI response
            
        Returns:
            Dictionary with requirements
        """
        functional = []
        non_functional = []
        
        # Split by lines and look for any requirement-like patterns
        lines = text.split('\n')
        
        fr_count = 1
        nfr_count = 1
        in_functional_section = False
        in_nonfunctional_section = False
        
        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if 'Functional Requirements' in line or 'FUNCTIONAL REQUIREMENTS' in line:
                in_functional_section = True
                in_nonfunctional_section = False
                continue
            elif 'Non-Functional Requirements' in line or 'NON-FUNCTIONAL REQUIREMENTS' in line:
                in_functional_section = False
                in_nonfunctional_section = True
                continue
            elif line.startswith('##'):
                in_functional_section = False
                in_nonfunctional_section = False
                continue
            
            # Extract requirements
            if line and len(line) > 20 and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                description = line.lstrip('-*•').strip()
                
                if in_functional_section:
                    functional.append({
                        'req_code': f'FR-{fr_count:03d}',
                        'req_type': 'Functional',
                        'description': description
                    })
                    fr_count += 1
                elif in_nonfunctional_section:
                    non_functional.append({
                        'req_code': f'NFR-{nfr_count:03d}',
                        'req_type': 'Non-Functional',
                        'description': description
                    })
                    nfr_count += 1
        
        return {
            'functional': functional,
            'non_functional': non_functional,
            'total_count': len(functional) + len(non_functional)
        }
    
    
    def format_for_display(self, requirements):
        """
        Format requirements for display in UI
        
        Args:
            requirements: Dictionary from extract() method
            
        Returns:
            Formatted string for display
        """
        output = []
        
        # Functional requirements
        if requirements['functional']:
            output.append("## 📋 Functional Requirements\n")
            for req in requirements['functional']:
                output.append(f"**{req['req_code']}**: {req['description']}\n")
        
        # Non-functional requirements
        if requirements['non_functional']:
            output.append("\n## ⚙️ Non-Functional Requirements\n")
            for req in requirements['non_functional']:
                output.append(f"**{req['req_code']}**: {req['description']}\n")
        
        # Summary
        output.append(f"\n---\n**Total Requirements**: {requirements['total_count']} ")
        output.append(f"({len(requirements['functional'])} Functional, {len(requirements['non_functional'])} Non-Functional)")
        
        return '\n'.join(output)
    
    
    def is_configured(self):
        """Check if API is properly configured"""
        return self.api_configured


# Initialize extractor instance
extractor = RequirementsExtractor()