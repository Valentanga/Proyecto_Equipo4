# modules/versiones_comentarios.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
from bson.objectid import ObjectId, InvalidId
from datetime import datetime

# --- ESTILOS ---
COLOR_FONDO = "#F4F6F7"       # Gris muy claro
COLOR_HEADER = "#2C3E50"      # Azul Marino Oscuro
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"         # Azul brillante
COLOR_TEXTO_BTN = "white"
COLOR_LOGOUT = "#E74C3C"      # Rojo suave para salir

FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_NORMAL = ("Segoe UI", 11)
FUENTE_BTN = ("Segoe UI", 10, "bold")


class VersionesComentariosGUI(tk.Frame):
    """
    GUI simplificada:
    - SOLO permite listar y agregar versiones de un documento.
    - NO usa repositorios (evita el error de utcnow en otros archivos).
    """

    def __init__(self, master, db, usuario):
        super().__init__(master, bg=COLOR_FONDO)

        self.db = db
        self.usuario = usuario or {}

        self.documento_id = tk.StringVar()

        # master aquí es el Toplevel; su master es el root (menú)
        self.menu_root = master.master if isinstance(master, tk.Toplevel) else master

        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)

        # --------- HEADER (opcional simple) ----------
        header = tk.Frame(self, bg=COLOR_HEADER, pady=10)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="Versiones de Documento",
            font=FUENTE_TITULO,
            bg=COLOR_HEADER,
            fg=COLOR_TEXTO_HEADER
        ).pack(side="left", padx=15)

        # --------- FILA: Documento ID + cargar ----------
        tk.Label(self, text="Documento ID", font=FUENTE_NORMAL, bg=COLOR_FONDO)\
            .grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(5, 2))

        tk.Entry(self, textvariable=self.documento_id, font=FUENTE_NORMAL, bg="white")\
            .grid(row=1, column=1, sticky="ew", pady=(5, 2))

        tk.Button(
            self, text="Cargar versiones", font=FUENTE_BTN,
            bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, relief="flat", cursor="hand2",
            command=self.refrescar
        ).grid(row=1, column=2, padx=5, pady=(5, 2))

        # --------- ESTILOS TREEVIEW ----------
        style = ttk.Style()
        style.configure("Treeview", font=FUENTE_NORMAL, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=FUENTE_BTN,
                        background=COLOR_HEADER, foreground=COLOR_TEXTO_HEADER)

        # --------- TABLA VERSIONES ----------
        self.tree = ttk.Treeview(self, columns=("numero", "ruta", "fecha"), show="headings")
        self.tree.heading("numero", text="Versión")
        self.tree.heading("ruta", text="Ruta")
        self.tree.heading("fecha", text="Fecha")

        self.tree.column("numero", width=80, anchor="center")
        self.tree.column("ruta", width=500, anchor="w")
        self.tree.column("fecha", width=180, anchor="w")

        self.tree.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=6)
        self.rowconfigure(2, weight=1)

        # --------- BOTÓN AGREGAR VERSIÓN ----------
        tk.Button(
            self, text="Agregar versión", font=FUENTE_BTN,
            bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, relief="flat", cursor="hand2",
            command=self.agregar_version
        ).grid(row=3, column=0, pady=10, sticky="w")

        # --------- BOTÓN REGRESAR ----------
        tk.Button(
            self,
            text="← Regresar al menú principal",
            font=FUENTE_BTN,
            bg=COLOR_LOGOUT,
            fg=COLOR_TEXTO_BTN,
            relief="flat",
            cursor="hand2",
            command=self.volver_menu
        ).grid(row=4, column=0, columnspan=3, pady=10)

    # ---------------- LÓGICA ----------------

    def _validar_doc_id(self):
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

    def refrescar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        doc_oid = self._validar_doc_id()
        if not doc_oid:
            return

        try:
            versiones = (
                self.db["versiones"]
                .find({"documento_id": doc_oid})
                .sort("numero", 1)
            )

            for v in versiones:
                fecha = v.get("createdAt", "")
                if isinstance(fecha, datetime):
                    fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")

                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(v.get("_id")),
                    values=(
                        v.get("numero", ""),
                        v.get("ruta", ""),
                        fecha
                    )
                )

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar versiones:\n{e}")

    def agregar_version(self):
        doc_oid = self._validar_doc_id()
        if not doc_oid:
            return

        ruta = filedialog.askopenfilename()
        if not ruta:
            return

        try:
            # Calcular hash
            with open(ruta, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()

            # Calcular número de versión
            existentes = self.db["versiones"].count_documents({"documento_id": doc_oid})
            numero = existentes + 1

            doc_version = {
                "documento_id": doc_oid,
                "numero": numero,
                "ruta": ruta,
                "hash": digest,
                "autor": self.usuario.get("nombre", self.usuario.get("username", "")),
                "createdAt": datetime.utcnow(),
            }

            self.db["versiones"].insert_one(doc_version)

            messagebox.showinfo("Éxito", f"Versión {numero} agregada correctamente.")
            self.refrescar()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la versión:\n{e}")

    def volver_menu(self):
        """Cerrar esta ventana y volver a mostrar el menú principal."""
        if self.menu_root is not None:
            try:
                self.menu_root.deiconify()
                # asegurar menú maximizado
                try:
                    self.menu_root.state("zoomed")
                except tk.TclError:
                    try:
                        self.menu_root.attributes("-zoomed", True)
                    except tk.TclError:
                        pass
            except Exception:
                pass

        self.master.destroy()


def abrir_modulo(master, db, usuario):
    """
    Crea una ventana Toplevel con la GUI de Versiones.
    - Oculta el menú principal mientras está abierta.
    - Abre esta ventana en pantalla completa.
    """
    try:
        master.withdraw()
    except Exception:
        pass

    ventana = tk.Toplevel(master)
    ventana.title("Versiones")
    ventana.configure(bg=COLOR_FONDO)

    # Pantalla completa / maximizada
    try:
        ventana.state("zoomed")
    except tk.TclError:
        try:
            ventana.attributes("-zoomed", True)
        except tk.TclError:
            pass

    gui = VersionesComentariosGUI(ventana, db, usuario)
    gui.pack(fill="both", expand=True)

    # Si cierran con la X, que haga lo mismo que el botón regresar
    ventana.protocol("WM_DELETE_WINDOW", gui.volver_menu)

    return ventana
