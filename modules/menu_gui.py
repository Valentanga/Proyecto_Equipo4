# modules/menu_gui.py

import tkinter as tk
from modules.auditoria_gui import VentanaAuditoria
# from modules.subida_gui import VentanaSubida  # ejemplo
# from modules.busqueda_gui import VentanaBusqueda
# etc.

class MenuPrincipal(tk.Tk):
    def __init__(self, usuario):
        super().__init__()
        self.title("Archivo de Documentos Legales Digitales")
        self.geometry("400x300")

        self.usuario = usuario
        self.rol = usuario.get("rol", "").lower()

        tk.Label(self, text=f"Bienvenido: {usuario.get('nombre','(sin nombre)')}").pack(pady=10)
        tk.Label(self, text=f"Rol: {self.rol}").pack(pady=5)

        # Aquí decidimos qué botones mostrar según el rol
        if self.rol == "administrador":
            self._boton_subida()
            self._boton_categorias()
            self._boton_auditoria()
        elif self.rol == "abogado":
            self._boton_subida()
            self._boton_busqueda()
            self._boton_versiones()
        else:
            tk.Label(self, text="Rol sin módulos asignados").pack(pady=20)

    def _boton_subida(self):
        tk.Button(self, text="Subida de documentos",
                  command=self.abrir_subida).pack(fill="x", padx=40, pady=5)

    def _boton_busqueda(self):
        tk.Button(self, text="Búsqueda avanzada",
                  command=self.abrir_busqueda).pack(fill="x", padx=40, pady=5)

    def _boton_categorias(self):
        tk.Button(self, text="Gestión de categorías",
                  command=self.abrir_categorias).pack(fill="x", padx=40, pady=5)

    def _boton_versiones(self):
        tk.Button(self, text="Versiones y comentarios",
                  command=self.abrir_versiones).pack(fill="x", padx=40, pady=5)

    def _boton_auditoria(self):
        tk.Button(self, text="Auditoría de accesos",
                  command=self.abrir_auditoria).pack(fill="x", padx=40, pady=5)

    # ---- A partir de aquí, cada función abre un módulo ----

    def abrir_auditoria(self):
        VentanaAuditoria(self)  # tu ventana ya funciona como Toplevel

    def abrir_subida(self):
        # VentanaSubida(self, self.usuario)
        pass  # aquí irá el módulo 1 de tu equipo

    def abrir_busqueda(self):
        # VentanaBusqueda(self, self.usuario)
        pass

    def abrir_categorias(self):
        # VentanaCategorias(self, self.usuario)
        pass

    def abrir_versiones(self):
        # VentanaVersiones(self, self.usuario)
        pass
