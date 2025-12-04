# modules/modulo1_Subida.py

# --- IMPORTACIONES ---
import tkinter as tk  # Librería principal
from tkinter import filedialog, messagebox, ttk
import os
from datetime import datetime
from bson.binary import Binary
from bson.objectid import ObjectId
from db.connection import get_db
import threading

# >>> NUEVA IMPORTACIÓN PARA EL CALENDARIO
from tkcalendar import DateEntry 

# >>> AUDITORÍA
from models.auditoria_service import AuditoriaService

# --- CONFIGURACIÓN DE DISEÑO ---
COLOR_FONDO = "#F4F6F7"
COLOR_HEADER = "#2C3E50"
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"
COLOR_TEXTO_BTN = "white"
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_LABEL = ("Segoe UI", 10, "bold")
FUENTE_NORMAL = ("Segoe UI", 10)


class Subida_modulo1(tk.Toplevel):
    
    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.master = parent          # <-- guardamos referencia al menú
        self.usuario = usuario_data
        self.aud = AuditoriaService()

        # Ocultar el menú mientras está abierto el módulo 1
        if self.master is not None:
            try:
                self.master.withdraw()
            except Exception:
                pass

        # Configuración de la ventana
        self.title("Módulo 1: Registro y Consulta de Documentos")
        self.geometry("900x700")  # fallback

        # Pantalla completa / maximizada (como en auditoría)
        try:
            self.state("zoomed")
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)
            except tk.TclError:
                pass

        self.configure(bg=COLOR_FONDO)
        
        self.ruta_archivo = None
        self.categorias_dict = {}
        self.tipos_dict = {}
        self._cargado_inicial = False

        # --- DISEÑO DE LA INTERFAZ ---

        # 1. ENCABEZADO
        header_frame = tk.Frame(self, bg=COLOR_HEADER, pady=15)
        header_frame.pack(fill="x")

        lbl_titulo = tk.Label(
            header_frame,
            text="REGISTRO DE EXPEDIENTE / DOCUMENTO",
            font=FUENTE_TITULO,
            bg=COLOR_HEADER,
            fg=COLOR_TEXTO_HEADER
        )
        lbl_titulo.pack(side="left", padx=20)

        # Botón para regresar al menú principal
        btn_volver = tk.Button(
            header_frame,
            text="← Regresar al menú principal",
            bg="#E74C3C",
            fg=COLOR_TEXTO_BTN,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.regresar_menu
        )
        btn_volver.pack(side="right", padx=20)

        # Si cierran con la X, que haga lo mismo que el botón regresar
        self.protocol("WM_DELETE_WINDOW", self.regresar_menu)

        # Marco para el Formulario
        frame_form = tk.Frame(self, padx=20, pady=15, bg=COLOR_FONDO)
        frame_form.pack(fill="x")

        # --- CAMPOS DEL FORMULARIO ---
        
        # Archivo
        tk.Label(
            frame_form,
            text="Archivo PDF (*):",
            font=FUENTE_LABEL,
            bg=COLOR_FONDO
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.lbl_archivo = tk.Label(
            frame_form,
            text="Sin archivo seleccionado",
            fg="#E74C3C",
            bg=COLOR_FONDO,
            font=("Segoe UI", 9, "italic")
        )
        self.lbl_archivo.grid(row=0, column=1, sticky="w")
        
        btn_select = tk.Button(
            frame_form,
            text="Seleccionar...",
            command=self.seleccionar, 
            bg="#ECF0F1",
            fg="#2C3E50",
            relief="flat",
            cursor="hand2"
        )
        btn_select.grid(row=0, column=2, padx=10)

        # Categoría
        tk.Label(
            frame_form,
            text="Categoría (*):",
            font=FUENTE_LABEL,
            bg=COLOR_FONDO
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.combo_categoria = ttk.Combobox(frame_form, state="readonly", width=40)
        self.combo_categoria.grid(row=1, column=1, columnspan=2, sticky="w")
        self.combo_categoria.bind("<<ComboboxSelected>>", self.cargar_tipos)

        # Tipo
        tk.Label(
            frame_form,
            text="Tipo de Documento (*):",
            font=FUENTE_LABEL,
            bg=COLOR_FONDO
        ).grid(row=2, column=0, sticky="w", pady=5)

        self.combo_tipo = ttk.Combobox(frame_form, state="readonly", width=40)
        self.combo_tipo.grid(row=2, column=1, columnspan=2, sticky="w")

        # Título
        tk.Label(
            frame_form,
            text="Título / Expediente (*):",
            font=FUENTE_LABEL,
            bg=COLOR_FONDO
        ).grid(row=3, column=0, sticky="w", pady=5)

        self.entry_titulo = tk.Entry(frame_form, width=50, font=FUENTE_NORMAL)
        self.entry_titulo.grid(row=3, column=1, columnspan=2, sticky="w")

        # Actores
        tk.Label(
            frame_form,
            text="Actores Involucrados (*):",
            font=FUENTE_LABEL,
            bg=COLOR_FONDO
        ).grid(row=4, column=0, sticky="nw", pady=5)

        self.txt_actores = tk.Text(frame_form, height=3, width=50, font=FUENTE_NORMAL)
        self.txt_actores.grid(row=4, column=1, columnspan=2, rowspan=2, pady=5)

        # Fecha Vencimiento (CON CALENDARIO)
        tk.Label(
            frame_form,
            text="Fecha Vencimiento (*):",
            font=FUENTE_LABEL,
            bg=COLOR_FONDO
        ).grid(row=6, column=0, sticky="w", pady=5)
        
        self.cal_fecha = DateEntry(
            frame_form,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            font=FUENTE_NORMAL,
            date_pattern='yyyy-mm-dd'
        )
        self.cal_fecha.grid(row=6, column=1, sticky="w")

        # BOTÓN GUARDAR
        tk.Button(
            self,
            text="💾  GUARDAR DOCUMENTO", 
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            pady=5,
            command=self.subir
        ).pack(fill="x", padx=40, pady=15)

        # ---------------------------------------------------------
        # 2. SECCIÓN DE TABLA (VISOR)
        # ---------------------------------------------------------
        lbl_tabla = tk.Label(
            self,
            text="DOCUMENTOS REGISTRADOS (DOBLE CLIC PARA ABRIR)", 
            bg=COLOR_HEADER,
            fg=COLOR_TEXTO_HEADER,
            font=("Segoe UI", 10, "bold"),
            pady=5
        )
        lbl_tabla.pack(fill="x", pady=(10, 0))

        frame_tabla = tk.Frame(self, bg=COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("ID", "Titulo", "Tipo", "Fecha")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=8)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9))

        self.tree.heading("ID", text="ID")
        self.tree.heading("Titulo", text="Título / Expediente")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Fecha", text="F. Vencimiento")

        self.tree.column("ID", width=0, stretch=tk.NO) 
        self.tree.column("Titulo", width=300)
        self.tree.column("Tipo", width=200)
        self.tree.column("Fecha", width=100)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.abrir_documento)

        tk.Button(
            self,
            text="⬇  Descargar PDF seleccionado",
            bg=COLOR_BTN,
            fg=COLOR_TEXTO_BTN,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.descargar_documento
        ).pack(fill="x", padx=40, pady=(0, 15))

        # --- INICIO ---
        self.cargar_categorias_async()
        self.cargar_tabla()

    # ----------------- REGRESAR AL MENÚ -----------------
    def regresar_menu(self):
        """Cerrar esta ventana y volver a mostrar el menú principal."""
        if self.master is not None:
            try:
                self.master.deiconify()
                # 👇 Maximizar también el menú principal
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

    # --- LÓGICA DE TABLA ---
    def cargar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        db = get_db()
        if db is None:
            return

        cursor = db["documentos"].find().sort("fecha_subida", -1).limit(20)

        for doc in cursor:
            tipo_mostrar = str(doc.get("tipo", "N/A"))
            self.tree.insert(
                "",
                "end",
                values=(
                    str(doc["_id"]), 
                    doc.get("titulo", "Sin Título"),
                    tipo_mostrar,
                    doc.get("fecha_evento", "")
                )
            )

    def abrir_documento(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion)
        doc_id = item["values"][0] 

        db = get_db()
        doc = db["documentos"].find_one({"_id": ObjectId(doc_id)})

        if doc and "archivo_pdf" in doc:
            try:
                nombre_temp = f"temp_{doc_id}.pdf"
                with open(nombre_temp, "wb") as f:
                    f.write(doc["archivo_pdf"])
                os.startfile(nombre_temp)

                # AUDITORÍA: ver documento
                try:
                    self.aud.registrar_evento(
                        usuario=self.usuario.get("username", ""),
                        rol=self.usuario.get("rol", ""),
                        accion="VER_DOCUMENTO",
                        documento_id=str(doc_id),
                        documento_nombre=doc.get("titulo", "Sin Título")
                    )
                except Exception as e:
                    print("Error auditoria VER_DOCUMENTO:", e)

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el PDF:\n{e}")
        else:
            messagebox.showerror("Aviso", "Sin archivo PDF válido.")

    def descargar_documento(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona", "Selecciona un documento.")
            return

        item = self.tree.item(seleccion)
        doc_id = item["values"][0]

        db = get_db()
        doc = db["documentos"].find_one({"_id": ObjectId(doc_id)})

        if not doc or "archivo_pdf" not in doc:
            messagebox.showerror("Aviso", "Sin archivo PDF válido.")
            return

        nombre_sugerido = (doc.get("titulo", "documento") or "documento") + ".pdf"
        ruta_destino = filedialog.asksaveasfilename(
            title="Guardar documento como...",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=nombre_sugerido
        )
        if not ruta_destino:
            return

        try:
            with open(ruta_destino, "wb") as f:
                f.write(doc["archivo_pdf"])

            messagebox.showinfo("Descarga completa", f"Documento guardado en:\n{ruta_destino}")
            
            # AUDITORÍA: descargar documento
            try:
                self.aud.registrar_evento(
                    usuario=self.usuario.get("username", ""),
                    rol=self.usuario.get("rol", ""),
                    accion="DESCARGAR_DOCUMENTO",
                    documento_id=str(doc_id),
                    documento_nombre=doc.get("titulo", "Sin Título")
                )
            except Exception as e:
                print("Error auditoria DESCARGAR_DOCUMENTO:", e)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    # --- LÓGICA TÉCNICA ---
    def cargar_categorias_async(self):
        def thread_carga():
            db = get_db()
            if db is None:
                return
            cursor = db["categorias"].find({"activo": True}).sort("descripcion", 1)
            self.categorias_dict = {c["descripcion"]: c["slug"] for c in cursor}
            self.after(0, self._actualizar_gui_categorias)

        threading.Thread(target=thread_carga, daemon=True).start()

    def _actualizar_gui_categorias(self):
        self.combo_categoria["values"] = list(self.categorias_dict.keys())
        if self.categorias_dict:
            self.combo_categoria.current(0)
            self.cargar_tipos()
            self._cargado_inicial = True

    def cargar_tipos(self, event=None):
        cat_visible = self.combo_categoria.get()
        if not cat_visible:
            return
        cat_slug = self.categorias_dict.get(cat_visible)
        db = get_db()
        cat = db["categorias"].find_one({"slug": cat_slug})
        if cat:
            tipos = [t for t in cat.get("tipos", []) if t.get("activo", True)]
            self.tipos_dict = {t["nombre"]: t["slug"] for t in tipos}
            self.combo_tipo["values"] = list(self.tipos_dict.keys())
            if self.tipos_dict:
                self.combo_tipo.current(0)
            else:
                self.combo_tipo.set("")

    def seleccionar(self):
        f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if f:
            self.ruta_archivo = f
            self.lbl_archivo.config(text=os.path.basename(f), fg="#27AE60")

    # --- GUARDADO ---
    def subir(self):
        titulo = self.entry_titulo.get().strip()
        actores = self.txt_actores.get("1.0", tk.END).strip()
        
        # OBTENER FECHA DEL CALENDARIO
        fecha = self.cal_fecha.get_date()              # objeto date
        fecha_str = fecha.strftime("%Y-%m-%d")         # string para BD
        
        cat_sel = self.combo_categoria.get()
        tipo_sel = self.combo_tipo.get()

        if not self.ruta_archivo:
            messagebox.showwarning("Falta", "Selecciona un PDF.")
            return
        if not titulo or not actores:
            messagebox.showwarning("Falta", "Llenar campos obligatorios.")
            return
        if not cat_sel or not tipo_sel:
            messagebox.showwarning("Falta", "Selecciona categoría y tipo.")
            return

        cat_slug = self.categorias_dict[cat_sel]
        tipo_slug = self.tipos_dict[tipo_sel]

        db = get_db()
        try:
            with open(self.ruta_archivo, 'rb') as f:
                binary_data = Binary(f.read())

            doc_data = {
                "titulo": titulo,
                "categoria": cat_slug,
                "tipo": tipo_slug,
                "actores_involucrados": actores,
                "fecha_evento": fecha_str,
                "subido_por": self.usuario["username"],
                "fecha_subida": datetime.utcnow(),
                "archivo_pdf": binary_data
            }

            # Guardar documento
            resultado = db["documentos"].insert_one(doc_data)

            # AUDITORÍA: registrar SUBIR_DOCUMENTO
            try:
                self.aud.registrar_evento(
                    usuario=self.usuario.get("username", ""),
                    rol=self.usuario.get("rol", ""),
                    accion="SUBIR_DOCUMENTO",
                    documento_id=str(resultado.inserted_id),
                    documento_nombre=titulo
                )
            except Exception as e:
                print("Error auditoria SUBIR_DOCUMENTO:", e)

            messagebox.showinfo("Éxito", "Documento guardado correctamente.")
            self.limpiar_formulario()
            self.cargar_tabla()

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")

    def limpiar_formulario(self):
        self.entry_titulo.delete(0, tk.END)
        self.txt_actores.delete("1.0", tk.END)
        self.cal_fecha.set_date(datetime.now()) 
        self.ruta_archivo = None
        self.lbl_archivo.config(text="Sin archivo seleccionado", fg="#E74C3C")
