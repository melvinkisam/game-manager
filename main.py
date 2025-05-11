import random
import threading
import sys
from intentMatching import intent_matching, dtm_vectorizer, similar_matching, extract_word
from dataLoading import load_dataset, load_json, qna_search, extract_column, lookup_details, add_json, clear_json, load_collection, remove_json
from interfaceFeatures import slow_print, wrapped_print, loading_animation, text_animation, print_table

# Load all necessary data
try:
    slow_print('''
     __          __  _                                                       
     \ \        / / | |                                                      
      \ \  /\  / /__| | ___ ___  _ __ ___   ___                              
      _\ \/  \/ / _ \ |/ __/ _ \| '_ ` _ \ / _ \                             
     | |\  /\  /  __/ | (_| (_) | | | | | |  __/                             
     | |_\/__\/ \___|_|\___\___/|_| |_| |_|\___|                             
     | __/ _ \                                                               
     | || (_) |                                                              
      \__\___/                      __  __                                   
      / ____|                      |  \/  |                                  
     | |  __  __ _ _ __ ___   ___  | \  / | __ _ _ __   __ _  __ _  ___ _ __ 
     | | |_ |/ _` | '_ ` _ \ / _ \ | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
     | |__| | (_| | | | | | |  __/ | |  | | (_| | | | | (_| | (_| |  __/ |   
      \_____|\__,_|_| |_| |_|\___| |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                              __/ |          
                                                             |___/                                                                                                                          
    ''', 0.0015)
    
    # Start the loading animation in a separate thread
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=text_animation, args=(stop_event, "Initialising Chatbot"))
    loading_thread.start()

    markers = load_json("data/markers.json")

    # Conversational markers
    greetings = markers.get("greetings")
    goodbyes = markers.get("goodbyes")
    unclear_responses = markers.get("unclear_responses")
    unclear_responses_half = [unclear_responses[i].split(". ")[0] for i in range(len(unclear_responses)-1)]
    acknowledgements = markers.get("acknowledgements")

    # Personalisation markers
    name_queries = markers.get("name_queries")
    direct_name_queries = markers.get("direct_name_queries")
    change_name_queries = markers.get("change_name_queries")

    # Discoverability markers
    discover_queries = markers.get("discover_queries")
    discover_response = markers.get("discover_responses")

    # Game markers
    game_markers = markers.get("game_markers")
    direct_game_markers = markers.get("direct_game_markers")
    add_game_markers = markers.get("add_game_markers")
    display_collection_markers = markers.get("display_collection_markers")
    remove_game_markers = markers.get("remove_game_markers")

    # Small talk, qna, and game datasets
    smalltalk_dict = load_dataset("data/smalltalk.csv")
    qna_dict = load_dataset("data/qna_dataset.csv", 1, 2)
    gnames_dict = load_dataset("data/game_dataset.csv")
    smalltalk_list = list(smalltalk_dict.keys())
    qna_list = list(qna_dict.keys())
    gnames_list = list(gnames_dict.keys())

    direct_markers = set(direct_name_queries + direct_game_markers + add_game_markers)

    # List of intents
    corpus = []
    corpus.extend(direct_name_queries)
    corpus.extend(name_queries)
    corpus.extend(change_name_queries)
    corpus.extend(discover_queries)
    corpus.extend(game_markers)
    corpus.extend(direct_game_markers)
    corpus.extend(add_game_markers)
    corpus.extend(display_collection_markers)
    corpus.extend(remove_game_markers)
    corpus.extend(qna_list)
    corpus.extend(smalltalk_list)

    game_corpus = extract_column("data/game_dataset.csv", 1)

    vectorizer = dtm_vectorizer(corpus)
    game_vectorizer = dtm_vectorizer(game_corpus)
except (KeyboardInterrupt, Exception) as e:
    print(f"Error: {e}")
finally:
    # Stop the loading animation when intent matching is done
    stop_event.set()
    loading_thread.join()

    # Overwrite the loading animation line
    sys.stdout.write("\r" + " " * 25 + "\r")
    sys.stdout.flush()

