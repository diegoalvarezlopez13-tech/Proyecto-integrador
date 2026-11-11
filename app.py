from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Aquí agregamos la nueva columna 'estado'
    c.execute('''CREATE TABLE IF NOT EXISTS registros 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, correo TEXT, estado TEXT DEFAULT 'Pendiente')''')
    conn.commit()
    conn.close()

@app.route('/')
def inicio():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registros")
    datos = c.fetchall()
    conn.close()
    return render_template('index.html', registros=datos)

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

# Ruta para ELIMINAR
@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# Ruta para COMPLETAR (cambiar estado)
@app.route('/completar/<int:id>')
def completar(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE registros SET estado = 'Completado' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)