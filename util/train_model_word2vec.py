import gensim, logging
import codecs
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class MySentences(object):
	def __init__(self, dirname):
		self.dirname = dirname
 
	def __iter__(self):
		for fname in os.listdir(self.dirname):
			for line in codecs.open(os.path.join(self.dirname, fname), 'r', 'utf-8'):
				yield line.split()

sentences = MySentences('/home/eduardo/corpus')
model = gensim.models.Word2Vec(sentences)
model.save('model')