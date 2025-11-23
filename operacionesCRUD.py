from neo4j import GraphDatabase
from datetime import datetime
import uuid

# --- CONEXIÓN ---
# URI de Aura 
URI = "neo4j+s://1d531dbc.databases.neo4j.io" 

# Usuario y contraseña
AUTH = ("neo4j", "CUX4IPIc0UntZiNa_oij6zTd2_rMOAlZEBC2aX1Bk8A") 

driver = GraphDatabase.driver(URI, auth=AUTH)

# --- FUNCIÓN PRINCIPAL (YA SIN EL 9) ---
def ejecutar_query(query, parameters=None):
    try:
        with driver.session() as session:
            result = session.run(query, parameters)
            # Retorna lista de diccionarios
            return [record.data() for record in result]
    except Exception as e:
        print(f"Error en Neo4j: {e}")
        return []

# --- CREAR / CREATE ---

def registrar_usuario(nombre, email, password):
    # 1. Checar si ya existe (para no repetir emails)
    check_query = """
    MATCH (u:Usuario) 
    WHERE u.email = $email OR u.nombre = $nombre
    RETURN u
    """
    existentes = ejecutar_query(check_query, {"email": email, "nombre": nombre})
    
    # Si devuelve algo, es que ya existe. Regresamos el texto de error específico.
    if existentes:
        return "El email o nombre de usuario ya está en uso."

    # 2. Si no existe, lo creamos como ADMIN
    create_query = """
    CREATE (u:Usuario {
        id: randomUUID(),
        nombre: $nombre,
        email: $email,
        password: $password,
        rol: "admin"
    })
    RETURN u.id as id
    """
    result = ejecutar_query(create_query, {"nombre": nombre, "email": email, "password": password})
    
    # Si se creó, devolvemos el ID. Si falló la BD, devolvemos None.
    if result:
        return result[0]['id']
    return None 

def agregar_comentario(article_id, user_id, texto_comentario):
    query = """
    MATCH (u:Usuario {id: $user_id})
    MATCH (a:Articulo {id: $article_id})
    CREATE (c:Comentario {
        id: randomUUID(),
        texto: $texto,
        fecha: datetime()
    })
    CREATE (u)-[:COMENTO]->(c)
    CREATE (c)-[:PERTENECE_A]->(a)
    RETURN c.id as id
    """
    result = ejecutar_query(query, {"user_id": user_id, "article_id": article_id, "texto": texto_comentario})
    
    if result:
        return result[0]['id']
    return None # Corregido: Regresa None si falla

def crear_articulo(user_id, titulo, texto, ids_categorias, ids_tags):
    #  Usuario -> Articulo -> Tags/Categorias
    query = """
    MATCH (u:Usuario {id: $user_id})
    
    // Crear el articulo
    CREATE (a:Articulo {
        id: randomUUID(),
        titulo: $titulo,
        texto: $texto,
        fecha: datetime()
    })
    CREATE (u)-[:ESCRIBIO]->(a)
    
    // Conectar categorias
    WITH a, $ids_categorias as cats, $ids_tags as tags
    UNWIND cats as cat_id
    MATCH (c:Categoria {id: cat_id})
    CREATE (a)-[:TIENE_CATEGORIA]->(c)
    
    // Conectar tags
    WITH a, tags
    UNWIND tags as tag_id
    MATCH (t:Tag {id: tag_id})
    CREATE (a)-[:TIENE_TAG]->(t)
    
    RETURN a.id as id
    """
    result = ejecutar_query(query, {
        "user_id": user_id, 
        "titulo": titulo, 
        "texto": texto, 
        "ids_categorias": ids_categorias, 
        "ids_tags": ids_tags
    })
    
    if result:
        return result[0]['id']
    return None # Corregido: Regresa None si falla

def crear_categoria(nombre):
    query = """
    MERGE (c:Categoria {nombre: $nombre})
    ON CREATE SET c.id = randomUUID()
    RETURN c.id as id
    """
    result = ejecutar_query(query, {"nombre": nombre})
    return result[0]['id'] if result else None

def crear_tag(nombre):
    query = """
    MERGE (t:Tag {nombre: $nombre})
    ON CREATE SET t.id = randomUUID()
    RETURN t.id as id
    """
    result = ejecutar_query(query, {"nombre": nombre})
    return result[0]['id'] if result else None


