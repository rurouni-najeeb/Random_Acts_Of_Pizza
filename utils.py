from collections import Counter
import re
import string

def Flesch_reading_ease(total_words,total_sentences,total_sylabls):
    "Calculates the Fleish Reading Score for the sentence with given parameters"
    if total_words!=0 and total_sentences!=0:
        return (0.39*(total_words/total_sentences)+11.8*(total_sylabls/total_words)-15.59)
    else:
        return -15 

#########################################################
## All the functions below are used for Spell Checking ##
#########################################################

def words(text): 
    return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('data/words.txt').read()))

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

#########################################################
##   Data below is used for narrative and politeness   ##
#########################################################

narrative = {'Money': 'money now broke week until time last \
day when today tonight paid next first night after tomorrow \
month while account before long Friday rent buy bank still \
bills bills ago cash due due soon past never paycheck check \
spent years poor till yesterday morning dollars financial \
hour bill evening credit budget loan bucks deposit dollar \
current payed'.split(),'Job':'work job paycheck unemployment\
interview fired employment hired hire'.split(),'Student':'college\
student school roommate studying university finals semester class\
study project dorm tuition'.split(),'Family':'family mom wife parents\
mother hus- band dad son daughter father parent mum'.split(),'Craving':'friend \
girlfriend craving birthday boyfriend celebrate party game games movie\
date drunk beer celebrating invited drinks crave wasted invite'.split()}

polite_words = [
    "please","thanks","thank you","think", "thought", "thinking", "almost",
    "apparent", "apparently", "appear", "appeared", "appears", "approximately", "around",
    "assume", "assumed", "certain amount", "certain extent", "certain level", "claim",
    "claimed", "doubt", "doubtful", "essentially", "estimate",
    "estimated", "feel", "felt", "frequently", "from our perspective", "generally", "guess",
    "in general", "in most cases", "in most instances", "in our view", "indicate", "indicated",
    "largely", "likely", "mainly", "may", "maybe", "might", "mostly", "often", "on the whole",
    "ought", "perhaps", "plausible", "plausibly", "possible", "possibly", "postulate",
    "postulated", "presumable", "probable", "probably", "relatively", "roughly", "seems",
    "should", "sometimes", "somewhat", "suggest", "suggested", "suppose", "suspect", "tend to",
    "tends to", "typical", "typically", "uncertain", "uncertainly", "unclear", "unclearly",
    "unlikely", "usually", "broadly", "tended to", "presumably", "suggests",
    "from this perspective", "from my perspective", "in my view", "in this view", "in our opinion",
    "in my opinion", "to my knowledge", "fairly", "quite", "rather", "argue", "argues", "argued",
    "claims", "feels", "indicates", "supposed", "supposes", "suspects", "postulates"
]

#################################################################
## All the functions below are used for Similarity calculation ##
#################################################################

def get_post_from_subreddit_by_user(self , author , subreddit):
        import urllib2
        from bs4 import BeautifulSoup
        url_ = "https://www.reddit.com/search?q=author%3A"+ author + "+subreddit%3A" + subreddit
        done = True
        while done:
            try:
                request = urllib2.Request(url_)
                response = urllib2.urlopen(request)
                soup = BeautifulSoup(response, 'html.parser')
                cnt = 0
                har_ = set()
                for a in soup.findAll('a' , href = True):
                  try:
                      if subreddit in a['href']:
                          ls_ = a['href'].split('/')
                          for i in ls_:
                              if i.isalnum():
                                  har_.add(i)
                          cnt += 1
                  except Exception as e :
                    print str(e)
                return len(har_)
            except:
                pass
