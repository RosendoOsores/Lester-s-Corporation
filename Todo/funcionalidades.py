import sqlite3

from datetime import date

DB_NAME = "bdSistemaDeStock.db"

# =========================
# FUNCIONES
# =========================

def agregar_rol(nombre_rol):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO rol (nombre_rol) VALUES (?)", (nombre_rol,))
        conn.commit()
        return {"status": "ok", "mensaje": f"Rol '{nombre_rol}' agregado correctamente."}
    except sqlite3.IntegrityError:
        return {"status": "error", "mensaje": f"El rol '{nombre_rol}' ya existe."}
    finally:
        conn.close()

def verificar_usuario(usuario, contrasenia):
    conn = sqlite3.connect("bdSistemaDeStock.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.usuario, e.contrasenia, r.nombre_rol
        FROM empleado e
        JOIN rol r ON e.id_rol = r.id
        WHERE e.usuario = ? AND e.contrasenia = ?
    """, (usuario, contrasenia))
    fila = cursor.fetchone()
    conn.close()

    if fila:
        return {"usuario": fila[0], "contrasenia": fila[1], "rol": fila[2]}
    else:
        return None


def agregar_empleado(usuario, contrasenia, nombre_rol):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM rol WHERE nombre_rol = ?", (nombre_rol,))
        rol = cursor.fetchone()
        if rol is None:
            raise Exception(f"El rol '{nombre_rol}' no existe en la base de datos.")

        id_rol = rol[0]

        cursor.execute(
            "INSERT INTO empleado (usuario, contrasenia, id_rol) VALUES (?, ?, ?)",
            (usuario, contrasenia, id_rol)
        )

        conn.commit()
        return {"status": "ok", "mensaje": f"Empleado '{usuario}' agregado correctamente."}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "mensaje": str(e)}
    finally:
        conn.close()


def registrar_producto(nombre_producto, descripcion, tipo, precio, stock_minimo, stock_maximo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''INSERT INTO producto (nombre_producto, descripcion, tipo, precio, stock_minimo, stock_maximo, stock_actual)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (nombre_producto, descripcion, tipo, precio, stock_minimo, stock_maximo, 0)  # stock_actual arranca en 0
        )
        conn.commit()
        return {"status": "ok", "mensaje": f"✅ Producto '{nombre_producto}' registrado correctamente."}
    except sqlite3.IntegrityError:
        return {"status": "error", "mensaje": f"❌ El producto '{nombre_producto}' ya existe en el sistema."}
    finally:
        conn.close()
        
def agregar_stock(nombre_producto, cantidad):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stock_actual, stock_maximo FROM producto WHERE nombre_producto = ?", (nombre_producto,))
        producto = cursor.fetchone()

        if producto is None:
            raise Exception(f"Producto '{nombre_producto}' no encontrado.")

        stock_actual, stock_maximo = producto
        nuevo_stock = stock_actual + cantidad

        if nuevo_stock > stock_maximo:
            raise Exception(
                f"No se puede agregar {cantidad} unidades a '{nombre_producto}'. "
                f"Stock máximo permitido: {stock_maximo}, stock actual: {stock_actual}."
            )

        cursor.execute(
            "UPDATE producto SET stock_actual = ? WHERE nombre_producto = ?",
            (nuevo_stock, nombre_producto)
        )
        conn.commit()
        return {"status": "ok", "mensaje": f"Stock actualizado. Nuevo stock de '{nombre_producto}': {nuevo_stock}."}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "mensaje": str(e)}

    finally:
        conn.close()



def crear_kit(nombre_kit, descripcion, productos_cantidades):
    """
    productos_cantidades: lista de tuplas [(nombre_producto, cantidad), ...]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM kit WHERE nombre_kit = ?", (nombre_kit,))
        if cursor.fetchone() is not None:
            raise Exception(f"El kit '{nombre_kit}' ya existe.")

        cursor.execute(
            "INSERT INTO kit (nombre_kit, descripcion, stock_actual) VALUES (?, ?, 0)",
            (nombre_kit, descripcion)
        )
        id_kit = cursor.lastrowid

        for nombre_prod, cantidad_requerida in productos_cantidades:
            cursor.execute("SELECT id, stock_actual FROM producto WHERE nombre_producto = ?", (nombre_prod,))
            resultado = cursor.fetchone()
            if resultado is None:
                raise Exception(f"Producto '{nombre_prod}' no existe.")

            id_producto, stock_actual = resultado
            if stock_actual < cantidad_requerida:
                raise Exception(
                    f"No hay suficiente stock para '{nombre_prod}'. Stock actual: {stock_actual}, requerido: {cantidad_requerida}")

            cursor.execute(
                "INSERT INTO producto_kit (id_producto, id_kit, cantidad) VALUES (?, ?, ?)",
                (id_producto, id_kit, cantidad_requerida)
            )

        conn.commit()
        return {"status": "ok", "mensaje": f"Kit '{nombre_kit}' creado correctamente con sus productos."}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "mensaje": str(e)}
    finally:
        conn.close()


