# coding: utf8

from ednet import Student
from ednet import AD

@auth.requires_membership('Students')
def changepassword():
	form = SQLFORM.factory(
		Field('old_password', 'password'),
		Field('new_password', 'password', requires=[IS_NOT_EMPTY(),IS_STRONG(min=6, special=1, upper=1,
			error_message='minimum 6 characters, and at least 1 uppercase character, 1 lower case character, 1 number, and 1 special character')]),
		Field('confirm_new_password', 'password', requires=IS_EXPR('value==%s' % repr(request.vars.get('new_password', None)),
			error_message="Password fields don't match")),
		submit_button="Change Password").process()
	user_id="empty"
	user_id =Student.GetUserIDFromUsername(auth.user.username)
	if (form.accepted):
		old_pw = request.vars.get('old_password')
		pw = request.vars.get('new_password', '')
		user_id = Student.GetUserIDFromUsername(auth.user.username)
		curr_password = Student.GetPassword(user_id)
		if (curr_password != old_pw):
			response.flash = "Incorrect old password!"
		elif (pw != ""):
			ret = Student.SetPassword(user_id, pw)
			if (ret != ""):
				response.flash = ret
			else:
				response.flash = "Password Changed." #+ ret + " - " + AD.GetErrorString()
	elif (form.errors):
		response.flash = "Unable to set new password"
	return dict(form=form)

@auth.requires_membership('Students')
def index():
    ret = ""
    return dict(message=ret)

def guidtest():
    from ednet import SequentialGUID
    l = []
    l.append("GUID AS STRING")
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AS_STRING))
    l.append("GUID AT END")
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    l.append(SequentialGUID.NewGUID(SequentialGUID.SEQUENTIAL_GUID_AT_END))
    return locals()
