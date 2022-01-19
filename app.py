#!flask/bin/python2
from flask import Flask, jsonify, request
import librosa as lr
import warnings
import numpy as np
import glob
import pickle
import os.path
import base64
from werkzeug.utils import secure_filename

BLOCKSIZE = 20000
WIDTH = 2  # Number of bytes per sample
CHANNELS = 1  # mono
global Fist_run
global Users
Fist_run = True

# Initialization
n = 1
m = 1

Name = []
Path_to_save = "trained/"
Path_to_save_waves = "waves/"
Path_to_save_config = "config/"
warnings.simplefilter("once")

p_weight = []
Mean = []
Covar = []
MFCC = []
vmfcc = []
tasks = []

global Users
Users = []


class Config:
    def __init__(self):
        self.use_nn = True
        self.threshold = 0.9
        self.samplerate = 44100


config = Config()


class User:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.mfcc = ""

    def __getitem__(self, i):
        return self[i]


def check_create_path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path)


def confidence(x, y):
    return np.sum((x - y) ** 2)


def process_audio(aname):
    audio, _ = lr.load(aname, sr=config.samplerate)
    afs = lr.feature.mfcc(audio,
                          sr=config.samplerate,
                          n_mfcc=34,
                          n_fft=2048)
    afss = np.sum(afs[2:], axis=-1)
    afss = afss / np.max(np.abs(afss))

    return afss


def filter_audio(audio):
    apower = lr.amplitude_to_db(np.abs(lr.stft(audio, n_fft=2048)), ref=np.max)
    apsums = np.sum(apower, axis=0) ** 2
    apsums -= np.min(apsums)
    apsums /= np.max(apsums)
    apsums = np.convolve(apsums, np.ones((9,)), 'same')
    apsums -= np.min(apsums)
    apsums /= np.max(apsums)
    apsums = np.array(apsums > 0.35, dtype=bool)
    apsums = np.repeat(apsums, np.ceil(len(audio) / len(apsums)))[:len(audio)]
    return audio[apsums]


def load_saved():
    if os.path.exists(Path_to_save + "Users.save") == True:
        global Users
        Users = pickle.load(open(Path_to_save + "Users.save", 'rb'))

        if os.path.exists(Path_to_save_config + "Config.save"):
            global config
            config = pickle.load(
                open(Path_to_save_config + "Config.save", 'rb'))

        for index, user in enumerate(Users):
            if not os.path.exists(Path_to_save_waves + user.id + "-" + user.name + ".wav"):
                del Users[index]
        pickle.dump(Users, open(Path_to_save + "Users.save", 'wb'))

        global Fist_run
        Fist_run = False

        n = len(Name)

        files = [f for f in glob.glob(Path_to_save + "*")]
        for f in files:
            f = f.replace(Path_to_save, '')
            if "Weight-" in f:
                p_weight.append(f)
            if "Mean-" in f:
                Mean.append(f)
            if "Covar-" in f:
                Covar.append(f)
            if "mfcc-" in f:
                vmfcc.append(f)

        vmfcc.sort()
        p_weight.sort()
        Mean.sort()
        Covar.sort()
        num = 0

        for c in vmfcc:
            floaded = np.load(Path_to_save + c)
            MFCC.append(floaded)
        for x in p_weight:
            ploaded = pickle.load(open(Path_to_save + x, 'rb'))
            p_weight.append(ploaded)
        for y in Mean:
            mloaded = pickle.load(open(Path_to_save + y, 'rb'))
            Mean.append(mloaded)
        for z in Covar:
            cloaded = pickle.load(open(Path_to_save + z, 'rb'))
            Covar.append(cloaded)


def train(id):
    global Users
    for _, user in enumerate(Users):
        if user.id == id:
            filename = id + '-' + user.name + '.wav'
            user.mfcc = process_audio(Path_to_save_waves + filename)
            global Users
            pickle.dump(Users, open(Path_to_save + "Users.save", 'wb'))
            return True

    return False


def user_identify(mfcc_to_identify):
    min = 100
    global name, id
    if not Fist_run:
        for _, user in enumerate(Users):
            result = confidence(mfcc_to_identify, user.mfcc)
            if result < min:
                min = result
                name = user.name
                id = user.id

        if min <= config.threshold:
            return id, name, min
        # if min < Threshold and minindex == Final:
        #     print Name[Final]
        else:
            return -1, "", ""
    else:
        return -2, "", ""


def check_exists(filename):
    mfcc = process_audio(Path_to_save_waves + filename)
    tmpid, tmpusername, min = user_identify(mfcc)
    if tmpid == -1:
        return False
    if tmpid == -2:
        return False
    else:
        return True


def save_config():
    pickle.dump(config, open(Path_to_save_config + "Config.save", 'wb'))


