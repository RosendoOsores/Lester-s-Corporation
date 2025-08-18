from flask import Flask, render_template, request, redirect, url_for, flash, session
import funcionalidades as func

app = Flask(__name__)
app.secret_key = "clave-secreta"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/estado")
def estado():
    return render_template("estado.html", datos={
        "status": "ok",
        "mensaje": "Página cargada",
        "alertas": {
            "productos": []
        }
    })

@app.route("/registro/<rol>", methods=["GET", "POST"])
def registro(rol):
    if request.method == "POST":
        usuario = request.form["usuario"]
        contrasenia = request.form["contraseña"]

        datos_usuario = func.verificar_usuario(usuario, contrasenia)

        if datos_usuario and datos_usuario["rol"].lower() == rol.lower():
            session["usuario"] = usuario
            session["rol"] = rol

            if rol.lower() == "administrador":
                return redirect(url_for("administrador"))
            elif rol.lower() == "vendedor":
                return redirect(url_for("vendedor"))
            elif rol.lower() == "repositor":
                return redirect(url_for("repositor"))
        else:
            flash("Usuario o contraseña incorrectos, o el rol no coincide.")
            return redirect(url_for("registro", rol=rol))

    return render_template("registro.html")

@app.route("/administrador", methods=["GET", "POST"])
def administrador():
    if "usuario" in session and session.get("rol", "").lower() == "administrador":
        if request.method == "POST":
            if "rol" in request.form and len(request.form) == 1:
                nombre_rol = request.form["rol"]
                resultado = func.agregar_rol(nombre_rol)
                flash(resultado["mensaje"])

            elif all(k in request.form for k in ("usuario", "rol", "contraseña")):
                usuario = request.form["usuario"]
                contrasenia = request.form["contraseña"]
                nombre_rol = request.form["rol"]
                resultado = func.agregar_empleado(usuario, contrasenia, nombre_rol)
                flash(resultado["mensaje"])

            elif all(k in request.form for k in ("nombre_producto", "descripcion", "tipo", "precio", "stock_minimo", "stock_maximo")):
                nombre_producto = request.form["nombre_producto"]
                descripcion = request.form["descripcion"]
                tipo = request.form["tipo"]
                precio = float(request.form["precio"])
                stock_minimo = int(request.form["stock_minimo"])
                stock_maximo = int(request.form["stock_maximo"])
    
                resultado = func.registrar_producto(nombre_producto, descripcion, tipo, precio, stock_minimo, stock_maximo)
                flash(resultado["mensaje"])

            elif all(k in request.form for k in ("nombre_kit", "descripcion_kit", "productos_cantidades")):
                nombre_kit = request.form["nombre_kit"]
                descripcion_kit = request.form["descripcion_kit"]

                productos_cantidades_str = request.form["productos_cantidades"]
                productos_cantidades = []
                for item in productos_cantidades_str.split(","):
                    nombre_prod, cantidad = item.split(":")
                    productos_cantidades.append((nombre_prod.strip(), int(cantidad.strip())))

                resultado = func.crear_kit(nombre_kit, descripcion_kit, productos_cantidades)
                flash(resultado["mensaje"])

        return render_template("administrador.html")
    else:
        flash("Acceso no autorizado.")
        return redirect(url_for("index"))

@app.route("/vendedor", methods=["GET", "POST"])
def vendedor():
    if "usuario" in session and session.get("rol", "").lower() == "vendedor":
        if request.method == "POST":
            try:
                nombre_comprador = request.form["nombre_comprador"]
                dni_comprador = request.form["dni_comprador"]
                id_empleado = request.form["id_empleado"]

                productos = request.form.getlist("productos[]")
                cantidades_prod = request.form.getlist("cantidades_productos[]")

                kits = request.form.getlist("kits[]")
                cantidades_kits = request.form.getlist("cantidades_kits[]")

                # Procesar productos
                for nombre, cant in zip(productos, cantidades_prod):
                    if nombre.strip():
                        resultado = func.procesar_pedido_vendedor(
                            nombre, int(cant), nombre_comprador, dni_comprador, id_empleado
                        )
                        flash(resultado["mensaje"], resultado["status"])

                # Procesar kits
                for nombre, cant in zip(kits, cantidades_kits):
                    if nombre.strip():
                        resultado = func.procesar_pedido_vendedor(
                            nombre, int(cant), nombre_comprador, dni_comprador, id_empleado
                        )
                        flash(resultado["mensaje"], resultado["status"])

            except Exception as e:
                flash(f"Error inesperado al procesar pedido: {e}", "error")

        return render_template("vendedor.html")
    else:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("index"))


@app.route("/repositor", methods=["GET", "POST"])
def repositor():
    if "usuario" in session and session.get("rol", "").lower() == "repositor":
        if request.method == "POST":
            nombre_producto = request.form["nombre_producto"]
            cantidad = int(request.form["cantidad"])
            resultado = func.agregar_stock(nombre_producto, cantidad)

            # Muestra mensaje si salió bien o mal
            if resultado["status"] == "ok":
                flash(resultado["mensaje"])
            else:
                flash(f"Error: {resultado['mensaje']}")  # también se muestra en el mismo cartel
        return render_template("repositor.html")
    else:
        flash("Acceso no autorizado.")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)