# MOSTRAR / READ 

def iniciar_sesion(email, password):
    print(f"--> Intentando Login: Email='{email}'")
    
    query = """
    MATCH (u:Usuario {email: $email, password: $password})
    RETURN u
    """
    result = ejecutar_query(query, {"email": email, "password": password})
    
    if result:
        print("--> Login Exitoso")
        return result[0]['u']
    else:
        print("--> Login Fallido: Email o contraseña incorrectos")
        return None


def Articulos_blog():
    query = """
    MATCH (a:Articulo)<-[:ESCRIBIO]-(u:Usuario)
    OPTIONAL MATCH (a)-[:TIENE_CATEGORIA]->(c:Categoria)
    OPTIONAL MATCH (a)-[:TIENE_TAG]->(t:Tag)
    RETURN 
        a.id as _id, 
        a.titulo as titulo, 
        toString(a.fecha) as fecha, 
        a.texto as texto, 
        u.nombre as autor_nombre,
        collect(DISTINCT c.nombre) as categorias,
        collect(DISTINCT t.nombre) as tags
    ORDER BY fecha DESC
    """
    return ejecutar_query(query)

def obtener_todos_comentarios():
    query = """
    MATCH (c:Comentario)-[:PERTENECE_A]->(a:Articulo)
    MATCH (u:Usuario)-[:COMENTO]->(c)
    RETURN 
        c.id as _id,
        c.texto as texto_comentario,
        toString(c.fecha) as fecha,
        u.nombre as autor_nombre,
        a.titulo as articulo_titulo
    ORDER BY fecha DESC
    """
    return ejecutar_query(query)

def obtener_todas_categorias():
    return ejecutar_query("MATCH (c:Categoria) RETURN c.id as _id, c.nombre as name")

def obtener_todos_tags():
    return ejecutar_query("MATCH (t:Tag) RETURN t.id as _id, t.nombre as name")

def obtener_todos_usuarios():
    return ejecutar_query("MATCH (u:Usuario) RETURN u.id as _id, u.nombre as name, u.email as email, u.rol as role ORDER BY u.nombre")

def obtener_articulo_por_id(article_id):
    query = """
    MATCH (a:Articulo {id: $id})
    OPTIONAL MATCH (a)-[:TIENE_CATEGORIA]->(c:Categoria)
    OPTIONAL MATCH (a)-[:TIENE_TAG]->(t:Tag)
    RETURN 
        a.id as _id,
        a.titulo as title,
        a.texto as text,
        collect(c.id) as categories,
        collect(t.id) as tags,
        a.autor_nombre as autor_nombre
    """
    result = ejecutar_query(query, {"id": article_id})
    return result[0] if result else None

# Funciones auxiliares para editar
def obtener_mi_perfil(user_id):
    query = """
    MATCH (u:Usuario {id: $id})
    RETURN u.id as _id, u.nombre as name, u.email as email, u.password as password
    """
    result = ejecutar_query(query, {"id": user_id})
    return result[0] if result else None


def obtener_categoria_por_id(cat_id):
    query = """
    MATCH (t:Categoria {id: $id})
    RETURN 
        t.id as _id,        
        t.nombre as name    
    """
    result = ejecutar_query(query, {"id": cat_id})
    return result[0] if result else None


def obtener_tag_por_id(tag_id):
    query = """
    MATCH (t:Tag {id: $id})
    RETURN 
        t.id as _id,        // El HTML pide ._id
        t.nombre as name    // El HTML pide .name
    """
    result = ejecutar_query(query, {"id": tag_id})
    return result[0] if result else None

def obtener_comentario_por_id(com_id):
    query = """
    MATCH (c:Comentario {id: $id})
    RETURN 
        c.id as _id,          
        c.texto as text,     
        toString(c.fecha) as fecha
    """
    result = ejecutar_query(query, {"id": com_id})
    return result[0] if result else None


# --- EDITAR / UPDATE ---
def actualizar_perfil(user_id, nombre, email, password):
    # Si la password no tiene ndaa, no se cambia para no borrar
    if password:
        query = """
        MATCH (u:Usuario {id: $id})
        SET u.nombre = $nombre, u.email = $email, u.password = $password
        RETURN u.id
        """
        params = {"id": user_id, "nombre": nombre, "email": email, "password": password}
    else:
        # Si no escribió password nueva, solo actualiza nombre y email
        query = """
        MATCH (u:Usuario {id: $id})
        SET u.nombre = $nombre, u.email = $email
        RETURN u.id
        """
        params = {"id": user_id, "nombre": nombre, "email": email}

    result = ejecutar_query(query, params)
    return True if result else False

