def rainbow():
    return """
        <style>
        .rainbow {
            font-size: 4em;
            color: #f39c12;
            font-family: 'Roboto', sans-serif;
            animation: rainbow 7s infinite;
            text-align: center;
            font-weight: bold;
        }

        @keyframes rainbow {
            0% { color: #f39c12; }
            25% { color: #e74c3c; }
            50% { color: #3498db; }
            75% { color: #e74c3c; }
            100% { color: #f39c12; }
        }
        </style>
    """


def shimmer(color):
    return f"""
        <style>
        .shimmer {{
            font-size: 3em;
            color: #ffffff;
            font-family: 'Roboto', sans-serif;
            animation: shimmer 7s infinite;
            text-align: center;
            font-weight: bold;
        }}

        @keyframes shimmer {{
            0% {{ color: #ffffff; }}
            25% {{ color: #ffffff; }}
            50% {{ color: {color}; }}
            75% {{ color: #ffffff; }}
            100% {{ color: #ffffff; }}
        }}
        </style>
    """
