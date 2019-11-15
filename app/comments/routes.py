# comments/routes.py
from flask import Blueprint, request, jsonify, make_response
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from datetime import datetime
from ..models import Question, Comment
from .. import db


# set up a blueprint
comments_bp = Blueprint('comments_bp', __name__)


@comments_bp.route('/add_comment', methods=['POST'])
# @login_required
def add_comment():
    """Add comment to the question thread with id 'question_id'."""

    # get query parameters from the frontend?
    user_id = request.args.get('user_id')
    question_id = request.args.get('question_id')
    content = request.args.get('content')
    is_anon = int(request.args.get('is_anonymous'))
    source = ('source')

    # check if user_id, content, is_anon are None or not
    if user_id is not None and content is not None and is_anon is not None:
        
        # check if source was provided
        if source is None:
            source = "SideEffects App" # default source

        # create new comment object
        new_comment = Comment(user_id=user_id,
                                question_id=question_id,
                                content=content,
                                date_created=datetime.now(),
                                date_updated=datetime.now(),
                                is_anonymous=is_anon,
                                source=source)
        db.session.add(new_comment) # adds a new comment to the database

        # need to add 1 to "num_comments" column of that question
        question = Question.query.filter_by(question_id=question_id).first()
        old_num = int(question.num_comments)
        question.num_comments = old_num + 1
        # update the date for that question
        question.date_updated = datetime.now()
        
        db.session.commit() # commit all changes to the database
        return make_response(f"Comment successfully created!", 200)

    # if there is missing information
    return make_response(f"Unable to create a comment due to missing information!", 400) 


@comments_bp.route('/get_comments', methods=['GET'])
#@login_required
def get_comments():
   """Return the comments associated with a specified question_id in JSON format.
   Precondition(s):
   - question_id is not None
   """
   # get query parameters
   question_id = request.args.get('question_id')

   # check if question_id is None or not
   if question_id is not None:
       # get all comments that is from the question_id
       comments = Comment.query.filter_by(question_id=question_id).all()
       response = []
       # put each comment's information in a dict, and append it in a list
       for comment in comments:
           response.append({"comment_id": comment.comment_id,
               "user_id": comment.user_id,
               "question_id": comment.question_id,
               "content": comment.content,
               "date_updated": comment.date_updated,
               "is_anon": comment.is_anonymous,
               "source": comment.source})
       
       return jsonify(response)
   
   # if question_id is None
   return make_response(f"Unable to return comments due to missing question_id!", 400)


@comments_bp.route('/update_comment', methods=['PUT'])
#@login_required
def update_comment():
    """Update the comment with id 'comment_id' that is associated with the
    question with id 'question_id'.

    """

    # get query parameters
    question_id = request.args.get('question_id')
    comment_id = request.args.get('comment_id')
    comment_new = request.args.get('content')    
    is_anon = int(request.args.get('is_anonymous'))

    # check if there is any missing variable
    if question_id is not None and comment_id is not None and comment_new is not None and is_anon is not None:
        # query the comment that need to be updated
        update = Comment.query.filter_by(comment_id=comment_id).first()
        # update the following fields for the comment
        time_now = datetime.now()
        update.content = comment_new
        update.date_updated = time_now
        update.is_anonymous = is_anon

        # update the date_updated for that question
        question = Question.query.filter_by(question_id=question_id).first()
        question.date_updated = time_now

        db.session.commit()
        return make_response(f"Comment successfully updated!", 200)
    
    # if one of the variables is missing
    return make_response(f"Unable to update comments due to missing information!", 400)


@comments_bp.route('/delete_comment', methods=['DELETE'])
#@login_required
def delete_comment():
    """Delete the comment with id 'comment_id' that is associated with the
    question with id 'question_id'.
    subtract 1 from the num_comments column for that question

    """

    # get query parameters
    question_id = request.args.get('question_id')
    comment_id = request.args.get('comment_id')

    # check if there is any missing variable
    if question_id is not None and comment_id is not None:
        # query the comment with the id of comment_id
        delete_com = Comment.query.filter_by(comment_id=comment_id).first()
        # delete the comment from the database
        db.session.delete(delete_com)

        # num_comments in the question table need to subtract 1
        question = Question.query.filter_by(question_id=question_id).first()
        old_num = int(question.num_comments) # get the current num_comments
        # subtract by 1 and update the num_comments
        question.num_comments = old_num - 1
        question.date_updated = datetime.now()

        db.session.commit()
        return make_response(f"Comment successfully deleted!", 200) 
    
    # if there is missing variable
    return make_response(f"Unable to delete the comment due to missing information!", 400)