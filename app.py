from flask import Flask, render_template, request, redirect, session, Response 
import sqlite3 
import csv
import io

app = Flask(__name__)
app.secret_key = 'clave_secreta_sigcem' # Necesario para usar sesiones

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registros 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, correo TEXT, estado TEXT DEFAULT 'Pendiente')''')
    conn.commit()
    conn.close()

# --- RUTA LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password'] 
        
        # Credenciales fijas para el prototipo
        if usuario == 'admin' and password == '1234':
            session['usuario'] = usuario
            return redirect('/')
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
            
    return render_template('login.html')

# --- RUTA LOGOUT (CERRAR SESIÓN) ---
@app.route('/logout')
def logout():
    session.pop('usuario', None) # Borra la sesión
    return redirect('/login')

# --- RUTA PRINCIPAL (PROTEGIDA) ---
@app.route('/')
def inicio():
    # Si no hay sesión, redirige al login
    if 'usuario' not in session:
        return redirect('/login')

    busqueda = request.args.get('buscar', '')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if busqueda:
        c.execute("SELECT * FROM registros WHERE nombre LIKE ? OR correo LIKE ?", ('%'+busqueda+'%', '%'+busqueda+'%'))
    else:
        c.execute("SELECT * FROM registros")
    datos = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM registros")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM registros WHERE estado = 'Completado'")
    completados = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM registros WHERE estado = 'Pendiente'")
    pendientes = c.fetchone()[0]
    
    conn.close()
    
    return render_template('index.html', registros=datos, busqueda=busqueda, 
                           total=total, completados=completados, pendientes=pendientes)

# --- RUTAS DE AGREGAR, ELIMINAR, COMPLETAR, EDITAR, ACTUALIZAR ---
# (Estas se mantienen igual, pero podríamos protegerlas también. Por rapidez, las dejamos así).

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    correo = request.form['correo']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO registros (nombre, correo) VALUES (?, ?)", (nombre, correo))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/completar/<int:id>')
def completar(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE registros SET estado = 'Completado' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/editar/<int:id>')
def editar(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registros WHERE id = ?", (id,))
    registro = c.fetchone()
    conn.close()
    return render_template('editar.html', registro=registro)

@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    nombre = request.form['nombre']
    correo = request.form['correo']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE registros SET nombre = ?, correo = ? WHERE id = ?", (nombre, correo, id))
    conn.commit()
    conn.close()
    return redirect('/')
@app.route('/exportar')
def exportar():
    if 'usuario' not in session:
        return redirect('/login')
        
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registros")
    datos = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Correo', 'Estado'])
    
    for fila in datos:
        writer.writerow(fila)
        
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=registros_sigcem.csv"})

if __name__ == '__main__':
    init_db() 
    app.run(debug=True)
    # Revision final para Qodo

