#  --- IMPORTACIONES ---
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from db.connection import get_db

# Usamos 'tk.Frame' porque el login no es una ventana flotante nueva,
# sino que se dibuja DENTRO de la ventana raíz que le pasa el main.py.
class LoginView(tk.Frame):
    
    def __init__(self, master, on_success_callback):
        super().__init__(master)
        self.master = master
        # Guardamos la función que nos pasó el MainApp.
        # Esta función (on_success_callback) es la que se ejecutará si el login es correcto.
        # Es como decirle: "Avísame al Main cuando termines aquí".
        self.on_success = on_success_callback
        
        self.pack(pady=50) # Nos mostramos en pantalla con un margen vertical

        # --- INTERFAZ GRÁFICA DEL LOGIN ---
        tk.Label(self, text="Inicio de sesión", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(self, text="Usuario:").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        tk.Label(self, text="Contraseña:").pack()
        # show="*" oculta lo que escribes poniendo asteriscos (seguridad visual)
        self.entry_pass = tk.Entry(self, show="*") 
        self.entry_pass.pack(pady=5)

        # Botón que llama a 'validar'
        tk.Button(self, text="INICIAR SESIÓN", bg="#1976D2", fg="white", 
                  command=self.validar).pack(pady=20, fill="x")

    def validar(self):
        # 1. OBTENER DATOS
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        # 2. CONEXIÓN
        db = get_db()
        if db is None:
            messagebox.showerror("Error", "No hay conexión a BD")
            return

        # 3. BÚSQUEDA DEL USUARIO
        # find_one busca un documento donde 'username' sea igual a lo que escribieron
        usuario_encontrado = db['usuarios'].find_one({"username": user})

        if usuario_encontrado:
            # --- 4. VERIFICACIÓN DE ESTADO (Nuevo) ---
            # Antes de checar la contraseña, vemos si el usuario está activo
            if usuario_encontrado.get('estado') != 'activo':
                messagebox.showwarning("Acceso Denegado", "El usuario está inactivo o bloqueado.")
                return

            # --- 5. VERIFICACIÓN DE CONTRASEÑA ---
            
            login_valido = False
            
            # Caso admin1
            if user == "admin1" and pwd == "123":
                login_valido = True
            
            # Caso abogado1
            # Aquí es donde hacemos la excepción para que tu clave sea 'abc'
            # aunque en la base de datos hayamos guardado un hash largo por estética.
            elif user == "abogado1" and pwd == "abc":
                login_valido = True
            
            # (En un sistema real, aquí usaríamos bcrypt.checkpw para desencriptar)

            if login_valido:
                # --- ACTUALIZACIÓN DE AUDITORÍA ---
                # Si entró bien, guardamos la fecha y reseteamos los intentos fallidos a 0
                db['usuarios'].update_one(
                    {"_id": usuario_encontrado["_id"]},
                    {"$set": {
                        "ultimo_login": datetime.utcnow(),
                        "intentos_fallidos": 0 
                    }}
                )
                
                # ¡ÉXITO! Llamamos a la función del Main y le entregamos los datos del usuario
                self.on_success(usuario_encontrado)
            else:
                # --- REGISTRO DE FALLO ---
                # Si falló la contraseña, sumamos +1 a los intentos fallidos en la BD
                intentos_actuales = usuario_encontrado.get("intentos_fallidos", 0) + 1
                db['usuarios'].update_one(
                    {"_id": usuario_encontrado["_id"]},
                    {"$set": {"intentos_fallidos": intentos_actuales}}
                )
                
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")