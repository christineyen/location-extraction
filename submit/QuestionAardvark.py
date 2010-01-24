import re, string
from lucene import \
    MultiFieldQueryParser, IndexSearcher, StopAnalyzer, FSDirectory, Hit, \
    Document, Sort, JavaError, initVM, CLASSPATH

def compare(aDoc, bDoc):
    """ Comparator to prioritize Documents with greater populations """
    assert type(aDoc) == Document
    assert type(bDoc) == Document
    return cmp(int(bDoc.get('population')), int(aDoc.get('population')))


class QuestionAardvark(object):
    prepositions = ['aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'anti', 'around', 'as', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'except', 'excepting', 'excluding', 'following', 'for', 'from', 'in', 'inside', 'into', 'like', 'near', 'of', 'off', 'on', 'onto', 'opposite', 'outside', 'over', 'past', 'regarding', 'round', 'save', 'since', 'than', 'through', 'to', 'toward', 'towards', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'via', 'with', 'within', 'without']
    # pronouns = ['the', 'this', 'that', 'my', 'mine', 'yours', 'his', 'hers', 'its', 'our', 'their']
    # want preposition list in regex of form: '(alpha|beta)(?!.*(alpha|beta)).*'
    prep_phrase = re.compile(r'\b(' + '|'.join(prepositions) + r')\b'
            + r'((?!.+\b(' + '|'.join(prepositions) + r')\b).*)')
    # identifies phrases referring to the user's current location
    current_location = re.compile(r'\b(here|this)\b')

    def __init__(self, user_loc_string, debug=False):
        analyzer = StopAnalyzer()
        fields = ['name', 'alternate_names', 'state']
        directory = FSDirectory.getDirectory("index")

        self.DEBUG = debug
        self.searcher = IndexSearcher(directory)
        self.parser = MultiFieldQueryParser(fields, analyzer)
        self.user_location = self.doSearch(user_loc_string)

    def run(self):
        """ Loops indefinitely and accepts questions from the user.
            Identifies prepositional phrases and returns corresponding
            locations, sorted by population, to the user.
        """
        while True:
            question= raw_input("\nEnter your Aardvark question: ")
            if question == '':
                return

            # logic here to feed into doSearch
            # find all prepositional phrases
            question = question.translate(string.maketrans("",""),
                string.punctuation)

            locations = []
            match = self.prep_phrase.search(question)
            while match is not None:
                if self.DEBUG: print "Found: ", match.group()
                
                doc = self.doSearch(match.group(2))
                if doc is not None:
                    if self.DEBUG: print doc.get('name')
                    locations.append(doc)
                else:
                    cur_loc_ref = self.current_location.search(question)
                    if cur_loc_ref is not None and self.user_location is not None:
                        locations.append(self.user_location)

                question = question[:match.start()]
                match = self.prep_phrase.search(question)

            # sorting locations, one ID'd per prepositional phrase
            locations.sort(compare)
            print [doc.get('name').title() \
                + ', ' + doc.get('state').upper() \
                + ': ' + doc.get('population') for doc in locations]


    def doSearch(self, string):
        """ Does the actual interacting with Lucene """
        try:
            query = self.parser.parse(self.parser, string)
            hits = self.searcher.search(query)

            if hits.length() > 0:
                return hits[0]
            return None
        except JavaError:
            return None

if __name__ == '__main__':
    initVM(CLASSPATH)
    print "To quit Aardvark question loop: submit an empty line."

    qa = QuestionAardvark("Cambridge, MA")
    qa.run()
    qa.searcher.close()

