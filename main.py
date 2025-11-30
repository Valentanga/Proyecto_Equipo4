# --- IMPORTACIONES ---
import tkinter as tk
from tkinter import messagebox
# Importamos las clases de nuestras otras ventanas (Login, Subida, auditoria, busqueda, etc)
from modules.login import LoginView
from modules.modulo1_Subida import Subida_modulo1
from modules.auditoria_gui import VentanaAuditoria
from modules.gestion_categorias import GestionCategorias


# Clase Principal que controla toda la aplicación
class MainApp:
    def __init__(self, root):
        self.root = root  # La ventana raíz de Windows
        self.root.geometry("400x300")
        self.root.title("Sistema de Gestión Legal")
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
        
        self.root.geometry("600x600") # Hacemos la ventana más grande para el menú
        
        # Extraemos datos del usuario para mostrar bienvenida
        nombre = self.usuario_actual['nombre']
        email = self.usuario_actual.get('email', '')
        # Extraemos la LISTA DE PERMISOS (Esto es la clave de tu sistema de roles)
        permisos = self.usuario_actual.get('permisos', [])

        # Mostramos encabezados
        tk.Label(self.root, text=f"Bienvenido, {nombre}", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(self.root, text=f"({email})", fg="gray").pack(pady=5)
        tk.Label(self.root, text="Seleccione una operación:", font=("Arial", 10)).pack(pady=15)

        # --- GENERACIÓN DINÁMICA DE BOTONES ---
        # Aquí decidimos qué botones pintar basándonos en la lista de permisos

        # 1. BOTÓN DE MÓDULO 1 (Subida de documentos)
        # Si la palabra 'subir_documentos' está en la lista de permisos del usuario...
        # Esta función abre la ventana de modulo 1
        # Le pasamos 'self.usuario_actual' para que el módulo sepa quién está subiendo el archivo
        if "subir_documentos" in permisos:
            # ...Dibujamos el botón
            btn = tk.Button(self.root, text="1. Registrar Nuevo Documento", 
                            bg="#E3F2FD", 
                            height=2,
                            command=lambda: Subida_modulo1(self.root, self.usuario_actual)) 
            # Al hacer click, llama a abrir_modulo_1
            btn.pack(fill="x", padx=50, pady=5)

        # 2. BOTÓN DE MODULO 2 BÚSQUEDA
        if "busqueda_avanzada" in permisos:
            btn = tk.Button(self.root, text="2. Búsqueda Avanzada", bg="#F3E5F5", height=2,
                            # Usamos lambda para imprimir en consola sin hacer nada visual (simulación)
                            command=lambda: print(">> Módulo Búsqueda: Pendiente de integración"))
            btn.pack(fill="x", padx=50, pady=5)

        # 3. BOTÓN DE  MODULO 3 CATEGORÍAS
        if "gestion_categorias" in permisos:
            btn = tk.Button(self.root, text="3. Gestión de Categorías", bg="#E8F5E9", height=2,
                            command=lambda:  GestionCategorias(self.root, self.usuario_actual))
            btn.pack(fill="x", padx=50, pady=5)

        # 4. BOTÓN DE  MODULO 4 VERSIONES
          #if "versiones_comentarios" in permisos:
            #btn = tk.Button(self.root, text="4. Versiones y Comentarios", bg="#FFF3E0", height=2,
                          #  command=lambda: abrir_modulo(self.root, db, self.usuario_actual))

            btn.pack(fill="x", padx=50, pady=5)
        # 5. BOTÓN DE  MODULO 5 AUDITORÍA
        if "auditoria_accesos" in permisos:
            btn = tk.Button(
                self.root,
                text="5. Auditoría de Accesos",
                bg="#FFEBEE",
                height=2,
                command=lambda: VentanaAuditoria(self.root) 
            )
            btn.pack(fill="x", padx=50, pady=5)


        # Botón para cerrar sesión (regresar al login)
        tk.Button(self.root, text="Cerrar Sesión", fg="red", command=self.mostrar_login).pack(pady=30)


# --- PUNTO DE ENTRADA DEL PROGRAMA ---
if __name__ == "__main__":
    root = tk.Tk()       # Creamos la ventana base invisible
    app = MainApp(root)  # Iniciamos nuestra aplicación
    root.mainloop()      # Mantiene la ventana abierta hasta que la cerremos
