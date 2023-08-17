"""
Фасад вокруг ruwordnet
"""
from random import choice
from ruwordnet import RuWordNet

wn = RuWordNet()

# Sense
# -----
# derivations
# id
# lemma
# metadata
# name
# phrases
# registry
# sources
# synset
# synset_id
# words

# Synset
# ------
# antonyms
# antonyms_reverse
# causes
# classes
# conclusions
# definition
# domain_items
# domains
# effects
# holonyms
# hypernyms
# hyponyms
# id
# ili
# instances
# meronyms
# metadata
# part_of_speech
# pos_synonyms
# pos_synonyms_reverse
# premises
# registry
# related
# related_reverse
# senses
# title


def random_hypernym(word: str) -> str | None:
    """
    Возвращает случайное обобщение если удалось найти
    """
    senses = wn.get_senses(word)

    if not senses:
        return None

    sense = choice(senses)
    hypernym = choice(sense.synset.hypernyms)

    return hypernym.title.lower()
