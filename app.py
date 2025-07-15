#!/usr/bin/env python3
"""
Recruitment Agent Web Application
Simple Flask app demonstrating Bedrock Agent integration
"""

from flask import Flask, render_template, request, jsonify, session
import os
import uuid
from bedrock_integration import BedrockAgentIntegration
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'recruitment-agent-demo-key')

# Initialize Bedrock integration
bedrock = BedrockAgentIntegration()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for agent interaction"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        agent_type = data.get('agent', 'supervisor')  # supervisor, resume_parser, resume_reviewer
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create session ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        # Select agent
        agent_id = bedrock.agents.get(agent_type, bedrock.agents['supervisor'])
        
        # Invoke agent
        result = bedrock.invoke_agent(agent_id, message, session['session_id'])
        
        if result['success']:
            return jsonify({
                'response': result['response'],
                'agent': agent_type,
                'session_id': result['session_id']
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    """Resume analysis endpoint"""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        target_role = data.get('target_role', '')
        
        if not resume_text:
            return jsonify({'error': 'Resume text is required'}), 400
        
        result = bedrock.analyze_resume(resume_text, target_role)
        
        if result['success']:
            return jsonify({
                'analysis': result['response'],
                'session_id': result['session_id']
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/career-guidance', methods=['POST'])
def career_guidance():
    """Career guidance endpoint"""
    try:
        data = request.get_json()
        user_profile = data.get('profile', {})
        
        result = bedrock.get_career_guidance(user_profile)
        
        if result['success']:
            return jsonify({
                'guidance': result['response'],
                'session_id': result['session_id']
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning-plan', methods=['POST'])
def learning_plan():
    """Learning plan generation endpoint"""
    try:
        data = request.get_json()
        skills_gap = data.get('skills_gap', [])
        target_role = data.get('target_role', '')
        
        if not skills_gap or not target_role:
            return jsonify({'error': 'Skills gap and target role are required'}), 400
        
        result = bedrock.generate_learning_plan(skills_gap, target_role)
        
        if result['success']:
            return jsonify({
                'plan': result['response'],
                'session_id': result['session_id']
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agents': list(bedrock.agents.keys()),
        'knowledge_base': bedrock.knowledge_base_id
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting Recruitment Agent Application...")
    print("📊 Available agents:", list(bedrock.agents.keys()))
    print("🧠 Knowledge Base ID:", bedrock.knowledge_base_id)
    print("🌐 Access the app at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)