@echo off
set VENV_PATH=.venv\Scripts\activate
call %VENV_PATH%
streamlit run src\SuperSTATs\Home.py