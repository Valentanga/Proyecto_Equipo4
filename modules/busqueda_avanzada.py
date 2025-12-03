import tkinter as tk
from tkinter import ttk, messagebox
from repositories.BusquedaRepo import BusquedaRepo

# --- CONFIGURACIÓN DE DISEÑO (Coherente con Main) ---
COLOR_FONDO = "#F4F6F7"
COLOR_HEADER = "#2C3E50"
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"
COLOR_TEXTO_BTN = "white"
COLOR_BTN_SECUNDARIO = "#95A5A6"
COLOR_BTN_LIMPIAR = "#E74C3C"
COLOR_BTN_MOSTRAR = "#27AE60"
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_NORMAL = ("Segoe UI", 10)
FUENTE_BTN = ("Segoe UI", 10, "bold")

class BusquedaAvanzada:
    def __init__(self, root, usuario_actual):
        self.root = root
        self.usuario_actual = usuario_actual
        self.repo = BusquedaRepo()

        # Limpiar pantalla
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("Búsqueda Avanzada")
        self.root.geometry("1100x750")
        self.root.configure(bg=COLOR_FONDO)

        # --- HEADER ---
        header_frame = tk.Frame(self.root, bg=COLOR_HEADER, pady=20)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame,
            text="Búsqueda Avanzada de Documentos",
            font=FUENTE_TITULO,
            bg=COLOR_HEADER,
            fg=COLOR_TEXTO_HEADER
        ).pack()

        tk.Label(
            header_frame,
            text="Sistema de Gestión Legal",
            font=("Segoe UI", 10, "italic"),
            bg=COLOR_HEADER,
            fg="#BDC3C7"
        ).pack()

        # --- BODY FRAME ---
        body_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        body_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # --- SECCIÓN DE FILTROS ---
        filtros_frame = tk.LabelFrame(
            body_frame,
            text="  Filtros de Búsqueda  ",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg="#2C3E50",
            relief="flat",
            bd=2,
            labelanchor="n"
        )
        filtros_frame.pack(fill="x", pady=(0, 20))

        form_container = tk.Frame(filtros_frame, bg=COLOR_FONDO)
        form_container.pack(pady=15, padx=20)

        self.campos = {}
        labels = [
            ("titulo", "Título"),
            ("categoria", "Categoría"),
            ("tipo", "Tipo de Documento"),
            ("actores_involucrados", "Actores Involucrados"),
            ("fecha_evento", "Fecha del Evento"),
            ("subido_por", "Subido Por")
        ]

        for idx, (campo, label_text) in enumerate(labels):
            fila = idx // 2
            columna = (idx % 2) * 2

            tk.Label(
                form_container,
                text=label_text + ":",
                font=FUENTE_NORMAL,
                bg=COLOR_FONDO,
                fg="#34495E",
                anchor="w"
            ).grid(row=fila, column=columna, padx=(0, 10), pady=8, sticky="w")

            entry = tk.Entry(
                form_container,
                width=25,
                font=FUENTE_NORMAL,
                relief="solid",
                bd=1
            )
            entry.grid(row=fila, column=columna + 1, padx=(0, 30), pady=8)
            self.campos[campo] = entry

        # --- BOTONES DE ACCIÓN ---
        botones_frame = tk.Frame(body_frame, bg=COLOR_FONDO)
        botones_frame.pack(pady=(0, 20))

        btn_style_buscar = {
            "font": FUENTE_BTN,
            "bg": COLOR_BTN,
            "fg": COLOR_TEXTO_BTN,
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "pady": 10,
            "width": 18,
            "activebackground": "#2980B9",
            "activeforeground": "white"
        }

        tk.Button(
            botones_frame,
            text="🔍 Buscar",
            command=self.buscar,
            **btn_style_buscar
        ).grid(row=0, column=0, padx=8)

        btn_limpiar = btn_style_buscar.copy()
        btn_limpiar.update({"bg": COLOR_BTN_LIMPIAR, "activebackground": "#C0392B"})
        tk.Button(
            botones_frame,
            text="🗑️ Limpiar Campos",
            command=self.limpiar_campos,
            **btn_limpiar
        ).grid(row=0, column=1, padx=8)

        btn_mostrar = btn_style_buscar.copy()
        btn_mostrar.update({"bg": COLOR_BTN_MOSTRAR, "activebackground": "#229954"})
        tk.Button(
            botones_frame,
            text="📋 Mostrar Todo",
            command=self.mostrar_todo,
            **btn_mostrar
        ).grid(row=0, column=2, padx=8)

        # --- SECCIÓN DE RESULTADOS ---
        resultados_frame = tk.LabelFrame(
            body_frame,
            text="  Resultados  ",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg="#2C3E50",
            relief="flat",
            bd=2
        )
        resultados_frame.pack(fill="both", expand=True)

        # Contenedor para la tabla con scrollbar
        tabla_container = tk.Frame(resultados_frame, bg=COLOR_FONDO)
        tabla_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(tabla_container)
        scrollbar.pack(side="right", fill="y")

        # --- TABLA CON ESTILO MEJORADO ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white",
            font=FUENTE_NORMAL
        )
        style.map("Custom.Treeview", background=[("selected", "#3498DB")])
        style.configure(
            "Custom.Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#34495E",
            foreground="white"
        )

        columnas = ("titulo", "categoria", "tipo", "actores", "fecha_evento", "subido_por")
        
        self.tabla = ttk.Treeview(
            tabla_container,
            columns=columnas,
            show="headings",
            height=12,
            yscrollcommand=scrollbar.set,
            style="Custom.Treeview"
        )
        
        scrollbar.config(command=self.tabla.yview)

        # Configurar columnas
        anchos = {"titulo": 180, "categoria": 120, "tipo": 140, 
                  "actores": 150, "fecha_evento": 120, "subido_por": 120}
        
        for col in columnas:
            self.tabla.heading(col, text=col.replace("_", " ").title())
            self.tabla.column(col, width=anchos.get(col, 120), anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # --- FOOTER CON BOTÓN VOLVER ---
        footer_frame = tk.Frame(self.root, bg=COLOR_FONDO, pady=15)
        footer_frame.pack(fill="x")

        tk.Button(
            footer_frame,
            text="← Volver al Menú",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_BTN_LIMPIAR,
            bg=COLOR_FONDO,
            activebackground=COLOR_FONDO,
            activeforeground="#C0392B",
            relief="flat",
            cursor="hand2",
            bd=0,
            command=self.volver_menu
        ).pack()

    def buscar(self):
        filtros = {campo: entry.get().strip() for campo, entry in self.campos.items() if entry.get().strip()}
        
        if not filtros:
            messagebox.showwarning("Advertencia", "Ingrese al menos un criterio de búsqueda")
            return
        
        resultados = self.repo.buscar(filtros)
        self._actualizar_tabla(resultados)

        if not resultados:
            messagebox.showinfo("Sin resultados", "No se encontraron documentos con esos filtros")
        else:
            messagebox.showinfo("Búsqueda exitosa", f"Se encontraron {len(resultados)} documento(s)")

    def limpiar_campos(self):
        """Limpia los campos de búsqueda y la tabla."""
        for entry in self.campos.values():
            entry.delete(0, tk.END)

        for row in self.tabla.get_children():
            self.tabla.delete(row)

    def mostrar_todo(self):
        """Carga todos los documentos sin filtros."""
        resultados = self.repo.buscar({})
        self._actualizar_tabla(resultados)

        if not resultados:
            messagebox.showinfo("Sin documentos", "No existen documentos en la base de datos")
        else:
            messagebox.showinfo("Carga completa", f"Se cargaron {len(resultados)} documento(s)")

    def _actualizar_tabla(self, resultados):
        """Limpia la tabla y agrega nuevos resultados."""
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        for doc in resultados:
            self.tabla.insert("", "end", values=(
                doc.get("titulo", ""),
                doc.get("categoria", ""),
                doc.get("tipo", ""),
                doc.get("actores_involucrados", ""),
                doc.get("fecha_evento", ""),
                doc.get("subido_por", "")
            ))

    def volver_menu(self):
        from main import MainApp
        MainApp(self.root)