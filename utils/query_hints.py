from django.db import IntegrityError
from collections import Counter
from nltk.corpus import stopwords
import string
from utilities.models import Queryterm

punctuation = string.punctuation + '“”«»’'

def handle_stop_words(words):
    dutch = stopwords.words('dutch')
    english = stopwords.words('english')
    output = []
    for word in words:
        w = word.lower()
        if w in dutch or w in english: continue
        output.append(word)
    return output

def check_start(word):
    remove_char = 0
    for word_character in word:
        if word_character not in punctuation: break
        else: remove_char += 1
    if remove_char == 0: return word
    if len(word) <= remove_char: return ''
    return word[remove_char:]

def check_end(word):
    remove_char = 0
    for word_character in word[::-1]:
        if word_character not in punctuation: break
        else: remove_char += 1
    if remove_char == 0: return word
    if len(word) <= remove_char: return ''
    return word[:-1*remove_char]


def handle_punctuation(words):
    output = []
    for word in words:
        word = check_start(word)
        word = check_end(word)
        if not word: continue
        if '.' in word: continue
        output.append(word)
    return output
    
def handle_word_length(words):
    output = []
    for word in words:
        if len(word) < 4: continue
        output.append(word)
    return output

def text_to_unigrams(text):
    text = text.replace('\r\n',' ')
    text = text.replace('\n',' ')
    words = [word for word in text.split(' ') if word]
    words = handle_punctuation(words)
    words = handle_word_length(words)
    words = handle_stop_words(words)
    return Counter(words)

def update_queryterms(terms):
    already_present = 0
    added = 0
    for term in terms:
        t = Queryterm(term = term)
        try: t.save()
        except IntegrityError: 
            already_present += 1
            continue
        else: added += 1
    print('already_present:',already_present,'added:',added)
    
def get_queryterms():
    qh = Queryterm.objects.all()
    terms = [x.term for x in qh]
    return sorted(terms)

            
    