# User interface
username = None
start = True
unclear_count = 0
try:
    while True:
        continue_response = False

        # Initialisation
        if start:
            slow_print("Type \"STOP\" or \"CTRL + C\" to quit...")
            slow_print("GameBot: " + random.choice(greetings) + " " + discover_response[0] + discover_response[1])
            start = False

        # Get response from the user
        query = input("    You: ")

        # Stop the Chatbot
        if query == "STOP":
            clear_json("data/collection.json")
            print("GameBot:", end=" ")
            wrapped_print(random.choice(goodbyes))
            break

        stop_event = threading.Event()
        loading_thread = threading.Thread(target=loading_animation, args=(stop_event,))
        loading_thread.start()

        # Perform intent matching on the query
        matching_result, score = intent_matching(query, corpus, vectorizer)

        stop_event.set()
        loading_thread.join()

        sys.stdout.write("\r" + " " + "\r")
        sys.stdout.flush()

        # print(matching_result, score)

        # Confidence score check
        # Bypass if direct markers
        if matching_result in direct_markers and score > 0.3:
            continue_response = True
        # If confidence score is between 0.6 and 0.3 or less than 0.6, perform confirmation
        elif score >= 0.3 and score < 0.6:
            print("GameBot:", end=" ")
            wrapped_print(f"Did you mean, \"{matching_result}\"? (yes/no)")
            user_confirmation = input("    You: ")
            if user_confirmation.lower() in "yes":
                continue_response = True
            elif user_confirmation.lower() in "no":
                print("GameBot:", end=" ")
                wrapped_print(random.choice(acknowledgements) + " Is there anything else I can help you with?")
            else:
                print("GameBot:", end=" ")
                wrapped_print(f"{random.choice(unclear_responses_half)}." + " Is there anything else I can help you with?")
        elif score < 0.3:
            print("GameBot:", end=" ")
            wrapped_print(random.choice(unclear_responses))
            unclear_count += 1
            if unclear_count == 3:
                wrapped_print(discover_response[5])
                unclear_count = 0
        else:
            continue_response = True

        # If confidence score is higher equal than 0.6, proceed to intent routing
        if continue_response == True:
            # Personalisation
            # Generic name management
            if matching_result in name_queries:
                if username is None:
                    print("GameBot:", end=" ")
                    slow_print("You haven't told me your name. What is your name?")
                    username = input("    You: ")
                    print("GameBot:", end=" ")
                    wrapped_print(f"{random.choice(greetings)}," + f" {username}!")
                else:
                    print("GameBot:", end=" ")
                    wrapped_print("Your name is" + f" {username}!")

            # Change name
            elif matching_result in change_name_queries:
                if username is None:
                    print("GameBot:", end=" ")
                    slow_print("You haven't told me your name. What is your name?")
                    username = input("    You: ")
                    print("GameBot:", end=" ")
                    wrapped_print(f"{random.choice(greetings)}," + f" {username}!")
                else:
                    print("GameBot:", end=" ")       
                    slow_print("Sure! What is your new name?")
                    username = input("    You: ")
                    print("GameBot:", end=" ")
                    wrapped_print("From now on, I will address you as" + f" {username}!")

            # Direct name management
            elif matching_result in direct_name_queries:
                direct_name = extract_word(query, direct_name_queries)
                if username is None:
                    username = direct_name
                    print("GameBot:", end=" ")
                    wrapped_print(f"{random.choice(greetings)}," + f" {username}!")
                else:
                    print("GameBot:", end=" ")
                    slow_print("Do you wish to change your name? (yes/no)")
                    user_confirmation = input("    You: ")
                    if user_confirmation.lower() in "yes":
                        username = direct_name
                        print("GameBot:", end=" ")
                        wrapped_print(f"{random.choice(greetings)}," + f" {username}!")
                    else:
                        print("GameBot:", end=" ")
                        wrapped_print(f"Your name is still {username}!")                 

            # Discoverability
            elif matching_result in discover_queries:
                print("GameBot:", end=" ")
                slow_print(discover_response[3] + discover_response[4])

            # Small talk
            elif matching_result in smalltalk_list:
                print("GameBot:", end=" ")
                wrapped_print(qna_search(matching_result, smalltalk_dict))

            # Question and answering
            elif matching_result in qna_list:
                print("GameBot:", end=" ")
                wrapped_print(qna_search(matching_result, qna_dict))

            # Game management
            # Generic option
            elif matching_result in game_markers:
                print("GameBot:", end=" ")
                slow_print("Sure! What games are you looking for? (specify the name only)")

                game_input = input("    You: ")

                stop_event = threading.Event()
                loading_thread = threading.Thread(target=text_animation, args=(stop_event, "Searching for similar games"))
                loading_thread.start()            

                game_description = extract_word(game_input, direct_game_markers)
                top_results = similar_matching(game_description, game_corpus, game_vectorizer)
                game_details, game_ids = lookup_details("data/game_dataset.csv", top_results)

                stop_event.set()
                loading_thread.join()

                sys.stdout.write("\r" + " " * 50 + "\r")
                sys.stdout.flush()

                print_table(game_details)

                if game_details:
                    print("GameBot:", end=" ")
                    slow_print("If you wish to add specific games to your collection, you can say \"Add [game name] to my collection\"")
                else:
                    print("GameBot:", end=" ")
                    wrapped_print("Is there anything else I can help you with?")                    

            # Specific option
            elif matching_result in direct_game_markers:
                stop_event = threading.Event()
                loading_thread = threading.Thread(target=text_animation, args=(stop_event, "Searching for similar games"))
                loading_thread.start()            

                game_description = extract_word(query, direct_game_markers)
                top_results = similar_matching(game_description, game_corpus, game_vectorizer)
                game_details, game_ids = lookup_details("data/game_dataset.csv", top_results)

                stop_event.set()
                loading_thread.join()

                sys.stdout.write("\r" + " " * 50 + "\r")
                sys.stdout.flush()

                # print(game_details)
                # print(game_ids)

                print_table(game_details)

                if game_details:
                    print("GameBot:", end=" ")
                    slow_print("If you wish to add specific games to your collection, you can say \"Add [game name] to my collection\"")
                else:
                    print("GameBot:", end=" ")
                    wrapped_print("Is there anything else I can help you with?")  

            # Add a game to the wishlist
            elif matching_result in add_game_markers:         
                game_description = extract_word(query, add_game_markers)

                stop_event = threading.Event()
                loading_thread = threading.Thread(target=text_animation, args=(stop_event, f"Searching for {game_description}"))
                loading_thread.start() 

                game_result, game_score = intent_matching(game_description, game_corpus, game_vectorizer)
                game_details, game_id = lookup_details("data/game_dataset.csv", [game_result])

                stop_event.set()
                loading_thread.join()

                sys.stdout.write("\r" + " " * 50 + "\r")
                sys.stdout.flush()

                # print(game_details)
                # print(game_id)

                if game_score < 0.3:
                    print("GameBot:", end=" ")
                    wrapped_print(f"Sorry, I could not find the game that you are looking for.")
                else:
                    print_table(game_details)
                    print("GameBot:", end=" ")
                    slow_print(f"Do you want to add {game_details[0]['name']} to your collection? (yes/no)")
                    user_confirmation = input("    You: ")
                    if user_confirmation.lower() in "yes":
                        print("GameBot:", end=" ")
                        add_json("data/collection.json", game_id[0], game_details)
                    elif user_confirmation.lower() in "no":
                        print("GameBot:", end=" ")
                        wrapped_print(random.choice(acknowledgements) + " Is there anything else I can help you with?")
                    else:
                        print("GameBot:", end=" ")
                        wrapped_print(f"{random.choice(unclear_responses_half)}." + " Is there anything else I can help you with?")

            # View collection
            elif matching_result in display_collection_markers:
                print("GameBot:", end=" ")
                wrapped_print("Sure! Here is your game collection:")
                games_list = load_collection("data/collection.json")
                print_table(games_list)
                print("GameBot:", end=" ")
                wrapped_print("Is there anything else I can help you with?")

            # Remove a game from the collection
            elif matching_result in remove_game_markers:
                game_exist = True
                game_description = extract_word(query, remove_game_markers)

                stop_event = threading.Event()
                loading_thread = threading.Thread(target=text_animation, args=(stop_event, f"Searching for {game_description}"))
                loading_thread.start() 

                games_list = load_collection("data/collection.json")
                game_names = [game["name"] for game in games_list]

                # print(game_names)

                if game_names:
                    collection_vectorizer = dtm_vectorizer(game_names)
                    game_result, game_score = intent_matching(game_description, game_names, collection_vectorizer)    
                    game_details, game_id = lookup_details("data/game_dataset.csv", [game_result])
                else:
                    game_exist = False

                stop_event.set()
                loading_thread.join()

                sys.stdout.write("\r" + " " * 50 + "\r")
                sys.stdout.flush()

                if game_exist == False:
                    print("GameBot:", end=" ")
                    wrapped_print(f"Sorry, your collection is empty. If you wish to add specific games to your collection, you can say \"Add [game name] to my collection\"")
                elif game_score < 0.3:
                    print("GameBot:", end=" ")
                    wrapped_print(f"Sorry, I could not find the game that you are looking for in your collection. If you wish to view your collection, you can say \"Show my collection\"")
                else:
                    print_table(game_details)
                    print("GameBot:", end=" ")
                    slow_print(f"Are you sure you want to remove {game_details[0]['name']} from your collection? (yes/no)")
                    user_confirmation = input("    You: ")
                    if user_confirmation.lower() in "yes":
                        print("GameBot:", end=" ")
                        remove_json("data/collection.json", game_id[0])
                    elif user_confirmation.lower() in "no":
                        print("GameBot:", end=" ")
                        wrapped_print(random.choice(acknowledgements) + " Is there anything else I can help you with?")
                    else:
                        print("GameBot:", end=" ")
                        wrapped_print(f"{random.choice(unclear_responses_half)}." + " Is there anything else I can help you with?")

except KeyboardInterrupt:
    clear_json("data/collection.json")
    print("\nKeyboard Interrupted. Program has exited gracefully :)")