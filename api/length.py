from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from model.length import db, Length

length_api = Blueprint('length_api', __name__, url_prefix='/api')
api = Api(length_api)

class LengthAPI(Resource):
    def get(self):
        try:
            posts = Length.query.all()
            serialized_posts = [post.serialize() for post in posts]
            return serialized_posts, 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    def post(self):
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid input: No JSON data provided"}), 400

            required_fields = ['video_length', 'engagement']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return jsonify({"error": f"Missing or empty field: {field}"}), 400

            new_post = Length(
                video_length=float(data['video_length']),
                engagement=int(data['engagement'])
            )

            db.session.add(new_post)
            db.session.commit()
            return new_post.read(), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    def delete(self):
        try:
            data = request.get_json()
            if not data or 'id' not in data:
                return jsonify({"error": "Invalid input: No ID provided"}), 400

            post = Length.query.get(data['id'])
            if not post:
                return jsonify({"error": "Post not found"}), 404
            json = post.read()
            db.session.delete(post)
            db.session.commit()
            return 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

api.add_resource(LengthAPI, '/lengths')
