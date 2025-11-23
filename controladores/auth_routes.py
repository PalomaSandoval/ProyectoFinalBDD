from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session
)
from operacionesCRUD import iniciar_sesion

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')

@auth_bp.route("/")
def index():
    if 'user_id' in session and session.get('user_role') == 'admin':
        return redirect(url_for('admin_bp.admin_dashboard'))
    return render_template("InicioSesion.html")

@auth_bp.route("/login", methods=["POST"])
def procesar_login():
    email = request.form['email'] 
    password = request.form['password']
    usuario = iniciar_sesion(email, password) 
    
    if usuario:
        session['user_id'] = usuario['id'] 
        session['user_name'] = usuario['nombre']
        session['user_role'] = usuario.get('rol', 'admin') 
        
        flash(f"Hola, {usuario['nombre']}!", "success")
        return redirect(url_for('admin_bp.admin_dashboard'))
    else:
        flash("Usuario no existe o la contraseña está incorrecta.")
        return redirect(url_for('auth_bp.index'))

@auth_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    flash("Vuelve pronto")
    return redirect(url_for('auth_bp.index'))