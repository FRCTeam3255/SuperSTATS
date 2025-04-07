import shutil
import os

launch_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(launch_dir, os.pardir, os.pardir))
venv_path = ".venv\\Scripts\\activate.bat"
setup = "src\\setup"

to_create = [
    "src\\pickles",  # Ensure the pickles folder is created as an empty folder
    ".streamlit",    # Ensure the .streamlit folder exists for secrets.toml
]

to_move = {
    f"{setup}\\streamlit\\secrets.toml": ".streamlit\\secrets.toml",
}

os.chdir(app_dir)

# Create necessary folders if they don't exist
for folder in to_create:
    if not os.path.exists(folder):
        os.makedirs(folder)

for py in ["python3", "py"]:
    print(f"Attempting environment creation with '{py}'...")
    os.system(f"{py} -m venv .venv")

    if os.path.exists(venv_path):
        print("Environment creation successful...")

        print("Moving setup files...")
        for origin, destination in to_move.items():
            if os.path.exists(origin):
                shutil.move(origin, destination)

        print("Removing empty folders")
        if os.path.exists(f"{setup}\\streamlit"):
            os.rmdir(f"{setup}\\streamlit")

        print("Installing libraries...")
        os.system("call .venv/Scripts/activate & pip install -e .")
        os.system(
            "call .venv/Scripts/activate & pip install -r requirements.txt"
        )

        break

    else:
        print(f"Environment creation failed with '{py}'...")

if os.path.exists(venv_path):
    print("Setup completed successfully!")

else:
    print("Setup completion unsuccessful")
