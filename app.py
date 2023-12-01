from flask import Flask, request, jsonify, url_for, Blueprint, render_template, redirect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash

db = SQLAlchemy()
app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:GHc8JaWh4oOrwwRuxJod@proyecto-db.cy5l082ix49i.us-east-1.rds.amazonaws.com:5432/aprendedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return f'<User {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password
        }

class Score(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    score=db.Column(db.Integer, nullable=False)
    video_id=db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Score {self.score}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "score": self.score,
            "video_id": self.video_id,
            "user_id": self.user_id
        }



class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    course_name = db.Column(db.String(50),  nullable=False)
    def __repr__(self):
        return f'<Video {self.name}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "course_name": self.course_name
        }

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    alternativa1 = db.Column(db.String(500), nullable=False)
    alternativa2 = db.Column(db.String(500), nullable=False)
    alternativa3 = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Integer, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    def __repr__(self):
        return f'<Quiz {self.question}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "question": self.question,
            "alternativa1": self.alternativa1,
            "alternativa2": self.alternativa2,
            "alternativa3": self.alternativa3,
            "answer": self.answer,
            "video_id": self.video_id
        }
    
with app.app_context():
    db.create_all()

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users = list(map(lambda user: user.serialize(), users))
    return jsonify(users), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user.serialize()), 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify(user.serialize()), 200


@app.route('/register', methods=['POST'])
def register():
    name = request.json.get('name', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not name:
        return jsonify({"msg": "Name is required"}), 400
    if not email:
        return jsonify({"msg": "Email is required"}), 400
    if not password:
        return jsonify({"msg": "Password is required"}), 400
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"msg": "Email already exists"}), 400
    user = User()
    user.name = name
    user.email = email
    user.password = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"msg": "Email is required"}), 400
    if not password:
        return jsonify({"msg": "Password is required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Email not found"}), 404
    if not check_password_hash(user.password, password):
        return jsonify({"msg": "Password incorrect"}), 400
    return jsonify(user.serialize()), 200



@app.route('/video/<int:videoid>', methods=['GET'])
def get_video(videoid):
    video = Video.query.get(videoid)
    if not video:
        return jsonify({"msg": "Video not found"}), 404
    return jsonify(video.serialize()), 200

@app.route('/video/<int:videoid>', methods=['PUT'])
def update_video(videoid):
    video = Video.query.get(videoid)
    if not video:
        return jsonify({"msg": "Video not found"}), 404
    name = request.json.get('name', None)
    url = request.json.get('url', None)
    course_name = request.json.get('course_name', None)
    if not name:
        return jsonify({"msg": "Name is required"}), 400
    if not url:
        return jsonify({"msg": "Url is required"}), 400
    if not course_name:
        return jsonify({"msg": "Course name is required"}), 400
    video.name = name
    video.url = url
    video.course_name = course_name
    db.session.commit()
    return jsonify(video.serialize()), 200


@app.route('/quiz/<int:videoid>', methods=['GET'])
def get_quiz(videoid):
    quiz = Quiz.query.filter_by(video_id=videoid).all()
    quiz = list(map(lambda quiz: quiz.serialize(), quiz))
    return jsonify(quiz), 200

@app.route('/score/<int:videoid>/<int:userid>', methods=['POST'])
def score(videoid, userid):
    score_value = request.json.get('score', None)
    if score_value is None:
        return jsonify({"msg": "Score is required"}), 400
    score = Score()
    score.score = score_value
    score.video_id = videoid
    score.user_id = userid
    db.session.add(score)
    db.session.commit()
    return jsonify(score.serialize()), 201


@app.route('/score', methods=['GET'])
def get_score():
    score = Score.query.all()
    score = list(map(lambda score: score.serialize(), score))
    return jsonify(score), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