def editar_articulo(article_id, titulo, texto, ids_categorias, ids_tags):
    query = """
    MATCH (a:Articulo {id: $id})
    SET a.titulo = $titulo, a.texto = $texto
    
    // Borrar relaciones viejas
    WITH a
    OPTIONAL MATCH (a)-[r1:TIENE_CATEGORIA]->()
    OPTIONAL MATCH (a)-[r2:TIENE_TAG]->()
    DELETE r1, r2
    
    // Crear nuevas relaciones
    WITH a
    UNWIND $ids_cats as cat_id
    MATCH (c:Categoria {id: cat_id})
    MERGE (a)-[:TIENE_CATEGORIA]->(c)
    
    WITH a
    UNWIND $ids_tags as tag_id
    MATCH (t:Tag {id: tag_id})
    MERGE (a)-[:TIENE_TAG]->(t)
    
    RETURN a.id
    """
    res = ejecutar_query(query, {
        "id": article_id, 
        "titulo": titulo, 
        "texto": texto,
        "ids_cats": ids_categorias,
        "ids_tags": ids_tags
    })
    return True if res else False

def editar_comentario(comment_id, nuevo_texto):
    query = "MATCH (c:Comentario {id: $id}) SET c.texto = $texto RETURN c.id"
    res = ejecutar_query(query, {"id": comment_id, "texto": nuevo_texto})
    return True if res else False

def editar_categoria(cat_id, nuevo_nombre):
    check = ejecutar_query("MATCH (c:Categoria {nombre: $nombre}) WHERE c.id <> $id RETURN c", 
                           {"nombre": nuevo_nombre, "id": cat_id})
    if check: return False
    
    query = "MATCH (c:Categoria {id: $id}) SET c.nombre = $nombre RETURN c.id"
    res = ejecutar_query(query, {"id": cat_id, "nombre": nuevo_nombre})
    return True if res else False

def editar_tag(tag_id, nuevo_nombre):
    check = ejecutar_query("MATCH (t:Tag {nombre: $nombre}) WHERE t.id <> $id RETURN t", 
                           {"nombre": nuevo_nombre, "id": tag_id})
    if check: return False

    query = "MATCH (t:Tag {id: $id}) SET t.nombre = $nombre RETURN t.id"
    res = ejecutar_query(query, {"id": tag_id, "nombre": nuevo_nombre})
    return True if res else False


# --- ELIMINAR / DELETE ---

def eliminar_usuario(user_id):
    query = """
    MATCH (u:Usuario {id: $id})
    
    // Borrar comentarios hechos por él
    OPTIONAL MATCH (u)-[:COMENTO]->(c_propio:Comentario)
    DETACH DELETE c_propio
    
    // Borrar artículos y los comentarios que tengan esos artículos
    WITH u
    OPTIONAL MATCH (u)-[:ESCRIBIO]->(a:Articulo)
    OPTIONAL MATCH (a)<-[:PERTENECE_A]-(c_ajeno:Comentario)
    DETACH DELETE c_ajeno, a
    
    // Finalmente borrar al usuario
    WITH u
    DETACH DELETE u
    RETURN count(u) as deleted
    """
    ejecutar_query(query, {"id": user_id})
    return True

def eliminar_articulo(article_id):
    query = """
    MATCH (a:Articulo {id: $id})
    OPTIONAL MATCH (a)<-[:PERTENECE_A]-(c:Comentario)
    DETACH DELETE c, a
    """
    ejecutar_query(query, {"id": article_id})
    return True

def eliminar_comentario_individual(comment_id):
    query = "MATCH (c:Comentario {id: $id}) DETACH DELETE c"
    ejecutar_query(query, {"id": comment_id})
    return True

def eliminar_categoria(cat_id):
    query = "MATCH (c:Categoria {id: $id}) DETACH DELETE c"
    ejecutar_query(query, {"id": cat_id})
    return True

def eliminar_tag(tag_id):
    query = "MATCH (t:Tag {id: $id}) DETACH DELETE t"
    ejecutar_query(query, {"id": tag_id})
    return True