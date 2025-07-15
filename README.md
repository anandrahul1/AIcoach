# 🚀 Euron AI Career Coach

An AI-powered career development platform that provides personalized resume analysis, learning plans, and conversational career guidance.

## ✨ Features

### 🎯 Core Functionality
- **Resume Analysis**: AI-powered analysis of resumes with skill gap identification
- **Personalized Learning Plans**: Structured curriculum generation based on career goals
- **Progress Tracking**: Monitor learning progress with detailed analytics
- **AI Career Coach**: Conversational AI assistant for career guidance
- **Admin Panel**: Bulk resume analysis and user management features

### 🔧 Technical Features
- **User Authentication**: Secure login/registration system
- **Database Integration**: SQLite database for user data persistence
- **Role-Based Access**: Admin and regular user roles
- **Responsive UI**: Clean, modern interface built with Streamlit

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI/ML**: OpenAI GPT, LangChain
- **Database**: SQLite
- **Additional Libraries**: Pandas, Matplotlib, PyPDF2, FAISS

## 📋 Prerequisites

- Python 3.8+
- OpenAI API Key
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/anandrahul1/AIcoach.git
cd AIcoach
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Application
```bash
streamlit run enhanced_app_with_admin.py
```

The application will be available at `http://localhost:8501`

## 📁 Project Structure

```
AIcoach/
├── enhanced_app_with_admin.py          # Main application file
├── ui.py                               # UI components
├── agents.py                           # Resume analysis agent
├── enhanced_agents.py                  # Enhanced career coach agent
├── conversational_agent.py             # Conversational AI functionality
├── enhanced_learning_plan_generator.py # Learning plan generation
├── enhanced_progress_tracking.py       # Progress tracking features
├── robust_admin_bulk.py               # Admin bulk analysis
├── simple_admin_bulk.py               # Admin authentication
├── app.py                             # Alternative main app
├── requirements.txt                   # Python dependencies
├── euron.jpg                          # Application logo
├── run_app.sh                         # Startup script
└── README.md                          # This file
```

## 🎯 Supported Career Roles

The application provides specialized analysis and learning paths for:

- **AI/ML Engineer**
- **AI Engineer** 
- **AWS Fullstack Developer**
- **AWS Python Developer**
- **AWS Data Engineer**
- **Frontend Engineer**
- **Backend Engineer**
- **Data Engineer**
- **DevOps Engineer**
- **Full Stack Developer**
- **Product Manager**
- **Data Scientist**

## 🔑 Key Components

### Resume Analysis Agent
- Analyzes uploaded PDF resumes
- Identifies skill gaps for target roles
- Provides detailed scoring and recommendations

### Learning Plan Generator
- Creates structured learning curricula
- Organizes courses by phases and prerequisites
- Tracks certification opportunities

### Conversational Career Coach
- AI-powered chat interface
- Context-aware career guidance
- Personalized advice based on user data

### Progress Tracking
- Visual progress analytics
- Learning session logging
- Achievement tracking

## 👨‍💼 Admin Features

- Bulk resume analysis
- User management
- Curriculum generation for multiple roles
- Analytics and reporting

## 🔒 Security

- Password hashing with SHA-256
- Session-based authentication
- Role-based access control
- Secure API key management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/anandrahul1/AIcoach/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🙏 Acknowledgments

- OpenAI for GPT API
- Streamlit for the web framework
- LangChain for AI orchestration
- The open-source community for various libraries used

---

**Made with ❤️ for career development and AI-powered learning**