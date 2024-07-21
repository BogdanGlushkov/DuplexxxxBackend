from flask import Blueprint, request, jsonify
from app.models import Project, User

from app.extensions import db

project = Blueprint('project', __name__, template_folder='templates')

@project.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    name = data.get('name')
    cost = data.get('cost')
    
    if not name or cost is None:
        return jsonify({'error': 'Invalid data'}), 400

    project = Project(name=name, cost=cost)
    db.session.add(project)
    db.session.commit()

    return jsonify(project.to_dict()), 201

@project.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict())

@project.route('/api/projects/<int:project_id>/users', methods=['POST'])
def add_user_to_project(project_id):
    data = request.json
    user_id = data.get('user_id')
    
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    
    if user not in project.users:
        project.users.append(user)
        db.session.commit()

    return jsonify(project.to_dict())