from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp, limpiar_sesion_y_redirigir
from operacionesCRUD import obtener_todos_usuarios, eliminar_usuario, registrar_usuario,obtener_mi_perfil,   actualizar_perfil

@admin_bp.route("/usuarios")
def admin_mostrar_usuarios():
    if 'user_id' not in session: 
        return limpiar_sesion_y_redirigir()

    try:
        lista_usuarios = obtener_todos_usuarios()
    except Exception as e:
        flash(f"Error: {e}")
        lista_usuarios = []
    
    return render_template("admin_usuarios.html", usuarios=lista_usuarios, active_page="usuarios")

@admin_bp.route("/usuario/crear", methods=["POST"])
def admin_crear_usuario():
    if 'user_id' not in session:
        return limpiar_sesion_y_redirigir()

    nombre = request.form.get('nombre')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not nombre or not email or not password:
        flash("Llena todo, pariente.", "error")
        return redirect(url_for('admin_bp.admin_mostrar_usuarios'))

    resultado = registrar_usuario(nombre, email, password)
    
    if isinstance(resultado, str) and len(resultado) > 20 and not " " in resultado: 
        pass 
        
    if " " in str(resultado): 
         flash(resultado, "error")
    else:
         flash(f"¡Bienvenido al equipo, {nombre}!", "success")
    
    return redirect(url_for('admin_bp.admin_mostrar_usuarios'))

@admin_bp.route("/usuario/eliminar/<user_id_str>", methods=["POST"])
def admin_eliminar_usuario(user_id_str):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return limpiar_sesion_y_redirigir()
        
    if user_id_str == session['user_id']:
        flash("No se puede eliminar este mismo usuario", "error")
        return redirect(url_for('admin_bp.admin_mostrar_usuarios'))

    if eliminar_usuario(user_id_str):
        flash("Usuario eliminado con éxito.", "success")
    else:
        flash("No se pudo eliminar al usuario.", "error")
    
    return redirect(url_for('admin_bp.admin_mostrar_usuarios'))


@admin_bp.route("/editar_perfil", methods=["GET", "POST"])
def admin_editar_perfil():
    if 'user_id' not in session:
        return limpiar_sesion_y_redirigir()

    my_id = session['user_id']

    # --- SI ES POST (Guardar cambios) ---
    if request.method == "POST":
        nuevo_nombre = request.form.get('nombre')
        nuevo_email = request.form.get('email')
        nueva_pass = request.form.get('password') 

        if not nuevo_nombre or not nuevo_email:
            flash("El nombre y el email son obligatorios", "error")
            return redirect(url_for('admin_bp.admin_editar_perfil'))

        exito = actualizar_perfil(my_id, nuevo_nombre, nuevo_email, nueva_pass)

        if exito:
            session['user_name'] = nuevo_nombre 
            flash("Perfil actualizado", "success")
            return redirect(url_for('admin_bp.admin_mostrar_usuarios'))
        else:
            flash("No se pudo actualizar tu perfil.", "error")
        
        return redirect(url_for('admin_bp.admin_editar_perfil'))

    mis_datos = obtener_mi_perfil(my_id)
    
    return render_template("admin_editar_perfil.html", usuario=mis_datos, active_page="perfil")