# <span style="color:#00a6ed;">🤖 SuperSTATs 🤖</span>

Welcome to SuperSTATs, a tool designed to process and analyze FIRST Robotics competition collected data in a user-friendly manner developed by FRC team 3255, the [SuperNURDs](https://www.frcteam3255.com/). The app is built using Python and leverages several libraries to perform statistical operations and display them in an easily managable and configurable way.

## <span style="color:#f8312f;">Getting Started</span>

To get started with SuperSTATs, follow these steps:

1. Clone the repository from [GitHub](https://github.com/FRCTeam3255/SuperSTATS/):

    ```git clone https://github.com/FRCTeam3255/SuperSTATS.git```

2. Navigate to the cloned directory:

    ```cd .\SuperSTATS```

3. Create a virtual environment:
    
    > ⚠️ Make sure you have Python installed. If not, download and install it from [python.org](https://www.python.org/downloads/). Ensure that Python is added to your system PATH.

    ```python3 -m venv env```

4. Activate the virtual environment:

    ```.\venv\Scripts\activate```

5. Install the required dependencies:

    ```pip install -e .```

    Or install them manually with:

    ```pip install streamlit~=1.30 tbapy~=1.3 urllib3~=1.26 plotly~=5.17 beautifulsoup4~=4.12.2```

## <span style="color:#f8312f;">Usage</span>

To start the stats app, run the main script with Streamlit:

```streamlit run src\SuperSTATs\Main.py```

All set! Head to http://localhost:8501 to use the app

## <span style="color:#f8312f;">Contributing</span>

N/A

## <span style="color:#f8312f;">License</span>

N/A