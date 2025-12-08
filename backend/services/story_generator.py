"""
User Story Generator Module
============================
Converts requirements into Agile user stories (Scrum format)
using Google Gemini API.

This is STEP 2 in the BA workflow:
Requirements → Generate User Stories
"""

import google.generativeai as genai
from backend.core.config import APIConfig
from utils.prompts import PromptTemplates
import re


class UserStoryGenerator:
    """Generate Agile user stories from requirements"""
    
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
    
    
    def generate(self, requirements_text, project_type="General"):
        """
        Generate user stories from requirements
        
        Args:
            requirements_text: Formatted requirements text
            project_type: Type of project
            
        Returns:
            Dictionary with user stories:
            {
                'stories': [
                    {
                        'story_code': 'US-001',
                        'title': '...',
                        'user_story': 'As a... I want... so that...',
                        'priority': 'High',
                        'story_points': 3,
                        'dependencies': 'US-002',
                        'notes': '...'
                    }
                ],
                'raw_output': 'Full AI response'
            }
        """
        if not self.api_configured:
            raise Exception("Gemini API not configured. Please add API key to api_config.py")
        
        try:
            # Generate prompt
            prompt = PromptTemplates.user_story_generator(requirements_text, project_type)
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            raw_output = response.text
            
            # Parse the response
            stories = self._parse_user_stories(raw_output)
            
            return {
                'stories': stories,
                'raw_output': raw_output,
                'total_count': len(stories)
            }
        
        except Exception as e:
            raise Exception(f"User story generation error: {str(e)}")
    
    
    def _parse_user_stories(self, text):
        """
        Parse AI output into structured user stories
        
        Args:
            text: Raw AI response text
            
        Returns:
            List of user story dictionaries
        """
        stories = []
        
        # Split by story separator (---)
        story_blocks = re.split(r'\n---+\n', text)
        
        for block in story_blocks:
            block = block.strip()
            if not block or len(block) < 50:
                continue
            
            story = self._extract_story_fields(block)
            if story and story.get('story_code'):
                stories.append(story)
        
        return stories
    
    
    def _extract_story_fields(self, block):
        """
        Extract individual fields from a user story block
        
        Args:
            block: Text containing one user story
            
        Returns:
            Dictionary with story fields
        """
        story = {
            'story_code': '',
            'title': '',
            'user_story': '',
            'priority': 'Medium',
            'story_points': 0,
            'dependencies': 'None',
            'notes': ''
        }
        
        # Extract Story ID
        story_id_match = re.search(r'\*\*Story ID\*\*:\s*(US-\d+)', block, re.IGNORECASE)
        if story_id_match:
            story['story_code'] = story_id_match.group(1)
        
        # Extract Title
        title_match = re.search(r'\*\*Title\*\*:\s*(.+?)(?=\n\*\*|\n|$)', block, re.IGNORECASE)
        if title_match:
            story['title'] = title_match.group(1).strip()
        
        # Extract User Story
        user_story_match = re.search(r'\*\*User Story\*\*:\s*(.+?)(?=\n\*\*|\n---|\Z)', block, re.IGNORECASE | re.DOTALL)
        if user_story_match:
            story['user_story'] = ' '.join(user_story_match.group(1).strip().split())
        
        # Extract Priority
        priority_match = re.search(r'\*\*Priority\*\*:\s*(High|Medium|Low)', block, re.IGNORECASE)
        if priority_match:
            story['priority'] = priority_match.group(1).capitalize()
        
        # Extract Story Points
        points_match = re.search(r'\*\*Story Points\*\*:\s*(\d+)', block, re.IGNORECASE)
        if points_match:
            story['story_points'] = int(points_match.group(1))
        
        # Extract Dependencies
        deps_match = re.search(r'\*\*Dependencies\*\*:\s*(.+?)(?=\n\*\*|\n|$)', block, re.IGNORECASE)
        if deps_match:
            story['dependencies'] = deps_match.group(1).strip()
        
        # Extract Notes
        notes_match = re.search(r'\*\*Notes\*\*:\s*(.+?)(?=\n\*\*|\n---|\Z)', block, re.IGNORECASE | re.DOTALL)
        if notes_match:
            story['notes'] = ' '.join(notes_match.group(1).strip().split())
        
        return story
    
    
    def format_for_display(self, stories_data):
        """
        Format user stories for display in UI
        
        Args:
            stories_data: Dictionary from generate() method
            
        Returns:
            Formatted string for display
        """
        output = []
        
        output.append("## 📖 User Stories\n")
        
        for story in stories_data['stories']:
            output.append(f"### {story['story_code']}: {story['title']}\n")
            output.append(f"**User Story**: {story['user_story']}\n")
            output.append(f"**Priority**: {story['priority']} | **Story Points**: {story['story_points']} | **Dependencies**: {story['dependencies']}\n")
            
            if story['notes']:
                output.append(f"**Notes**: {story['notes']}\n")
            
            output.append("\n---\n")
        
        # Summary
        output.append(f"\n**Total User Stories**: {stories_data['total_count']}")
        
        return '\n'.join(output)
    
    
    def format_for_jira(self, stories_data):
        """
        Format user stories for JIRA import (CSV format)
        
        Args:
            stories_data: Dictionary from generate() method
            
        Returns:
            CSV formatted string
        """
        csv_lines = ["Summary,Description,Priority,Story Points,Issue Type"]
        
        for story in stories_data['stories']:
            summary = story['title']
            description = story['user_story']
            priority = story['priority']
            points = story['story_points']
            
            csv_lines.append(f'"{summary}","{description}",{priority},{points},Story')
        
        return '\n'.join(csv_lines)
    
    
    def is_configured(self):
        """Check if API is properly configured"""
        return self.api_configured


# Initialize generator instance
story_gen = UserStoryGenerator()