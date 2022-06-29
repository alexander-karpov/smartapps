import stanza

stanza.download('ru', processors="tokenize,pos,lemma")
nlp = stanza.Pipeline('ru', processors="tokenize,pos,lemma")