def init():
    check_create_path(Path_to_save_config)
    check_create_path(Path_to_save)
    check_create_path(Path_to_save_waves)
    load_saved()


app = Flask(__name__)
init()


@app.route('/auth/api/v1.0/userdel/<id>', methods=['DELETE'])
def user_del(id):
    if request.method == 'DELETE':

        if len(id) == 0:
            return jsonify(400, {"err": "Specify user id"})
        else:
            for index, user in enumerate(Users):
                if id == user.id:
                    userid = user.id
                    username = user.name
                    filename = userid + "-" + username + ".wav"
                    os.remove(Path_to_save_waves + filename)
                    del Users[index]
                    pickle.dump(Users, open(Path_to_save + "Users.save", 'wb'))
                    return jsonify(200, {'id': userid, 'name': username})


@app.route('/auth/api/v1.0/useradd', methods=['POST'])
def user_add():
    if request.method == 'POST':

        f = request.files['file']

        if len(f.filename) == 0:
            return jsonify(400, {"err": "Empty file"})

        id = str(base64.b64encode(os.urandom(6)).decode('ascii'))
        id = secure_filename(id)
        filename = id + "-" + f.filename
        f.save(Path_to_save_waves + filename)
        fname = f.filename.replace(".wav", '')
        newuser = User()
        newuser.name = fname
        newuser.id = id

        global Fist_run
        if Fist_run:
            global Users
            Users.append(newuser)
            if not train(newuser.id):
                return jsonify(400, {"err": "Can not add user"})
            global Fist_run
            Fist_run = False
            return jsonify(200, {'id': newuser.id, 'name': newuser.name})
        else:
            if not check_exists(filename):
                global Users
                Users.append(newuser)
                if not train(newuser.id):
                    return jsonify(400, {"err": "Can not add user"})
                Fist_run = False
                return jsonify(200, {'id': newuser.id, 'name': newuser.name})

            else:
                os.remove(Path_to_save_waves + filename)
                return jsonify(400, {"err": "User exists"})


@app.route('/auth/api/v1.0/list', methods=['GET'])
def get_list():
    if Fist_run:
        return jsonify(400, {"err": "Empty list of user"})
    else:
        users = []
        for index, user in enumerate(Users):
            users.append({"id": user.id, "name": user.name})
        return jsonify(200, {"users": users})


@app.route('/auth/api/v1.0/threshold', methods=['GET', 'POST'])
def get_threshold():
    if request.method == 'GET':
        return jsonify(200, {"threshold": str(config.threshold)})

    if request.method == 'POST':

        result = request.get_json()
        resThreshold = result["threshold"]

        try:
            config.threshold = float(resThreshold)
        except ValueError as verr:
            return jsonify(400, {"err": "Value is not type of float"})
            pass
        save_config()
        return jsonify(200, {"threshold": config.threshold})


@app.route('/auth/api/v1.0/samplerate', methods=['GET', 'POST'])
def get_samplerate():
    if request.method == 'GET':
        return jsonify(200, {"samplerate": str(config.samplerate)})

    if request.method == 'POST':
        result = request.get_json()
        resSamplerate = result["samplerate"]

        try:
            config.samplerate = int(resSamplerate)
        except ValueError as verr:
            return jsonify(400, {"err": "Value is not type of integer"})
            pass
        save_config()
        return jsonify(200, {"samplerate": str(config.samplerate)})


@app.route('/auth/api/v1.0/neuralnet', methods=['GET', 'POST'])
def get_neuralnet():
    if request.method == 'GET':

        if config.use_nn == True:
            return jsonify(200, {"neuralnet": "True"})
        else:
            return jsonify(200, {"neuralnet": "False"})

    if request.method == 'POST':

        result = request.get_json()
        use_nn = result["neuralnet"]

        if use_nn in ("True", "False"):
            config.use_nn = result["neuralnet"]
            save_config()
            return jsonify(200, {"neuralnet": str(config.use_nn)})
        else:
            return jsonify(400, {"err": "Value is not type of bool"})


@app.route('/auth/api/v1.0/auth', methods=['POST'])
def auth():
    if request.method == 'POST':

        f = request.files['file']
        if len(f.filename) == 0:
            return jsonify(400, {"err": "Empty file"})

        filename = "to_auth.wav"
        f.save(Path_to_save_waves + filename)
        authmfcc = process_audio(Path_to_save_waves + filename)
        userid, username, mine = user_identify(authmfcc)
        os.remove(Path_to_save_waves + filename)
        if userid == -1:
            return jsonify(400, {"err": "Can not identify user"})
        if userid == -2:
            return jsonify(400, {"err": "Empty database. Add users first"})
        else:
            return jsonify(200, {"id": userid, "username": username})
    return jsonify(400, {"err": "Can not identify user"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
