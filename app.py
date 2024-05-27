from flask import Flask, render_template, request, jsonify
from spellchecker import SpellChecker
import re
import os

app = Flask(__name__)

# Initialize the spell checker without a pre-defined language dictionary
spell = SpellChecker(language=None)

# Path to the custom British English word list file
dictionary_path = os.path.join(os.path.dirname(__file__), 'fox.txt')

# Function to load custom British English word list into the spell checker
def load_custom_dictionary(spell, filepath):
    word_count = 0
    print(f"Loading custom dictionary from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as file:  # Open the custom dictionary file
        for line in file:  # Read the file line by line
            word = line.strip()  # Strip any surrounding whitespace from the word
            if word:  # Ensure the line is not empty
                spell.word_frequency.add(word)  # Add the word to the spell checker's frequency list
                word_count += 1
                # Print progress every 500 words
                if word_count % 500 == 0:
                    print(f"{word_count} words loaded...")
    print(f"Custom dictionary loaded with {word_count} words.")  # Print the number of words loaded

# Load the custom dictionary using the defined function
load_custom_dictionary(spell, dictionary_path)

@app.route('/test')  # Define a route for the /test URL
def test():
    return "<h1>Hello, Flask!</h1>"  # Return a simple HTML message for the /test URL

@app.route('/', methods=['GET', 'POST'])  # Define a route for the root URL that accepts both GET and POST requests
def index():
    return render_template('index.html')  # Render the index.html template

@app.route('/check_spelling', methods=['POST'])  # Define a route for the /check_spelling URL that accepts POST requests
def check_spelling():
    """Checks spelling errors in a provided text.

This function receives JSON data containing a 'text' field and performs spell checking on the text. 
It removes punctuation (except apostrophes) and identifies misspelled words. 
The function then returns a JSON response with a list of misspelled words and suggested corrections.

Args:
    data: A dictionary containing the request data.

Returns:
    A JSON response containing a list of dictionaries with misspelled words and suggestions.
"""
    data = request.get_json()  # Get the JSON data from the request
    text = data.get('text', '')  # Extract the 'text' field from the JSON data, defaulting to an empty string if not found
    # Remove punctuation for spell checking, but keep words with apostrophes
    words = re.findall(r'\b[\w\']+\b', text)  # Use a regular expression to find all words, including those with apostrophes
    misspelled = spell.unknown(words)  # Identify misspelled words
    # Create a list of dictionaries with misspelled words and their suggestions
    errors = [{'word': word, 'suggestions': list(spell.candidates(word))} for word in misspelled]
    return jsonify(errors=errors)  # Return the errors as a JSON response

if __name__ == '__main__':  # If this script is run directly (and not imported as a module)
    app.run(debug=True)  # Run the Flask application in debug mode
