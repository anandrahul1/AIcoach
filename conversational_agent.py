"""
Conversational Agent - Hybrid approach that adds intelligent conversation
while keeping the existing system intact.
"""

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
from datetime import datetime

class ConversationalCareerCoach:
    """
    A conversational agent that enhances the existing system with 
    intelligent, context-aware conversations about career development.
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatOpenAI(model="gpt-4o", api_key=api_key, temperature=0.7)
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # Remember last 10 exchanges
        )
        self.agent_executor = self._create_agent()
    
    def _create_tools(self):
        """Create tools that the agent can use"""
        
        def explain_analysis_tool(analysis_data: str) -> str:
            """Explain resume analysis results in conversational way"""
            try:
                analysis = json.loads(analysis_data) if isinstance(analysis_data, str) else analysis_data
                
                score = analysis.get('overall_score', 0)
                strengths = analysis.get('strengths', [])
                gaps = analysis.get('missing_skills', [])
                
                explanation = f"""
                Based on your resume analysis:
                
                📊 Your overall score is {score}/100. 
                
                🌟 Your strengths include: {', '.join(strengths[:3])}
                
                🎯 Areas to focus on: {', '.join(gaps[:3])}
                
                This gives me a good foundation to help you plan your next steps!
                """
                return explanation.strip()
            except:
                return "I can help explain your resume analysis once it's completed."
        
        def suggest_learning_path_tool(user_goal: str, current_skills: str = "", timeline: str = "") -> str:
            """Suggest personalized learning paths based on user goals"""
            
            prompt = f"""
            As a career coach, suggest a personalized learning path for someone who wants to: {user_goal}
            
            Their current skills: {current_skills}
            Their timeline: {timeline}
            
            Provide:
            1. Immediate next steps (this week)
            2. Short-term goals (1-3 months) 
            3. Long-term vision (6-12 months)
            4. Specific actionable advice
            
            Be encouraging and realistic.
            """
            
            response = self.llm.invoke(prompt)
            return response.content
        
        def motivational_coaching_tool(user_concern: str, progress_data: str = "") -> str:
            """Provide motivational coaching and address concerns"""
            
            prompt = f"""
            As an encouraging career coach, address this concern: {user_concern}
            
            Progress context: {progress_data}
            
            Provide:
            1. Acknowledgment of their concern
            2. Realistic perspective
            3. Actionable next steps
            4. Motivational encouragement
            
            Be empathetic, practical, and inspiring.
            """
            
            response = self.llm.invoke(prompt)
            return response.content
        
        def career_transition_advice_tool(current_role: str, target_role: str, experience_level: str = "") -> str:
            """Provide specific advice for career transitions"""
            
            prompt = f"""
            Help someone transition from {current_role} to {target_role}.
            Experience level: {experience_level}
            
            Provide:
            1. Key skills to develop
            2. Common transition challenges
            3. Timeline expectations
            4. Networking strategies
            5. Portfolio/project recommendations
            
            Be specific and actionable.
            """
            
            response = self.llm.invoke(prompt)
            return response.content
        
        def interview_prep_coaching_tool(role: str, experience_level: str, specific_concerns: str = "") -> str:
            """Provide interview preparation coaching"""
            
            prompt = f"""
            Help prepare for {role} interviews.
            Experience level: {experience_level}
            Specific concerns: {specific_concerns}
            
            Provide:
            1. Common interview questions for this role
            2. How to present experience effectively
            3. Technical preparation tips
            4. Confidence-building strategies
            5. Questions to ask the interviewer
            
            Be practical and confidence-building.
            """
            
            response = self.llm.invoke(prompt)
            return response.content
        
        return [
            Tool(
                name="explain_analysis",
                func=explain_analysis_tool,
                description="Explain resume analysis results in a conversational, easy-to-understand way"
            ),
            Tool(
                name="suggest_learning_path", 
                func=suggest_learning_path_tool,
                description="Create personalized learning paths based on user goals and timeline"
            ),
            Tool(
                name="motivational_coaching",
                func=motivational_coaching_tool,
                description="Provide encouragement and address user concerns about their career journey"
            ),
            Tool(
                name="career_transition_advice",
                func=career_transition_advice_tool,
                description="Give specific advice for transitioning between different roles"
            ),
            Tool(
                name="interview_prep_coaching",
                func=interview_prep_coaching_tool,
                description="Help users prepare for job interviews with role-specific guidance"
            )
        ]
    
    def _create_agent_prompt(self):
        """Create the agent prompt template"""
        
        system_message = """
        You are Euron, an expert AI Career Coach with years of experience helping people advance their careers.
        
        Your personality:
        - Encouraging and supportive, but realistic
        - Expert in technology careers (AI, software development, data, cloud)
        - Great at breaking down complex career paths into actionable steps
        - Always provide specific, practical advice
        - Remember context from previous conversations
        
        Your approach:
        1. Listen carefully to understand the user's situation
        2. Use available tools to provide detailed, personalized advice
        3. Always be encouraging while being honest about challenges
        4. Provide specific next steps, not just general advice
        5. Reference their resume analysis when relevant
        
        Available tools help you:
        - Explain resume analysis results clearly
        - Create personalized learning paths
        - Provide motivational coaching
        - Give career transition advice
        - Help with interview preparation
        
        Always end responses with a question to keep the conversation going and show you care about their progress.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    def _create_agent(self):
        """Create the conversational agent"""
        tools = self._create_tools()
        prompt = self._create_agent_prompt()
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=False,  # Set to True for debugging
            handle_parsing_errors=True,
            max_iterations=3  # Prevent infinite loops
        )
        
        return agent_executor
    
    def chat(self, user_message, context=None):
        """
        Main chat interface
        
        Args:
            user_message: User's message
            context: Optional context (resume analysis, learning plan, etc.)
        
        Returns:
            Agent's response
        """
        try:
            # Add context to the message if provided
            enhanced_message = user_message
            if context:
                enhanced_message = f"""
                Context: {json.dumps(context, indent=2)}
                
                User message: {user_message}
                """
            
            response = self.agent_executor.invoke({
                "input": enhanced_message
            })
            
            return response["output"]
            
        except Exception as e:
            return f"I apologize, but I encountered an issue: {str(e)}. Could you please rephrase your question?"
    
    def get_conversation_summary(self):
        """Get a summary of the current conversation"""
        try:
            messages = self.memory.chat_memory.messages
            if not messages:
                return "No conversation history yet."
            
            # Get last few messages for summary
            recent_messages = messages[-6:] if len(messages) > 6 else messages
            
            summary_prompt = """
            Summarize this career coaching conversation:
            
            """ + "\n".join([f"{msg.type}: {msg.content}" for msg in recent_messages]) + """
            
            Provide a brief summary of:
            1. Main topics discussed
            2. Key advice given
            3. User's goals/concerns
            """
            
            response = self.llm.invoke(summary_prompt)
            return response.content
            
        except Exception as e:
            return f"Unable to generate summary: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
    
    def suggest_follow_up_questions(self, last_response):
        """Suggest follow-up questions based on the conversation"""
        
        prompt = f"""
        Based on this career coaching response: "{last_response}"
        
        Suggest 3 relevant follow-up questions the user might want to ask.
        Make them specific and actionable.
        
        Format as a simple list.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except:
            return """
            Here are some questions you might want to ask:
            • What should I focus on first?
            • How long will this take?
            • What resources do you recommend?
            """

# Utility functions for integration
def create_career_coach(api_key):
    """Factory function to create a career coach agent"""
    return ConversationalCareerCoach(api_key)

def format_context_for_agent(analysis_result=None, learning_plan=None, user_profile=None):
    """Format context data for the agent"""
    context = {}
    
    if analysis_result:
        context["resume_analysis"] = {
            "overall_score": analysis_result.get("overall_score"),
            "strengths": analysis_result.get("strengths", []),
            "missing_skills": analysis_result.get("missing_skills", []),
            "selected": analysis_result.get("selected", False)
        }
    
    if learning_plan:
        context["learning_plan"] = [
            {
                "skill": plan[0],
                "current_level": plan[1], 
                "target_level": plan[2],
                "course": plan[3],
                "duration": plan[5]
            }
            for plan in learning_plan[:5]  # First 5 courses
        ]
    
    if user_profile:
        context["user_profile"] = user_profile
    
    return context