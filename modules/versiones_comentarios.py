import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from repositories.VersionesRepo import VersionesRepo
from repositories.ComentariosRepo import ComentariosRepo
from repositories.AuditoriaRepo import AuditoriaRepo
import hashlib
from bson.objectid import ObjectId, InvalidId
from datetime import datetime

# --- ESTILOS ---
COLOR_FONDO = "#F4F6F7"       # Gris muy claro (Casi blanco)
COLOR_HEADER = "#2C3E50"      # Azul Marino Oscuro (Profesional)
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"         # Azul brillante para botones
COLOR_TEXTO_BTN = "white"
COLOR_LOGOUT = "#E74C3C"      # Rojo suave para salir

FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_NORMAL = ("Segoe UI", 11)
FUENTE_BTN = ("Segoe UI", 10, "bold")


class VersionesComentariosGUI(tk.Frame):
    def __init__(self, master, db, usuario):
        super().__init__(master, bg=COLOR_FONDO)
        self.vers_repo = VersionesRepo(db)
        self.comm_repo = ComentariosRepo(db)
        self.audit = AuditoriaRepo(db)
        self.usuario = usuario

        self.documento_id = tk.StringVar()
        self.comentario = tk.StringVar()
        self.version_sel = None

        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)

        
        tk.Label(self, text="Documento ID", font=FUENTE_NORMAL, bg=COLOR_FONDO).grid(row=0, column=0, sticky="w")
        tk.Entry(self, textvariable=self.documento_id, font=FUENTE_NORMAL, bg="white").grid(row=0, column=1, sticky="ew")

        tk.Button(self, text="Cargar versiones", font=FUENTE_BTN,
                  bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, command=self.refrescar).grid(row=0, column=2)

     
        style = ttk.Style()
        style.configure("Treeview", font=FUENTE_NORMAL, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=FUENTE_BTN, background=COLOR_HEADER, foreground=COLOR_TEXTO_HEADER)

        self.tree = ttk.Treeview(self, columns=("numero", "ruta", "fecha"), show="headings")
        self.tree.heading("numero", text="Versión")
        self.tree.heading("ruta", text="Ruta")
        self.tree.heading("fecha", text="Fecha")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.rowconfigure(1, weight=1)

        
        tk.Button(self, text="Agregar versión", font=FUENTE_BTN,
                  bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, command=self.agregar_version).grid(row=2, column=0, pady=6)

       
        tk.Label(self, text="Comentario", font=FUENTE_NORMAL, bg=COLOR_FONDO).grid(row=3, column=0, sticky="w")
        tk.Entry(self, textvariable=self.comentario, width=40, font=FUENTE_NORMAL, bg="white").grid(row=3, column=1, sticky="ew")
        tk.Button(self, text="Agregar comentario", font=FUENTE_BTN,
                  bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, command=self.agregar_comentario).grid(row=3, column=2)

        self.list_comm = tk.Listbox(self, width=60, font=FUENTE_NORMAL, bg="white")
        self.list_comm.grid(row=4, column=0, columnspan=3, sticky="nsew")

        tk.Button(self, text="Regresar al menú principal", font=FUENTE_BTN,
                  bg=COLOR_LOGOUT, fg=COLOR_TEXTO_BTN, command=self.volver_menu).grid(row=5, column=0, columnspan=3, pady=10)

    def refrescar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        doc_id = self.documento_id.get().strip()
        if not doc_id:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return

        try:
            doc_oid = ObjectId(doc_id)
        except InvalidId:
            messagebox.showerror("Error", "El Documento ID no es válido. Debe ser un ObjectId de 24 caracteres hexadecimales.")
            return

        versiones = self.vers_repo.listar_por_documento(doc_oid)
        for v in versiones:
            self.tree.insert("", tk.END, iid=str(v["_id"]),
                             values=(v["numero"], v["ruta"], v.get("createdAt", "")))

        self.list_comm.delete(0, tk.END)

    def on_select(self, _):
        sel = self.tree.selection()
        if sel:
            self.version_sel = sel[0]
            self.refrescar_comentarios()

    def refrescar_comentarios(self):
        self.list_comm.delete(0, tk.END)
        for c in self.comm_repo.listar_por_version(self.version_sel):
            linea = f'{c["autor"]}: {c["texto"]}'
            self.list_comm.insert(tk.END, linea)

    def agregar_version(self):
        doc_id = self.documento_id.get().strip()
        if not doc_id:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return
        ruta = filedialog.askopenfilename()
        if not ruta:
            return
        try:
            with open(ruta, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            numero = len(self.vers_repo.listar_por_documento(ObjectId(doc_id))) + 1
            vid = self.vers_repo.crear(doc_id, numero, ruta, digest, self.usuario["nombre"])
            self.audit.registrar(self.usuario["rol"], doc_id, "AGREGAR_VERSION", {"versionId": str(vid)})
            self.refrescar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def agregar_comentario(self):
        if not self.version_sel:
            messagebox.showerror("Error", "Selecciona una versión")
            return
        if not self.comentario.get().strip():
            messagebox.showerror("Error", "El comentario no puede estar vacío")
            return
        try:
            cid = self.comm_repo.crear(self.version_sel, self.comentario.get(), self.usuario["nombre"])
            self.audit.registrar(self.usuario["rol"], self.documento_id.get().strip(),
                                 "AGREGAR_COMENTARIO", {"comentarioId": str(cid)})
            self.refrescar_comentarios()
            self.comentario.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def volver_menu(self):
        self.master.destroy()


def abrir_modulo(master, db, usuario):
    """Crea una ventana Toplevel con la GUI de Versiones y Comentarios."""
    ventana = tk.Toplevel(master)
    ventana.title("Versiones y Comentarios")
    ventana.geometry("700x500")
    ventana.configure(bg=COLOR_FONDO)

    gui = VersionesComentariosGUI(ventana, db, usuario)
    gui.pack(fill="both", expand=True)

    return ventana
