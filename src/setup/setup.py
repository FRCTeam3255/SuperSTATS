import shutil, os

launch_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(launch_dir, os.pardir, os.pardir))
venv_path = ".venv\\Scripts\\activate.bat"
setup = f"src\\setup"

to_move = {
    f"{setup}\\pickles": "src\\pickles",
    f"{setup}\\streamlit\\secrets.toml": ".streamlit\\secrets.toml",
}

os.chdir(app_dir)

for py in ["python3", "py"]:
    print(f"Attempting enviornment creation with '{py}'...")
    os.system(f"{py} -m venv .venv")

    if os.path.exists(venv_path):
        print("Enviornment creation successful...")

        print("Moving setup files...")
        for origin, destination in to_move.items():
            shutil.move(origin, destination)

        print("Removing empty folders")
        os.rmdir(f"{setup}\\streamlit")

        print("Installing libraries...")
        os.system("call .venv/Scripts/activate & pip install -e .")

        break

    else:
        print(f"Enviornment creation failed with '{py}'...")

if os.path.exists(venv_path):
    print("Setup completed successfully!")

else:
    print("Setup completion unsuccessful")
