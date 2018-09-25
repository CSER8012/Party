import os
import bson
from application import app
from application import User, Party
from flask import Blueprint,render_template,request,redirect,session,abort
from forms import RegistrationForm, LoginForm, EditProfileForm, PasswordForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import cloudinary
import cloudinary.uploader
import cloudinary.api
cloudinary.config(cloud_name="dahfv80os",api_key="892623573547898",api_secret="p-yHFMGb_oevIfCNGGVdCG1A0MU")
userage = Blueprint('user_page',__name__)

@userage.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    error = None
    user = None
    if request.method == 'POST' and form.validate():
        try:
            user = User.objects(email=form.email.data)[0]
        except:
            error = 'Your email or password was incorrect'
            return render_template('user/login.html',form=form,error=error)
        if user:
            if user.password.lower() == form.password.data.lower():
                session['email'] = user.email
                return redirect('/user/edit')
            else:
                user = None
        if not user:
            error = 'Your email or password was incorrect'
    return render_template('user/login.html',form=form,error=error,user = user)

@userage.route('/signup',methods=['GET','POST'])
def signup():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(username=form.username.data,email=form.email.data,password=form.password.data)
        user_search = User.objects(email=form.email.data)
        if len(user_search) > 0:
            return render_template('user/signup.html',form=form, message = "Email already in use !")

        user.save()
        return redirect('/user/login')

    return render_template('user/signup.html',form=form)

@userage.route('/logout',methods=['GET'])
def logout():
    if session.get('email') is None:
        return redirect('/user/login')
    if(session.get('email') is not None):
        session.pop('email')
    return redirect("/user/login")


@userage.route('/edit',methods=['GET','POST'])
def edit():
    if session.get('email') is None:
        return redirect('/user/login')
    useremail = session.get('email')
    if not useremail:
        return redirect('/user/login')
    form = EditProfileForm(CombinedMultiDict((request.files, request.form)))
    error = None
    user = User.objects(email=useremail)[0]
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.bio.data = user.bio
    message = None
    if request.method == 'POST' and form.validate():
        if(form.email.data != user.email):
            error = "You can not change your email!"
        else:
            editUser = User.objects(email=user.email)[0]
            editUser.username = form.username.data
            f = form.image.data
            if f is not None:
                upload_result = cloudinary.uploader.upload(file = f)
                image_url = upload_result['url']
                editUser.profile_image = image_url
            editUser.bio = form.bio.data
            editUser.save()
            message = "You have updated you information!"
    return render_template('user/edit.html', user=user, form=form, error=error, message=message)

@userage.route('/password',methods=['GET','POST'])
def password():
    if session.get('email') is None:
        return redirect('/user/login')
    useremail = session.get('email')
    if not useremail:
        return redirect('/user/login')
    error = None
    message = None
    form = PasswordForm(request.form)
    user = User.objects(email=useremail)[0]
    if request.method == 'POST':
        if form.old_password.data == user.password:
            if form.new_password.data != form.confirm.data:
                error = "Password must match!"
            else:
                user.password = form.new_password.data
                user.save()
                message = "You have changed your password!"
        else:
            error = 'Your old password is incorrect!'

    return render_template('user/password.html',form=form,error=error,message=message,user = user)

@userage.route('/<id>/<int:page>', methods=['GET'])
@userage.route('/<id>', methods=['GET'])
def profile(id,page = 1):
    if session.get('email') is None:
        return redirect('/user/login')
    try:
        user = User.objects(id=bson.ObjectId(id))[0]
    except bson.errors.InvalidId:
        abort(404)

    if user:
        parties = Party.objects(attendees__in=[user]).order_by('-start_datetime').paginate(page=page, per_page=4)
        return render_template('user/profile.html', user=user, parties=parties)
    else:
        abort(404)








