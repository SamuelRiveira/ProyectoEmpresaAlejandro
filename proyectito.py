import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# Lista de métodos TODO
# Asignar gestor a proyecto
# Asignar cliente a proyecto
# Crear tareas a proyecto (debe estar asignado)
# Asignar programador a proyecto
# Asignar programadores a tareas
# Obtener programadores
# Obtener proyectos (activos o todos)
# Obtener tareas de un proyecto (sin asignar o asignada)

@app.route('/asignar/gestor-proyecto', methods=['POST'])
def asignar_gestor_proyecto():
    body_request = request.json
    gestor = body_request["gestor"]
    proyecto = body_request["proyecto"]

    sql = f"""
    INSERT INTO public."GestoresProyecto"(gestor, proyecto, fecha_asignacion)
        VALUES (
            {gestor}, 
            {proyecto}, 
            NOW()
        );
    """

    return jsonify(ejecutar_sql(sql))

@app.route('/login', methods=['POST'])
def gestor_login():
    body_request = request.json
    user = body_request["usuario"]
    passwd = body_request["passwd"]

    is_logged = ejecutar_sql(
        f"SELECT * FROM public.\"Gestor\" WHERE usuario = '{user}' AND passwd = '{passwd}';"
    )

    if len(is_logged.json) == 0:
        return jsonify({"msg":"Usuario o contraseña incorrecto"})

    empleado = ejecutar_sql(
        f"SELECT * FROM public.\"Empleado\" WHERE id = '{is_logged.json[0]["empleado"]}';"
    )

    return jsonify(
        {
            "id_empleado": empleado.json[0]["id"],
            "id_gestor": is_logged.json[0]["id"],
            "nombre": empleado.json[0]["nombre"],
            "email": empleado.json[0]["email"]
        }
    )

@app.route('/crear_proyecto', methods=['POST'])
def crear_proyecto():

    data = request.json
    id_proyecto = data.get('id')
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    fecha_creacion = data.get('fecha_creacion')
    fecha_inicio = data.get('fecha_inicio')
    fecha_finalizacion = data.get('fecha_finalizacion')
    cliente = data.get('cliente')

    ejecutar_sql(
        f"""
        INSERT INTO public."Proyecto"(
            id, nombre, descripcion, fecha_creacion, fecha_inicio, fecha_finalizacion, cliente)
            VALUES ({id_proyecto}, {nombre}, {descripcion}, {fecha_creacion}, {fecha_inicio}, {fecha_finalizacion}, {cliente});
        """
    )

    return jsonify({"message": "Proyecto creado exitosamente"}), 201

@app.route('/proyecto/proyectos_gestor', methods=['GET'])
def obtener_proyectos_gestor_id():
    empleado_id = request.args.get('id')

    if not empleado_id:
        return jsonify({"error": "Falta el parámetro 'id' en la solicitud"}), 400

    query = f"""
        SELECT * FROM public."Proyecto" p
        INNER JOIN public."GestoresProyecto" gp ON p.id = gp.proyecto
        WHERE gp.gestor = {empleado_id};
    """

    return ejecutar_sql(query)


@app.route('/proyecto/proyectos_activos', methods=['GET'])
def obtener_proyectos_activos():
    return ejecutar_sql(
        'SELECT nombre, descripcion, fecha_creacion, fecha_inicio, cliente FROM public."Proyecto" WHERE fecha_finalizacion is null OR fecha_finalizacion >= CURRENT_TIMESTAMP;'
    )

@app.route('/proyecto/proyectos', methods=['GET'])
def obtener_proyectos():
    return ejecutar_sql(
        'SELECT * FROM public."Proyecto"'
    )

@app.route('/hola_mundo', methods=['GET'])
def hola_mundo():
    return jsonify({"msg":"Hola Mundo"})


@app.route('/empleado/empleados', methods = ['GET'])
def obtener_empleados():
    resultado1 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Gestor\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Gestor" g ON e.id = g.empleado;'
    )
    resultado2 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Programador\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Programador" p ON e.id = p.empleado;'
    )

    todos_los_empleados = resultado1.json + resultado2.json

    return jsonify(todos_los_empleados)

def ejecutar_sql(query = ""):

    host = "localhost" # Ejemplo: 'localhost'
    port = "5432" # Puerto por defecto de PostgreSQL
    dbname = "alexsoft" # Nombre de la base de datos
    user = "postgres" # Usuario de la base de datos
    password = "postgres" # Contraseña del usuario

    try:
        # Establecer la conexión
        connection = psycopg2.connect(
            host = host,
            port = port,
            dbname = dbname,
            user = user,
            password = password,
            options = "-c search_path=public"
        )

        cursor = connection.cursor()
        cursor.execute(query)

        # Obtener columnas para construit claves JSON
        columnas = [desc[0] for desc in cursor.description]

        # Convertir resultados a JSON
        resultados = cursor.fetchall()
        empleados = [dict(zip(columnas, fila)) for fila in resultados]

        # Cerrar el cursor y la conexión
        cursor.close()
        connection.close()

        return jsonify(empleados)

    except psycopg2.Error as e:
        print("Error: ", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug = True)