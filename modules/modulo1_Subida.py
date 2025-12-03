# --- IMPORTACIONES ---
import tkinter as tk  # Librería principal para la interfaz gráfica
from tkinter import filedialog, messagebox, ttk  # Herramientas extra
import os  # Para manejar rutas de archivos
from datetime import datetime  # Para guardar fecha
from bson.binary import Binary  # Para guardar PDF en Mongo
from bson.objectid import ObjectId # Para buscar por ID
from db.connection import get_db  # Conexión
import threading  # Carga asíncrona

# --- CONFIGURACIÓN DE DISEÑO (Igual al Main) ---
COLOR_FONDO = "#F4F6F7"       # Gris muy claro
COLOR_HEADER = "#2C3E50"      # Azul Marino Oscuro (Encabezados)
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"         # Azul Brillante (Botones de acción)
COLOR_TEXTO_BTN = "white"
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_LABEL = ("Segoe UI", 10, "bold")
FUENTE_NORMAL = ("Segoe UI", 10)

# Clase del Módulo de Subida
# NOTA: Mantenemos el nombre 'Subida_modulo1' para compatibilidad con tu Main
class Subida_modulo1(tk.Toplevel):
    
    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.usuario = usuario_data
        
        # Configuración de la ventana
        self.title("Módulo 1: Registro y Consulta de Documentos")
        self.geometry("900x750")
        self.configure(bg=COLOR_FONDO) # Color de fondo general
        
        # Variables de estado
        self.ruta_archivo = None
        self.categorias_dict = {}
        self.tipos_dict = {}
        self._cargado_inicial = False

        # --- DISEÑO DE LA INTERFAZ (GUI) ---

        # 1. ENCABEZADO PRINCIPAL (Estilo Main)
        header_frame = tk.Frame(self, bg=COLOR_HEADER, pady=15)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="REGISTRO DE EXPEDIENTE / DOCUMENTO",
                 font=FUENTE_TITULO, bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER).pack()

        # Marco para el Formulario
        frame_form = tk.Frame(self, padx=20, pady=15, bg=COLOR_FONDO)
        frame_form.pack(fill="x")

        # --- CAMPOS DEL FORMULARIO ---
        # Nota: Agregamos bg=COLOR_FONDO a los Labels para que combinen
        
        # Archivo
        tk.Label(frame_form, text="Archivo PDF (*):", font=FUENTE_LABEL, bg=COLOR_FONDO).grid(row=0, column=0, sticky="w", pady=5)
        self.lbl_archivo = tk.Label(frame_form, text="Sin archivo seleccionado", fg="#E74C3C", bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"))
        self.lbl_archivo.grid(row=0, column=1, sticky="w")
        
        btn_select = tk.Button(frame_form, text="Seleccionar...", command=self.seleccionar, 
                               bg="#ECF0F1", fg="#2C3E50", relief="flat", cursor="hand2")
        btn_select.grid(row=0, column=2, padx=10)

        # Categoría
        tk.Label(frame_form, text="Categoría (*):", font=FUENTE_LABEL, bg=COLOR_FONDO).grid(row=1, column=0, sticky="w", pady=5)
        self.combo_categoria = ttk.Combobox(frame_form, state="readonly", width=40)
        self.combo_categoria.grid(row=1, column=1, columnspan=2, sticky="w")
        self.combo_categoria.bind("<<ComboboxSelected>>", self.cargar_tipos)

        # Tipo
        tk.Label(frame_form, text="Tipo de Documento (*):", font=FUENTE_LABEL, bg=COLOR_FONDO).grid(row=2, column=0, sticky="w", pady=5)
        self.combo_tipo = ttk.Combobox(frame_form, state="readonly", width=40)
        self.combo_tipo.grid(row=2, column=1, columnspan=2, sticky="w")

        # Título
        tk.Label(frame_form, text="Título / Expediente (*):", font=FUENTE_LABEL, bg=COLOR_FONDO).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_titulo = tk.Entry(frame_form, width=50, font=FUENTE_NORMAL)
        self.entry_titulo.grid(row=3, column=1, columnspan=2, sticky="w")

        # Actores
        tk.Label(frame_form, text="Actores Involucrados (*):", font=FUENTE_LABEL, bg=COLOR_FONDO).grid(row=4, column=0, sticky="nw", pady=5)
        self.txt_actores = tk.Text(frame_form, height=3, width=50, font=FUENTE_NORMAL)
        self.txt_actores.grid(row=4, column=1, columnspan=2, rowspan=2, pady=5)

        # Fecha
        tk.Label(frame_form, text="Fecha Evento (*):", font=FUENTE_LABEL, bg=COLOR_FONDO).grid(row=6, column=0, sticky="w", pady=5)
        self.entry_fecha = tk.Entry(frame_form, width=15, font=FUENTE_NORMAL)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.grid(row=6, column=1, sticky="w")

        # Hora
        tk.Label(frame_form, text="Hora (*):", font=FUENTE_LABEL, bg=COLOR_FONDO).grid(row=7, column=0, sticky="w", pady=5)
        frame_hora = tk.Frame(frame_form, bg=COLOR_FONDO)
        frame_hora.grid(row=7, column=1, sticky="w")
        
        self.entry_hora = tk.Entry(frame_hora, width=8, font=FUENTE_NORMAL)
        self.entry_hora.pack(side="left")
        
        self.combo_am_pm = ttk.Combobox(frame_hora, values=["AM", "PM"], width=5, state="readonly")
        self.combo_am_pm.current(0)
        self.combo_am_pm.pack(side="left", padx=5)
        
        tk.Label(frame_hora, text="(Ej: 04:30)", fg="gray", bg=COLOR_FONDO, font=("Segoe UI", 8)).pack(side="left")

        # BOTÓN GUARDAR (Estilo Main)
        tk.Button(self, text="💾  GUARDAR DOCUMENTO", 
                  bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=("Segoe UI", 11, "bold"),
                  relief="flat", cursor="hand2", pady=5,
                  command=self.subir).pack(fill="x", padx=40, pady=15)

        # ---------------------------------------------------------
        # 2. SECCIÓN DE TABLA (VISOR)
        # ---------------------------------------------------------
        
        # Título de sección (Barra oscura igual que el header)
        lbl_tabla = tk.Label(self, text="DOCUMENTOS REGISTRADOS (DOBLE CLIC PARA ABRIR)", 
                             bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER, font=("Segoe UI", 10, "bold"), pady=5)
        lbl_tabla.pack(fill="x", pady=(10,0))

        frame_tabla = tk.Frame(self, bg=COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        # Configuración de columnas
        cols = ("ID", "Titulo", "Tipo", "Fecha")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=8)
        
        # Estilo de la tabla (opcional, para que se vea mejor)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9))

        # Encabezados
        self.tree.heading("ID", text="ID")
        self.tree.heading("Titulo", text="Título / Expediente")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Fecha", text="Fecha")

        # Ancho de columnas (Ocultamos ID)
        self.tree.column("ID", width=0, stretch=tk.NO) 
        self.tree.column("Titulo", width=300)
        self.tree.column("Tipo", width=200)
        self.tree.column("Fecha", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Evento Doble Clic
        self.tree.bind("<Double-1>", self.abrir_documento)

        # --- INICIO ---
        self.cargar_categorias_async()
        self.cargar_tabla()

    # --- LÓGICA DE TABLA ---

    def cargar_tabla(self):
        """ Consulta MongoDB y llena la tabla """
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        db = get_db()
        if db is None: return

        cursor = db["documentos"].find().sort("fecha_subida", -1).limit(20)

        for doc in cursor:
            tipo_mostrar = str(doc.get("tipo", "N/A"))
            self.tree.insert("", "end", values=(
                str(doc["_id"]), 
                doc.get("titulo", "Sin Título"),
                tipo_mostrar,
                doc.get("fecha_evento", "")
            ))

    def abrir_documento(self, event):
        """ Abre el PDF seleccionado """
        seleccion = self.tree.selection()
        if not seleccion: return
        
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
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el PDF:\n{e}")
        else:
            messagebox.showerror("Aviso", "Sin archivo PDF válido.")

    # --- LÓGICA TÉCNICA (Hilos) ---

    def cargar_categorias_async(self):
        def thread_carga():
            db = get_db()
            if db is None: return
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
        if not cat_visible: return
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
            self.lbl_archivo.config(text=os.path.basename(f), fg="#27AE60") # Verde bonito

    # --- GUARDADO ---

    def subir(self):
        titulo = self.entry_titulo.get().strip()
        actores = self.txt_actores.get("1.0", tk.END).strip()
        fecha = self.entry_fecha.get().strip()
        hora_num = self.entry_hora.get().strip()
        am_pm = self.combo_am_pm.get()
        cat_sel = self.combo_categoria.get()
        tipo_sel = self.combo_tipo.get()

        if not self.ruta_archivo:
            messagebox.showwarning("Falta", "Selecciona un PDF.")
            return
        if not titulo or not actores or not fecha:
            messagebox.showwarning("Falta", "Llenar campos obligatorios.")
            return
        if not hora_num.replace(":", "").isdigit():
            messagebox.showerror("Error", "Hora inválida.")
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

            hora_completa = f"{hora_num} {am_pm}"

            doc_data = {
                "titulo": titulo,
                "categoria": cat_slug,
                "tipo": tipo_slug,
                "actores_involucrados": actores,
                "fecha_evento": fecha,
                "hora_duracion": hora_completa,
                "subido_por": self.usuario["username"],
                "fecha_subida": datetime.utcnow(),
                "archivo_pdf": binary_data
            }

            db["documentos"].insert_one(doc_data)
            messagebox.showinfo("Éxito", "Documento guardado correctamente.")
            self.limpiar_formulario()
            self.cargar_tabla()

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")

    def limpiar_formulario(self):
        self.entry_titulo.delete(0, tk.END)
        self.txt_actores.delete("1.0", tk.END)
        self.entry_hora.delete(0, tk.END)
        self.ruta_archivo = None
        self.lbl_archivo.config(text="Sin archivo seleccionado", fg="#E74C3C")