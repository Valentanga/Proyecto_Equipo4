# modules/auditoria_gui.py

import tkinter as tk
from tkinter import ttk
from models.auditoria_service import AuditoriaService


class VentanaAuditoria(tk.Toplevel):
    """
    Ventana de Tkinter para consultar la auditoría de accesos.
    Solo la debería abrir el Administrador.
    """

    def __init__(self, master=None, auditoria_service=None):
        super().__init__(master)
        self.title("Auditoría de accesos")
        self.geometry("800x400")

        # Servicio de auditoría (si no te pasan uno, crea uno nuevo)
        self.auditoria_service = auditoria_service or AuditoriaService()

        self._crear_widgets()
        self.cargar_eventos()  # cargar datos al inicio

    def _crear_widgets(self):
        # ----- Frame de filtros -----
        filtro_frame = tk.Frame(self)
        filtro_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filtro_frame, text="Usuario:").grid(row=0, column=0, sticky="w")
        self.entry_usuario = tk.Entry(filtro_frame, width=20)
        self.entry_usuario.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(filtro_frame, text="Acción:").grid(row=0, column=2, sticky="w")
        self.combo_accion = ttk.Combobox(
            filtro_frame,
            values=["", "VER_DOCUMENTO", "DESCARGAR_DOCUMENTO"],
            width=22,
            state="readonly"
        )
        self.combo_accion.grid(row=0, column=3, padx=5, pady=2)
        self.combo_accion.set("")  # valor vacío por defecto

        btn_filtrar = tk.Button(
            filtro_frame,
            text="Aplicar filtros",
            command=self.cargar_eventos
        )
        btn_filtrar.grid(row=0, column=4, padx=5, pady=2)

        # ----- Tabla (Treeview) -----
        columnas = ("fecha", "usuario", "rol", "accion", "documento")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")

        self.tree.heading("fecha", text="Fecha / Hora")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("accion", text="Acción")
        self.tree.heading("documento", text="Documento")

        self.tree.column("fecha", width=160)
        self.tree.column("usuario", width=120)
        self.tree.column("rol", width=120)
        self.tree.column("accion", width=150)
        self.tree.column("documento", width=220)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

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
