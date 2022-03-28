from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.categories import Category

parser = reqparse.RequestParser()
parser.add_argument('color', required=True)
parser.add_argument('name', required=True)
parser.add_argument('user_id', required=True)


def abort_if_category_not_found(category_id):
    session = db_session.create_session()
    category = session.query(Category).get(category_id)
    if not category:
        abort(404,  message=f"Category {category_id} not found")


class CategoryResource(Resource):
    def get(self, category_id):
        abort_if_category_not_found(category_id)
        session = db_session.create_session()
        category = session.query(Category).get(category_id)
        return jsonify({'category': category.to_dict(only=('id', 'color', 'name', 'user_id'))})

    def delete(self, category_id):
        abort_if_category_not_found(category_id)
        session = db_session.create_session()
        category = session.query(Category).get(category_id)
        session.delete(category)
        session.commit()
        return jsonify({'success': 'OK'})


class CategoriesResource(Resource):
    def get(self):
        session = db_session.create_session()
        categories = session.query(Category).all()
        return jsonify({'category': [item.to_dict(only=('id', 'color', 'name', 'user_id')) for item in categories]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        category = Category(
            color=args['color'],
            name=args['name'],
            user_id=args['user_id']
        )
        session.add(category)
        session.commit()
        return jsonify({'success': 'OK'})
