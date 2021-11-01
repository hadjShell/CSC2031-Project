# IMPORTS
import copy
from flask import Blueprint, render_template, request, flash
from flask_login import current_user
from app import db, login_required, requires_roles
from models import User, Draw

# CONFIG
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


# VIEWS
# view admin homepage
@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
    return render_template('admin.html', name=current_user.firstname)


# view all registered users
@admin_blueprint.route('/view_all_users', methods=['POST'])
@login_required
@requires_roles('admin')
def view_all_users():
    return render_template('admin.html', name=current_user.firstname,
                           current_users=User.query.filter_by(role='user').all())


# create a new winning draw
@admin_blueprint.route('/create_winning_draw', methods=['POST'])
@login_required
@requires_roles('admin')
def create_winning_draw():
    # get current winning draw
    current_winning_draw = Draw.query.filter_by(win=True).first()
    round = 1

    # if a current winning draw exists
    if current_winning_draw:
        # update lottery round by 1
        round = current_winning_draw.round + 1

        # delete current winning draw
        db.session.delete(current_winning_draw)
        db.session.commit()

    # get new winning draw entered in form
    submitted_draw = ''
    for i in range(6):
        submitted_draw += request.form.get('no' + str(i + 1)) + ' '
    # remove any surrounding whitespace
    submitted_draw.strip()

    # create a new draw object with the form data.
    new_winning_draw = Draw(user_id=current_user.id, draw=submitted_draw, win=True, round=round,
                            draw_key=current_user.draw_key)

    # add the new winning draw to the database
    db.session.add(new_winning_draw)
    db.session.commit()

    # re-render admin page
    flash("New winning draw added.")
    return admin()


# view current winning draw
@admin_blueprint.route('/view_winning_draw', methods=['POST'])
@login_required
@requires_roles('admin')
def view_winning_draw():

    # get winning draw from DB
    current_winning_draw = Draw.query.filter_by(win=True).first()
    # create a copy which is independent of database
    draw_copy = copy.deepcopy(current_winning_draw)
    # decrypt copy of draw
    draw_copy.view_draw(current_user.draw_key)

    # if a winning draw exists
    if current_winning_draw:
        # re-render admin page with current winning draw and lottery round
        return render_template('admin.html', winning_draw=draw_copy, name=current_user.firstname)

    # if no winning draw exists, rerender admin page
    flash("No winning draw exists. Please add winning draw.")
    return admin()


# view lottery results and winners
@admin_blueprint.route('/run_lottery', methods=['POST'])
@login_required
@requires_roles('admin')
def run_lottery():

    # get current unplayed winning draw
    current_winning_draw = Draw.query.filter_by(win=True, played=False).first()
    # create a copy which is independent of database
    draw_copy = copy.deepcopy(current_winning_draw)
    # decrypt copy of draw
    draw_copy.view_draw(current_user.draw_key)

    # if current unplayed winning draw exists
    if current_winning_draw:

        # get all unplayed user draws
        user_draws = Draw.query.filter_by(win=False, played=False).all()
        # creates a list of copied draw objects which are independent of database.
        user_draws_copies = list(map(lambda x: copy.deepcopy(x), user_draws))
        # empty list for decrypted copied draw objects
        decrypted_user_draws = []

        # decrypt each copied draw object and add it to decrypted_draws array.
        for d in user_draws_copies:
            d.view_draw(User.query.filter_by(id=d.user_id).first().draw_key)
            decrypted_user_draws.append(d)

        results = []

        # if at least one unplayed user draw exists
        if user_draws:

            # update current winning draw as played
            current_winning_draw.played = True
            db.session.add(current_winning_draw)
            db.session.commit()

            # for each unplayed user draw
            for draw in decrypted_user_draws:

                # get the owning user (instance/object)
                user = User.query.filter_by(id=draw.user_id).first()

                # if user draw matches current unplayed winning draw
                if draw.draw == draw_copy.draw:

                    # add details of winner to list of results
                    results.append((draw_copy.round, draw.draw, draw.user_id, user.email))

                    # update draw as a winning draw (this will be used to highlight winning draws in the user's
                    # lottery page)
                    for d in user_draws:
                        if d.id == draw.id:
                            d.match = True

            for d in user_draws:
                # update draw as played
                d.played = True

                # update draw with current lottery round
                d.round = current_winning_draw.round

                # commit draw changes to DB
                db.session.add(d)
                db.session.commit()

            # if no winners
            if len(results) == 0:
                flash("No winners.")

            return render_template('admin.html', results=results, name=current_user.firstname)

        flash("No user draws entered.")
        return admin()

    # if current unplayed winning draw does not exist
    flash("Current winning draw expired. Add new winning draw for next round.")
    return admin()


# view last 10 log entries
@admin_blueprint.route('/logs', methods=['POST'])
@login_required
@requires_roles('admin')
def logs():
    with open("lottery.log", "r") as f:
        content = f.read().splitlines()[-10:]
        content.reverse()

    return render_template('admin.html', logs=content, name=current_user.firstname)
