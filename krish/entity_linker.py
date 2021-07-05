import spacy

nlp = spacy.load('en_core_web_sm')

nlp.add_pipe('entityLinker', last=True)

doc = nlp('I watched pirates of the caribbean last night')

all_linked_entities = doc._.linkedEntities

for sent in doc.sents:
    sent._.linkedEntitites.pretty_print()

