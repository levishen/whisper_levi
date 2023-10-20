from flask import Flask, request, jsonify
#from flask_cors import CORS

app = Flask(__name__)


@app.route('/voice_start', methods=['GET'])
def saveVoice():

    # text = "是"
    # response = {"result": text}

    pass


@app.route('/voice_end', methods=['GET'])
def voice2text():

    text = "是"
    response = {"result": text}

    return jsonify(response)


if __name__ == '__main__':
    app.run(port=8080, host='192.168.137.96')