def actualizar_stock_kits():
    """
    Actualiza automáticamente el stock de todos los kits según el stock de los productos que los componen.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre_kit FROM kit")
        kits = cursor.fetchall()

        for id_kit, nombre_kit in kits:
            cursor.execute(
                "SELECT p.id, p.nombre_producto, p.stock_actual, pk.cantidad "
                "FROM producto_kit pk "
                "JOIN producto p ON pk.id_producto = p.id "
                "WHERE pk.id_kit = ?", (id_kit,)
            )
            productos_kit = cursor.fetchall()
            if not productos_kit:
                cursor.execute("UPDATE kit SET stock_actual = 0 WHERE id = ?", (id_kit,))
                continue

            stock_max_kit = min(stock_actual // cantidad for _, _, stock_actual, cantidad in productos_kit)
            cursor.execute("UPDATE kit SET stock_actual = ? WHERE id = ?", (stock_max_kit, id_kit))

        conn.commit()
        return {"status": "ok", "mensaje": "Stock de todos los kits actualizado correctamente."}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "mensaje": str(e)}
    finally:
        conn.close()


def procesar_pedido_vendedor(nombre_item, cantidad, nombre_comprador, dni_comprador, id_empleado):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # 1. Intentar como producto
        cursor.execute("SELECT id, stock_actual, precio FROM producto WHERE nombre_producto = ?", (nombre_item,))
        resultado = cursor.fetchone()

        if resultado:
            id_producto, stock_actual, precio = resultado
            if stock_actual < cantidad:
                raise Exception(f"No hay suficiente stock para '{nombre_item}'. Stock actual: {stock_actual}, requerido: {cantidad}")

            total = precio * cantidad
            fecha_hoy = date.today().isoformat()
            estado = "confirmado"

            # Crear pedido
            cursor.execute(
                "INSERT INTO pedido (fecha, estado, id_empleado, nombre_comprador, dni_comprador) VALUES (?, ?, ?, ?, ?)",
                (fecha_hoy, estado, id_empleado, nombre_comprador, dni_comprador)
            )
            id_pedido = cursor.lastrowid

            # Actualizar stock y registrar relación producto-pedido
            cursor.execute("UPDATE producto SET stock_actual = stock_actual - ? WHERE id = ?", (cantidad, id_producto))
            for _ in range(cantidad):
                cursor.execute("INSERT INTO producto_pedido (id_producto, id_pedido) VALUES (?, ?)", (id_producto, id_pedido))

        else:
            # 2. Intentar como kit
            cursor.execute("SELECT id, stock_actual FROM kit WHERE nombre_kit = ?", (nombre_item,))
            resultado = cursor.fetchone()
            if not resultado:
                raise Exception(f"El producto o kit '{nombre_item}' no existe.")

            id_kit, stock_kit = resultado
            if stock_kit < cantidad:
                raise Exception(f"No hay suficiente stock para el kit '{nombre_item}'. Stock actual: {stock_kit}, requerido: {cantidad}")

            # Obtener productos del kit
            cursor.execute("""
                SELECT p.id, p.precio, pk.cantidad 
                FROM producto_kit pk 
                JOIN producto p ON pk.id_producto = p.id 
                WHERE pk.id_kit = ?
            """, (id_kit,))
            productos_kit = cursor.fetchall()

            total = sum(precio_producto * cant_por_kit * cantidad for _, precio_producto, cant_por_kit in productos_kit)

            fecha_hoy = date.today().isoformat()
            estado = "confirmado"
            cursor.execute(
                "INSERT INTO pedido (fecha, estado, id_empleado, nombre_comprador, dni_comprador) VALUES (?, ?, ?, ?, ?)",
                (fecha_hoy, estado, id_empleado, nombre_comprador, dni_comprador)
            )
            id_pedido = cursor.lastrowid

            # Descontar stock del kit
            cursor.execute("UPDATE kit SET stock_actual = stock_actual - ? WHERE id = ?", (cantidad, id_kit))

            # Descontar stock de los productos del kit
            for id_producto, _, cant_por_kit in productos_kit:
                cursor.execute("UPDATE producto SET stock_actual = stock_actual - ? WHERE id = ?", (cant_por_kit * cantidad, id_producto))
                for _ in range(cant_por_kit * cantidad):
                    cursor.execute("INSERT INTO producto_pedido (id_producto, id_pedido) VALUES (?, ?)", (id_producto, id_pedido))

        conn.commit()
        return {"status": "ok", "id_pedido": id_pedido, "mensaje": "Venta realizada con éxito ✅"}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "mensaje": str(e)}
    finally:
        conn.close()


def estado_general():
    """
    Retorna un resumen general de productos, kits, pedidos y alertas.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Productos
        cursor.execute("SELECT id, nombre_producto, tipo, precio, stock_minimo, stock_actual FROM producto")
        productos = cursor.fetchall()
        lista_productos = []
        alertas_productos = []

        for p in productos:
            id_p, nombre, tipo, precio, stock_min, stock_actual = p
            lista_productos.append({
                "id": id_p,
                "nombre": nombre,
                "tipo": tipo,
                "precio": precio,
                "stock_minimo": stock_min,
                "stock_actual": stock_actual
            })
            if stock_actual < stock_min:
                alertas_productos.append(f"Producto '{nombre}' por debajo del stock mínimo. Actual: {stock_actual}, Mínimo: {stock_min}")

        # Kits
        cursor.execute("SELECT id, nombre_kit, descripcion, stock_actual FROM kit")
        kits = cursor.fetchall()
        lista_kits = []
        alertas_kits = []

        for k in kits:
            id_kit, nombre_kit, descripcion, stock_kit = k
            cursor.execute(
                "SELECT p.nombre_producto, pk.cantidad, p.stock_actual FROM producto_kit pk "
                "JOIN producto p ON pk.id_producto = p.id "
                "WHERE pk.id_kit = ?", (id_kit,)
            )
            productos_kit = cursor.fetchall()

            lista_kits.append({
                "id": id_kit,
                "nombre_kit": nombre_kit,
                "descripcion": descripcion,
                "stock_actual": stock_kit,
                "productos": [{"nombre_producto": np, "cantidad": c} for np, c, _ in productos_kit]
            })

            # Verificar si se puede armar
            for nombre_producto, cantidad_req, stock_actual_producto in productos_kit:
                if stock_actual_producto < cantidad_req:
                    alertas_kits.append(
                        f"Kit '{nombre_kit}' no se puede armar. Producto '{nombre_producto}' insuficiente (Necesario: {cantidad_req}, Stock: {stock_actual_producto})"
                    )

        # Pedidos
        cursor.execute("SELECT id, fecha, estado, id_empleado, nombre_comprador, dni_comprador FROM pedido")
        pedidos = cursor.fetchall()
        lista_pedidos = [
            {
                "id": ped[0],
                "fecha": ped[1],
                "estado": ped[2],
                "id_empleado": ped[3],
                "nombre_comprador": ped[4],
                "dni_comprador": ped[5]
            }
            for ped in pedidos
        ]

        alertas = {
            "productos": alertas_productos,
            "kits": alertas_kits
        }

        return {
            "status": "ok",
            "productos": lista_productos,
            "kits": lista_kits,
            "pedidos": lista_pedidos,
            "alertas": alertas
        }

    except Exception as e:
        return {"status": "error", "mensaje": str(e)}
    finally:
        conn.close()

