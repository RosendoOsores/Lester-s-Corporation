import sqlite3

conn = sqlite3.connect('bdSistemaDeStock.db')
cursor = conn.cursor()


# =========================
# CREACIÓN DE TABLAS
# =========================



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

cursor.execute('''
    create table if not exists producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nombre_producto TEXT NOT NULL UNIQUE,
        descripcion TEXT NOT NULL,
        tipo TEXT NOT NULL,
        precio FLOAT NOT NULL,
        stock_minimo INTEGER NOT NULL,
        stock_maximo INTEGER NOT NULL,       
        stock_actual INTEGER NOT NULL
    );
''')
conn.commit()

cursor.execute('''
    create table if not exists kit (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nombre_kit TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        stock_actual INTEGER NOT NULL,
        id_producto INTEGER,
        FOREIGN KEY (id_producto) REFERENCES producto(id)
    );
''')
conn.commit()

cursor.execute('''
    ALTER TABLE producto ADD COLUMN stock_actual INTEGER DEFAULT 0;
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS producto_kit (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        id_kit INTEGER NOT NULL,
        id_producto INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        FOREIGN KEY (id_kit) REFERENCES kit(id),
        FOREIGN KEY (id_producto) REFERENCES producto(id)
    );
''')
conn.commit()

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

#cursor.execute('''ALTER TABLE pedido ADD COLUMN nombre_comprador TEXT;''')
#conn.commit()
#cursor.execute('''ALTER TABLE pedido ADD COLUMN dni_comprador TEXT;''')
#conn.commit()


#Usuario: Admin1
#Contraseña: 1234
#Rol: Administrador

#Usuario: usuario1
#Contraseña: 1234
#Rol: Vendedor

#Usuario: usuario2
#Contraseña: 1234
#Rol: Repositor


def agregar_admin():
    conn = sqlite3.connect('bdSistemaDeStock.db')
    cursor = conn.cursor()

    try:
        # Crear el rol "Administrador" si no existe
        cursor.execute("SELECT id FROM rol WHERE nombre_rol = ?", ("Administrador",))
        rol = cursor.fetchone()

        if not rol:
            cursor.execute("INSERT INTO rol (nombre_rol) VALUES (?)", ("Administrador",))
            conn.commit()
            rol_id = cursor.lastrowid
            print("Rol 'Administrador' creado.")
        else:
            rol_id = rol[0]
            print("Rol 'Administrador' ya existe.")

        # Verificar si ya existe el usuario Admin1
        cursor.execute("SELECT id FROM empleado WHERE usuario = ?", ("Admin1",))
        existente = cursor.fetchone()

        if not existente:
            cursor.execute("""
                INSERT INTO empleado (usuario, contrasenia, id_rol)
                VALUES (?, ?, ?)
            """, ("Admin1", "1234", rol_id))
            conn.commit()
            print("Usuario 'Admin1' agregado correctamente.")
        else:
            print("El usuario 'Admin1' ya existe.")

    except Exception as e:
        print("Error:", e)
        conn.rollback()

    finally:
        conn.close()
        
def verificar_producto(nombre_producto):
    conn = sqlite3.connect("bdSistemaDeStock.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM producto WHERE TRIM(LOWER(nombre_producto)) = ?",
            (nombre_producto.strip().lower(),)
        )
        producto = cursor.fetchone()

        if producto:
            print("✅ Producto encontrado en la base de datos:")
            print(producto)
        else:
            print(f"❌ Producto '{nombre_producto}' no encontrado.")

    except Exception as e:
        print("❌ Error al verificar el producto:", e)

    finally:
        conn.close()




DB_NAME = "bdSistemaDeStock.db"

def mostrar_productos_consola():
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, nombre_producto, descripcion, tipo, precio, stock_minimo, stock_maximo, stock_actual
            FROM producto
        """)
        productos = cursor.fetchall()
        if not productos:
            print("No hay productos en la base de datos.")
            return

        print("=== LISTA DE PRODUCTOS ===")
        for p in productos:
            id_p, nombre, descripcion, tipo, precio, stock_min, stock_max, stock_actual = p
            print(f"ID: {id_p}")
            print(f"Nombre: {nombre}")
            print(f"Descripción: {descripcion}")
            print(f"Tipo: {tipo}")
            print(f"Precio: {precio}")
            print(f"Stock mínimo: {stock_min}")
            print(f"Stock máximo: {stock_max}")
            print(f"Stock actual: {stock_actual}")
            print("----------------------------")

    except Exception as e:
        print(f"Error al obtener productos: {e}")
    finally:
        conn.close()



if __name__ == "__main__":
    mostrar_productos_consola()