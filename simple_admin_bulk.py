"""
Simple Admin Bulk Resume Analysis - Step 1
Basic bulk upload and analysis functionality
"""

import streamlit as st
import sqlite3
import tempfile
import os
from datetime import datetime
import json
from agents import ResumeAnalysisAgent

def init_admin_tables():
    """Initialize simple admin tables"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    # Simple admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Simple bulk results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bulk_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            job_role TEXT,
            filename TEXT,
            score INTEGER,
            selected BOOLEAN,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def make_admin(user_id):
    """Make user an admin"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO admin_users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def is_admin(user_id):
    """Check if user is admin"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM admin_users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()[0] > 0
    conn.close()
    return result

def simple_admin_page(api_key, user_id):
    """Simple admin interface"""
    st.subheader("👨‍💼 Admin: Bulk Resume Analysis")
    
    # Initialize tables
    init_admin_tables()
    
    # Check admin status
    if not is_admin(user_id):
        st.error("❌ Admin access required")
        if st.button("Grant Admin Access (Demo)"):
            make_admin(user_id)
            st.success("✅ Admin access granted!")
            st.rerun()
        return
    
    st.success("✅ Admin access confirmed")
    
    # Job role selection
    job_role = st.selectbox(
        "Select Job Role for Analysis",
        ["AWS Fullstack Developer", "AI Engineer", "AWS Python Developer", 
         "AWS Data Engineer", "Frontend Engineer", "Backend Engineer"]
    )
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload Resume Files",
        type=['pdf', 'txt', 'docx'],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("🚀 Analyze Resumes"):
        if not api_key:
            st.error("Please enter OpenAI API key")
            return
            
        # Initialize analyzer
        analyzer = ResumeAnalysisAgent(api_key=api_key)
        
        # Progress tracking
        progress_bar = st.progress(0)
        results = []
        
        # Analyze each resume
        for i, uploaded_file in enumerate(uploaded_files):
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            try:
                # Analyze resume
                analysis = analyzer.analyze_resume(uploaded_file)
                
                result = {
                    'filename': uploaded_file.name,
                    'score': analysis.get('overall_score', 0),
                    'selected': analysis.get('selected', False),
                    'strengths': analysis.get('strengths', []),
                    'missing_skills': analysis.get('missing_skills', [])
                }
                results.append(result)
                
                # Save to database
                conn = sqlite3.connect('career_coach.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO bulk_results (admin_id, job_role, filename, score, selected)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, job_role, uploaded_file.name, result['score'], result['selected']))
                conn.commit()
                conn.close()
                
            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {e}")
        
        # Display results
        st.success("✅ Analysis completed!")
        
        matched_count = sum(1 for r in results if r['selected'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Resumes", len(results))
        with col2:
            st.metric("Matched Candidates", matched_count)
        with col3:
            match_rate = (matched_count / len(results) * 100) if results else 0
            st.metric("Match Rate", f"{match_rate:.1f}%")
        
        # Show detailed results
        st.subheader("📊 Detailed Results")
        
        for result in sorted(results, key=lambda x: x['score'], reverse=True):
            status = "✅ MATCHED" if result['selected'] else "❌ NOT MATCHED"
            
            with st.expander(f"{status} - {result['filename']} (Score: {result['score']}/100)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Strengths:**")
                    for strength in result['strengths']:
                        st.success(f"✅ {strength}")
                
                with col2:
                    st.markdown("**Missing Skills:**")
                    for skill in result['missing_skills']:
                        st.error(f"❌ {skill}")

# Test the functionality
if __name__ == "__main__":
    st.set_page_config(page_title="Admin Bulk Analysis", layout="wide")
    
    # Mock session state for testing
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    simple_admin_page(api_key, st.session_state.user_id)