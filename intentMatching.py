import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk import pos_tag, word_tokenize, ne_chunk

# Function to lemmatize text
def lemmatize_text(text):
    lemmatizer = WordNetLemmatizer()

    lemmatized_text = " ".join(lemmatizer.lemmatize(token) for token in word_tokenize(text))

    return lemmatized_text


# Function to remove stopwords
def remove_stopwords(text):
    words = text.split()

    filtered_words = [word for word in words if word.lower() not in stopwords.words("english")]

    return " ".join(filtered_words)


# Function to create document-term matrix vectorizer
def dtm_vectorizer(corpus):
    lemmatized_corpus = [lemmatize_text(document) for document in corpus]

    tfidf_vectorizer = TfidfVectorizer()

    vectorizer = tfidf_vectorizer.fit(lemmatized_corpus)

    return vectorizer


# Function for intent matching with cosine similarity
def intent_matching(query, corpus, vectorizer):
    lemmatized_query = lemmatize_text(query)
    lemmatized_corpus = [lemmatize_text(document) for document in corpus]

    corpus_matrix = vectorizer.transform(lemmatized_corpus)
    query_vector = vectorizer.transform([lemmatized_query])
    
    cos_similarities = cosine_similarity(query_vector, corpus_matrix).flatten()
    highest_index = cos_similarities.argmax()
    score = cos_similarities[highest_index]
    
    matching_document = corpus[highest_index]

    return matching_document, score


# Function to return most similar results with cosine similarity
def similar_matching(query, corpus, vectorizer, top_n=10, similarity_threshold=0.3):
    lemmatized_query = lemmatize_text(query)
    lemmatized_corpus = [lemmatize_text(document) for document in corpus]

    corpus_matrix = vectorizer.transform(lemmatized_corpus)
    query_vector = vectorizer.transform([lemmatized_query])

    cos_similarities = cosine_similarity(query_vector, corpus_matrix).flatten()

    valid_indices = []
    for i in range(len(cos_similarities)):
        if cos_similarities[i] >= similarity_threshold:
            valid_indices.append(i)

    sorted_indices = sorted(valid_indices, key=lambda index: cos_similarities[index], reverse=True)

    top_results = []
    for i in range(min(top_n, len(sorted_indices))):
        top_results.append(corpus[sorted_indices[i]])

    return top_results


# Function to separate a certain key word from the query
def extract_word(query, markers):
    marker_tokens = set()
    for marker in markers:
        marker_tokens.update(marker.lower().split())

    query_tokens = query.split()
    name_tokens = [word for word in query_tokens if word.lower() not in marker_tokens]

    return " ".join(name_tokens)


# Function to extract name from the query
def get_name(query):
    tokens = word_tokenize(query)
    tokens_without_sw = [word for word in tokens if word not in stopwords.words()]

    pos_tags = pos_tag(tokens_without_sw)
    named_entities = ne_chunk(pos_tags)

    username = ""
    for subtree in named_entities:
        if isinstance(subtree, nltk.Tree) and subtree.label() == "PERSON":
            username = " ".join(word for word, _ in subtree.leaves())

    if username:
        return username
    
    message = "Sorry, I couldn't find what you are looking for."

    return message