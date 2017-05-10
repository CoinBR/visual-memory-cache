import os
from uuid import uuid4 as uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

from main import Tracer, Cache


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'traces/'
CORS(app)

tracers = {}


@app.route('/traces/', methods=['GET', 'POST'])
def new_trace():

    FILE_ERROR = jsonify({
        'error': 'Invalid or Empty File',
    }), 400

    if request.method == 'POST':
        # check if the post request has the file part
        if 'tracefile' not in request.files:
            return FILE_ERROR
        tracefile = request.files['tracefile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if tracefile.filename == '':
            return FILE_ERROR

        tid = str(uuid())
        tracefile.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    '.'.join((tid, 'trace'))))
        tracers[tid] = Tracer(Cache(int(request.form['n_blocks']),
                                    int(request.form['n_words']),
                                    int(request.form['n_layers']),
                                    32,
                                    request.form['method']
                                    ), tid)
        return jsonify({'id': tid, }), 201

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=tracefile>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/traces/<tid>/forward', methods=['GET'])
def forward_redirect(tid):
    return forward(tid, 1)


@app.route('/traces/<tid>/forward/<int:forward>', methods=['GET'])
def forward(tid, forward):
    if tid not in tracers:
        return jsonify({'error':
                        'The requested trace is not loaded in our servers'})
    tracer = tracers[tid]
    if forward > 1 or forward == 0:
        if forward == 0:
            forward = 1024**1024

        for nd in range(forward - 1):
            step_r = tracer.trace_step(False)
            if type(step_r) is dict:
                break

    return jsonify(tracer.trace_step(True)), 200


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
