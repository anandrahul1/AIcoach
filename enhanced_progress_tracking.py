"""
Enhanced Progress Tracking System
Adds automatic tracking, detailed metrics, and better user experience
"""

import sqlite3
import streamlit as st
from datetime import datetime, timedelta
import json

def update_learning_progress_database():
    """Add enhanced progress tracking tables"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    # Enhanced progress tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detailed_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT,
            course_name TEXT,
            progress_percentage INTEGER DEFAULT 0,
            time_spent_minutes INTEGER DEFAULT 0,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_date TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Learning sessions table for time tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT,
            session_date DATE,
            minutes_studied INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_type TEXT,
            achievement_name TEXT,
            description TEXT,
            earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def log_learning_session(user_id, skill_name, minutes_studied, notes=""):
    """Log a learning session"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO learning_sessions (user_id, skill_name, session_date, minutes_studied, notes)
        VALUES (?, ?, DATE('now'), ?, ?)
    ''', (user_id, skill_name, minutes_studied, notes))
    
    # Update detailed progress
    cursor.execute('''
        INSERT OR REPLACE INTO detailed_progress 
        (user_id, skill_name, time_spent_minutes, last_activity)
        VALUES (?, ?, 
            COALESCE((SELECT time_spent_minutes FROM detailed_progress 
                     WHERE user_id = ? AND skill_name = ?), 0) + ?,
            CURRENT_TIMESTAMP)
    ''', (user_id, skill_name, user_id, skill_name, minutes_studied))
    
    conn.commit()
    conn.close()

def update_course_progress(user_id, skill_name, course_name, progress_percentage, notes=""):
    """Update progress for a specific course"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    # Update detailed progress
    cursor.execute('''
        INSERT OR REPLACE INTO detailed_progress 
        (user_id, skill_name, course_name, progress_percentage, last_activity, notes)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
    ''', (user_id, skill_name, course_name, progress_percentage, notes))
    
    # Update learning plan status based on progress
    if progress_percentage >= 100:
        status = 'completed'
        # Log completion date
        cursor.execute('''
            UPDATE detailed_progress 
            SET completion_date = CURRENT_TIMESTAMP 
            WHERE user_id = ? AND skill_name = ? AND course_name = ?
        ''', (user_id, skill_name, course_name))
        
        # Check for achievements
        check_and_award_achievements(user_id, skill_name)
        
    elif progress_percentage > 0:
        status = 'in_progress'
    else:
        status = 'not_started'
    
    # Update learning plan
    cursor.execute('''
        UPDATE learning_plans 
        SET status = ? 
        WHERE user_id = ? AND skill_name = ?
    ''', (status, user_id, skill_name))
    
    conn.commit()
    conn.close()

def check_and_award_achievements(user_id, skill_name):
    """Check and award achievements"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    # Check if achievement already exists
    cursor.execute('''
        SELECT COUNT(*) FROM achievements 
        WHERE user_id = ? AND achievement_type = 'course_completion' AND achievement_name = ?
    ''', (user_id, f"Completed {skill_name}"))
    
    if cursor.fetchone()[0] == 0:
        # Award achievement
        cursor.execute('''
            INSERT INTO achievements (user_id, achievement_type, achievement_name, description)
            VALUES (?, 'course_completion', ?, ?)
        ''', (user_id, f"Completed {skill_name}", f"Successfully completed {skill_name} course"))
        
        conn.commit()
    
    conn.close()

def get_detailed_progress(user_id):
    """Get detailed progress for a user"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT skill_name, course_name, progress_percentage, time_spent_minutes, 
               last_activity, completion_date, notes
        FROM detailed_progress 
        WHERE user_id = ?
        ORDER BY last_activity DESC
    ''', (user_id,))
    
    progress = cursor.fetchall()
    conn.close()
    return progress

