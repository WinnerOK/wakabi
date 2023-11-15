import re
import nltk
from nltk.probability import FreqDist
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pattern.text.en import singularize
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from pattern.text.en import singularize


nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')

words_pattern = r'\b[a-zA-Z\'-]+\b'
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def get_wordnet_pos(treebank_tag):
    """ Convert the part-of-speech naming scheme from the Penn Treebank tag to the WordNet's scheme """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def norm_word(word, pos):
    wordnet_pos = get_wordnet_pos(pos) or wordnet.NOUN
    return singularize(lemmatizer.lemmatize(word, pos=wordnet_pos)).lower()


def extract_words(text, words_limit=None):
    words_to_learn = set()
    all_words_to_learn = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        words = word_tokenize(sentence)
        tagged_words = nltk.pos_tag(words)
        for word, tag in tagged_words:
            # Skip proper nouns and non-alphabetic tokens
            if tag.startswith('NNP') or not word.isalpha():
                continue
            if word.lower() not in stop_words:
                normalized_word = norm_word(word, tag)
                words_to_learn.add(normalized_word)
                all_words_to_learn.append(normalized_word)

    freq_dist = FreqDist(all_words_to_learn)
    if words_limit:
        words_to_learn = set(
            [w[0] for w in freq_dist.most_common(words_limit)]
        )
    return sorted(words_to_learn, key=lambda w: freq_dist[w], reverse=True)
        


def filter_words(words_to_learn: list, exclude_words: set) -> list:
    return list(filter(lambda w: w not in exclude_words, words_to_learn))

def process_file(file_path: str, learning_words: set, level_words: set, words_limit: int = None) -> set:
    words_to_learn = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        words_to_learn = extract_words(text, words_limit)

    # Assuming 'NN' (noun) for simplicity
    learning_words_norm = set(map(lambda w: norm_word(w, 'NN'), learning_words))
    level_words_norm = set(map(lambda w: norm_word(w, 'NN'), level_words))
    return sorted(filter_words(words_to_learn, learning_words_norm, level_words_norm))

def process_text(text: str, learning_words: set, level_words: set, words_limit: int = None) -> set:
    words_to_learn = extract_words(text, words_limit)
    # Assuming 'NN' (noun) for simplicity
    learning_words_norm = set(map(lambda w: norm_word(w, 'NN'), learning_words))
    level_words_norm = set(map(lambda w: norm_word(w, 'NN'), level_words))
    exclude_words = learning_words_norm | level_words_norm
    return filter_words(words_to_learn, exclude_words)