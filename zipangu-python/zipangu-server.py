from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import comlist as cl
import typeAnalysis as ta
import entrysheet as es
import test as t
import gensim
model = gensim.models.Doc2Vec.load("./wiki_pos_tokenizer_without_taginfo.doc2vec.model")

app = Flask(__name__)
cors = CORS(app, resources={
    r"/*":{"origin":"*"},
})

@app.route('/analysis', methods=['POST'])
def analysis():
    jsonData = request.get_json()
    inputText = jsonData['inputText']
    listnum = jsonData['listnum']
    result = ta.getTypeList(inputText,listnum,model)
    return make_response(jsonify(result),200)

@app.route('/comlist', methods=['POST'])
def comlist():
    jsonData = request.get_json()
    inputText = jsonData['inputText']
    comtype = jsonData['comtype']
    result = cl.getList(inputText,comtype,model)
    return make_response(jsonify(result),200)

@app.route('/getTotalEntrysheet', methods=['POST'])
def getTotalEntrysheet():
    jsonData = request.get_json()
    result = es.getTotalList();
    return make_response(jsonify(result),200)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
