# modules/auditoria_gui.py

import tkinter as tk
from tkinter import ttk
from models.auditoria_service import AuditoriaService

# -------- ESTILOS COMPARTIDOS --------
COLOR_FONDO = "#F4F6F7"       # Gris muy claro (casi blanco)
COLOR_HEADER = "#2C3E50"      # Azul marino oscuro (profesional)
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"         # Azul brillante para botones
COLOR_TEXTO_BTN = "white"
COLOR_LOGOUT = "#E74C3C"      # Rojo suave para 'regresar / salir'
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_NORMAL = ("Segoe UI", 11)
FUENTE_BTN = ("Segoe UI", 10, "bold")


class VentanaAuditoria(tk.Toplevel):
    """
    Ventana de Tkinter para consultar la auditoría de accesos.
    Solo la debería abrir el Administrador.

    - Se abre en pantalla completa (maximizada).
    - Oculta la ventana anterior (menú) mientras está abierta.
    - Botón "Regresar al menú principal" que cierra esta ventana
      y vuelve a mostrar el menú.
    """

    def __init__(self, master=None, auditoria_service=None):
        super().__init__(master)
        self.master = master

        # Ocultar la ventana anterior (menú) mientras está abierta la auditoría
        if self.master is not None:
            try:
                self.master.withdraw()
            except Exception:
                pass

        self.title("Auditoría de accesos")
        self.configure(bg=COLOR_FONDO)

        # Pantalla completa / maximizada (Windows)
        try:
            self.state("zoomed")
        except tk.TclError:
            # Fallback por si en algún sistema no existe 'zoomed'
            try:
                self.attributes("-zoomed", True)
            except tk.TclError:
                pass

        # Servicio de auditoría
        self.auditoria_service = auditoria_service or AuditoriaService()

        self._crear_widgets()
        self.cargar_eventos()

        # Si cierran con la X de la ventana, que haga lo mismo que el botón "Regresar"
        self.protocol("WM_DELETE_WINDOW", self.regresar_menu)

    # -------------------------------------------------
    # GUI
    # -------------------------------------------------
    def _crear_widgets(self):
        # ----- HEADER -----
        header = tk.Frame(self, bg=COLOR_HEADER, pady=10)
        header.pack(fill="x")

        lbl_titulo = tk.Label(
            header,
            text="Auditoría de accesos",
            bg=COLOR_HEADER,
            fg=COLOR_TEXTO_HEADER,
            font=FUENTE_TITULO
        )
        lbl_titulo.pack(side="left", padx=20)

        btn_volver = tk.Button(
            header,
            text="← Regresar al menú principal",
            bg=COLOR_LOGOUT,
            fg=COLOR_TEXTO_BTN,
            font=FUENTE_BTN,
            relief="flat",
            cursor="hand2",
            command=self.regresar_menu,
        )
        btn_volver.pack(side="right", padx=20)

        # ----- FILTROS -----
        filtro_frame = tk.Frame(self, bg=COLOR_FONDO, pady=10)
        filtro_frame.pack(fill="x", padx=20)

        tk.Label(
            filtro_frame,
            text="Usuario:",
            bg=COLOR_FONDO,
            font=FUENTE_NORMAL,
        ).grid(row=0, column=0, sticky="w")

        self.entry_usuario = tk.Entry(filtro_frame, width=25, font=FUENTE_NORMAL)
        self.entry_usuario.grid(row=0, column=1, padx=(5, 15))

        tk.Label(
            filtro_frame,
            text="Acción:",
            bg=COLOR_FONDO,
            font=FUENTE_NORMAL,
        ).grid(row=0, column=2, sticky="w")

        # Lista de acciones disponibles en la auditoría
        acciones = [
            "",
            "SUBIR_DOCUMENTO",     
            "VER_DOCUMENTO",
            "DESCARGAR_DOCUMENTO",
            "CREAR_CATEGORIA",
            "EDITAR_CATEGORIA",
            "ELIMINAR_CATEGORIA",
            "AGREGAR_TIPO",
            "EDITAR_TIPO",
            "ELIMINAR_TIPO",
            "AGREGAR_VERSION",
            "LOGIN",
            "LOGOUT",
        ]

        self.combo_accion = ttk.Combobox(
            filtro_frame,
            values=acciones,
            state="readonly",
            width=28,
        )
        self.combo_accion.grid(row=0, column=3, padx=(5, 15))
        self.combo_accion.set("")

        btn_filtrar = tk.Button(
            filtro_frame,
            text="Aplicar filtros",
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            font=FUENTE_BTN,
            relief="flat",
            cursor="hand2",
            command=self.cargar_eventos,
        )
        btn_filtrar.grid(row=0, column=4, padx=5)

        # ----- TABLA -----
        tabla_frame = tk.Frame(self, bg=COLOR_FONDO)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columnas = ("fecha", "usuario", "rol", "accion", "documento")
        self.tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings")

        self.tree.heading("fecha", text="Fecha / Hora")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("accion", text="Acción")
        self.tree.heading("documento", text="Documento")

        self.tree.column("fecha", width=160, anchor="w")
        self.tree.column("usuario", width=120, anchor="w")
        self.tree.column("rol", width=120, anchor="w")
        self.tree.column("accion", width=180, anchor="w")
        self.tree.column("documento", width=320, anchor="w")

        vsb = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    # -------------------------------------------------
    # LÓGICA
    # -------------------------------------------------
    def cargar_eventos(self):
        """Carga los eventos desde MongoDB y los muestra en la tabla usando los filtros."""
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtro = {}
        usuario = self.entry_usuario.get().strip()
        accion = self.combo_accion.get().strip()

        if usuario:
            filtro["usuario"] = usuario
        if accion:
            filtro["accion"] = accion

        eventos = self.auditoria_service.obtener_eventos(filtro)

        for ev in eventos:
            fecha_dt = ev.get("fecha_hora")
            if fecha_dt:
                try:
                    fecha_str = fecha_dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    fecha_str = str(fecha_dt)
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
                    ev.get("documento_nombre", "-"),
                ),
            )

    def regresar_menu(self):
        """Cerrar esta ventana y volver a mostrar la ventana principal (menú)."""
        if self.master is not None:
            try:
                # Volver a mostrar la ventana principal
                self.master.deiconify()

                # 👇 Y asegurarnos de que se vea en pantalla completa
                try:
                    self.master.state("zoomed")
                except tk.TclError:
                    try:
                        self.master.attributes("-zoomed", True)
                    except tk.TclError:
                        pass
            except Exception:
                pass
        self.destroy()


# Para probar esta ventana de manera aislada:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba Auditoría")
    app = VentanaAuditoria(root)
    root.mainloop()
