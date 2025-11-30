# --- IMPORTACIONES --- (agrega threading si no está)
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from datetime import datetime
from bson.binary import Binary
from db.connection import get_db
import threading  # ← ADD: Para async

class Subida_modulo1(tk.Toplevel):

    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.usuario = usuario_data
        self.title("Módulo 1: Registro Legal Detallado")
        self.geometry("700x650")
        self.ruta_archivo = None
        self.categorias_dict = {}  # Inicial vacío
        self.tipos_dict = {}  # Inicial vacío
        self._cargado_inicial = False  # Flag para evitar warnings repetidos

        # --- GUI ---

        tk.Label(self, text="Registro de Expediente / Documento",
                 font=("Arial", 16, "bold"), bg="#E3F2FD").pack(fill="x", pady=10)

        frame_form = tk.Frame(self, padx=20, pady=10)
        frame_form.pack(fill="both", expand=True)

        # 1. SELECCIÓN DE ARCHIVO
        tk.Label(frame_form, text="Archivo PDF (*):", font=("bold")).grid(row=0, column=0, sticky="w")
        self.lbl_archivo = tk.Label(frame_form, text="Sin archivo seleccionado", fg="red")
        self.lbl_archivo.grid(row=0, column=1, sticky="w")
        tk.Button(frame_form, text="Seleccionar", command=self.seleccionar).grid(row=0, column=2, padx=5)

        # 2. TIPO DE DOCUMENTO
        tk.Label(frame_form, text="Tipo de Documento (*):").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_tipo = ttk.Combobox(frame_form, values=[], state="readonly", width=30)
        self.combo_tipo.grid(row=1, column=1, columnspan=2, sticky="w")  # ← columnspan=2 ahora que no hay botón

        # 2.1 CATEGORÍA (sin botón)
        tk.Label(frame_form, text="Categoría (*):").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_categoria = ttk.Combobox(frame_form, values=[], state="readonly", width=30)
        self.combo_categoria.grid(row=2, column=1, columnspan=2, sticky="w")  # ← columnspan=2, limpio

        self.combo_categoria.bind("<<ComboboxSelected>>", self.cargar_tipos)

        # 3. TÍTULO
        tk.Label(frame_form, text="Título / Expediente (*):").grid(row=3, column=0, sticky="w")
        self.entry_titulo = tk.Entry(frame_form, width=50)
        self.entry_titulo.grid(row=3, column=1, columnspan=2, sticky="w", pady=5)

        # 4. ACTORES
        tk.Label(frame_form, text="Actores Involucrados (*):").grid(row=4, column=0, sticky="nw", pady=5)
        tk.Label(frame_form, text="(Juez, Secretario, Testigos...)", fg="gray",
                 font=("Arial", 8)).grid(row=5, column=0, sticky="nw")
        self.txt_actores = tk.Text(frame_form, height=4, width=50)
        self.txt_actores.grid(row=4, column=1, columnspan=2, rowspan=2, pady=5)

        # 5. FECHA
        tk.Label(frame_form, text="Fecha del Evento (*):").grid(row=6, column=0, sticky="w")
        self.entry_fecha = tk.Entry(frame_form, width=15)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.grid(row=6, column=1, sticky="w")

        # 6. HORA
        tk.Label(frame_form, text="Hora (*):").grid(row=7, column=0, sticky="w")
        frame_hora = tk.Frame(frame_form)
        frame_hora.grid(row=7, column=1, sticky="w")

        self.entry_hora = tk.Entry(frame_hora, width=8)
        self.entry_hora.pack(side="left")

        self.combo_am_pm = ttk.Combobox(frame_hora, values=["AM", "PM"], width=5, state="readonly")
        self.combo_am_pm.current(0)
        self.combo_am_pm.pack(side="left", padx=5)

        tk.Label(frame_hora, text="(Ej: 04:30)", fg="gray",
                 font=("Arial", 8)).pack(side="left")

        tk.Button(self, text="💾 GUARDAR EN BD", bg="#2E7D32", fg="white",
                  height=2, command=self.subir).pack(fill="x", padx=20, pady=20)

        # ← ADD: Lanza carga async al final del init
        self.cargar_categorias_async()

    # ← NEW: Método async para cargar sin bloquear
    def cargar_categorias_async(self):
        def thread_carga():
            # Query en background
            db = get_db()
            cursor = db["categorias"].find({"activo": True}).sort("descripcion", 1)
            cats_list = list(cursor)
            self.categorias_dict = {c["descripcion"]: c["slug"] for c in cats_list}
            # Actualiza GUI en main thread
            self.after(0, self._actualizar_gui_categorias)

        threading.Thread(target=thread_carga, daemon=True).start()

    # ← NEW: Actualiza combos en main thread
    def _actualizar_gui_categorias(self):
        self.combo_categoria["values"] = list(self.categorias_dict.keys())
        if self.categorias_dict:
            self.combo_categoria.current(0)
            self.cargar_tipos()  # Auto-carga tipos
            self._cargado_inicial = True
        else:
            # Solo warn si no cargado antes
            if not self._cargado_inicial:
                messagebox.showwarning("Sin Datos", "No hay categorías activas. Ve a Gestión y crea algunas.")
                self._cargado_inicial = True

    # -------------------------
    def seleccionar(self):
        f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if f:
            self.ruta_archivo = f
            self.lbl_archivo.config(text=os.path.basename(f), fg="green")

    # -------------------------
    def cargar_tipos(self, event=None):
        categoria_visible = self.combo_categoria.get()
        if not categoria_visible:
            return
        categoria_slug = self.categorias_dict.get(categoria_visible)
        if not categoria_slug:
            return

        # ← Para tipos, también hazlo async si quieres (pero con 1 cat es overkill)
        db = get_db()
        cat = db["categorias"].find_one({"slug": categoria_slug})
        if not cat:
            messagebox.showerror("Error", "Categoría no encontrada. Recarga la app.")
            return

        tipos = [t for t in cat.get("tipos", []) if t.get("activo", True)]
        self.tipos_dict = {t["nombre"]: t["slug"] for t in tipos}
        self.combo_tipo["values"] = list(self.tipos_dict.keys())

        if tipos:
            self.combo_tipo.current(0)
        else:
            self.combo_tipo.set("")
            messagebox.showwarning("Sin Tipos", f"'{categoria_visible}' no tiene tipos activos. Agrega en Gestión.")

    # -------------------------
    def subir(self):
        # ... (igual que antes, sin cambios en validaciones)
        titulo = self.entry_titulo.get().strip()
        actores = self.txt_actores.get("1.0", tk.END).strip()
        fecha = self.entry_fecha.get().strip()
        hora_numeros = self.entry_hora.get().strip()
        am_pm = self.combo_am_pm.get()
        categoria_visible = self.combo_categoria.get()
        tipo_visible = self.combo_tipo.get()

        if not self.ruta_archivo:
            messagebox.showwarning("Falta Archivo", "Selecciona un PDF.")
            return
        if not titulo:
            messagebox.showwarning("Falta Título", "El título es obligatorio.")
            return
        if not actores:
            messagebox.showwarning("Falta Actores", "Escribe los actores involucrados.")
            return
        if not fecha:
            messagebox.showwarning("Falta Fecha", "La fecha es obligatoria.")
            return
        if not hora_numeros.replace(":", "").isdigit():
            messagebox.showerror("Formato Incorrecto", "La hora debe ser numérica (ej: 12:00).")
            return
        if not categoria_visible:
            messagebox.showwarning("Falta Categoría", "Selecciona una categoría.")
            return
        if not tipo_visible or tipo_visible not in self.tipos_dict:
            messagebox.showwarning("Falta Tipo", "Selecciona un tipo válido (elige categoría primero).")
            return

        categoria_slug = self.categorias_dict[categoria_visible]
        tipo_slug = self.tipos_dict[tipo_visible]

        db = get_db()

        try:
            with open(self.ruta_archivo, 'rb') as f:
                binary_data = Binary(f.read())

            hora_completa = f"{hora_numeros} {am_pm}"

            doc_data = {
                "titulo": titulo,
                "categoria": categoria_slug,
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
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar:\n{str(e)}")