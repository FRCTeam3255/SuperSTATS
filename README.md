# <span style="color:#00a6ed;">🤖 SuperSTATs 🤖</span>

<span style="font-size: 1.2em;">Welcome to SuperSTATs, a tool designed to process and analyze FIRST Robotics competition collected data in a user-friendly manner developed by FRC team 3255, the [SuperNURDs](https://www.frcteam3255.com/). The app is built using Python and leverages several libraries to perform statistical operations and display them in an easily manageable and configurable way.</span>

## <span style="color:#f8312f;">Getting Started</span>

<span style="font-size: 1.2em;">To get started with SuperSTATs, follow these steps:</span>

1. Clone the repository from [GitHub](https://github.com/FRCTeam3255/SuperSTATS/):

    `git clone https://github.com/FRCTeam3255/SuperSTATS.git`

2. Navigate to the cloned directory:

    `cd SuperSTATS/`

3. Create a virtual environment:
    
    > ⚠️ Make sure you have Python installed. If not, download and install it from [python.org](https://www.python.org/downloads/). Ensure that Python is added to your system PATH.

    `python3 -m venv venv`

4. Activate the virtual environment:

    `source venv/Scripts/activate`

6. Install the required dependencies:

    `pip install -e .`

    Or install them manually with:

    `pip install streamlit~=1.30 tbapy~=1.3 urllib3~=1.26 plotly~=5.17 beautifulsoup4~=4.12.2`

7. Create secrets.toml in `SuperSTATs/.streamlit`:

    ```
    GSHEET_DOC_ID = "GOOGLE_SHEET_ID"
    TBA_API = "THE_BLUE_ALLIANCE_API_KEY"
    
    GID_RAW = "RAW_STATS_DATA_GID"
    GID_PICKED = "PICKED_TEAMS_GID"
    GID_MATCHES = "MATCH_LIST_GID"
    GID_SCOUTING = "SCOUTING_DATA_GID"
    
    FORM_URL = "GOOGLE_FORM_URL"
    
    TEAM_NUMBER = TEAM_NUMBER
    DEFAULT_EVENT_KEY = "EVENT_KEY"

    SCOUTER_LIST = ["NAME_1", "NAME_2", "NAME_3", ...]
    ```

## <span style="color:#f8312f;">Setup</span>

<span style="font-size: 1.2em;">To start the stats app, run the startup script:</span>

`./run` or `./run.bat`

Or launch it manually with Streamlit:

`streamlit run src/SuperSTATs/Main.py`

> ⚠️ Make sure you have enabled your venv environment using `venv/Scripts/activate`, otherwise this method will not work.

<span style="font-size: 1.2em;">All set! Head to http://localhost:8501 to access the app, or the URL provided when launching.</span>

## <span style="color:#f8312f;">Usage</span>

N/A

## <span style="color:#f8312f;">Contributing</span>

<span style="font-size: 1.2em;">We welcome and greatly appreciate contributions to enhance SuperSTATs! Whether you find a bug, have a suggestion, or want to contribute code, your input is valuable to us. Here's how you can help out:<span>

1. **Report Issues:**
    If you encounter a bug or have a feature request, please [open an issue](https://github.com/FRCTeam3255/SuperSTATS/issues).

2. **Contribute Code:**
    
    Fork the repository.
    
    Create a new branch for your changes:

    `git checkout -b branch-name`
    
    Make your modifications and commit them.
    
    Push your changes to your fork:
    
    `git push origin branch-name`
    
    
    [Open a pull request](https://github.com/FRCTeam3255/SuperSTATS/pulls) with a clear title and description.

<span style="font-size: 1.2em;">Feel free to [reach out](https://www.frcteam3255.com/contact) if you have any questions or need assistance in contributing!</span>



## <span style="color:#f8312f;">License</span>

N/A
