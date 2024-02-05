import shutil, os

setup = f"src\\setup"
py_prefixes = ["python3", "py"]

venv_path = ".venv\\Scripts\\activate.bat"

to_move = {
    f"{setup}\\pickles": "src\\pickles",
    f"{setup}\\streamlit\\secrets.toml": ".streamlit\\secrets.toml",
    f"{setup}\\root\\run.bat": "run.bat"
}

empty_folders = ["streamlit", "root"]

batch_content = """@echo off
set VENV_PATH=.venv\\Scripts\\activate
call %VENV_PATH%
streamlit run src\\SuperSTATs\\Main.py
"""

for py in py_prefixes:
    print(f"Attempting enviornment creation with '{py}'...")
    os.system(f"{py} -m venv .venv")
    
    if os.path.exists(venv_path):
        print("Enviornment creation successful...")
        
        print("Moving setup files...")
        for origin, destination in to_move:
            shutil.move(origin, destination)
        
        print("Removing empty folders")
        for folder in empty_folders:
            os.rmdir(f"{setup}\\{folder}")
        
        print("Installing libraries...")
        os.system("call .venv/Scripts/activate & pip install -e .")
        
        break
    
    else:
        print(f"Enviornment creation failed with '{py}'...")

if os.path.exists(venv_path):
    print("Setup completed successfully!")

else:
    print("Setup completion unsuccessful")