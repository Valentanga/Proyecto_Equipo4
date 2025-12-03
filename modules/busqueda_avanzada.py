import tkinter as tk
from tkinter import ttk, messagebox
from repositories.BusquedaRepo import BusquedaRepo

class BusquedaAvanzada:
    def __init__(self, root, usuario_actual):
        self.root = root
        self.usuario_actual = usuario_actual
        self.repo = BusquedaRepo()

        # Limpiar pantalla
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("Búsqueda Avanzada")
        self.root.geometry("950x650")

        tk.Label(root, text="Búsqueda Avanzada de Documentos", font=("Arial", 16, "bold")).pack(pady=10)

        # --- FORMULARIO DE BÚSQUEDA ---
        form = tk.Frame(root)
        form.pack(pady=10)

        self.campos = {
            "titulo": tk.Entry(form, width=30),
            "categoria": tk.Entry(form, width=30),
            "tipo": tk.Entry(form, width=30),
            "actores_involucrados": tk.Entry(form, width=30),
            "fecha_evento": tk.Entry(form, width=30),
            "subido_por": tk.Entry(form, width=30)
        }

        fila = 0
        for campo, entry in self.campos.items():
            tk.Label(form, text=campo.replace("_", " ").title()).grid(row=fila, column=0, padx=5, pady=5)
            entry.grid(row=fila, column=1, padx=5, pady=5)
            fila += 1

        # --- BOTONES DE ACCIÓN ---
        botones_frame = tk.Frame(root)
        botones_frame.pack(pady=10)

        tk.Button(botones_frame, text="Buscar", bg="#D1C4E9", width=18, command=self.buscar).grid(row=0, column=0, padx=10)
        tk.Button(botones_frame, text="Limpiar Campos", bg="#FFCDD2", width=18, command=self.limpiar_campos).grid(row=0, column=1, padx=10)
        tk.Button(botones_frame, text="Mostrar Todo", bg="#C8E6C9", width=18, command=self.mostrar_todo).grid(row=0, column=2, padx=10)

        # --- TABLA ---
        columnas = ("titulo", "categoria", "tipo", "actores", "fecha_evento", "subido_por")

        self.tabla = ttk.Treeview(root, columns=columnas, show="headings", height=15)
        for col in columnas:
            self.tabla.heading(col, text=col.title())
            self.tabla.column(col, width=150)

        self.tabla.pack(pady=10, fill="both", expand=True)

        # Botón volver
        tk.Button(root, text="Volver al Menú", fg="red", command=self.volver_menu).pack(pady=10)

    def buscar(self):
        filtros = {campo: entry.get() for campo, entry in self.campos.items()}
        resultados = self.repo.buscar(filtros)

        self._actualizar_tabla(resultados)

        if not resultados:
            messagebox.showinfo("Sin resultados", "No se encontraron documentos con esos filtros")

    def limpiar_campos(self):
        """Limpia los campos de búsqueda y la tabla."""
        for entry in self.campos.values():
            entry.delete(0, tk.END)

        # Limpiar la tabla
        for row in self.tabla.get_children():
            self.tabla.delete(row)

    def mostrar_todo(self):
        """Carga todos los documentos sin filtros."""
        resultados = self.repo.buscar({})  # Sin filtros = trae todo
        self._actualizar_tabla(resultados)

        if not resultados:
            messagebox.showinfo("Sin documentos", "No existen documentos en la base de datos")

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
