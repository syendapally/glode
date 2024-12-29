import argparse
import json
from openai import OpenAI

# Load your OpenAI API key
client = OpenAI(
    api_key=""
)

# Load the language syntax JSON
with open("language_syntax.json", "r", encoding="utf-8") as file:
    language_syntax = json.load(file)


def detect_language(file_name):
    """Detect the language from the first line of the file."""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            first_line = file.readline().strip()
            if first_line.startswith("#"):
                language = first_line[1:].strip()  # Extract the language name after '#'
                return language
            else:
                return None
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {str(e)}"


def validate_and_translate(file_name, language):
    """Validate syntax and translate to Python."""
    try:
        # Check if the language is supported
        if language not in language_syntax["languages"]:
            return f"Language '{language}' not supported."

        # Read the code content from the file (excluding the first line)
        with open(file_name, "r", encoding="utf-8") as file:
            lines = file.readlines()
            code_content = "".join(lines[1:]).strip()  # Skip the first line for language detection

        # Extract syntax guide for the language
        syntax_guide = language_syntax["languages"][language]

        # Prompt to validate and translate
        prompt = f"""
        You are a programming assistant. The user writes code in {language}. Below is the syntax guide:

        {json.dumps(syntax_guide, indent=4, ensure_ascii=False)}

        User Input:
        {code_content}

        Task:
        1. Validate if the syntax matches the expected structure, ensuring that all spellings are correct for the language-specific keywords.
        2. If not, explain why and suggest corrections. Make sure the suggestions and explanations are in the {language} language.
        3. If valid, translate the code to Python.

        The response must always be in the following JSON format:

       {{
        "syntax_valid": true or false,
        "explanations": "Detailed explanation of why the syntax is invalid or issues found, if any. Explanations should be in the {language} language. If valid, this can be empty.",
        "suggestions": "Suggestions to correct the code, if invalid. If valid, this can be empty. Suggestions should be in the {language} language.",
        "python_translation": "The Python code translation of the input, if the syntax is valid. If invalid, this should be empty."
        }}
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the message content from the response
        message_content = completion.choices[0].message.content

        # Convert the content to a JSON object
        response_json = json.loads(message_content)

        # Check if the syntax is valid
        if response_json.get("syntax_valid", False):
            python_code = response_json.get("python_translation", "").strip()
            local_scope = {}
            exec(python_code, {}, local_scope)
            return f"Python Code Executed:\n{python_code}\n\nOutput:\n{local_scope}"
        else:
            suggestions = response_json.get("suggestions", "").strip()
            return f"Suggestions:\n{suggestions}" if suggestions else "No suggestions provided."
    except (KeyError, json.JSONDecodeError):
        return "Error: Invalid response format or JSON structure."
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {str(e)}"


# Main function
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Validate and translate code from a .glode file.")
    parser.add_argument("filename", type=str, help="The name of the .glode file containing the user's input.")

    # Parse arguments
    args = parser.parse_args()
    file_name = args.filename

    # Check if the file has a .glode extension
    if not file_name.endswith(".glode"):
        print("Error: The file must have a .glode extension.")
    else:
        # Detect language from the file
        language = detect_language(file_name)

        if language and not language.startswith("Error"):
            # Validate and translate
            result = validate_and_translate(file_name, language)
            print(result)
        else:
            print(language if language else "Language not detected. Please specify it using a '#' at the beginning of the input.")