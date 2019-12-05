from urllib.parse import urlparse
import mistletoe
import re

from ruqqus.helpers.wrappers import *
from ruqqus.helpers.base36 import *
from ruqqus.helpers.sanitize import *
from ruqqus.helpers.filters import *
from ruqqus.helpers.markdown import *
from ruqqus.helpers.get import *
from ruqqus.classes import *
from flask import *
from ruqqus.__main__ import app, db, limiter

valid_board_regex=re.compile("^\w{3,25}")

@app.route("/create_guild", methods=["GET"])
@is_not_banned
def create_board_get(v):
    if not v.is_activated:
        return render_template("message.html", title="Unable to make board", text="You need to verify your email adress first.")
    if v.karma<100:
        return render_template("message.html", title="Unable to make board", text="You need more rep to do that.")

        
    return render_template("make_board.html", v=v)

@app.route("/api/board_available/<name>", methods=["GET"])
def api_board_available(name):
    if db.query(Board).filter(Board.name.ilike(name)).first():
        return jsonify({"board":name, "available":False})
    else:
        return jsonify({"board":name, "available":True})

@app.route("/create_guild", methods=["POST"])
@is_not_banned
@validate_formkey
def create_board_post(v):

    board_name=request.form.get("name")
    board_name=board_name.lstrip("+")

    if not re.match(valid_board_regex, board_name):
        return render_template("message.html", title="Unable to make board", text="Valid board names are 3-25 letters or numbers.")

    if not v.is_activated:
        return render_template("message.html", title="Unable to make board", text="Please verify your email first")

    if v.karma<100:
        return render_template("message.html", title="Unable to make board", text="You need more rep to do that")


    #check name
    if db.query(Board).filter(Board.name.ilike(board_name)).first():
        abort(409)

    description = request.form.get("description")

    with CustomRenderer as Renderer:
        description_md=Renderer.render(mistletoe.Document(description))
    description_html=sanitize(description_md, linkgen=True)

    #make the board

    new_board=Board(name=board_name,
                    description=description,
                    description_html=description_html)

    db.add(new_board)
    db.commit()

    #add user as mod
    mod=ModRelationship(user_id=v.id,
                        board_id=new_board.id)
    db.add(mod)
    db.commit()

    return redirect(new_board.permalink)

@app.route("/board/<name>", methods=["GET"])
@app.route("/+<name>", methods=["GET"])
@auth_desired
def board_name(name, v):

    board=db.query(Board).filter(Board.name.ilike(name)).first()

    if not board:
        abort(404)

    if not board.name==name:
        return redirect(board.permalink)

    sort=request.args.get("sort","hot")
    page=int(request.args.get("page", 1))
             
    return board.rendered_board_page(v=v,
                                     sort=sort,
                                     page=page)

@app.route("/mod/kick/<bid>/<pid>", methods=["POST"])
@auth_required
@validate_formkey
def mod_kick_bid_pid(bid,pid):

    board=get_board(bid)

    post = get_post(pid)

    if not post.board_id==board.id:
        abort(422)

    if not board.has_mod(v):
        abort(403)

    post.board_id=1
    db.add(post)
    db.commit()

@app.route("/mod/ban/<bid>/<username>", methods=["POST"])
@auth_required
@validate_formkey
def mod_ban_bid_user(bid, username, v):

    user=get_user(username)
    board=get_board(bid)

    if not board.has_mod(v):
        abort(403)

    if board.has_ban(user):
        abort(409)

    new_ban=BanRelationship(user_id=user.id,
                            board_id=board.id)

    db.add(new_ban)
    db.commit()
    
@app.route("/mod/unban/<bid>/<username>", methods=["POST"])
@auth_required
@validate_formkey
def mod_unban_bid_user(bid, username, v):

    user=get_user(username)
    board=get_board(bid)

    if not board.has_mod(v):
        abort(403)

    x= board.has_ban(user)
    if not x:
        abort(409)

    db.delete(x)
    db.commit()
    
    

@app.route("/user/kick/<pid>", methods=["POST"])
@auth_required
@validate_formkey
def user_kick_pid(pid, v):

    #allows a user to yank their content back to +general if it was there previously
    
    post=get_post(pid)

    if not post.author_id==v.id:
        abort(403)

    if post.board_id==post.original_board_id:
        abort(403)

    if post.board_id==1:
        abort(400)

    #block further yanks to the same board
    new_rel=PostRelationship(post_id=post.id,
                             board_id=post.board.id)
    db.add(new_rel)
    db.commit()

    post.board_id=1
    
    db.add(post)
    db.commit()
    

@app.route("/mod/take/<bid>/<pid>", methods=["POST"])
@auth_required
@validate_formkey
def mod_take_bid_pid(bid,pid):

    board=get_board(bid)

    post = get_post(pid)

    if not post.board_id==1:
        abort(422)

    if not board.has_mod(v):
        abort(403)

    if not board.can_take(post):
        abort(403)

    post.board_id=board.id
    db.add(post)
    db.commit()

@app.route("/mod/invite/<bid>/<username>", methods=["POST"])
@auth_required
@validate_formkey
def mod_invite_username(bid, username,v):

    user=get_user(username)

    board = get_board(bid)

    if not board.has_mod(v):
        abort(403)

    if not board.can_invite_mod(user):
        abort(409)

    new_mod=ModRelationship(user_id=user.id,
                            board_id=board.id,
                            accepted=False)
    db.add(new_mod)
    db.commit()

@app.route("/mod/accept/<bid>", methods=["POST"])
@auth_required
@validate_formkey
def mod_accept_board(bid, v):

    board=get_board(bid)

    x=board.has_invite(user)
    if not x:
        abort(403)

    x.accepted=True
    db.add(x)
    db.commit()
    

@app.route("/mod/remove/<bid>/<username>", methods=["POST"])
@auth_required
@validate_formkey
def mod_remove_username(bid, username,v):

    user=db.query(User).filter_by(username=username).first()
    if not user:
        abort(404)

    board = db.query(Board).filter_by(id=base36decode(bid)).first()
    if not board:
        abort(404)

    v_mod=board.has_mod(v)
    u_mod=board.has_mod(user)

    if not v_mod:
        abort(403)
    if not u_mod:
        abort(422)
    if v_mod.id > u_mod.id:
        abort(403)

    db.delete(u_mod)
    db.commit()