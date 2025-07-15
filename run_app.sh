#!/bin/bash

# Activate virtual environment and run the application
source venv/bin/activate
streamlit run enhanced_app_with_admin.py --server.port 8501 --server.address 0.0.0.0