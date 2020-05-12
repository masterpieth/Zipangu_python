from gensim.models import doc2vec
import sys
import multiprocessing

cores = multiprocessing.cpu_count()

vector_size = 300
window_size = 15
word_min_count = 2
sampling_threshold = 1e-5
negative_size = 5
train_epoch = 100
dm = 1 #0 = dbow; 1 = dmpv
worker_count = cores #number of parallel processes

inputfile = r"D:\user\Desktop\project\wiki_pos_tokenizer_without_taginfo.txt"
modelfile = r"D:\user\Desktop\project\wiki_pos_tokenizer_without_taginfo.doc2vec.model"
word2vec_file = modelfile + ".word2vec_format"

sentences = doc2vec.TaggedLineDocument(inputfile)

#build voca
model = doc2vec.Doc2Vec(min_count=word_min_count, vector_size=vector_size, alpha=0.025, min_alpha=0.025, seed=1234, workers=worker_count)
model.build_vocab(sentences)

# Train document vectors
model.train(sentences, epochs=model.iter, total_examples=model.corpus_count)

# To save

model.save(modelfile)
model.save_word2vec_format(word2vec_file, binary=False)
