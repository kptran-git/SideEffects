# questions/routes.py
from flask import Blueprint, request, make_response, jsonify
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from ..models import Question, Comment
from datetime import datetime
from flask_login import login_required
from .. import db


# set up a blueprint
questions_bp = Blueprint("questions_bp", __name__)


@questions_bp.route("/add_question", methods=["POST"])
@login_required
def add_question():
    """Add a question to the database.

    Precondition(s):
    - user_id is not None
    - question_text is not None
    - is_anon is not None
    """

    # get query parameters
    user_id = request.args.get("user_id")
    title = request.args.get("title")
    content = request.args.get("content")
    is_anon = int(request.args.get("is_anonymous"))
    source = request.args.get("source")

    # prepare headers for response
    headers = {"Content-Type": "application/json"}

    if user_id is not None and content is not None and is_anon is not None:

        # check if a question with this content exists already
        existing_question = Question.query.filter(Question.content == content).first()
        if existing_question:
            return make_response(f"This question already exists!", 400)

        # check if source was provided
        if source is None:
            source = "SideEffects App" # default source

        # create new question object
        new_question = Question(user_id=user_id,
                        title=title,
                        content=content,
                        date_created=datetime.now(),
                        date_updated=datetime.now(),
                        is_anonymous=is_anon,
                        source=source,
                        num_comments=0)
        db.session.add(new_question) # adds a new question to the database
        db.session.commit() # commit all changes to the database
        response = {
            "message": f"Question successfully created!",
            "success": True
        }
        return jsonify(response), 200, headers

    # return make_response(f"Unable to create question due to missing information!", 400)
    response = {
        "message": f"Unable to create question due to missing information!",
        "success": False
    }
    return jsonify(response), 200, headers


@questions_bp.route("/get_question", methods=["GET"])
@login_required
def get_question():
    """Return a question from the database with id 'question_id' in JSON format.

    Returns a JSON response containing the question text of the given question_id.
    """

    # get query parameters
    question_id = request.args.get("question_id")

    # query for question
    question = Question.query.get(question_id)

    # format response
    response = []
    response.append({
        "question_id": question_id,
        "question_user_id": question.user_id,
        "question_title": question.title,
        "question_content": question.content,
        "question_date_updated": question.date_updated,
        "question_source": question.source,
        "question_is_anon": question.is_anonymous,
        "question_num_comments": question.num_comments,
        "message": "Successfully retrieved question.",
        "success": True
    })

    # prepare headers for response
    headers = {"Content-Type": "application/json"}

    return jsonify(response), 200, headers


@questions_bp.route("/get_faqs", methods=["GET"])
@login_required
def get_faqs():
    """Return a JSON object of the top 10 most frequently asked questions FAQs."""

    # get top 10 questions from database (what metric defines a FAQ?)
    faqs = Question.query.order_by(Question.question_id).limit(10)

    # construct response
    response = []
    for question in faqs:

        question_id = question.question_id

        # get comments associated with the question_id
        comments = Comment.query.filter_by(question_id=question_id).all()
        comment_user_id = []
        comment_content = []
        comment_source = []
        comment_is_anon = []
        comment_date_updated = []
        for comment in comments:
            comment_user_id.append(comment.user_id)
            comment_content.append(comment.content)
            comment_source.append(comment.source)
            comment_is_anon.append(comment.is_anonymous)
            comment_date_updated.append(comment.date_updated)

        # add question data into response
        response.append({
            "id": question.question_id,
            "question_user_id": question.user_id,
            "question_title": question.title,
            "question_date_updated": question.date_updated,
            "question_source": question.source,
            "question_content": question.content,
            "question_num_comments": question.num_comments,
            "question_is_anon": question.is_anonymous,
            "comment_content": comment_content,
            "comment_source": comment_source,
            "comment_date_updated": comment_date_updated,
            "comment_is_anon": comment_is_anon,
            "comment_user_id": comment_user_id
        })

    # prepare headers for response
    headers = {"Content-Type": "application/json"}

    return jsonify(response), 200, headers


# not sure about the methods
@questions_bp.route("/delete_question", methods=["DELETE"])
def delete_question():
    # get query parameters
    question_id = request.args.get("question_id")

    # get the question that needs to be deleted
    delete_q = Question.query.filter_by(question_id=question_id)
    db.session.delete(delete_q)

    db.session.commit()
    return make_response(f"Question successfully deleted!", 200)


@questions_bp.route("/update_question", methods=["DELETE"])
def update_question():
    # get query parameters
    question_id = request.args.get("question_id")
    new_title = request.args.get("title")
    new_content = request.args.get("content")
    new_date = request.args.get("date_updated")
    is_anon = request.args.get("is_anonymous")

    # get the question that needs to be updated
    update_q = Question.query.filter_by(question_id=question_id)
    # update the following fields of the question
    update_q.title = new_title
    update_q.content = new_content
    update_q.date_updated = new_date
    update_q.is_anonymous = is_anon

    db.session.commit()
    return make_response(f"Question successfully updated!", 200)
