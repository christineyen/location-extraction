from lucene import \
    QueryParser, IndexSearcher, StopAnalyzer, FSDirectory, Hit, \
    Sort, VERSION, initVM, CLASSPATH


"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""
def run(searcher, parser):
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query: ")
        if command == '':
            return

        print "Searching for:", command
        query = parser.parse(command)
        hits = searcher.search(query, Sort("population", True))
        print "%s total matching documents." % hits.length()

        for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            print 'name:', doc.get("name"), ' state:', doc.get("state")


if __name__ == '__main__':
    STORE_DIR = "index"
    initVM(CLASSPATH)
    print 'lucene', VERSION
    directory = FSDirectory.getDirectory(STORE_DIR)
    searcher = IndexSearcher(directory)
    analyzer = StopAnalyzer()
    parser = QueryParser("all_names", analyzer)
    parser.setDefaultOperator(parser.AND_OPERATOR)
    run(searcher, parser)
    searcher.close()

