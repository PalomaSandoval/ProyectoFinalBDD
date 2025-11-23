// ADMIN 
CREATE (u:Usuario {
    id: randomUUID(),
    nombre: "Wikiblogs",
    email: "Admin@wikiblogs.com",
    password: "Admin1",
    rol: "admin"
})

//CATEGORÍAS Y TAGS
CREATE (c1:Categoria {id: randomUUID(), nombre: "Lanzamientos"})
CREATE (c2:Categoria {id: randomUUID(), nombre: "IA"})

CREATE (t1:Tag {id: randomUUID(), nombre: "Audifonos"})
CREATE (t2:Tag {id: randomUUID(), nombre: "2025"})
CREATE (t3:Tag {id: randomUUID(), nombre: "Cancelacion de Ruido"})
CREATE (t4:Tag {id: randomUUID(), nombre: "EchoBuds 3"})

// ARTÍCULO
CREATE (a:Articulo {
    id: randomUUID(),
    titulo: 'AudioFlow Lanza los "EchoBuds 3": Cancelación de Ruido que Aprende de tu Entorno',
    texto: "La compañía de audio AudioFlow ha lanzado hoy sus nuevos auriculares insignia...",
    fecha: datetime("2025-11-09T14:08:47.414Z")
})

// Conexiones del Artículo
CREATE (u)-[:ESCRIBIO]->(a)
CREATE (a)-[:TIENE_CATEGORIA]->(c1)
CREATE (a)-[:TIENE_CATEGORIA]->(c2)
CREATE (a)-[:TIENE_TAG]->(t1)
CREATE (a)-[:TIENE_TAG]->(t2)
CREATE (a)-[:TIENE_TAG]->(t3)
CREATE (a)-[:TIENE_TAG]->(t4)

// COMENTARIO
CREATE (com:Comentario {
    id: randomUUID(),
    texto: "¡Qué buen artículo! Me sirvió mucho la explicación.",
    fecha: datetime("2025-11-10T22:42:00.123Z")
})

// Comentario
CREATE (com)-[:PERTENECE_A]->(a)
CREATE (u)-[:COMENTO]->(com)