# --- IMPORTACIONES ---
import tkinter as tk
from tkinter import messagebox
# Importamos las clases de nuestras otras ventanas (Login, Subida, auditoria, busqueda, etc)
from modules.login import LoginView
from modules.modulo1_Subida import Subida_modulo1
from modules.auditoria_gui import VentanaAuditoria
from modules.gestion_categorias import GestionCategorias
from modules.busqueda_avanzada import BusquedaAvanzada

# --- CONFIGURACIÓN DE DISEÑO (Igual al Módulo de Subida) ---
COLOR_FONDO = "#F4F6F7"       # Gris muy claro (Casi blanco)
COLOR_HEADER = "#2C3E50"      # Azul Marino Oscuro (Profesional)
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"         # Azul brillante para botones
COLOR_TEXTO_BTN = "white"
COLOR_LOGOUT = "#E74C3C"      # Rojo suave para salir
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_NORMAL = ("Segoe UI", 11)
FUENTE_BTN = ("Segoe UI", 10, "bold")

# Clase Principal que controla toda la aplicación
class MainApp:
    def __init__(self, root):
        self.root = root  # La ventana raíz de Windows
        self.root.geometry("500x400")
        self.root.title("Sistema de Gestión Legal")
        self.root.configure(bg=COLOR_FONDO) # Color de fondo inicial
        self.usuario_actual = None  # Al principio no hay nadie logueado
        
        # Al iniciar la app, mostramos la pantalla de Login inmediatamente
        self.mostrar_login()

    def mostrar_login(self):
        # LIMPIEZA: Eliminamos cualquier botón o texto que haya en pantalla
        for widget in self.root.winfo_children(): widget.destroy()
        
        # Llamamos a la clase LoginView (que está en modules/login.py)
        # Le pasamos 'self.login_exitoso' como callback (qué hacer cuando el login sea correcto)
        LoginView(self.root, self.login_exitoso)

    # Esta función se ejecuta SOLO si el usuario y contraseña fueron correctos
    def login_exitoso(self, usuario):
        self.usuario_actual = usuario  # Guardamos quién entró (admin1 o abogado1)
        self.mostrar_menu_principal()  # Cambiamos de pantalla al menú

    def mostrar_menu_principal(self):
        # LIMPIEZA: Borramos la pantalla de login para dejar el lienzo blanco
        for widget in self.root.winfo_children(): widget.destroy()
        
        self.root.geometry("600x700") # Hacemos la ventana más grande para el menú
        self.root.configure(bg=COLOR_FONDO) # Aseguramos el color de fondo
        
        # Extraemos datos del usuario para mostrar bienvenida
        nombre = self.usuario_actual['nombre']
        email = self.usuario_actual.get('email', '')
        # Extraemos la LISTA DE PERMISOS (Esto es la clave de tu sistema de roles)
        permisos = self.usuario_actual.get('permisos', [])

        # --- SECCIÓN DE ENCABEZADO (HEADER) ---
        header_frame = tk.Frame(self.root, bg=COLOR_HEADER, pady=20)
        header_frame.pack(fill="x") # Se estira a lo ancho

        # Título y Bienvenida con estilo
        tk.Label(header_frame, text=f"Bienvenido, {nombre}", font=FUENTE_TITULO, 
                 bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER).pack(pady=(0,5))
        
        tk.Label(header_frame, text=f"{email}", font=("Segoe UI", 10, "italic"), 
                 bg=COLOR_HEADER, fg="#BDC3C7").pack()

        # --- SECCIÓN DE CONTENIDO (CUERPO) ---
        body_frame = tk.Frame(self.root, bg=COLOR_FONDO, pady=20)
        body_frame.pack(fill="both", expand=True)

        tk.Label(body_frame, text="PANEL DE CONTROL", font=("Segoe UI", 12, "bold"), 
                 bg=COLOR_FONDO, fg="#7F8C8D").pack(pady=(0, 15))
        
        tk.Label(body_frame, text="Seleccione una operación:", font=FUENTE_NORMAL, 
                 bg=COLOR_FONDO, fg="#2C3E50").pack(pady=(0, 10))

        # Estilo para los botones (Diccionario para no repetir código)
        btn_style = {
            "font": FUENTE_BTN,
            "bg": COLOR_BTN,
            "fg": COLOR_TEXTO_BTN,
            "relief": "flat",   # Botón plano moderno
            "bd": 0,
            "cursor": "hand2",  # Manita al pasar el mouse
            "pady": 10,
            "activebackground": "#2980B9", # Color al presionar
            "activeforeground": "white"
        }

        # --- GENERACIÓN DINÁMICA DE BOTONES ---
        # Aquí decidimos qué botones pintar basándonos en la lista de permisos

        # 1. BOTÓN DE MÓDULO 1 (Subida de documentos)
        if "subir_documentos" in permisos:
            btn = tk.Button(body_frame, text="1. Registrar Nuevo Documento", 
                            command=lambda: Subida_modulo1(self.root, self.usuario_actual), 
                            **btn_style) # Aplicamos el estilo bonito
            btn.pack(fill="x", padx=80, pady=6)

        # 2. BOTÓN DE MODULO 2 BÚSQUEDA
        if "busqueda_avanzada" in permisos:
            btn = tk.Button(body_frame, text="2. Búsqueda Avanzada", 
                            command=lambda: BusquedaAvanzada(self.root, self.usuario_actual), 
                            **btn_style)
            btn.pack(fill="x", padx=80, pady=6)

        # 3. BOTÓN DE MÓDULO 3 CATEGORÍAS
        if "gestion_categorias" in permisos:
            btn = tk.Button(body_frame, text="3. Gestión de Categorías", 
                            command=lambda: GestionCategorias(self.root, self.usuario_actual), 
                            **btn_style)
            btn.pack(fill="x", padx=80, pady=6)

        # 4. BOTÓN DE MÓDULO 4 VERSIONES
               if "versiones_comentarios" in permisos:
            btn = tk.Button(self.root, text="4. Versiones y Comentarios", bg="#FFF3E0", height=2,
                            command=lambda: abrir_modulo(self.root, db, self.usuario_actual))

            btn.pack(fill="x", padx=50, pady=5)

        # 5. BOTÓN DE MÓDULO 5 AUDITORÍA
        if "auditoria_accesos" in permisos:
            btn = tk.Button(
                body_frame,
                text="5. Auditoría de Accesos",
                command=lambda: VentanaAuditoria(self.root),
                font=FUENTE_BTN, bg=COLOR_BTN, fg="white", # Un color naranja para diferenciar admin
                relief="flat", cursor="hand2", pady=10, bd=0
            )
            btn.pack(fill="x", padx=80, pady=6)

        # Botón para cerrar sesión (regresar al login)
        # Lo ponemos abajo con un estilo de "Salida"
        tk.Button(self.root, text="Cerrar Sesión", 
                  font=("Segoe UI", 10, "bold"), fg=COLOR_LOGOUT, bg=COLOR_FONDO, 
                  activebackground=COLOR_FONDO, activeforeground="black",
                  relief="flat", cursor="hand2", bd=0,
                  command=self.mostrar_login).pack(side="bottom", pady=30)

# --- PUNTO DE ENTRADA DEL PROGRAMA ---
if __name__ == "__main__":
    root = tk.Tk()       # Creamos la ventana base invisible
    app = MainApp(root)  # Iniciamos nuestra aplicación
    root.mainloop()      # Mantiene la ventana abierta hasta que la cerremos
