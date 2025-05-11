import csv
import json
import random
import re
from interfaceFeatures import wrapped_print

# Function to load and preprocess the data
def load_dataset(filename, question_index=0, answer_index=1):
    qna_dict= {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)

            for row in reader:
                if row[question_index] in qna_dict.keys():
                    qna_dict[row[question_index]].append(row[answer_index])
                else:
                    qna_dict[row[question_index]] = [row[answer_index]]
    except FileNotFoundError:
        print(f"Error: The file \"{filename}\" is not found.")
        return None
    except csv.Error:
        print(f"Error: The file \"{filename}\" is not a valid CSV file.")
        return None

    return qna_dict


# Function to load json data
def load_json(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file \"{filename}\" is not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file \"{filename}\" is not a valid JSON file.")
        return None


# Function to search for answer in the dictionary
def qna_search(question, qna_dict):
    answer = qna_dict[question]

    if len(answer) > 1:
        return random.choice(answer)

    return answer[0]


# Function to remove all non-ASCII characters
def remove_non_ascii(input_file, output_file):
    try:
        with open(input_file, mode="r", encoding="utf-8") as infile, open(output_file, mode="w", encoding="utf-8") as outfile:
            for line in infile:
                line = re.sub(r"[^\x00-\x7F]+", "", line)
                outfile.write(line)
        print(f"Output file: {output_file}")
    except FileNotFoundError:
        print(f"Error: The file \"{input_file}\" is not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Function to get one column as a list
def extract_column(filename, column_index=0):
    column_data = []
    try:
        with open(filename, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)

            for row in reader:
                column_data.append(row[column_index])
    except FileNotFoundError:
        print(f"Error: The file \"{filename}\" was not found.")
        return None
    except csv.Error:
        print(f"Error: The file \"{filename}\" is not a valid CSV file.")
        return None

    return column_data


# Function to search additional information from the dataset
def lookup_details(dataset_file, name_list):
    details = []
    ids = []
    try:
        with open(dataset_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["name"] in name_list:
                    details.append({
                        "name": row["name"],
                        "release_date": row["release_date"],
                        "price": row["price"],
                        "genres": row["genres"]
                    })
                    ids.append(row["AppID"])
    except FileNotFoundError:
        print(f"Error: The file \"{dataset_file}\" is not found.")
    except csv.Error:
        print(f"Error: The file \"{dataset_file}\" is not a valid CSV file.")
    
    return details, ids


# function to add a game to the collection
def add_json(filename, game_id, game_details):
    try:
        try:
            with open(filename, "r", encoding="utf-8") as file:
                games = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            games = {}

        if game_id in games:
            wrapped_print(f"\"{game_details[0]['name']}\" already exists. Skipping this step...")
        else:
            games[game_id] = game_details
            wrapped_print(f"\"{game_details[0]['name']}\" has been successfully added to your collection! To view your collection, simply type \"Show my collection\"")

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(games, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Function to remove a game from the collection
def remove_json(filename, game_id):
    try:
        try:
            with open(filename, "r", encoding="utf-8") as file:
                games = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            games = {}

        if game_id in games:
            removed_game = games[game_id][0]['name']
            del games[game_id]
            wrapped_print(f"\"{removed_game}\" has been successfully removed from your collection!")
        else:
            wrapped_print(f"Sorry, the game that you are looking for does not exist in your collection. Nothing was removed.")

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(games, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# function to clear data from the collection
def clear_json(filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Function to load JSON and transform it back to the desired format
def load_collection(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            games_data = json.load(file)

        games_list = []
        for game_id, details in games_data.items():
            games_list.extend(details)

        return games_list
    except FileNotFoundError:
        wrapped_print(f"Error: The file \"{filename}\" is not found.")
        return []
    except json.JSONDecodeError:
        wrapped_print(f"Error: The file \"{filename}\" is not a valid JSON file.")
        return []
    except Exception as e:
        wrapped_print(f"An unexpected error occurred: {e}")
        return []