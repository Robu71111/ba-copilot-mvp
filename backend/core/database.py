import sqlite3
import json
from datetime import datetime
from pathlib import Path


class Database:
    """Database manager for BA Copilot"""
    
    def __init__(self, db_path="database/ba_copilot.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create database directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database tables
        self._initialize_tables()
    
    
    def _get_connection(self):
        """Create and return database connection"""
        return sqlite3.connect(self.db_path)
    
    
    def _initialize_tables(self):
        """Create all necessary tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_type TEXT,
                industry TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inputs table (raw transcripts/documents)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inputs (
                input_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                input_type TEXT,
                raw_text TEXT,
                file_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)
        
        # Requirements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                req_id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_id INTEGER,
                req_code TEXT,
                req_type TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (input_id) REFERENCES inputs(input_id)
            )
        """)
        
        # User stories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stories (
                story_id INTEGER PRIMARY KEY AUTOINCREMENT,
                req_id INTEGER,
                story_code TEXT,
                title TEXT,
                user_story TEXT,
                priority TEXT,
                story_points INTEGER,
                dependencies TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (req_id) REFERENCES requirements(req_id)
            )
        """)
        
        # Acceptance criteria table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acceptance_criteria (
                criteria_id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER,
                scenario_name TEXT,
                given_clause TEXT,
                when_clause TEXT,
                then_clause TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES user_stories(story_id)
            )
        """)
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                item_type TEXT,
                rating INTEGER,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    
    # ========================================
    # PROJECT OPERATIONS
    # ========================================
    
    def create_project(self, name, project_type="General", industry="General", description=""):
        """Create a new project"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (project_name, project_type, industry, description)
            VALUES (?, ?, ?, ?)
        """, (name, project_type, industry, description))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    
    def get_all_projects(self):
        """Retrieve all projects"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT project_id, project_name, project_type, industry, created_at
            FROM projects
            ORDER BY created_at DESC
        """)
        
        projects = cursor.fetchall()
        conn.close()
        
        return projects
    
    
    def get_project(self, project_id):
        """Get specific project details"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM projects WHERE project_id = ?
        """, (project_id,))
        
        project = cursor.fetchone()
        conn.close()
        
        return project
    
    
    def delete_project(self, project_id):
        """Delete a project and all related data"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Delete in reverse order of dependencies
        cursor.execute("DELETE FROM acceptance_criteria WHERE story_id IN (SELECT story_id FROM user_stories WHERE req_id IN (SELECT req_id FROM requirements WHERE input_id IN (SELECT input_id FROM inputs WHERE project_id = ?)))", (project_id,))
        cursor.execute("DELETE FROM user_stories WHERE req_id IN (SELECT req_id FROM requirements WHERE input_id IN (SELECT input_id FROM inputs WHERE project_id = ?))", (project_id,))
        cursor.execute("DELETE FROM requirements WHERE input_id IN (SELECT input_id FROM inputs WHERE project_id = ?)", (project_id,))
        cursor.execute("DELETE FROM inputs WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        
        conn.commit()
        conn.close()
    
    
    # ========================================
    # INPUT OPERATIONS
    # ========================================
    
    def save_input(self, project_id, input_type, raw_text, file_name=None):
        """Save raw input (transcript or document)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO inputs (project_id, input_type, raw_text, file_name)
            VALUES (?, ?, ?, ?)
        """, (project_id, input_type, raw_text, file_name))
        
        input_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return input_id
    
    
    # ========================================
    # REQUIREMENTS OPERATIONS
    # ========================================
    
    def save_requirements(self, input_id, requirements_list):
        """
        Save extracted requirements
    
        Args:
        input_id: ID of the input source
        requirements_list: List of dicts with keys: req_code, req_type, description
        """
        conn = self._get_connection()
        cursor = conn.cursor()
    
        try:
            for req in requirements_list:
                # Ensure all required fields exist
                req_code = req.get('req_code', 'UNKNOWN')
                req_type = req.get('req_type', 'Functional')
                description = req.get('description', '')
            
                cursor.execute("""
                INSERT INTO requirements (input_id, req_code, req_type, description)
                VALUES (?, ?, ?, ?)
                """, (input_id, req_code, req_type, description))
        
            conn.commit()
            print(f"Successfully saved {len(requirements_list)} requirements")
        except Exception as e:
            print(f"Error saving requirements: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    
    def get_requirements(self, input_id):
        """Get all requirements for an input"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT req_id, req_code, req_type, description
            FROM requirements
            WHERE input_id = ?
            ORDER BY req_code
        """, (input_id,))
        
        requirements = cursor.fetchall()
        conn.close()
        
        return requirements
    
    
    # ========================================
    # USER STORY OPERATIONS
    # ========================================
    
    def save_user_stories(self, req_id, stories_list):
        """
        Save generated user stories
        
        Args:
            req_id: ID of the requirement
            stories_list: List of dicts with story details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for story in stories_list:
            cursor.execute("""
                INSERT INTO user_stories 
                (req_id, story_code, title, user_story, priority, story_points, dependencies, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req_id,
                story.get('story_code'),
                story.get('title'),
                story.get('user_story'),
                story.get('priority'),
                story.get('story_points'),
                story.get('dependencies'),
                story.get('notes')
            ))
        
        conn.commit()
        conn.close()
    
    
    def get_user_stories(self, req_id=None):
        """Get user stories (all or for specific requirement)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if req_id:
            cursor.execute("""
                SELECT * FROM user_stories WHERE req_id = ?
                ORDER BY story_code
            """, (req_id,))
        else:
            cursor.execute("SELECT * FROM user_stories ORDER BY story_code")
        
        stories = cursor.fetchall()
        conn.close()
        
        return stories
    
    
    # ========================================
    # ACCEPTANCE CRITERIA OPERATIONS
    # ========================================
    
    def save_acceptance_criteria(self, story_id, criteria_list):
        """
        Save acceptance criteria
        
        Args:
            story_id: ID of the user story
            criteria_list: List of dicts with scenario details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for criteria in criteria_list:
            cursor.execute("""
                INSERT INTO acceptance_criteria 
                (story_id, scenario_name, given_clause, when_clause, then_clause)
                VALUES (?, ?, ?, ?, ?)
            """, (
                story_id,
                criteria.get('scenario_name'),
                criteria.get('given'),
                criteria.get('when'),
                criteria.get('then')
            ))
        
        conn.commit()
        conn.close()
    
    
    def get_acceptance_criteria(self, story_id):
        """Get acceptance criteria for a user story"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM acceptance_criteria WHERE story_id = ?
        """, (story_id,))
        
        criteria = cursor.fetchall()
        conn.close()
        
        return criteria
    
    
    # ========================================
    # UTILITY OPERATIONS
    # ========================================
    
    def get_project_summary(self, project_id):
        """Get complete summary of a project"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM inputs WHERE project_id = ?) as input_count,
                (SELECT COUNT(*) FROM requirements WHERE input_id IN 
                    (SELECT input_id FROM inputs WHERE project_id = ?)) as req_count,
                (SELECT COUNT(*) FROM user_stories WHERE req_id IN 
                    (SELECT req_id FROM requirements WHERE input_id IN 
                        (SELECT input_id FROM inputs WHERE project_id = ?))) as story_count
        """, (project_id, project_id, project_id))
        
        summary = cursor.fetchone()
        conn.close()
        
        return {
            'inputs': summary[0],
            'requirements': summary[1],
            'user_stories': summary[2]
        }


# Initialize database instance
db = Database()