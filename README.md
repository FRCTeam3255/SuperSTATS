# 🤖 SuperSTATs 🤖

<span style="font-size: 1.2em;">Welcome to SuperSTATs, a tool designed to process and analyze FIRST Robotics competition collected data in a user-friendly manner developed by FRC team 3255, the [SuperNURDs](https://www.frcteam3255.com/). The app is built using Python and leverages several libraries to perform statistical operations and display them in an easily manageable and configurable way.</span>

## Contents

[🚀 Getting Started](#getting-started) |
[⚙️ Setup](#setup) |
[📈 Usage](#usage) |
[💡 Get Involved](#get-involved) |
[💎 Contributors](#contributors) |
[📜 License](#license)

## Getting Started

<span style="font-size: 1.2em;">To get started with SuperSTATs, follow these steps:</span>

1. Clone the repository from [GitHub](https://github.com/FRCTeam3255/SuperSTATS/):

    ```
   git clone https://github.com/FRCTeam3255/SuperSTATS.git
    ```

2. Navigate to the cloned directory:

    ```
   cd SuperSTATS/
    ```

3. Run the setup script with one of the following depending on your Python installation

   ```
   python3 -m src/setup/setup.py
   ```

   ```
   py src/setup/setup.py
   ```
    
## Setup

<span style="font-size: 1.2em;">To start the stats app, run the startup script:</span>

```
./run.bat
```

Or launch it manually with Streamlit:

> ⚠️ Make sure you have enabled your venv environment using `source .venv/Scripts/activate`, otherwise this method will not work.

```
streamlit run src/SuperSTATs/Main.py
```

<span style="font-size: 1.2em;">All set! Head to http://localhost:8501 to access the app, or the URL provided when launching.</span>

## Usage

N/A

## Get Involved

<span style="font-size: 1.2em;">We welcome and greatly appreciate contributions to enhance SuperSTATs! Whether you find a bug, have a suggestion, or want to contribute code, your input is valuable to us. Here's how you can help out:<span>

1. **Report Issues:**
    If you encounter a bug or have a feature request, please [open an issue](https://github.com/FRCTeam3255/SuperSTATS/issues).

2. **Contribute Code:**
    
    Fork the repository.
    
    Create a new branch for your changes:

    ```
   git checkout -b branch-name
    ```
    
    Make your modifications and commit them.
    
    Push your changes to your fork:
    
    ```
   git push origin branch-name
    ```
    
    
    [Open a pull request](https://github.com/FRCTeam3255/SuperSTATS/pulls) with a clear title and description.

<span style="font-size: 1.2em;">Feel free to [reach out](https://www.frcteam3255.com/contact) if you have any questions or need assistance in contributing!</span>

## Contributors

- [Kane Barnes](https://github.com/FRCTeam3255/SuperSTATS/commits/package-conversion/?author=KaneBarnes) - [3255](https://github.com/FRCTeam3255)

- [Tayler Uva](https://github.com/FRCTeam3255/SuperSTATS/commits/package-conversion/?author=TaylerUva) - [3255](https://github.com/FRCTeam3255)

## License

N/A
