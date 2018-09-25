import os
import bson
from application import app
from application import User, Party
from flask import Blueprint, render_template, request, redirect, session, abort, url_for
from forms import RegistrationForm, LoginForm, EditProfileForm, PasswordForm, BasicPartyForm, EditPartyForm, CancelPartyForm, exploreForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from mongoengine.queryset.visitor import Q
import cloudinary
import cloudinary.uploader
import cloudinary.api
cloudinary.config(cloud_name="dahfv80os",api_key="892623573547898",api_secret="p-yHFMGb_oevIfCNGGVdCG1A0MU")
party_page = Blueprint('party_page',__name__)

@party_page.route('/create',methods = ['GET','POST'])
def create():
    if session.get('email') is None:
        return redirect('/user/login')
    form = BasicPartyForm(CombinedMultiDict((request.files, request.form)))
    error = None
    try:
        user = User.objects(email=session.get('email'))[0]
    except:
        user = None
    if user and request.method == 'POST' and form.validate():
        if form.end_datetime.data < form.start_datetime.data:
            error = "A party must end after it starts!"
        else:
            party = Party(
                name=form.name.data,
                place=form.place.data,
                location=[form.lng.data, form.lat.data],
                start_datetime=form.start_datetime.data,
                end_datetime=form.end_datetime.data,
                description=form.description.data,
                host=user.id,
                attendees=[user]
            )
            party.save()
            return redirect(url_for('party_page.edit', id=party.id))

    return render_template('party/create.html',form = form, error = error, user = user)

@party_page.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    if session.get('email') is None:
        return redirect('/user/login')
    try:
        party = Party.objects(id=bson.ObjectId(id))[0]
    except bson.errors.InvalidId:
        abort(404)

    user = User.objects(email = session.get('email'))[0]
    if user and user.id == party.host:
        form = EditPartyForm(obj=party)
        error = None
        message = None
        if request.method == 'POST' and form.validate():
            if form.end_datetime.data < form.start_datetime.data:
                error = 'A party must end after it starts!'
            if not error:
                form.populate_obj(party)
                if form.lng.data and form.lat.data:
                    party.location = [form.lng.data, form.lat.data]
                f = form.photo.data
                if f is not None:
                    upload_result = cloudinary.uploader.upload(file=f)
                    image_url = upload_result['url']
                    party.party_photo = image_url
                party.save()
                message = "You have updated your party!"
        return render_template('party/edit.html', form=form, error=error,
                               message=message, party=party, user = user)
    else:
        return redirect('/user/login')


@party_page.route('/<id>/public', methods=['GET'])
def public(id):
    try:
        party = Party.objects(id=bson.ObjectId(id))[0]
    except:
        abort(404)

    if party:
        try:
            host = User.objects(id=party.host)[0]
        except:
            host = None
        try:
            user = User.objects(email=session.get('email'))[0]
        except:
            user =None
        return render_template('party/public.html', party=party, host=host, user=user)
    else:
        abort(404)

@party_page.route('/<id>/cancel', methods=['GET', 'POST'])
def cancel(id):
    if session.get('email') is None:
        return redirect('/user/login')
    try:
        party = Party.objects(id=bson.ObjectId(id))[0]
    except:
        abort(404)
    user = User.objects(email = session.get('email'))[0]
    if party and party.host == user.id and party.cancel == False:
        error = None
        form = CancelPartyForm(request.form)
        if request.method == 'POST' and form.validate():
            if form.confirm.data == 'yes':
                party.cancel = True
                party.save()
                return redirect(url_for('party_page.edit', id=party.id))
            else:
                error = 'Say yes if you want to cancel'
        return render_template('party/cancel.html', form=form, error=error, party=party, user = user)
    return redirect(url_for('party_page.edit',id = party.id))


@party_page.route('/<id>/join', methods=['GET'])
def join(id):
    if session.get('email') is None:
        return redirect('/user/login')
    try:
        party = Party.objects(id=bson.ObjectId(id))[0]
    except bson.errors.InvalidId:
        abort(404)

    try:
        user = User.objects(email=session.get('email'))[0]
    except:
        user = None

    if user and party:
        if user not in party.attendees:
            party.attendees.append(user)
            party.save()
        return redirect(url_for('party_page.public', id=id))
    else:
        abort(404)

@party_page.route('/<id>/leave', methods=['GET'])
def leave(id):
    if session.get('email') is None:
        return redirect('/user/login')
    try:
        party = Party.objects(id=bson.ObjectId(id))[0]
    except bson.errors.InvalidId:
        abort(404)

    try:
        user = User.objects(email=session.get('email'))[0]
    except:
        user = None

    if user and party:
        if user in party.attendees:
            party.attendees.remove(user)
            party.save()
        return redirect(url_for('party_page.public', id=id))
    else:
        abort(404)


@party_page.route('/manage/<int:page>', methods=['GET'])
def manage(page=1):
    if session.get('email') is None:
        return redirect('/user/login')
    user = User.objects.filter(email=session.get('email')).first()
    if user:
        parties = Party.objects.filter(host=user.id).order_by('-start_datetime').paginate(page=page, per_page=4)
        return render_template('party/manage.html', parties=parties, user = user)
    else:
        abort(404)

@party_page.route('/explore/<int:page>', methods=['GET'])
@party_page.route('/explore', methods=['GET','POST'])
def explore(page=1):
    form = exploreForm(request.form)
    keyword = form.keyword.data
    user = User.objects.filter(email=session.get('email')).first()
    if keyword is not None and len(keyword) > 0:
        parties = Party.objects(Q(name__icontains = keyword) | Q(description__icontains = keyword) | Q(place__icontains = keyword)).order_by('-start_datetime').paginate(page=page, per_page=4)
    else:
        parties = Party.objects.order_by('-start_datetime').paginate(page=page, per_page=4)
    return render_template('party/explore.html', parties=parties,form = form,user = user)


