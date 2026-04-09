from django.db import IntegrityError
from collections import Counter
import string
from utilities.models import Queryterm

punctuation = string.punctuation + '“”«»’'

ENGLISH_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'being', 'but', 'by',
    'for', 'from', 'had', 'has', 'have', 'he', 'her', 'here', 'hers', 'him',
    'his', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'me', 'my', 'of', 'on',
    'or', 'our', 'ours', 'she', 'that', 'the', 'their', 'theirs', 'them',
    'there', 'these', 'they', 'this', 'those', 'to', 'us', 'was', 'we', 'were',
    'what', 'when', 'where', 'which', 'who', 'why', 'will', 'with', 'you',
    'your', 'yours',
}

DUTCH_STOPWORDS = {
    'aan', 'af', 'al', 'als', 'bij', 'dan', 'dat', 'de', 'den', 'der', 'deze',
    'die', 'dit', 'doch', 'door', 'dus', 'een', 'en', 'er', 'ge', 'geen',
    'haar', 'had', 'heb', 'hebben', 'heeft', 'hem', 'het', 'hier', 'hij', 'hoe',
    'hun', 'ik', 'in', 'is', 'je', 'kan', 'me', 'men', 'met', 'mij', 'nog',
    'nu', 'of', 'om', 'onder', 'ons', 'onze', 'ook', 'op', 'te', 'tegen', 'toch',
    'toen', 'tot', 'u', 'uit', 'uw', 'van', 'veel', 'voor', 'want', 'waren',
    'was', 'wat', 'we', 'wel', 'werd', 'wezen', 'wie', 'wij', 'worden', 'zal',
    'ze', 'zei', 'zelf', 'zich', 'zij', 'zijn', 'zo', 'zonder', 'zou',
}

STOPWORDS = ENGLISH_STOPWORDS | DUTCH_STOPWORDS

def handle_stop_words(words):
    output = []
    for word in words:
        w = word.lower()
        if w in STOPWORDS: continue
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

            
    
