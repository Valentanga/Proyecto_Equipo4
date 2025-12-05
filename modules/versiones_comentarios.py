# modules/versiones_comentarios.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
from bson.objectid import ObjectId, InvalidId
from datetime import datetime

from repositories.VersionesRepo import VersionesRepo
from repositories.ComentariosRepo import ComentariosRepo
from repositories.AuditoriaRepo import AuditoriaRepo


# --- ESTILOS ---
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
    """
    GUI de Versiones y Comentarios dentro de un Toplevel.

    Objetivo principal de esta versión:
    - Que SIEMPRE liste y agregue versiones aunque exista variación
      en el esquema de Mongo entre compañeros (campos/tipos).
    - Que los comentarios también aparezcan aunque el campo cambie.
    """

    def __init__(self, master, db, usuario):
        super().__init__(master, bg=COLOR_FONDO)

        self.db = db
        self.usuario = usuario or {}

        # Repos (se intentan usar primero)
        self.vers_repo = VersionesRepo(db)
        self.comm_repo = ComentariosRepo(db)
        self.audit = AuditoriaRepo(db)

        self.documento_id = tk.StringVar()
        self.comentario = tk.StringVar()
        self.version_sel = None

        # master aquí es el Toplevel; su master es el root (menú)
        self.menu_root = master.master if isinstance(master, tk.Toplevel) else master

        self._build()

    # ---------------- UI ----------------

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)  # tabla
        self.grid_rowconfigure(4, weight=1)  # comentarios

        # ---- FILA 0: Documento ID + botón cargar ----
        tk.Label(
            self, text="Documento ID", font=FUENTE_NORMAL, bg=COLOR_FONDO
        ).grid(row=0, column=0, sticky="w", padx=(10, 6), pady=(8, 4))

        tk.Entry(
            self, textvariable=self.documento_id, font=FUENTE_NORMAL, bg="white"
        ).grid(row=0, column=1, sticky="ew", pady=(8, 4))

        tk.Button(
            self,
            text="Cargar versiones",
            font=FUENTE_BTN,
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.refrescar
        ).grid(row=0, column=2, padx=(6, 10), pady=(8, 4), sticky="e")

        # ---- Estilos del Treeview ----
        style = ttk.Style()
        style.configure("Treeview", font=FUENTE_NORMAL, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=FUENTE_BTN, background=COLOR_HEADER, foreground=COLOR_TEXTO_HEADER)

        # ---- FILA 1: Tabla de versiones ----
        self.tree = ttk.Treeview(
            self, columns=("numero", "ruta", "fecha"), show="headings", height=8
        )
        self.tree.heading("numero", text="Versión")
        self.tree.heading("ruta", text="Ruta")
        self.tree.heading("fecha", text="Fecha")

        self.tree.column("numero", width=80, anchor="w")
        self.tree.column("ruta", width=520, anchor="w")
        self.tree.column("fecha", width=180, anchor="w")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 8))

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=3, sticky="ns", pady=(0, 8))

        # ---- FILA 2: Botón agregar versión ----
        tk.Button(
            self,
            text="Agregar versión",
            font=FUENTE_BTN,
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.agregar_version
        ).grid(row=2, column=0, padx=10, pady=(0, 8), sticky="w")

        # ---- FILA 3: Comentario + botón ----
        tk.Label(
            self, text="Comentario", font=FUENTE_NORMAL, bg=COLOR_FONDO
        ).grid(row=3, column=0, sticky="w", padx=(10, 6))

        tk.Entry(
            self, textvariable=self.comentario, font=FUENTE_NORMAL, bg="white"
        ).grid(row=3, column=1, sticky="ew")

        tk.Button(
            self,
            text="Agregar comentario",
            font=FUENTE_BTN,
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.agregar_comentario
        ).grid(row=3, column=2, padx=(6, 10), sticky="e")

        # ---- FILA 4: Lista de comentarios ----
        self.list_comm = tk.Listbox(self, font=FUENTE_NORMAL, bg="white")
        self.list_comm.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=(6, 10))

        # ---- FILA 5: Botón regresar ----
        tk.Button(
            self,
            text="Regresar al menú principal",
            font=FUENTE_BTN,
            bg=COLOR_LOGOUT,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.volver_menu
        ).grid(row=5, column=0, columnspan=3, sticky="ew", padx=120, pady=(0, 12))

    # ---------------- Helpers robustos ----------------

    def _build_doc_or_filter(self, doc_oid, doc_id_str):
        # Campos comunes que pueden usar distintos compañeros
        posibles = [
            {"documento_id": doc_oid},
            {"documento_id": doc_id_str},
            {"documento": doc_oid},
            {"documento": doc_id_str},
            {"documentoId": doc_oid},
            {"documentoId": doc_id_str},
            {"doc_id": doc_oid},
            {"doc_id": doc_id_str},
        ]
        return {"$or": posibles}

    def _build_version_or_filter(self, version_id_str):
        filtros = [{"version_id": version_id_str},
                   {"versionId": version_id_str},
                   {"version": version_id_str}]

        # Si el id del tree es un ObjectId válido, añadimos esas variantes
        try:
            vid_oid = ObjectId(version_id_str)
            filtros.extend([
                {"version_id": vid_oid},
                {"versionId": vid_oid},
                {"version": vid_oid},
            ])
        except Exception:
            pass

        return {"$or": filtros}

    def _listar_versiones_robusto(self, doc_oid, doc_id_str):
        # 1) intento repo
        try:
            versiones = self.vers_repo.listar_por_documento(doc_oid) or []
        except Exception:
            versiones = []

        # 2) si repo no trajo nada, buscamos directo con varios campos
        if not versiones:
            try:
                q = self._build_doc_or_filter(doc_oid, doc_id_str)
                versiones = list(self.db["versiones"].find(q).sort("numero", 1))
            except Exception:
                versiones = []

        return versiones

    def _listar_comentarios_robusto(self, version_id_str):
        # 1) intento repo
        try:
            comentarios = self.comm_repo.listar_por_version(version_id_str) or []
        except Exception:
            comentarios = []

        # 2) si repo no trajo nada, buscamos directo
        if not comentarios:
            try:
                q = self._build_version_or_filter(version_id_str)
                comentarios = list(self.db["comentarios"].find(q).sort("createdAt", 1))
            except Exception:
                comentarios = []

        return comentarios

    def _obtener_numero_siguiente(self, doc_oid, doc_id_str):
        versiones = self._listar_versiones_robusto(doc_oid, doc_id_str)
        max_num = 0
        for v in versiones:
            try:
                n = int(v.get("numero", 0))
                if n > max_num:
                    max_num = n
            except Exception:
                pass
        return max_num + 1

    # ---------------- LÓGICA ----------------

    def refrescar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        doc_id_str = self.documento_id.get().strip()
        if not doc_id_str:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return

        try:
            doc_oid = ObjectId(doc_id_str)
        except InvalidId:
            messagebox.showerror(
                "Error",
                "El Documento ID no es válido. Debe ser un ObjectId de 24 caracteres hexadecimales."
            )
            return

        versiones = self._listar_versiones_robusto(doc_oid, doc_id_str)

        for v in versiones:
            created = v.get("createdAt", "")
            if isinstance(created, datetime):
                created = created.strftime("%Y-%m-%d %H:%M:%S")

            self.tree.insert(
                "",
                tk.END,
                iid=str(v.get("_id", "")),
                values=(v.get("numero", ""), v.get("ruta", ""), created)
            )

        self.list_comm.delete(0, tk.END)

    def on_select(self, _):
        sel = self.tree.selection()
        if sel:
            self.version_sel = sel[0]
            self.refrescar_comentarios()

    def refrescar_comentarios(self):
        self.list_comm.delete(0, tk.END)
        if not self.version_sel:
            return

        comentarios = self._listar_comentarios_robusto(self.version_sel)
        for c in comentarios:
            autor = c.get("autor", "")
            texto = c.get("texto", "")
            self.list_comm.insert(tk.END, f"{autor}: {texto}")

    def agregar_version(self):
        doc_id_str = self.documento_id.get().strip()
        if not doc_id_str:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return

        try:
            doc_oid = ObjectId(doc_id_str)
        except InvalidId:
            messagebox.showerror("Error", "Documento ID inválido.")
            return

        ruta = filedialog.askopenfilename()
        if not ruta:
            return

        try:
            with open(ruta, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()

            numero = self._obtener_numero_siguiente(doc_oid, doc_id_str)
            autor = self.usuario.get("nombre", "") or self.usuario.get("username", "")

            vid = None

            # 1) Intento normal repo
            try:
                vid = self.vers_repo.crear(doc_id_str, numero, ruta, digest, autor)

            except Exception as e:
                # 2) Fallback directo: insert robusto con varios campos compatibles
                version_doc = {
                    # Guardamos en múltiples llaves típicas para compatibilidad
                    "documento_id": doc_oid,
                    "documento": doc_oid,
                    "documentoId": doc_id_str,

                    "numero": numero,
                    "ruta": ruta,
                    "hash": digest,
                    "autor": autor,
                    "createdAt": datetime.utcnow()
                }
                res = self.db["versiones"].insert_one(version_doc)
                vid = res.inserted_id

            # Auditoría (no rompe si falla)
            try:
                self.audit.registrar(
                    self.usuario.get("rol", ""),
                    doc_id_str,
                    "AGREGAR_VERSION",
                    {"versionId": str(vid)}
                )
            except Exception:
                pass

            # IMPORTANTÍSIMO: recargar lista al instante
            self.refrescar()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def agregar_comentario(self):
        if not self.version_sel:
            messagebox.showerror("Error", "Selecciona una versión")
            return

        texto = self.comentario.get().strip()
        if not texto:
            messagebox.showerror("Error", "El comentario no puede estar vacío")
            return

        try:
            autor = self.usuario.get("nombre", "") or self.usuario.get("username", "")

            cid = None

            # 1) Intento repo
            try:
                cid = self.comm_repo.crear(self.version_sel, texto, autor)

            except Exception:
                # 2) Fallback directo, guardando llaves compatibles
                doc = {
                    "version_id": self.version_sel,
                    "versionId": self.version_sel,
                    "version": self.version_sel,

                    "texto": texto,
                    "autor": autor,
                    "createdAt": datetime.utcnow()
                }
                res = self.db["comentarios"].insert_one(doc)
                cid = res.inserted_id

            # Auditoría (no romper)
            try:
                self.audit.registrar(
                    self.usuario.get("rol", ""),
                    self.documento_id.get().strip(),
                    "AGREGAR_COMENTARIO",
                    {"comentarioId": str(cid)}
                )
            except Exception:
                pass

            self.comentario.set("")
            self.refrescar_comentarios()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def volver_menu(self):
        """Cerrar esta ventana y volver a mostrar el menú principal."""
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

        try:
            self.master.destroy()
        except Exception:
            pass


def abrir_modulo(master, *args):
    """
    Compatible con:
      1) abrir_modulo(master, usuario)
      2) abrir_modulo(master, db, usuario)

    - Oculta el menú principal mientras está abierta.
    - Abre esta ventana en pantalla completa.
    """
    db = None
    usuario = None

    if len(args) == 1:
        usuario = args[0]

    elif len(args) >= 2:
        a0, a1 = args[0], args[1]

        # Heurística: usuario suele ser dict
        if isinstance(a0, dict) and not isinstance(a1, dict):
            usuario = a0
            db = a1
        else:
            db = a0
            usuario = a1

    else:
        raise TypeError("abrir_modulo requiere al menos el usuario.")

    # Si no pasan db, lo obtenemos aquí
    if db is None:
        from db.connection import get_db
        db = get_db()

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

    ventana.protocol("WM_DELETE_WINDOW", gui.volver_menu)

    return ventana
