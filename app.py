from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbdictionary


@app.route('/')
def main():
    words = list(db.pracwords.find({}, {"_id": False}))
    msg = request.args.get('msg')
    return render_template("index.html", words=words, msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}",
                     headers={"Authorization": "Token aa5305d310653561ed8cc64b64a962274975090e"})
    if r.status_code != 200:
        return redirect(url_for('main', msg='Wrong word'))
    result = r.json()
    status_receive = request.args.get('status_give', 'new')
    print(result)
    return render_template("detail.html", word=keyword, result=result, status=status_receive)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    word_receive = request.form['word_give']
    definition_receive = request.form['definition_give']
    doc = {'word': word_receive, 'definition': definition_receive}
    db.pracwords.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'단어 "{word_receive}" 저장'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word_receive = request.form['word_give']
    db.pracwords.delete_one({'word': word_receive})
    return jsonify({'result': 'success', 'msg': f'단어 "{word_receive}" 삭제'})


@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word_receive = request.args['word_give']
    result = list(db.pracexamples.find({'word': word_receive}, {'_id': False}))
    return jsonify({'result': 'success', 'example_list': result})


@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word_receive = request.form['word_give']
    example_receive = request.form['example_give']
    doc = {'word': word_receive, 'example': example_receive}
    db.pracexamples.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'예문 "{example_receive}" 저장'})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    word_receive = request.form['word_give']
    number_receive = int(request.form['number_give'])
    example = list(db.pracexamples.find({'word': word_receive}))[number_receive]['example']
    db.pracexamples.delete_one({'word': word_receive, 'example': example})
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
