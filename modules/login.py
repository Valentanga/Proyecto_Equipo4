# --- IMPORTACIONES ---
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from db.connection import get_db

# --- CONFIGURACIÓN DE DISEÑO (Igual al Main) ---
COLOR_FONDO = "#F4F6F7"       # Gris muy claro
COLOR_HEADER = "#2C3E50"      # Azul oscuro
COLOR_TITULO = "#34495E"      # Azul grisáceo
COLOR_BTN = "#2980B9"         # Azul brillante
COLOR_TEXTO_BTN = "white"
FUENTE_TITULO = ("Segoe UI", 24, "bold")
FUENTE_LABEL = ("Segoe UI", 12)
FUENTE_ENTRY = ("Segoe UI", 12)

# Usamos 'tk.Frame' porque el login no es una ventana flotante nueva,
# sino que se dibuja DENTRO de la ventana raíz que le pasa el main.py.
class LoginView(tk.Frame):
    
    def __init__(self, master, on_success_callback):
        super().__init__(master)
        self.master = master
        
        # Guardamos la función que nos pasó el MainApp.
        self.on_success = on_success_callback
        
        # Configuramos el fondo de este Frame y de la ventana principal
        self.configure(bg=COLOR_FONDO)
        self.master.configure(bg=COLOR_FONDO)
        
        # Usamos place() para centrar todo el bloque de login en medio de la ventana
        # relx=0.5, rely=0.5 -> Centro exacto
        self.place(relx=0.5, rely=0.5, anchor="center")

        # --- INTERFAZ GRÁFICA DEL LOGIN ---

        # Título Grande
        tk.Label(self, text="ACCESO AL SISTEMA", font=FUENTE_TITULO, 
                 bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=(20, 10))
        
        # Subtítulo descriptivo
        tk.Label(self, text="Archivo de Documentos Legales Digitales", font=("Segoe UI", 10, "italic"),
                 bg=COLOR_FONDO, fg="#7F8C8D").pack(pady=(0, 30))

        # Campo Usuario
        tk.Label(self, text="Usuario:", font=FUENTE_LABEL, 
                 bg=COLOR_FONDO, fg="#2C3E50").pack(anchor="w", padx=20)
        
        self.entry_user = tk.Entry(self, font=FUENTE_ENTRY, width=30, bd=2, relief="groove")
        self.entry_user.pack(pady=5, padx=20, ipady=3) # ipady hace la caja más alta y fácil de clicar

        # Campo Contraseña
        tk.Label(self, text="Contraseña:", font=FUENTE_LABEL, 
                 bg=COLOR_FONDO, fg="#2C3E50").pack(anchor="w", padx=20, pady=(10, 0))
        
        # show="•" oculta la contraseña con puntos en lugar de asteriscos (más moderno)
        self.entry_pass = tk.Entry(self, show="•", font=FUENTE_ENTRY, width=30, bd=2, relief="groove")
        self.entry_pass.pack(pady=5, padx=20, ipady=3)

        # Botón INICIAR SESIÓN (Estilo plano y moderno)
        tk.Button(self, text="INGRESAR AL SISTEMA", 
                  font=("Segoe UI", 11, "bold"), 
                  bg=COLOR_BTN, fg=COLOR_TEXTO_BTN,
                  activebackground="#1A5276", activeforeground="white",
                  relief="flat", cursor="hand2", width=25,
                  command=self.validar).pack(pady=40)

        # Footer pequeño (Copyright falso)
        tk.Label(self, text="© 2025 Seguridad Interna", font=("Segoe UI", 8), 
                 bg=COLOR_FONDO, fg="#BDC3C7").pack(pady=10)

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
            # --- 4. VERIFICACIÓN DE ESTADO ---
            if usuario_encontrado.get('estado') != 'activo':
                messagebox.showwarning("Acceso Denegado", "El usuario está inactivo o bloqueado.")
                return

            # --- 5. VERIFICACIÓN DE CONTRASEÑA ---
            login_valido = False
            
            # Caso admin1
            if user == "admin1" and pwd == "123":
                login_valido = True
            
            # Caso abogado1
            elif user == "abogado1" and pwd == "abc":
                login_valido = True
            
            if login_valido:
                # --- ACTUALIZACIÓN DE AUDITORÍA (EXITOSO) ---
                db['usuarios'].update_one(
                    {"_id": usuario_encontrado["_id"]},
                    {"$set": {
                        "ultimo_login": datetime.utcnow(),
                        "intentos_fallidos": 0 
                    }}
                )
                # Llamamos a la función del Main y le entregamos los datos del usuario
                self.on_success(usuario_encontrado)
            else:
                # --- REGISTRO DE FALLO ---
                intentos_actuales = usuario_encontrado.get("intentos_fallidos", 0) + 1
                db['usuarios'].update_one(
                    {"_id": usuario_encontrado["_id"]},
                    {"$set": {"intentos_fallidos": intentos_actuales}}
                )
                
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")