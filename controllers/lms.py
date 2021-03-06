import sys
import os
import subprocess
import urllib
from gluon import current

import paramiko

from ednet.ad import AD
from ednet.canvas import Canvas
from ednet.appsettings import AppSettings


# Needed for remote connection?
auth.settings.allow_basic_login = True
#auth.settings.actions_disabled.append('login')
#auth.settings.allow_basic_login_only = True
#auth.settings.actions.login_url=URL('your_own_error_page')

@auth.requires_membership("Administrators")
def test():
    try:
        canvas_db_pw = str(os.environ["IT_PW"]) + ""
    except KeyError as ex:
        # IT_PW not set?
        canvas_db_pw = "<IT_PW_NOT_SET>"
    db_canvas = None
    err = None
    try:
        db_canvas = DAL('postgres://postgres:' + urllib.quote_plus(canvas_db_pw) + '@postgresql/canvas_production', decode_credentials=True, migrate=False)
    except RuntimeError as ex:
        # Error connecting, move on and return None
        db_canvas = None
        err = str(ex)
    return dict(db_canvas=db_canvas, err=err)

@auth.requires_membership("Administrators")
def credential_student():
    response.view = 'generic.json'
    db = current.db
    
    key = ""
    msg = ""
    hash = ""
    user_name = ""
    full_name = ""
    # Get the user in question
    if len(request.args) > 0:
        user_name = request.args[0]
    if user_name is not None:
        # First - does the user exist?
        user_exists = False
        rows = db(db.auth_user.username == user_name).select(db.auth_user.id)
        for row in rows:
            user_exists = True
        if user_exists is True:
            key, msg, hash, full_name = Canvas.EnsureStudentAccessToken(user_name)
            
        else:
            # User doesn't exit!
            msg = "Invalid User!"
    return dict(key=key, msg=msg, hash=hash, full_name=full_name)

def get_firewall_list():
    response.view = 'default/index.json'
    db = current.db
    rs = db(db.ope_laptop_firewall_rules).select(db.ope_laptop_firewall_rules.ALL).as_list()
    return response.json(rs)
