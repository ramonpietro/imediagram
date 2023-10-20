from flask import  render_template, url_for, redirect, request,send_from_directory
from app_imediagram import app, bcrypt, database
from app_imediagram.forms import FormLogin, FormCriarConta, FormFoto
from flask_login import login_required, login_user, logout_user, current_user
from app_imediagram.models import Usuario, Foto
from sqlalchemy import text
from werkzeug.utils import secure_filename
import uuid as uuid

import os

@app.route("/", methods=["GET", "POST"])
def index():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("index.html", form=form_login)

@app.route('/login', methods = [ "GET", "POST" ] )
def login():
    formlogin = FormLogin()

    if formlogin.validate_on_submit():
        
        usuario = Usuario.query.filter_by( email = formlogin.email.data ).first()
        if usuario and bcrypt.check_password_hash( usuario.senha, formlogin.senha.data ):
            login_user( usuario )
            return redirect( url_for( "homepage" ,id_usuario = usuario.id) )

    return render_template( 'login.html', form = formlogin )

@app.route('/register', methods = [ "GET", "POST" ] )
def register():
    reisterForm = FormCriarConta()
    if reisterForm.is_submitted():
        photo = request.files['foto_perfil']
        photo_filename = secure_filename(photo.filename)
        photo_name = str(uuid.uuid1()) + "_" + photo_filename
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], photo_name )

        photo.save(caminho)
        
        senha = bcrypt.generate_password_hash( reisterForm.senha.data )
        usuario = Usuario( username = reisterForm.username.data, senha = senha, email = reisterForm.email.data, foto_perfil=photo_name )
        database.session.add( usuario )
        database.session.commit()

        login_user( usuario, remember = True )

        return redirect( url_for( "perfil", id_usuario = usuario.id ) )

    return render_template( 'register.html', form = reisterForm )


@app.route( '/logout' )
@login_required
def logout():
    logout_user()
    return redirect( url_for( "login" ) )

@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data,
                          senha=senha, email=form_criarconta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form = form_criarconta)

@app.route('/perfil/<id_usuario>', methods = [ "GET", "POST" ])
@login_required
def perfil( id_usuario ):
    fotos = Foto.query.filter_by(id_usuario=id_usuario).all()
    usuario = Usuario.query.get( int( id_usuario ) )
    return render_template( 'perfil.html', usuario = usuario, form = None,fotos=fotos  )
    
    
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    
    
