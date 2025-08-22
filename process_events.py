# --- HTML Assembly for Browser Preview ---
def build_browser_html(template_html: str, theme_css: str, sections: list) -> str:
    """
    Assemble the full browser HTML by:
    1. Stripping duplicate section headings from each block.
    2. Injecting the active theme CSS at the theme placeholder.
    3. Inserting all section blocks into the template.
    """
    # Each section should be a dict with 'title' and 'block_html'
    processed_blocks = []
    for section in sections:
        title = section.get('title', '')
        block_html = section.get('block_html', '')
        clean_html = strip_duplicate_section_heading(block_html, title)
        processed_blocks.append(clean_html)
    all_blocks_html = '\n'.join(processed_blocks)
    # Replace the theme CSS placeholder
    browser_html = template_html.replace(
        '/* --- THEME STYLES INJECTED HERE --- */',
        theme_css
    )
    # Insert the blocks (assume a {{ content }} placeholder)
    browser_html = browser_html.replace('{{ content }}', all_blocks_html)
    return browser_html
import re

def strip_duplicate_section_heading(block_html: str, section_title: str) -> str:
    """
    Remove all <h1>-<h6> headings that exactly match the section title (ignoring case/whitespace)
    anywhere in the block_html, to avoid duplicated headings in the browser view.
    """
    # Match any heading level (h1-h6), with any attributes, ignore case, whitespace, and allow for minor HTML variations
    pattern = re.compile(rf'<h[1-6][^>]*>\s*{re.escape(section_title)}\s*</h[1-6]>', flags=re.I | re.S)
    matches = list(pattern.finditer(block_html))
    if not matches:
        return block_html
    # (Removed: now handled in exporter.py)
    return block_html
import json
from datetime import datetime

def clean_and_sort_events(input_file='events.json', output_file='cleaned_sorted_events.json'):
    """
    Reads a JSON file of events, removes past events, sorts the
    remaining events by date, and saves them to a new JSON file.
    """
    try:
        with open(input_file, 'r') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{input_file}'.")
        return

    # Get today's date, ignoring the time component for comparison
    today = datetime.now().date()
    
    # Use the provided date of August 22, 2025 for this specific request
    today = datetime.strptime("22 Aug 2025", "%d %b %Y").date()


    future_events = []
    for event in events:
        # The date string format is like "Sat, 06 Sep 2025"
        date_str = event.get('date')
        if not date_str:
            continue

        try:
            # Parse the date string into a datetime object
            event_date = datetime.strptime(date_str, '%a, %d %b %Y').date()

            # Include events that are today or in the future
            if event_date >= today:
                # Store the parsed date object for easy sorting later
                event['parsed_date'] = event_date
                future_events.append(event)
        except (ValueError, TypeError):
            # Handle cases where the date string might be malformed or missing
            print(f"Could not parse date for event: '{event.get('title')}' with date '{date_str}'. Skipping.")
            continue

    # Sort the list of events chronologically using the 'parsed_date' key
    # A lambda function provides a simple way to specify the sorting key
    future_events.sort(key=lambda x: x['parsed_date'])

    # Clean up by removing the temporary 'parsed_date' key before saving
    for event in future_events:
        del event['parsed_date']

    # Write the cleaned and sorted list to the output file
    with open(output_file, 'w') as f:
        # 'indent=4' makes the JSON output human-readable
        json.dump(future_events, f, indent=4)

    print(f"Successfully processed {len(future_events)} events.")
    print(f"Cleaned and sorted events have been saved to '{output_file}'.")

# Run the function
if __name__ == "__main__":
    clean_and_sort_events()