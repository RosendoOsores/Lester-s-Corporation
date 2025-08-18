import os
import sqlite3

DB_NAME = "bdSistemaDeStock.db"


# Crear conexión
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Crear tablas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS rol (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nombre_rol TEXT NOT NULL
    );
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS empleado (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        usuario TEXT NOT NULL,
        contrasenia TEXT NOT NULL,
        id_rol INTEGER,
        FOREIGN KEY (id_rol) REFERENCES rol(id)
    );
''')
conn.commit()

cursor.execute("DROP TABLE IF EXISTS producto;")
cursor.execute('''
    CREATE TABLE producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nombre_producto TEXT NOT NULL UNIQUE,
        descripcion TEXT NOT NULL,
        tipo TEXT NOT NULL,
        precio FLOAT NOT NULL,
        stock_minimo INTEGER NOT NULL,
        stock_maximo INTEGER NOT NULL,       
        stock_actual INTEGER NOT NULL DEFAULT 0
    );
''')
conn.commit()


cursor.execute('''
    create table if not exists kit (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nombre_kit TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        stock_actual INTEGER NOT NULL DEFAULT 0,
        id_producto INTEGER,
        FOREIGN KEY (id_producto) REFERENCES producto(id)
    );
''')

cursor.execute('''
    create table if not exists stock(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        fecha DATE NOT NULL,
        cantidad INTEGER NOT NULL,
        tipo_movimiento TEXT NOT NULL,
        id_empleado INTEGER,
        FOREIGN KEY (id_empleado) REFERENCES empleado(id)
    );


''' )
conn.commit()

cursor.execute('''
    create table if not exists pedido(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        fecha DATE NOT NULL,
        estado TEXT NOT NULL,
        dni_comprador TEXT,
        nombre_comprador TEXT,
        id_empleado INTEGER,
        id_factura INTEGER,
        FOREIGN KEY (id_empleado) REFERENCES empleado(id),
        FOREIGN KEY (id_factura) REFERENCES factura(id)
    );
''')
conn.commit()

cursor.execute('''
    create table if not exists factura(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        fecha DATE NOT NULL,
        total INTEGER NOT NULL
    );
''')
conn.commit()

#----------------------------------------------------------------------------------

cursor.execute('''
    create table if not exists producto_pedido(
        id_producto INTEGER,
        id_pedido INTEGER,
        FOREIGN KEY (id_producto) REFERENCES producto(id),
        FOREIGN KEY (id_pedido) REFERENCES pedido(id)
    );
''')
conn.commit()
conn.close()

print("✅ Base de datos recreada desde cero con todas las tablas.")
print("🔁 Ahora podés correr app.py o cargar los datos iniciales.")
