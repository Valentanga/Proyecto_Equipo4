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

    Objetivos:
    - UI similar a tu captura (layout limpio).
    - Agregar versiones sin fallar por el bug de datetime en repos.
    - Mantener comentarios si ya los usan.
    - Botón para regresar al menú principal.
    """

    def __init__(self, master, db, usuario):
        super().__init__(master, bg=COLOR_FONDO)

        self.db = db
        self.usuario = usuario or {}

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
        # Configuración de grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)  # tabla
        self.grid_rowconfigure(4, weight=1)  # comentarios

        # ---- FILA 0: Documento ID + botón cargar ----
        tk.Label(
            self, text="Documento ID", font=FUENTE_NORMAL, bg=COLOR_FONDO
        ).grid(row=0, column=0, sticky="w", padx=(10, 6), pady=(8, 4))

        entry_doc = tk.Entry(
            self, textvariable=self.documento_id, font=FUENTE_NORMAL, bg="white"
        )
        entry_doc.grid(row=0, column=1, sticky="ew", pady=(8, 4))

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
        style.configure(
            "Treeview",
            font=FUENTE_NORMAL,
            background="white",
            fieldbackground="white"
        )
        style.configure(
            "Treeview.Heading",
            font=FUENTE_BTN,
            background=COLOR_HEADER,
            foreground=COLOR_TEXTO_HEADER
        )

        # ---- FILA 1: Tabla de versiones ----
        self.tree = ttk.Treeview(
            self, columns=("numero", "ruta", "fecha"), show="headings", height=8
        )
        self.tree.heading("numero", text="Versión")
        self.tree.heading("ruta", text="Ruta")
        self.tree.heading("fecha", text="Fecha")

        self.tree.column("numero", width=80, anchor="w")
        self.tree.column("ruta", width=420, anchor="w")
        self.tree.column("fecha", width=180, anchor="w")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 8))

        # Scroll vertical tabla
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

        entry_com = tk.Entry(
            self, textvariable=self.comentario, font=FUENTE_NORMAL, bg="white"
        )
        entry_com.grid(row=3, column=1, sticky="ew")

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
        self.list_comm = tk.Listbox(
            self, font=FUENTE_NORMAL, bg="white"
        )
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

    # ---------------- LÓGICA ----------------

    def refrescar(self):
        # Limpiar tabla
        for i in self.tree.get_children():
            self.tree.delete(i)

        doc_id = self.documento_id.get().strip()
        if not doc_id:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return

        try:
            doc_oid = ObjectId(doc_id)
        except InvalidId:
            messagebox.showerror(
                "Error",
                "El Documento ID no es válido. Debe ser un ObjectId de 24 caracteres hexadecimales."
            )
            return

        # Cargar versiones
        try:
            versiones = self.vers_repo.listar_por_documento(doc_oid)
        except Exception:
            # Fallback por si algo raro pasa en el repo
            versiones = list(self.db["versiones"].find({"documento_id": doc_oid}).sort("numero", 1))

        for v in versiones:
            created = v.get("createdAt", "")
            if isinstance(created, datetime):
                created = created.strftime("%Y-%m-%d %H:%M:%S")

            self.tree.insert(
                "",
                tk.END,
                iid=str(v.get("_id")),
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

        try:
            comentarios = self.comm_repo.listar_por_version(self.version_sel)
        except Exception:
            # Fallback directo a colección
            try:
                comentarios = list(self.db["comentarios"].find({"version_id": self.version_sel}))
            except Exception:
                comentarios = []

        for c in comentarios:
            autor = c.get("autor", "")
            texto = c.get("texto", "")
            self.list_comm.insert(tk.END, f"{autor}: {texto}")

    def _obtener_numero_siguiente(self, doc_oid):
        # Intenta usar el repo
        try:
            actuales = self.vers_repo.listar_por_documento(doc_oid)
            return len(actuales) + 1
        except Exception:
            # Fallback directo
            return self.db["versiones"].count_documents({"documento_id": doc_oid}) + 1

    def agregar_version(self):
        doc_id = self.documento_id.get().strip()
        if not doc_id:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return

        try:
            doc_oid = ObjectId(doc_id)
        except InvalidId:
            messagebox.showerror("Error", "Documento ID inválido.")
            return

        ruta = filedialog.askopenfilename()
        if not ruta:
            return

        try:
            with open(ruta, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()

            numero = self._obtener_numero_siguiente(doc_oid)

            autor = self.usuario.get("nombre", "") or self.usuario.get("username", "")

            # -------- 1) Intento normal con repo --------
            vid = None
            try:
                vid = self.vers_repo.crear(doc_id, numero, ruta, digest, autor)

            except Exception as e:
                # -------- 2) Fallback por bug típico de datetime --------
                if "utcnow" in str(e):
                    version_doc = {
                        "documento_id": doc_oid,
                        "numero": numero,
                        "ruta": ruta,
                        "hash": digest,
                        "autor": autor,
                        "createdAt": datetime.utcnow()
                    }
                    res = self.db["versiones"].insert_one(version_doc)
                    vid = res.inserted_id
                else:
                    raise

            # Auditoría (si falla, no rompe la demo)
            try:
                self.audit.registrar(
                    self.usuario.get("rol", ""),
                    doc_id,
                    "AGREGAR_VERSION",
                    {"versionId": str(vid)}
                )
            except Exception:
                pass

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

            try:
                cid = self.comm_repo.crear(self.version_sel, texto, autor)
            except Exception:
                # Fallback directo
                doc = {
                    "version_id": self.version_sel,
                    "texto": texto,
                    "autor": autor,
                    "createdAt": datetime.utcnow()
                }
                res = self.db["comentarios"].insert_one(doc)
                cid = res.inserted_id

            try:
                self.audit.registrar(
                    self.usuario.get("rol", ""),
                    self.documento_id.get().strip(),
                    "AGREGAR_COMENTARIO",
                    {"comentarioId": str(cid)}
                )
            except Exception:
                pass

            self.refrescar_comentarios()
            self.comentario.set("")

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

        # Cerramos el Toplevel que contiene este Frame
        try:
            self.master.destroy()
        except Exception:
            pass


def abrir_modulo(master, *args):
    """
    Compatible con:
      1) abrir_modulo(master, usuario)
      2) abrir_modulo(master, db, usuario)
      3) abrir_modulo(master, usuario, db=algo)  (indirecto vía args)

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

    # Si no pasan db, lo obtenemos aquí (sin tocar main)
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

    # Cerrar con X = volver menú
    ventana.protocol("WM_DELETE_WINDOW", gui.volver_menu)

    return ventana
