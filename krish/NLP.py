import spacy

nlp = spacy.load('en_core_web_sm')

def parse_clause(str):
    doc = nlp(filter(str))
    subj, aux, obj = None, None, []
    sf, af, of = False, False, False

    for i in range(len(doc)):
        if doc[i].dep_ == 'nsubj' and not sf:
            subj = doc[i].text
            sf = True

        if doc[i].pos_ == 'AUX' and not af:
            aux = doc[i].text
            if doc[i].tag_ != 'NNS':
                aux += ' a'
            af = True

        if doc[i].dep_ == 'dobj' or doc[i].dep_ == 'pobj' or doc[i].dep_ == 'attr':
            obj.append(doc[i].text)

    return [subj, aux, obj]

def filter(str):
    start = -1
    doc = nlp(str)
    final = str
    """
    for i in range(len(doc)):
        if doc[i].text == ',':
            start = i
            break
    # find where the auxiliary verb is
    end = -1
    for i in range(len(doc)):
        if doc[i].pos_ == 'AUX':
            end = i
            break
    for i in range(0, start):
        final += doc[i].text + " "
    for i in range(end, len(doc)):
        final += doc[i].text + " "
    """
    while '(' in final:
        final = final[:final.find('(')-1] + final[final.find(')')+1:]
    return final.replace('[disambiguation needed]', '')


def READ(str):
    if '(' in str:
        str = str[:str.find('(')-1] + str[str.find(')')+1:]
    doc = nlp(str)
    for token in doc:
        print(token.text, token.tag_, token.pos_, token.dep_)

"""
TEST_STR = 'In biology, an organism (from Greek: ὀργανισμός, organismos) is any organic[disambiguation needed] living system that functions as an individual entity[disambiguation needed].'
print(filter(TEST_STR))
"""