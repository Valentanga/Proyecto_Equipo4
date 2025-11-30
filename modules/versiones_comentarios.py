import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from repositories.VersionesRepo import VersionesRepo
from repositories.ComentariosRepo import ComentariosRepo
from repositories.AuditoriaRepo import AuditoriaRepo
import hashlib
from bson.objectid import ObjectId, InvalidId


class VersionesComentariosGUI(tk.Frame):
    def __init__(self, master, db, usuario):
        super().__init__(master)
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

        tk.Label(self, text="Documento ID").grid(row=0, column=0, sticky="w")
        tk.Entry(self, textvariable=self.documento_id).grid(row=0, column=1, sticky="ew")

        tk.Button(self, text="Cargar versiones", command=self.refrescar).grid(row=0, column=2)

        self.tree = ttk.Treeview(self, columns=("numero", "ruta"), show="headings")
        self.tree.heading("numero", text="Versión")
        self.tree.heading("ruta", text="Ruta")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.rowconfigure(1, weight=1)

        tk.Button(self, text="Agregar versión", command=self.agregar_version).grid(row=2, column=0, pady=6)

        tk.Label(self, text="Comentario").grid(row=3, column=0, sticky="w")
        tk.Entry(self, textvariable=self.comentario, width=40).grid(row=3, column=1, sticky="ew")
        tk.Button(self, text="Agregar comentario", command=self.agregar_comentario).grid(row=3, column=2)

        self.list_comm = tk.Listbox(self, width=60)
        self.list_comm.grid(row=4, column=0, columnspan=3, sticky="nsew")

    def refrescar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        doc_id = self.documento_id.get().strip()
        if not doc_id:
            messagebox.showerror("Error", "Ingresa Documento ID")
            return
        versiones = self.vers_repo.listar_por_documento(doc_id)
        for v in versiones:
            self.tree.insert("", tk.END, iid=str(v["_id"]), values=(v["numero"], v["ruta"]))
        self.list_comm.delete(0, tk.END)

        try:
            versiones = self.vers_repo.listar_por_documento(ObjectId(doc_id))
        except InvalidId:
            messagebox.showerror("Error",
                                 "El Documento ID no es válido. ")
            return

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
            numero = len(self.vers_repo.listar_por_documento(doc_id)) + 1
            vid = self.vers_repo.crear(doc_id, numero, ruta, digest, self.usuario["nombre"])
            self.audit.registrar(self.usuario["rol"], doc_id, "AGREGAR_VERSION", {"versionId": str(vid)})
            self.refrescar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def agregar_comentario(self):
        if not self.version_sel:
            messagebox.showerror("Error", "Selecciona una versión")
            return
        try:
            cid = self.comm_repo.crear(self.version_sel, self.comentario.get(), self.usuario["nombre"])
            self.audit.registrar(self.usuario["rol"], self.documento_id.get().strip(), "AGREGAR_COMENTARIO", {"comentarioId": str(cid)})
            self.refrescar_comentarios()
            self.comentario.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def abrir_modulo(master, db, usuario):
        """Crea una ventana Toplevel con la GUI de Versiones y Comentarios."""
        ventana = tk.Toplevel(master)
        ventana.title("Versiones y Comentarios")
        ventana.geometry("600x400")

        gui = VersionesComentariosGUI(ventana, db, usuario)
        gui.pack(fill="both", expand=True)


        return ventana