def get_learning_sessions(user_id, days_back=30):
    """Get learning sessions for the last N days"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT skill_name, session_date, minutes_studied, notes
        FROM learning_sessions 
        WHERE user_id = ? AND session_date >= DATE('now', '-{} days')
        ORDER BY session_date DESC
    '''.format(days_back), (user_id,))
    
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_achievements(user_id):
    """Get user achievements"""
    conn = sqlite3.connect('career_coach.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT achievement_type, achievement_name, description, earned_date
        FROM achievements 
        WHERE user_id = ?
        ORDER BY earned_date DESC
    ''', (user_id,))
    
    achievements = cursor.fetchall()
    conn.close()
    return achievements

def enhanced_progress_tracking_page(user_id):
    """Enhanced progress tracking page with detailed metrics"""
    
    st.subheader("📊 Enhanced Progress Tracking")
    
    # Initialize enhanced database
    update_learning_progress_database()
    
    # Get data
    detailed_progress = get_detailed_progress(user_id)
    learning_sessions = get_learning_sessions(user_id)
    achievements = get_achievements(user_id)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "⏱️ Time Tracking", "🏆 Achievements", "📝 Log Session"])
    
    with tab1:
        st.markdown("### 📊 Progress Overview")
        
        if detailed_progress:
            # Create progress cards
            for progress in detailed_progress:
                skill, course, percentage, time_spent, last_activity, completion_date, notes = progress
                
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{skill}**")
                        if course:
                            st.markdown(f"*{course}*")
                        st.progress(percentage / 100 if percentage else 0)
                        st.markdown(f"{percentage}% Complete")
                    
                    with col2:
                        hours = time_spent // 60 if time_spent else 0
                        minutes = time_spent % 60 if time_spent else 0
                        st.metric("Time Spent", f"{hours}h {minutes}m")
                    
                    with col3:
                        if completion_date:
                            st.success("✅ Completed")
                        elif percentage > 0:
                            st.info("🔄 In Progress")
                        else:
                            st.warning("⏳ Not Started")
                    
                    if notes:
                        st.markdown(f"*Notes: {notes}*")
                    
                    st.markdown("---")
        else:
            st.info("No detailed progress data yet. Start logging your learning sessions!")
    
    with tab2:
        st.markdown("### ⏱️ Learning Sessions")
        
        if learning_sessions:
            # Create a chart of daily study time
            import pandas as pd
            
            df = pd.DataFrame(learning_sessions, columns=['Skill', 'Date', 'Minutes', 'Notes'])
            df['Hours'] = df['Minutes'] / 60
            
            # Group by date
            daily_study = df.groupby('Date')['Hours'].sum().reset_index()
            
            st.line_chart(daily_study.set_index('Date'))
            
            # Show recent sessions
            st.markdown("#### Recent Sessions")
            for session in learning_sessions[:10]:
                skill, date, minutes, notes = session
                hours = minutes // 60
                mins = minutes % 60
                
                st.markdown(f"""
                **{skill}** - {date}  
                ⏱️ {hours}h {mins}m  
                📝 {notes if notes else 'No notes'}
                """)
                st.markdown("---")
        else:
            st.info("No learning sessions logged yet. Use the 'Log Session' tab to start tracking!")
    
    with tab3:
        st.markdown("### 🏆 Achievements")
        
        if achievements:
            for achievement in achievements:
                achievement_type, name, description, earned_date = achievement
                
                st.markdown(f"""
                <div style="background-color: #1f4e79; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <h4>🏆 {name}</h4>
                    <p>{description}</p>
                    <small>Earned on: {earned_date}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No achievements yet. Complete your first course to earn your first achievement!")
    
    with tab4:
        st.markdown("### 📝 Log Learning Session")
        
        # Get user's learning plan for skill selection
        conn = sqlite3.connect('career_coach.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT skill_name FROM learning_plans WHERE user_id = ?', (user_id,))
        skills = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if skills:
            with st.form("log_session_form"):
                skill = st.selectbox("Select Skill", skills)
                
                col1, col2 = st.columns(2)
                with col1:
                    hours = st.number_input("Hours Studied", min_value=0, max_value=24, value=1)
                with col2:
                    minutes = st.number_input("Minutes Studied", min_value=0, max_value=59, value=0)
                
                notes = st.text_area("Session Notes", placeholder="What did you learn? Any challenges?")
                
                submitted = st.form_submit_button("Log Session")
                
                if submitted:
                    total_minutes = (hours * 60) + minutes
                    if total_minutes > 0:
                        log_learning_session(user_id, skill, total_minutes, notes)
                        st.success(f"✅ Logged {hours}h {minutes}m for {skill}!")
                        st.rerun()
                    else:
                        st.error("Please enter a valid study time.")
        
        st.markdown("---")
        st.markdown("### 📊 Update Course Progress")
        
        if skills:
            with st.form("update_progress_form"):
                skill = st.selectbox("Select Skill", skills, key="progress_skill")
                course_name = st.text_input("Course Name", placeholder="e.g., Machine Learning by Andrew Ng")
                progress = st.slider("Progress Percentage", 0, 100, 0)
                notes = st.text_area("Progress Notes", placeholder="What topics did you cover?")
                
                submitted = st.form_submit_button("Update Progress")
                
                if submitted:
                    update_course_progress(user_id, skill, course_name, progress, notes)
                    st.success(f"✅ Updated {skill} progress to {progress}%!")
                    st.rerun()

# Integration function for the main app
def integrate_enhanced_progress_tracking():
    """Function to integrate enhanced progress tracking into main app"""
    
    # Add this to your enhanced_app.py in the progress_tracking_page function
    st.markdown("## 🚀 Enhanced Progress Tracking")
    
    if st.checkbox("Enable Enhanced Progress Tracking"):
        enhanced_progress_tracking_page(st.session_state.user_id)
    else:
        # Keep existing progress tracking
        st.info("Enable enhanced tracking above for detailed progress monitoring!")