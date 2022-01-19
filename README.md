# Text-Independent-Speaker-Indentification-System
Speaker-Indentification System based on **MFCC** model.

##**Installation**
Venv - python2.7
pip install Flask-1.1.2, librosa

##**REST API**

**Base url** - '/auth/api/v1.0/'

**CMD**

1.**'list'** - Get list of added users. Method - GET

Example cmd: curl -X GET  127.0.0.1:5000/auth/api/v1.0/list

Return example: [
  200, 
  {
    "users": [
      {
        "id": "6wT6CCOT", 
        "name": "Viktor"
      }
    ]
  }
]


2.**'useradd'** - Add user to base. Method - POST

Example cmd: curl -X POST -F 'file=@Shilong.wav'  127.0.0.1:5000/auth/api/v1.0/useradd

Return example: [
  200, 
  {
    "id": "pD51tf7d", 
    "name": "Shilong"
  }
]


3.**'auth'** - Authenticate user. Method - POST

Example cmd: curl -X POST -F 'file=@Testing.wav'  127.0.0.1:5000/auth/api/v1.0/auth

Return example: [
  200, 
  {
    "id": "6wT6CCOT", 
    "username": "Viktor"
  }
]

4.**'userdel/id'** - Delete user with given id. Method - DELETE

Example cmd: curl -X DELETE   127.0.0.1:5000/auth/api/v1.0/userdel/6wT6CCOT

Return example: [
  200, 
  {
    "id": "Gu7nshTt", 
    "name": "He"
  }
]

5.**'threshold'** - Get or Set threshold level. Methods - GET and POST

Example cmd: curl -X GET 127.0.0.1:5000/auth/api/v1.0/threshold

Return example: [
  200, 
  {
    "threshold": "0.9"
  }
]

Example cmd: curl --header "Content-Type: application/json" -X POST -d '{"threshold":"1.0"}' 127.0.0.1:5000/auth/api/v1.0/threshold

Return example: [
  200, 
  {
    "threshold": 1.0
  }
]

6.**'samplerate'** - Get or Set samplerate. Methods - Get and POST

Example cmd: curl -X GET  127.0.0.1:5000/auth/api/v1.0/samplerate

Return example: [
  200, 
  {
    "samplerate": "44100"
  }
]

Example cmd: curl --header "Content-Type: application/json" -X POST -d '{"samplerate":"48000"}' 127.0.0.1:5000/auth/api/v1.0/samplerate

Return example: [
  200, 
  {
    "samplerate": "48000"
  }
]

7.**'neuralnet'** - Set use neural network or not for user authentication. Methods - GET and POST

Example cmd: curl -X GET  127.0.0.1:5000/auth/api/v1.0/neuralnet

Return example: [
  200, 
  {
    "neuralnet": "False"
  }
]

Example cmd: curl --header "Content-Type: application/json" -X POST -d '{"neuralnet":"False"}' 127.0.0.1:5000/auth/api/v1.0/neuralnet

Return example: [
  200, 
  {
    "neuralnet": "False"
  }
]

