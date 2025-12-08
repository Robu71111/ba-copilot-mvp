"""
AI Prompt Templates
===================
Contains all prompt templates for different BA tasks.
These prompts are optimized for Gemini API.
"""


class PromptTemplates:
    """Collection of all AI prompt templates"""
    
    @staticmethod
    def requirements_extractor(raw_text, project_type="General", industry="General"):
        """
        Prompt for extracting requirements from raw text
        
        Args:
            raw_text: Meeting transcript or document text
            project_type: Type of project (Web, Mobile, Desktop, etc.)
            industry: Industry domain (Finance, Healthcare, E-commerce, etc.)
        """
        return f"""You are an expert Business Analyst with 15+ years of experience in requirements engineering.

CONTEXT:
Project Type: {project_type}
Industry: {industry}

TASK:
Analyze the following text and extract ALL requirements. Be thorough and identify both explicit and implicit requirements.

TEXT TO ANALYZE:
{raw_text}

INSTRUCTIONS:
1. Extract every requirement mentioned or implied
2. Classify each as Functional (FR) or Non-Functional (NFR)
3. Make each requirement:
   - Specific and measurable
   - Testable and verifiable
   - Clear and unambiguous
4. Use unique sequential IDs (FR-001, FR-002, NFR-001, etc.)
5. Include both what's explicitly stated and logically implied

OUTPUT FORMAT (Strict):
## Functional Requirements
- FR-001: [Clear, actionable requirement description]
- FR-002: [Clear, actionable requirement description]
- FR-003: [Clear, actionable requirement description]

## Non-Functional Requirements
- NFR-001: [Performance/Security/Usability requirement]
- NFR-002: [Performance/Security/Usability requirement]

EXAMPLE OUTPUT:
## Functional Requirements
- FR-001: User shall be able to log in using email and password
- FR-002: System shall send password reset link to registered email within 5 minutes
- FR-003: Dashboard shall display user's last 30 days of activity

## Non-Functional Requirements
- NFR-001: Login response time shall not exceed 2 seconds under normal load
- NFR-002: System shall support at least 1000 concurrent users
- NFR-003: All passwords shall be encrypted using bcrypt with minimum 12 character length

Now analyze the provided text and extract requirements:"""


    @staticmethod
    def user_story_generator(requirements, project_type="General"):
        """
        Prompt for generating Agile user stories from requirements
        
        Args:
            requirements: List of extracted requirements
            project_type: Type of project
        """
        return f"""You are an expert Scrum Master and Agile Coach specializing in writing perfect user stories.

CONTEXT:
Project Type: {project_type}

REQUIREMENTS:
{requirements}

TASK:
Convert each requirement into a well-structured Agile User Story following Scrum best practices.

INSTRUCTIONS:
1. Follow the format: "As a [role], I want [feature], so that [business value]"
2. Keep stories small, independent, and testable (INVEST criteria)
3. Focus on USER VALUE, not technical implementation
4. Use appropriate personas: End User, Admin, Business Analyst, System, Guest
5. Estimate story points (1, 2, 3, 5, 8, 13)
6. Identify dependencies between stories

OUTPUT FORMAT (Strict):
**Story ID**: US-001
**Title**: [Concise title - max 6 words]
**User Story**: As a [role], I want [feature], so that [business value]
**Priority**: High / Medium / Low
**Story Points**: [1, 2, 3, 5, 8, 13]
**Dependencies**: [US-XXX or None]
**Notes**: [Any additional context]

---

EXAMPLE OUTPUT:
**Story ID**: US-001
**Title**: User Login Functionality
**User Story**: As an end user, I want to log in using my email and password, so that I can securely access my personalized dashboard and account information.
**Priority**: High
**Story Points**: 3
**Dependencies**: None
**Notes**: Foundation for all authenticated features

---

**Story ID**: US-002
**Title**: Password Reset via Email
**User Story**: As an end user, I want to receive a password reset link via email, so that I can regain access to my account if I forget my password.
**Priority**: High
**Story Points**: 5
**Dependencies**: US-001
**Notes**: Must include email verification and link expiration (24 hours)

---

Now generate user stories for all requirements:"""


    @staticmethod
    def acceptance_criteria_generator(user_story):
        """
        Prompt for generating acceptance criteria from user story
        
        Args:
            user_story: Single user story text
        """
        return f"""You are an expert QA Engineer and Test Analyst specializing in behavior-driven development (BDD).

USER STORY:
{user_story}

TASK:
Generate comprehensive acceptance criteria using Given-When-Then (Gherkin) format.

INSTRUCTIONS:
1. Create at least 3-5 scenarios covering:
   - Happy path (successful flow)
   - Alternative paths (different valid flows)
   - Edge cases (boundary conditions)
   - Error scenarios (validation failures)
2. Each scenario must be:
   - Testable and specific
   - Independent from other scenarios
   - Clear about expected outcomes
3. Include UI/UX expectations where relevant
4. Specify validation rules and error messages

OUTPUT FORMAT (Strict):
**Scenario 1: [Scenario Name - Happy Path]**
- GIVEN [initial context/state]
- AND [additional context if needed]
- WHEN [user action or event trigger]
- AND [additional action if needed]
- THEN [expected outcome]
- AND [additional outcome if needed]

**Scenario 2: [Scenario Name - Alternative Path]**
- GIVEN [different context]
- WHEN [different action]
- THEN [different outcome]

**Scenario 3: [Scenario Name - Error Handling]**
- GIVEN [error condition]
- WHEN [action attempted]
- THEN [error message or behavior]

EXAMPLE OUTPUT:
**Scenario 1: Successful Login with Valid Credentials**
- GIVEN the user is on the login page
- AND has a registered account with verified email
- WHEN the user enters correct email "user@example.com"
- AND enters correct password
- AND clicks the "Login" button
- THEN the system authenticates the user successfully
- AND redirects to the dashboard page
- AND displays welcome message "Welcome back, [Username]!"
- AND sets session token with 24-hour expiration

**Scenario 2: Login Attempt with Invalid Password**
- GIVEN the user is on the login page
- AND has a registered account
- WHEN the user enters correct email
- AND enters incorrect password
- AND clicks the "Login" button
- THEN the system displays error message "Invalid email or password"
- AND the password field is cleared
- AND the email field retains the entered value
- AND the user remains on the login page
- AND the failed attempt is logged for security

**Scenario 3: Login Attempt with Unregistered Email**
- GIVEN the user is on the login page
- WHEN the user enters an email that is not registered
- AND enters any password
- AND clicks the "Login" button
- THEN the system displays error message "Invalid email or password"
- AND does not reveal whether email exists (security measure)
- AND suggests "Forgot password?" or "Sign up" options

**Scenario 4: Account Locked After Multiple Failed Attempts**
- GIVEN the user has failed login 5 times consecutively
- WHEN the user attempts to log in again
- THEN the system displays message "Account temporarily locked. Please try again in 30 minutes or reset your password"
- AND sends security alert email to registered email address
- AND prevents any login attempts for 30 minutes
- AND logs the security event

**Scenario 5: Login Form Validation**
- GIVEN the user is on the login page
- WHEN the user clicks "Login" without entering credentials
- THEN the system displays validation error "Email is required"
- AND displays validation error "Password is required"
- AND prevents form submission
- AND highlights the empty fields in red

Now generate acceptance criteria for the provided user story:"""


    @staticmethod
    def summarize_meeting(transcript):
        """
        Prompt for summarizing meeting transcripts
        
        Args:
            transcript: Raw meeting transcript
        """
        return f"""You are an expert Business Analyst specializing in meeting documentation and analysis.

MEETING TRANSCRIPT:
{transcript}

TASK:
Create a comprehensive meeting summary that captures all important information.

OUTPUT FORMAT:
## Meeting Summary
[2-3 sentence executive summary of the meeting]

## Key Discussion Points
- [Point 1]
- [Point 2]
- [Point 3]

## Decisions Made
- [Decision 1 with rationale]
- [Decision 2 with rationale]

## Action Items
- [Action 1] - Owner: [Name] - Due: [Date]
- [Action 2] - Owner: [Name] - Due: [Date]

## Open Questions / Risks
- [Question or risk 1]
- [Question or risk 2]

## Next Steps
- [Step 1]
- [Step 2]

Now summarize the provided transcript:"""