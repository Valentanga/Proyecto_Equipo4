# modules/auditoria_gui.py

import tkinter as tk
from tkinter import ttk
from models.auditoria_service import AuditoriaService

# --------- ESTILOS ----------
COLOR_FONDO = "#F4F6F7"       # Gris muy claro (casi blanco)
COLOR_HEADER = "#2C3E50"      # Azul marino oscuro (profesional)
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"         # Azul brillante para botones
COLOR_TEXTO_BTN = "white"
COLOR_LOGOUT = "#E74C3C"      # (Por si luego agregas botón de cerrar)
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_NORMAL = ("Segoe UI", 11)
FUENTE_BTN = ("Segoe UI", 10, "bold")


class VentanaAuditoria(tk.Toplevel):
    """
    Ventana de Tkinter para consultar la auditoría de accesos.
    Solo la debería abrir el Administrador.
    """

    def __init__(self, master=None, auditoria_service=None):
        super().__init__(master)
        self.title("Auditoría de accesos")
        self.geometry("900x450")
        self.configure(bg=COLOR_FONDO)

        # Servicio de auditoría (si no te pasan uno, crea uno nuevo)
        self.auditoria_service = auditoria_service or AuditoriaService()

        # Estilo para la tabla
        style = ttk.Style(self)
        style.configure("Audit.Treeview", font=FUENTE_NORMAL)
        style.configure("Audit.Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self._crear_widgets()
        self.cargar_eventos()  # cargar datos al inicio

    def _crear_widgets(self):
        # ----- HEADER -----
        header = tk.Frame(self, bg=COLOR_HEADER)
        header.pack(fill="x")

        lbl_titulo = tk.Label(
            header,
            text="Auditoría de accesos",
            bg=COLOR_HEADER,
            fg=COLOR_TEXTO_HEADER,
            font=FUENTE_TITULO,
            pady=10
        )
        lbl_titulo.pack(fill="x")

        # ----- CONTENEDOR PRINCIPAL -----
        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # ----- Frame de filtros -----
        filtro_frame = tk.Frame(contenedor, bg=COLOR_FONDO)
        filtro_frame.pack(fill="x", pady=5)

        tk.Label(
            filtro_frame,
            text="Usuario:",
            bg=COLOR_FONDO,
            font=FUENTE_NORMAL
        ).grid(row=0, column=0, sticky="w")

        self.entry_usuario = tk.Entry(filtro_frame, width=20)
        self.entry_usuario.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(
            filtro_frame,
            text="Acción:",
            bg=COLOR_FONDO,
            font=FUENTE_NORMAL
        ).grid(row=0, column=2, sticky="w")

        # 👇 Aquí agregamos TODAS las acciones que ya aparecen en tus logs
        acciones_posibles = [
            "",
            "VER_DOCUMENTO",
            "DESCARGAR_DOCUMENTO",
            "CREAR_CATEGORIA",
            "EDITAR_CATEGORIA",
            "ELIMINAR_CATEGORIA",
            "AGREGAR_TIPO",
            "EDITAR_TIPO",
            "ELIMINAR_TIPO",
            "AGREGAR_VERSION",
        ]

        self.combo_accion = ttk.Combobox(
            filtro_frame,
            values=acciones_posibles,
            width=25,
            state="readonly"
        )
        self.combo_accion.grid(row=0, column=3, padx=5, pady=2)
        self.combo_accion.set("")  # valor vacío por defecto

        btn_filtrar = tk.Button(
            filtro_frame,
            text="Aplicar filtros",
            command=self.cargar_eventos,
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            font=FUENTE_BTN,
            relief="flat",
            activebackground=COLOR_HEADER,
            activeforeground=COLOR_TEXTO_BTN,
            padx=10,
            pady=3
        )
        btn_filtrar.grid(row=0, column=4, padx=5, pady=2)

        # ----- Tabla (Treeview) -----
        tabla_frame = tk.Frame(contenedor, bg=COLOR_FONDO)
        tabla_frame.pack(fill="both", expand=True, pady=(5, 0))

        columnas = ("fecha", "usuario", "rol", "accion", "documento")
        self.tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            style="Audit.Treeview"
        )

        self.tree.heading("fecha", text="Fecha / Hora")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("accion", text="Acción")
        self.tree.heading("documento", text="Documento")

        self.tree.column("fecha", width=160)
        self.tree.column("usuario", width=120)
        self.tree.column("rol", width=120)
        self.tree.column("accion", width=180)
        self.tree.column("documento", width=260)

        scrollbar = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=5)
        scrollbar.pack(side="right", fill="y", padx=(5, 0), pady=5)

    def cargar_eventos(self):
        """
        Carga los eventos desde MongoDB y los muestra en la tabla,
        aplicando los filtros de usuario y acción.
        """
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Construir filtro
        filtro = {}
        usuario = self.entry_usuario.get().strip()
        accion = self.combo_accion.get().strip()

        if usuario:
            filtro["usuario"] = usuario
        if accion:
            filtro["accion"] = accion

        # Obtener eventos desde el servicio
        eventos = self.auditoria_service.obtener_eventos(filtro)

        # Insertar filas
        for ev in eventos:
            fecha_dt = ev.get("fecha_hora")
            if fecha_dt:
                fecha_str = fecha_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                fecha_str = "-"

            self.tree.insert(
                "",
                "end",
                values=(
                    fecha_str,
                    ev.get("usuario", "-"),
                    ev.get("rol", "-"),
                    ev.get("accion", "-"),
                    ev.get("documento_nombre", "-")
                )
            )


# Permite probar esta ventana ejecutando SOLO este archivo:
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # ocultar la ventana raíz
    VentanaAuditoria(root)
    root.mainloop()
