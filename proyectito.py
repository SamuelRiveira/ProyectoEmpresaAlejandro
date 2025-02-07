from crypt import methods

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/proyecto/asignar_programador_tarea', methods=['POST'])
def asignar_programador_tarea():
    body_request = request.json
    tarea = body_request["tarea"]
    programador = body_request["programador"]

    query = f"""
            UPDATE public."Tarea"
            SET programador = {programador}
            WHERE id = {tarea}
        """

    return jsonify(ejecutar_sql(query))

@app.route('/proyecto/programador_proyecto', methods=['POST'])
def asignar_programador_proyecto():
    body_request = request.json
    programador = body_request["programador"]
    proyecto = body_request["proyecto"]
    fecha_asignacion = body_request["fecha_asignacion"]

    sql = f"""
            INSERT INTO public."ProgramadoresProyecto" (programador, proyecto, fecha_asignacion)
			VALUES (
			    {programador}, 
			    {proyecto}, 
			    '{fecha_asignacion}'
			)"""

    return jsonify(ejecutar_sql(sql))

@app.route('/proyecto/tarea_proyecto', methods=['POST'])
def crear_tarea_proyecto():
    body_request = request.json
    nombre = body_request["nombre"]
    descripcion = body_request["descripcion"]
    estimacion = body_request["estimacion"]
    fecha_creacion = body_request["fecha_creacion"]
    fecha_finalizacion = body_request["fecha_finalizacion"]
    programador = body_request["programador"]
    proyecto = body_request["proyecto"]

    # consulta para comprobar programador
    query1 = \
        f"""
            SELECT 1 FROM public."ProgramadoresProyecto"
            WHERE proyecto = {proyecto} AND programador = {programador};
        """

    comprobacion = ejecutar_sql(query1)
    if not comprobacion.json:
        return jsonify({"Error":"El programador no está asignado"})

    query2 = f"""
            INSERT INTO public."Tarea" (nombre, descripcion, estimacion, fecha_creacion, fecha_finalizacion, programador, proyecto)
			VALUES (
			    '{nombre}', 
			    '{descripcion}', 
			    {estimacion}, 
			    '{fecha_creacion}', 
			    '{fecha_finalizacion}', 
			    {programador}, 
			    {proyecto}
			)"""

    return ejecutar_sql(query2)

@app.route('/proyecto/asignar_cliente_proyecto', methods=['POST'])
def asignar_cliente_proyecto():
    body_request = request.json
    id_cliente = body_request["id_cliente"]
    id_proyecto = body_request["id_proyecto"]

    query = f"""
            UPDATE public."Proyecto"
            SET cliente = {id_cliente}
            WHERE id = {id_proyecto}
        """

    return jsonify(ejecutar_sql(query))

@app.route('/proyecto/asignar_gestor_proyecto', methods=['POST'])
def asignar_gestor_proyecto():
    body_request = request.json
    gestor = body_request["gestor"]
    proyecto = body_request["proyecto"]

    query = f"""
            INSERT INTO public."GestoresProyecto" (gestor, proyecto, fecha_asignacion)
            VALUES (
                {gestor},
                {proyecto},
                NOW()
            )"""

    return jsonify(ejecutar_sql(query))

@app.route('/proyecto/crear_proyecto', methods=['POST'])
def crear_proyectos():
    body_request = request.json
    nombre = body_request["nombre"]
    descripcion = body_request["descripcion"]
    fecha_creacion = body_request["fecha_creacion"]
    fecha_inicio = body_request["fecha_inicio"]
    cliente = body_request["cliente"]

    query = f"""
        INSERT INTO public."Proyecto" (nombre, descripcion, fecha_creacion, fecha_inicio, cliente)
        VALUES (
            '{nombre}',
            '{descripcion}',
            '{fecha_creacion}',
            '{fecha_inicio}',
             {cliente}
        )"""
    return jsonify(ejecutar_sql(query))

@app.route('/gestor/login', methods=['POST'])
def gestor_login():
    body_request = request.json
    user = body_request["user"]
    passwd = body_request["passwd"]

    is_logged = ejecutar_sql(
        f"SELECT * FROM public.\"Gestor\" WHERE usuario = '{user}' AND passwd = '{passwd}';"
    )

    if len(is_logged.json) == 0:
        return jsonify({"msg": "Usuario o contraseña incorrectos"})
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

@app.route('/empleado/empleados', methods=['GET'])
def obtener_lista_empleados():
    query1 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Gestor\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Gestor" g ON e.id = g.empleado;'
    )
    query2 = ejecutar_sql(
        'SELECT e.nombre AS "nombre", \'Programador\' AS "empleado" FROM public."Empleado" e INNER JOIN public."Programador" p on e.id = p.empleado;'
    )

    lista_empleados = query1.json + query2.json

    return jsonify(lista_empleados)

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

@app.route('/proyecto/tareas_proyectos', methods=['GET'])
def obtener_tareas_proyectos():
    proyecto_id = request.args.get('id')

    sql = f'SELECT * FROM public."Tarea" WHERE proyecto = {proyecto_id}'

    return ejecutar_sql(sql)


@app.route('/proyecto/proyectos_activos', methods=['GET'])
def obtener_proyectos_activos():
    return ejecutar_sql(
        'SELECT * FROM public."Proyecto" WHERE fecha_finalizacion is null OR fecha_finalizacion >= CURRENT_TIMESTAMP;'
    )

@app.route('/proyecto/historial', methods=['GET'])
def obtener_historial_proyectos():
    return ejecutar_sql(
        'SELECT * FROM public."Proyecto" WHERE fecha_finalizacion < CURRENT_TIMESTAMP;'
    )

@app.route('/proyecto/proyectos', methods=['GET'])
def obtener_proyectos():
    return ejecutar_sql(
        'SELECT * FROM public."Proyecto"'
    )

@app.route('/proyecto/programadores', methods=['GET'])
def obtener_programadores():

    return ejecutar_sql(
        f'SELECT * FROM public."Programador";'
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

        if "UPDATE" in query:
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'msg': 'actualizado'})

        if "INSERT" in query:
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'msg': 'insertado'})

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
