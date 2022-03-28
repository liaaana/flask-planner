from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.tasks import Task

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=False)
parser.add_argument('date', required=False)
parser.add_argument('start_time', required=False)
parser.add_argument('end_time', required=False)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('category_id', required=True, type=int)
parser.add_argument('is_done', required=False, type=bool)


def abort_if_task_not_found(task_id):
    session = db_session.create_session()
    task = session.query(Task).get(task_id)
    if not task:
        abort(404,  message=f"Task {task_id} not found")


class TaskResource(Resource):
    def get(self, task_id):
        abort_if_task_not_found(task_id)
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        return jsonify({'task': task.to_dict(only=('title', 'content', 'date', 'start_time', 'end_time','user_id', 'category_id', 'is_done'))})

    def delete(self, task_id):
        abort_if_task_not_found(task_id)
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        session.delete(task)
        session.commit()
        return jsonify({'success': 'OK'})


class TasksResource(Resource):
    def get(self):
        session = db_session.create_session()
        tasks = session.query(Task).all()
        return jsonify({'tasks': [item.to_dict(only=('title', 'content', 'user.name')) for item in tasks]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        task = Task(
            title=args['title'],
            content=args['content'],
            date=args['date'],
            start_time=args['start_time'],
            end_time=args['end_time'],
            user_id=args['user_id'],
            category_id=args['category_id'],
            is_done=args['is_done']
        )
        session.add(task)
        session.commit()
        return jsonify({'success': 'OK'})
