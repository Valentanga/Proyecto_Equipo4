import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib

from bson.objectid import ObjectId, InvalidId
from datetime import datetime

from models.auditoria_service import AuditoriaService


# --- ESTILOS (alineados a tu proyecto) ---
COLOR_FONDO = "#F4F6F7"
COLOR_HEADER = "#2C3E50"
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"
COLOR_TEXTO_BTN = "white"
COLOR_LOGOUT = "#E74C3C"

FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_NORMAL = ("Segoe UI", 11)
FUENTE_BTN = ("Segoe UI", 10, "bold")


class VersionesComentariosGUI(tk.Frame):
    def __init__(self, master, db, usuario):
        super().__init__(master, bg=COLOR_FONDO)

        self.db = db
        self.usuario = usuario or {}

        # Colecciones (sin repos)
        self.col_versiones = self.db["versiones"]
        self.col_comentarios = self.db["comentarios_versiones"]
        self.col_documentos = self.db["documentos"]

        # Auditoría del proyecto (tu servicio real)
        self.aud = AuditoriaService()

        self.documento_id = tk.StringVar()
        self.comentario = tk.StringVar()
        self.version_sel = None

        # master aquí es el Toplevel; su master es el root (menú)
        self.menu_root = master.master if isinstance(master, tk.Toplevel) else master

        self._build()

    # ---------------- UI ----------------
    def _build(self):
        # ---------- HEADER ----------
        header = tk.Frame(self, bg=COLOR_HEADER, pady=10)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Versiones y Comentarios",
            bg=COLOR_HEADER,
            fg=COLOR_TEXTO_HEADER,
            font=FUENTE_TITULO
        ).pack(side="left", padx=20)

        tk.Button(
            header,
            text="← Regresar al menú principal",
            bg=COLOR_LOGOUT,
            fg=COLOR_TEXTO_BTN,
            font=FUENTE_BTN,
            relief="flat",
            cursor="hand2",
            command=self.volver_menu
        ).pack(side="right", padx=20)

        # ---------- CONTENIDO ----------
        cont = tk.Frame(self, bg=COLOR_FONDO)
        cont.pack(fill="both", expand=True, padx=20, pady=15)

        cont.columnconfigure(1, weight=1)
        cont.rowconfigure(2, weight=1)
        cont.rowconfigure(5, weight=1)

        # Fila 0: Documento ID + botón cargar
        tk.Label(cont, text="Documento ID", font=FUENTE_NORMAL, bg=COLOR_FONDO)\
            .grid(row=0, column=0, sticky="w")

        tk.Entry(cont, textvariable=self.documento_id, font=FUENTE_NORMAL, bg="white")\
            .grid(row=0, column=1, sticky="ew", padx=(8, 8))

        tk.Button(
            cont,
            text="Cargar versiones",
            font=FUENTE_BTN,
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.refrescar_versiones
        ).grid(row=0, column=2, sticky="e")

        # Separador ligero
        ttk.Separator(cont, orient="horizontal").grid(row=1, column=0, columnspan=3, sticky="ew", pady=8)

        # Fila 2: Tabla de versiones
        style = ttk.Style()
        style.configure("Treeview", font=FUENTE_NORMAL, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=FUENTE_BTN)

        self.tree = ttk.Treeview(cont, columns=("numero", "ruta", "fecha"), show="headings", height=8)
        self.tree.heading("numero", text="Versión")
        self.tree.heading("ruta", text="Ruta")
        self.tree.heading("fecha", text="Fecha")
        self.tree.column("numero", width=80, anchor="center")
        self.tree.column("ruta", width=520, anchor="w")
        self.tree.column("fecha", width=180, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        vsb = ttk.Scrollbar(cont, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 8))
        vsb.grid(row=2, column=2, sticky="ns", pady=(0, 8))

        # Fila 3: botón agregar versión
        tk.Button(
            cont,
            text="Agregar versión",
            font=FUENTE_BTN,
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.agregar_version
        ).grid(row=3, column=0, sticky="w", pady=(0, 10))

        # Separador
        ttk.Separator(cont, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=8)

        # Fila 5: Comentarios (entrada + botón)
        tk.Label(cont, text="Comentario", font=FUENTE_NORMAL, bg=COLOR_FONDO)\
            .grid(row=5, column=0, sticky="nw")

        tk.Entry(cont, textvariable=self.comentario, font=FUENTE_NORMAL, bg="white")\
            .grid(row=5, column=1, sticky="ew", padx=(8, 8))

        tk.Button(
            cont,
            text="Agregar comentario",
            font=FUENTE_BTN,
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.agregar_comentario
        ).grid(row=5, column=2, sticky="e")

        # Fila 6: Lista de comentarios
        self.list_comm = tk.Listbox(cont, font=FUENTE_NORMAL, bg="white", height=8)
        self.list_comm.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(8, 0))

    # ---------------- Helpers ----------------
    def _autor_display(self):
        return (
            self.usuario.get("nombre")
            or self.usuario.get("username")
            or "SinNombre"
        )

    def _parse_doc_oid(self):
        doc_id = self.documento_id.get().strip()
        if not doc_id:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return None

        try:
            return ObjectId(doc_id)
        except InvalidId:
            messagebox.showerror(
                "Error",
                "El Documento ID no es válido. Debe ser un ObjectId de 24 caracteres hexadecimales."
            )
            return None

    def _get_doc_titulo(self, doc_oid):
        try:
            doc = self.col_documentos.find_one({"_id": doc_oid})
            if doc:
                return doc.get("titulo")
        except Exception:
            pass
        return None

    # ---------------- Versiones ----------------
    def refrescar_versiones(self):
        # limpiar tabla
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.list_comm.delete(0, tk.END)
        self.version_sel = None

        doc_oid = self._parse_doc_oid()
        if not doc_oid:
            return

        try:
            versiones = list(
                self.col_versiones.find({"documento_id": doc_oid}).sort("numero", 1)
            )

            for v in versiones:
                fecha = v.get("createdAt", "")
                if isinstance(fecha, datetime):
                    fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")

                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(v["_id"]),
                    values=(
                        v.get("numero", ""),
                        v.get("ruta", ""),
                        fecha
                    )
                )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar versiones:\n{e}")

    def agregar_version(self):
        doc_oid = self._parse_doc_oid()
        if not doc_oid:
            return

        ruta = filedialog.askopenfilename(
            title="Selecciona un archivo para la nueva versión"
        )
        if not ruta:
            return

        try:
            # hash
            with open(ruta, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()

            # calcular siguiente número
            ultima = self.col_versiones.find({"documento_id": doc_oid}).sort("numero", -1).limit(1)
            ultima = list(ultima)
            numero = (ultima[0].get("numero", 0) + 1) if ultima else 1

            data = {
                "documento_id": doc_oid,
                "numero": numero,
                "ruta": ruta,
                "sha256": digest,
                "autor": self._autor_display(),
                "createdAt": datetime.utcnow()
            }

            res = self.col_versiones.insert_one(data)

            # Auditoría
            try:
                self.aud.registrar_evento(
                    usuario=self.usuario.get("username", ""),
                    rol=self.usuario.get("rol", ""),
                    accion="AGREGAR_VERSION",
                    documento_id=str(doc_oid),
                    documento_nombre=self._get_doc_titulo(doc_oid)
                )
            except Exception:
                pass

            # refrescar y seleccionar la nueva
            self.refrescar_versiones()
            try:
                self.tree.selection_set(str(res.inserted_id))
                self.tree.see(str(res.inserted_id))
                self.version_sel = str(res.inserted_id)
                self.refrescar_comentarios()
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar versión:\n{e}")

    # ---------------- Comentarios ----------------
    def on_select(self, _):
        sel = self.tree.selection()
        if sel:
            self.version_sel = sel[0]
            self.refrescar_comentarios()

    def refrescar_comentarios(self):
        self.list_comm.delete(0, tk.END)

        if not self.version_sel:
            return

        doc_oid = self._parse_doc_oid()
        if not doc_oid:
            return

        try:
            vers_oid = ObjectId(self.version_sel)

            comentarios = list(
                self.col_comentarios.find({"version_id": vers_oid}).sort("createdAt", 1)
            )

            for c in comentarios:
                autor = c.get("autor", "")
                texto = c.get("texto", "")
                self.list_comm.insert(tk.END, f"{autor}: {texto}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar comentarios:\n{e}")

    def agregar_comentario(self):
        if not self.version_sel:
            messagebox.showerror("Error", "Selecciona una versión")
            return

        texto = self.comentario.get().strip()
        if not texto:
            messagebox.showerror("Error", "El comentario no puede estar vacío")
            return

        doc_oid = self._parse_doc_oid()
        if not doc_oid:
            return

        try:
            vers_oid = ObjectId(self.version_sel)

            data = {
                "version_id": vers_oid,
                "documento_id": doc_oid,
                "texto": texto,
                "autor": self._autor_display(),
                "createdAt": datetime.utcnow()
            }

            self.col_comentarios.insert_one(data)

            # Auditoría opcional
            try:
                self.aud.registrar_evento(
                    usuario=self.usuario.get("username", ""),
                    rol=self.usuario.get("rol", ""),
                    accion="AGREGAR_COMENTARIO",
                    documento_id=str(doc_oid),
                    documento_nombre=self._get_doc_titulo(doc_oid)
                )
            except Exception:
                pass

            self.comentario.set("")
            self.refrescar_comentarios()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar comentario:\n{e}")

    # ---------------- Volver menú ----------------
    def volver_menu(self):
        """Cerrar ventana de versiones y regresar el menú principal."""
        if self.menu_root is not None:
            try:
                self.menu_root.deiconify()
                try:
                    self.menu_root.state("zoomed")
                except tk.TclError:
                    try:
                        self.menu_root.attributes("-zoomed", True)
                    except tk.TclError:
                        pass
            except Exception:
                pass

        # self.master es el Toplevel
        try:
            self.master.destroy()
        except Exception:
            pass


def abrir_modulo(master, db, usuario):
    """
    Crea una ventana Toplevel con la GUI de Versiones y Comentarios.
    - Oculta el menú principal mientras está abierta.
    - Abre esta ventana en pantalla completa.
    """
    # Ocultar menú
    try:
        master.withdraw()
    except Exception:
        pass

    ventana = tk.Toplevel(master)
    ventana.title("Versiones y Comentarios")
    ventana.configure(bg=COLOR_FONDO)

    # Maximizar
    try:
        ventana.state("zoomed")
    except tk.TclError:
        try:
            ventana.attributes("-zoomed", True)
        except tk.TclError:
            pass

    gui = VersionesComentariosGUI(ventana, db, usuario)
    gui.pack(fill="both", expand=True)

    # Si cierran con X, mismo comportamiento que regresar
    ventana.protocol("WM_DELETE_WINDOW", gui.volver_menu)

    return ventana


# Prueba aislada (opcional)
if __name__ == "__main__":
    from db.connection import get_db

    root = tk.Tk()
    root.title("Menú (Prueba)")
    try:
        root.state("zoomed")
    except tk.TclError:
        pass

    fake_user = {
        "username": "admin1",
        "nombre": "Admin",
        "rol": "Administrador"
    }

    tk.Button(
        root,
        text="Abrir Versiones",
        command=lambda: abrir_modulo(root, get_db(), fake_user)
    ).pack(pady=20)

    root.mainloop()
