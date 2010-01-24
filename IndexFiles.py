import sys, os
from lucene import FSDirectory, IndexWriter, Document, Field, \
    StopAnalyzer, initVM, CLASSPATH, VERSION
from datetime import datetime

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)
        store = FSDirectory.getDirectory(storeDir, True)
        writer = IndexWriter(store, analyzer, True)
        writer.setMaxFieldLength(1048576)
        self.indexDocs(root, writer)
        print 'optimizing index',
        writer.optimize()
        writer.close()
        print 'done'

    def indexDocs(self, root, writer):
        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if not filename.endswith('.txt'):
                    continue
                print "adding", filename
                try:
                    path = os.path.join(root, filename)
                    file = open(path)
                    for line in file:
                        doc = Document()
                        arr = line.split('\t')
                        field = Field("name", arr[2].lower(),
                                             Field.Store.YES,
                                             Field.Index.TOKENIZED)
                        field.setBoost(1.5)
                        doc.add(field)
                        doc.add(Field("alternate_names", arr[3].lower(),
                                             Field.Store.YES,
                                             Field.Index.TOKENIZED))
                        doc.add(Field("state", arr[10].lower(),
                                             Field.Store.YES,
                                             Field.Index.TOKENIZED))
                        doc.add(Field("population", arr[14],
                                             Field.Store.YES,
                                             Field.Index.UN_TOKENIZED))
                        if int(arr[14]) > 1000000:
                            doc.setBoost(1.2)
                        writer.addDocument(doc)
                    file.close()
                except Exception, e:
                    print "Failed in indexDocs:", e

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    initVM(CLASSPATH)
    print 'lucene', VERSION
    start = datetime.now()
    try:
        IndexFiles(sys.argv[1], "index", StopAnalyzer())
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e

