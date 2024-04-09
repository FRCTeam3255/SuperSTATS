def rainbow():
    """
    Returns a CSS style string that creates a rainbow animation effect.

    The returned style string can be used to apply the rainbow animation to HTML elements.

    Returns:
        str: CSS style string for the rainbow animation.
    """
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

        @media screen and (max-width: 480px) {
            .rainbow {
                font-size: 2.5em;
            }
        }
        </style>
    """


def shimmer(color):
    """
    Generate CSS code for a shimmer effect.

    Args:
        color (str): The color to use for the shimmer effect.

    Returns:
        str: The CSS code for the shimmer effect.

    """
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

        @media screen and (max-width: 600px) {{
            .shimmer {{
                font-size: 2em;
            }}
        }}
        </style>
    """
