# --- IMPORTACIONES ---
import tkinter as tk  # Librería principal para crear ventanas y botones
from tkinter import filedialog, messagebox, ttk  # Herramientas extra: explorador, alertas y menús
import os  # Para manejar rutas de archivos (obtener nombre del PDF)
from datetime import datetime  # Para guardar la fecha exacta de subida
from bson.binary import Binary  # IMPORTANTE: Para guardar el PDF como bytes en Mongo
from db.connection import get_db  # Nuestra función de conexión

# Clase del Módulo de Subida
# Hereda de Toplevel para ser una ventana secundaria
class Subida_modulo1(tk.Toplevel):
    
    def __init__(self, parent, usuario_data):
        super().__init__(parent)  # Inicializa la ventana secundaria
        self.usuario = usuario_data  # Guardamos quién está usando el módulo
        self.title("Módulo 1: Registro Legal Detallado")
        self.geometry("700x650")
        self.ruta_archivo = None  # Aquí guardaremos la ruta del PDF seleccionado

        # --- DISEÑO DE LA INTERFAZ (GUI) ---
        
        # Encabezado azul
        tk.Label(self, text="Registro de Expediente / Documento", 
                 font=("Arial", 16, "bold"), bg="#E3F2FD").pack(fill="x", pady=10)

        # Marco principal para los campos
        frame_form = tk.Frame(self, padx=20, pady=10)
        frame_form.pack(fill="both", expand=True)

        # 1. SELECCIÓN DE ARCHIVO
        tk.Label(frame_form, text="Archivo PDF (*):", font=("bold")).grid(row=0, column=0, sticky="w")
        self.lbl_archivo = tk.Label(frame_form, text="Sin archivo seleccionado", fg="red")
        self.lbl_archivo.grid(row=0, column=1, sticky="w")
        tk.Button(frame_form, text="Seleccionar", command=self.seleccionar).grid(row=0, column=2)

        # 2. TIPO DE DOCUMENTO (Combobox)
        tk.Label(frame_form, text="Tipo de Documento (*):").grid(row=1, column=0, sticky="w", pady=5)
        tipos_legales = ["Demanda Inicial", "Sentencia Definitiva", "Audiencia (Acta)", "Ratificación", "Oficio", "Otro"]
        self.combo_tipo = ttk.Combobox(frame_form, values=tipos_legales, state="readonly", width=30)
        self.combo_tipo.current(0)
        self.combo_tipo.grid(row=1, column=1, columnspan=2, sticky="w")

        # 3. TÍTULO
        tk.Label(frame_form, text="Título / Expediente (*):").grid(row=2, column=0, sticky="w")
        self.entry_titulo = tk.Entry(frame_form, width=50)
        self.entry_titulo.grid(row=2, column=1, columnspan=2, sticky="w", pady=5)

        # 4. ACTORES (Caja de texto grande)
        tk.Label(frame_form, text="Actores Involucrados (*):").grid(row=3, column=0, sticky="nw", pady=5)
        tk.Label(frame_form, text="(Juez, Secretario, Testigos...)", fg="gray", font=("Arial", 8)).grid(row=4, column=0, sticky="nw")
        self.txt_actores = tk.Text(frame_form, height=4, width=50)
        self.txt_actores.grid(row=3, column=1, columnspan=2, rowspan=2, pady=5)

        # 5. FECHA
        tk.Label(frame_form, text="Fecha del Evento (*):").grid(row=5, column=0, sticky="w")
        self.entry_fecha = tk.Entry(frame_form, width=15)
        # Ponemos la fecha de hoy automáticamente
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.grid(row=5, column=1, sticky="w")

        # 6. HORA (Sección Mejorada con AM/PM)
        tk.Label(frame_form, text="Hora (*):").grid(row=6, column=0, sticky="w")
        
        # Sub-frame invisible para alinear la caja de números y el combo AM/PM
        frame_hora = tk.Frame(frame_form)
        frame_hora.grid(row=6, column=1, sticky="w")
        
        # Caja pequeña para los números (Ej: 10:30)
        self.entry_hora = tk.Entry(frame_hora, width=8)
        self.entry_hora.pack(side="left")
        
        # Selector para AM o PM
        self.combo_am_pm = ttk.Combobox(frame_hora, values=["AM", "PM"], width=5, state="readonly")
        self.combo_am_pm.current(0) # Empieza en AM
        self.combo_am_pm.pack(side="left", padx=5)
        
        # Texto de ayuda visual
        tk.Label(frame_hora, text="(Ej: 04:30)", fg="gray", font=("Arial", 8)).pack(side="left")

        # BOTÓN GUARDAR (Verde)
        tk.Button(self, text="💾 GUARDAR EN BD", bg="#2E7D32", fg="white", height=2,
                  command=self.subir).pack(fill="x", padx=20, pady=20)

    # --- LÓGICA DEL PROGRAMA ---

    def seleccionar(self):
        # Abre ventana para buscar PDF
        f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if f:
            self.ruta_archivo = f
            # Cambia el texto rojo a verde con el nombre del archivo
            self.lbl_archivo.config(text=os.path.basename(f), fg="green")

    def subir(self):
        # 1. RECOLECCIÓN DE DATOS (Limpiamos espacios vacíos con .strip())
        titulo = self.entry_titulo.get().strip()
        actores = self.txt_actores.get("1.0", tk.END).strip()
        fecha = self.entry_fecha.get().strip()
        hora_numeros = self.entry_hora.get().strip()
        am_pm = self.combo_am_pm.get()

        # 2. VALIDACIONES DE CAMPOS VACÍOS
        # Si falta algo, mostramos alerta y usamos 'return' para NO cerrar la ventana
        if not self.ruta_archivo:
            messagebox.showwarning("Falta Archivo", "Por favor selecciona un archivo PDF.")
            return

        if not titulo:
            messagebox.showwarning("Falta Título", "El campo 'Título / Expediente' es obligatorio.")
            return

        if not actores:
            messagebox.showwarning("Falta Actores", "Debes indicar quiénes participan.")
            return

        if not fecha:
            messagebox.showwarning("Falta Fecha", "La fecha del evento es obligatoria.")
            return

        if not hora_numeros:
            messagebox.showwarning("Falta Hora", "Por favor escribe la hora (Ej: 10:30).")
            return

        # 3. VALIDACIÓN DE FORMATO DE HORA
        # Verificamos que solo sean números y dos puntos (sin letras)
        # .replace(":", "") quita los dos puntos temporalmente para checar si lo demás son dígitos
        if not hora_numeros.replace(":", "").isdigit():
            messagebox.showerror("Formato Incorrecto", "La hora solo debe tener números y ':' (Ej: 05:45). No uses letras.")
            return

        # 4. CONEXIÓN A LA BASE DE DATOS
        db = get_db()
        if db is None:
            messagebox.showerror("Error Crítico", "No hay conexión con la base de datos.")
            return

        try:
            # 5. LEER EL ARCHIVO PDF A BINARIO
            with open(self.ruta_archivo, 'rb') as f:
                binary_data = Binary(f.read())

            # 6. CONCATENAR LA HORA
            # Unimos los números con el AM/PM (Ej: "10:30" + " " + "AM" = "10:30 AM")
            hora_completa = f"{hora_numeros} {am_pm}"

            # 7. CREAR EL DICCIONARIO DEL DOCUMENTO
            doc_data = {
                "titulo": titulo,
                "tipo": self.combo_tipo.get(),
                "actores_involucrados": actores,
                "fecha_evento": fecha,
                "hora_duracion": hora_completa, # Guardamos la hora completa
                "subido_por": self.usuario['username'], # Usuario logueado
                "fecha_subida": datetime.utcnow(),
                "archivo_pdf": binary_data  # El PDF incrustado
            }

            # 8. INSERTAR EN MONGO
            db['documentos'].insert_one(doc_data)
            
            # Éxito: Avisamos y cerramos la ventana
            messagebox.showinfo("Éxito", "Documento Legal Guardado Correctamente.")
            self.destroy()

        except Exception as e:
            # Error técnico: Avisamos y NO cerramos la ventana para que intenten de nuevo
            messagebox.showerror("Error", f"Ocurrió un error al guardar: {e}")