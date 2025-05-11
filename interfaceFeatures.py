import time
import sys
import textwrap

# Function to slow print the text
def slow_print(text, delay=0.01):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


# Function to wrap the text and maintain proper indentation
def wrapped_print(text, width=120, indent=9):
    wrapped_text = textwrap.wrap(text, width=width)

    slow_print(f"{wrapped_text[0]}")

    for line in wrapped_text[1:]:
        slow_print(" " * indent + line)


# Function for the starting animation
def text_animation(stop_event, text):
    dots = ["", ".", "..", "..."]

    while not stop_event.is_set():
        for i in range(len(dots)):
            if stop_event.is_set():
                break
            if i == 0:
                sys.stdout.write(f"\r{text}   ")
                sys.stdout.write(f"\r{text}")
                sys.stdout.flush()
                time.sleep(0.5)
            else:
                sys.stdout.write(f"\r{text}{dots[i]}")
                sys.stdout.flush()
                time.sleep(0.5)


# Function for the loading animation
def loading_animation(stop_event):
    spinner = ["|", "/", "-", "\\"]

    while not stop_event.is_set():
        for symbol in spinner:
            if stop_event.is_set():
                break
            sys.stdout.write(f'\r{symbol}')
            sys.stdout.flush()
            time.sleep(0.1)


def print_table(data):
    if not data:
        print("No results found.")
        return

    # Determine column widths
    col_width_index = 3
    col_width_name = max(max(len(item["name"]) for item in data), len("name")) + 2
    col_width_date = max(max(len(item["release_date"]) for item in data), len("release_date")) + 2
    col_width_price = max(max(len(item["price"]) for item in data), len("price")) + 2
    col_width_genre = max(max(len(item["genres"]) for item in data), len("genres")) + 2

    # Horizontal border
    horizontal_border = f"+{'-' * col_width_index}-+{'-' * col_width_name}-+{'-' * col_width_date}-+{'-' * col_width_genre}-+{'-' * col_width_price}-+"

    # Table
    # Header
    print(horizontal_border)
    print(f"| {'#'.ljust(col_width_index)}| {'Name'.ljust(col_width_name)}| {'Release Date'.ljust(col_width_date)}| {'Genres'.ljust(col_width_genre)}| {'Price'.ljust(col_width_price)}|")
    print(horizontal_border)
    # Content
    for index, item in enumerate(data, start=1):
        print(f"| {str(index).ljust(col_width_index)}| {item['name'].ljust(col_width_name)}| {item['release_date'].ljust(col_width_date)}| {item['genres'].ljust(col_width_genre)}| {item['price'].ljust(col_width_price)}|")
    print(horizontal_border)