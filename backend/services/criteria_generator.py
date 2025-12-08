"""
Acceptance Criteria Generator Module
=====================================
Generates Given-When-Then acceptance criteria from user stories
using Google Gemini API.

This is STEP 3 in the BA workflow:
User Stories → Generate Acceptance Criteria
"""

import google.generativeai as genai
from backend.core.config import APIConfig
from utils.prompts import PromptTemplates
import re


class AcceptanceCriteriaGenerator:
    """Generate acceptance criteria from user stories"""
    
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
    
    
    def generate(self, user_story_text):
        """
        Generate acceptance criteria for a user story
        
        Args:
            user_story_text: Single user story text
            
        Returns:
            Dictionary with acceptance criteria:
            {
                'criteria': [
                    {
                        'scenario_name': 'Successful Login',
                        'given': 'the user is on login page AND has valid credentials',
                        'when': 'the user enters email and password AND clicks Login',
                        'then': 'system authenticates user AND redirects to dashboard'
                    }
                ],
                'raw_output': 'Full AI response'
            }
        """
        if not self.api_configured:
            raise Exception("Gemini API not configured. Please add API key to api_config.py")
        
        try:
            # Generate prompt
            prompt = PromptTemplates.acceptance_criteria_generator(user_story_text)
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            raw_output = response.text
            
            # Parse the response
            criteria = self._parse_criteria(raw_output)
            
            return {
                'criteria': criteria,
                'raw_output': raw_output,
                'total_scenarios': len(criteria)
            }
        
        except Exception as e:
            raise Exception(f"Acceptance criteria generation error: {str(e)}")
    
    
    def _parse_criteria(self, text):
        """
        Parse AI output into structured acceptance criteria
        
        Args:
            text: Raw AI response text
            
        Returns:
            List of criteria dictionaries
        """
        criteria_list = []
        
        # Split by scenario headers
        scenario_pattern = r'\*\*Scenario \d+:([^*]+)\*\*'
        scenarios = re.split(scenario_pattern, text)
        
        # Process scenarios (skip first element which is usually empty or intro)
        for i in range(1, len(scenarios), 2):
            if i + 1 < len(scenarios):
                scenario_name = scenarios[i].strip()
                scenario_content = scenarios[i + 1].strip()
                
                criteria = self._extract_given_when_then(scenario_name, scenario_content)
                if criteria:
                    criteria_list.append(criteria)
        
        return criteria_list
    
    
    def _extract_given_when_then(self, scenario_name, content):
        """
        Extract GIVEN-WHEN-THEN clauses from scenario content
        
        Args:
            scenario_name: Name of the scenario
            content: Content containing GIVEN-WHEN-THEN
            
        Returns:
            Dictionary with criteria fields
        """
        criteria = {
            'scenario_name': scenario_name,
            'given': '',
            'when': '',
            'then': ''
        }
        
        # Extract GIVEN clauses
        given_pattern = r'-\s*GIVEN\s+(.+?)(?=-\s*(?:AND|WHEN)|$)'
        given_matches = re.findall(given_pattern, content, re.IGNORECASE | re.DOTALL)
        
        # Extract AND clauses after GIVEN
        given_and_pattern = r'(?:GIVEN.+?)-\s*AND\s+(.+?)(?=-\s*WHEN)'
        given_and_matches = re.findall(given_and_pattern, content, re.IGNORECASE | re.DOTALL)
        
        all_given = given_matches + given_and_matches
        if all_given:
            criteria['given'] = ' AND '.join([' '.join(g.strip().split()) for g in all_given])
        
        # Extract WHEN clauses
        when_pattern = r'-\s*WHEN\s+(.+?)(?=-\s*(?:AND|THEN)|$)'
        when_matches = re.findall(when_pattern, content, re.IGNORECASE | re.DOTALL)
        
        # Extract AND clauses after WHEN
        when_and_pattern = r'(?:WHEN.+?)-\s*AND\s+(.+?)(?=-\s*THEN)'
        when_and_matches = re.findall(when_and_pattern, content, re.IGNORECASE | re.DOTALL)
        
        all_when = when_matches + when_and_matches
        if all_when:
            criteria['when'] = ' AND '.join([' '.join(w.strip().split()) for w in all_when])
        
        # Extract THEN clauses
        then_pattern = r'-\s*THEN\s+(.+?)(?=-\s*(?:AND|\*\*)|$)'
        then_matches = re.findall(then_pattern, content, re.IGNORECASE | re.DOTALL)
        
        # Extract AND clauses after THEN
        then_and_pattern = r'(?:THEN.+?)-\s*AND\s+(.+?)(?=-\s*\*\*|\Z)'
        then_and_matches = re.findall(then_and_pattern, content, re.IGNORECASE | re.DOTALL)
        
        all_then = then_matches + then_and_matches
        if all_then:
            criteria['then'] = ' AND '.join([' '.join(t.strip().split()) for t in all_then])
        
        # Only return if we have all three components
        if criteria['given'] and criteria['when'] and criteria['then']:
            return criteria
        
        return None
    
    
    def format_for_display(self, criteria_data):
        """
        Format acceptance criteria for display in UI
        
        Args:
            criteria_data: Dictionary from generate() method
            
        Returns:
            Formatted string for display
        """
        output = []
        
        output.append("## ✅ Acceptance Criteria (Given-When-Then)\n")
        
        for idx, criteria in enumerate(criteria_data['criteria'], 1):
            output.append(f"### Scenario {idx}: {criteria['scenario_name']}\n")
            output.append(f"**GIVEN** {criteria['given']}\n")
            output.append(f"**WHEN** {criteria['when']}\n")
            output.append(f"**THEN** {criteria['then']}\n")
            output.append("\n---\n")
        
        # Summary
        output.append(f"\n**Total Scenarios**: {criteria_data['total_scenarios']}")
        
        return '\n'.join(output)
    
    
    def format_for_gherkin(self, criteria_data, feature_name="User Story"):
        """
        Format acceptance criteria in Gherkin syntax for BDD tools
        
        Args:
            criteria_data: Dictionary from generate() method
            feature_name: Name of the feature
            
        Returns:
            Gherkin formatted string
        """
        output = [f"Feature: {feature_name}\n"]
        
        for criteria in criteria_data['criteria']:
            output.append(f"  Scenario: {criteria['scenario_name']}")
            output.append(f"    Given {criteria['given']}")
            output.append(f"    When {criteria['when']}")
            output.append(f"    Then {criteria['then']}")
            output.append("")
        
        return '\n'.join(output)
    
    
    def is_configured(self):
        """Check if API is properly configured"""
        return self.api_configured


# Initialize generator instance
criteria_gen = AcceptanceCriteriaGenerator()