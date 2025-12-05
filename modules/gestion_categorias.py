# modules/gestion_categorias.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.categorias_service import CategoriasService
from models.auditoria_service import AuditoriaService

# Colores y fuentes para emular el diseño web
COLOR_FONDO = "#F4F6F7"       # Gris muy claro (Casi blanco)
COLOR_HEADER = "#2C3E50"      # Azul Marino Oscuro (Profesional)
COLOR_TEXTO_HEADER = "white"
COLOR_BTN = "#3498DB"         # Azul brillante para botones
COLOR_TEXTO_BTN = "white"
COLOR_LOGOUT = "#E74C3C"      # Rojo suave para salir (no usado aquí, pero incluido)
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_NORMAL = ("Segoe UI", 11)
FUENTE_BTN = ("Segoe UI", 10, "bold")

class GestionCategorias:
    def __init__(self, parent, usuario):
        self.usuario = usuario
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Categorías y Tipos")
        self.window.geometry("1200x800")
        self.window.state("zoomed")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.configure(bg=COLOR_FONDO)

        btn_back = tk.Button(
            self.window,
            text="⭠ Volver al Menú Principal",
            bg=COLOR_LOGOUT,
            fg="white",
            font=FUENTE_BTN,
            relief="flat",
            bd=0,
            command=self.volver_menu_principal
        )
        btn_back.pack(anchor="w", padx=10, pady=10)

        self.service = CategoriasService()
        self.aud = AuditoriaService()

        # Configurar estilo para ttk (emular diseño web)
        self.style = ttk.Style()
        self.style.theme_use('default')  # Base simple para custom
        self.style.configure("Treeview", background=COLOR_FONDO, foreground="black", fieldbackground=COLOR_FONDO, borderwidth=1, font=FUENTE_NORMAL)
        self.style.configure("Treeview.Heading", background=COLOR_HEADER, foreground=COLOR_TEXTO_HEADER, font=FUENTE_TITULO, relief="flat")
        self.style.map("Treeview", background=[('selected', COLOR_BTN)])
        self.style.map("Treeview.Heading", background=[('active', COLOR_BTN)])

        # Layout: left = categorias, right = tipos
        left = tk.Frame(self.window, bg=COLOR_FONDO, width=450, padx=10, pady=10)
        left.pack(side="left", fill="y")
        right = tk.Frame(self.window, bg=COLOR_FONDO, padx=10, pady=10)
        right.pack(side="right", expand=True, fill="both")

        # --- LEFT: CATEGORÍAS ---
        # Header frame para emular barra oscura
        header_left = tk.Frame(left, bg=COLOR_HEADER, height=40)
        header_left.pack(fill="x", pady=(0, 5))
        header_left.pack_propagate(False)
        tk.Label(header_left, text="Categorías", bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER, font=FUENTE_TITULO).pack(anchor="w", padx=10, pady=10)

        cols = ("slug", "descripcion", "activo")
        self.tree_cat = ttk.Treeview(left, columns=cols, show="headings", height=20, style="Treeview")
        self.tree_cat.heading("slug", text="Slug")
        self.tree_cat.heading("descripcion", text="Descripción")
        self.tree_cat.heading("activo", text="Activo")
        self.tree_cat.column("slug", width=150, anchor="w")
        self.tree_cat.column("descripcion", width=200, anchor="w")
        self.tree_cat.column("activo", width=100, anchor="center")
        self.tree_cat.pack(fill="y", expand=True)
        self.tree_cat.bind("<<TreeviewSelect>>", self._on_categoria_select)

        btnf = tk.Frame(left, bg=COLOR_FONDO)
        btnf.pack(pady=6, anchor="w")
        tk.Button(btnf, text="Nueva", width=8, command=self.nueva_categoria, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=0, padx=3)
        tk.Button(btnf, text="Editar", width=8, command=self.editar_categoria, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=1, padx=3)
        tk.Button(btnf, text="Eliminar", width=8, command=self.eliminar_categoria, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=2, padx=3)
        tk.Button(btnf, text="Refrescar", width=8, command=self.cargar_categorias, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=3, padx=3)

        # --- RIGHT: TIPOS de la categoría seleccionada ---
        # Header frame para emular barra oscura
        header_right = tk.Frame(right, bg=COLOR_HEADER, height=40)
        header_right.pack(fill="x", pady=(0, 5))
        header_right.pack_propagate(False)
        tk.Label(header_right, text="Tipos de Documento", bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER, font=FUENTE_TITULO).pack(anchor="w", padx=10, pady=10)

        cols2 = ("id", "nombre", "descripcion", "activo")
        self.tree_tipos = ttk.Treeview(right, columns=cols2, show="headings", height=15, style="Treeview")
        self.tree_tipos.heading("id", text="ID")
        self.tree_tipos.heading("nombre", text="Nombre")
        self.tree_tipos.heading("descripcion", text="Descripción")
        self.tree_tipos.heading("activo", text="Activo")
        self.tree_tipos.column("id", width=100, anchor="w")
        self.tree_tipos.column("nombre", width=180, anchor="w")
        self.tree_tipos.column("descripcion", width=250, anchor="w")
        self.tree_tipos.column("activo", width=60, anchor="center")
        self.tree_tipos.pack(fill="both", expand=True)
        self.tree_tipos.bind("<<TreeviewSelect>>", lambda e: None)

        tbtnf = tk.Frame(right, bg=COLOR_FONDO)
        tbtnf.pack(pady=6, anchor="e")
        tk.Button(tbtnf, text="Agregar Tipo", width=12, command=self.agregar_tipo, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=0, padx=4)
        tk.Button(tbtnf, text="Editar Tipo", width=12, command=self.editar_tipo, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=1, padx=4)
        tk.Button(tbtnf, text="Eliminar Tipo", width=12, command=self.eliminar_tipo, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=2, padx=4)

        # Cargar inicialmente
        self.cargar_categorias()

    # ---------- Categorías ----------
    def cargar_categorias(self):
        for i in self.tree_cat.get_children():
            self.tree_cat.delete(i)
        cats = self.service.listar_categorias(solo_activas=True)
        for c in cats:
            slug = c.get("nombre", "")
            desc = c.get("descripcion", "")
            activo = c.get("activo", True)
            self.tree_cat.insert("", "end", iid=str(c["_id"]), values=(slug, desc, "Sí" if activo else "No"))
        # limpiar tipos
        self._limpiar_tipos()

    def _on_categoria_select(self, event):
        sel = self.tree_cat.selection()
        if not sel:
            return
        cat_id = sel[0]
        self.mostrar_tipos(cat_id)

    def nueva_categoria(self):
        # modal dialog para pedir descripcion y slug opcional
        dlg = CategoriaDialog(self.window, title="Nueva Categoría")
        self.window.wait_window(dlg.top)
        if not dlg.result:
            return
        descripcion, slug = dlg.result
        # si slug vacío lo generamos
        if not slug:
            slug = descripcion.lower().strip().replace(" ", "-")
        try:
            new_id = self.service.crear_categoria(slug, descripcion, creado_por=self.usuario["username"])
            self.aud.registrar_evento(self.usuario["username"], self.usuario.get("rol",""), "CREAR_CATEGORIA", documento_id=new_id, documento_nombre=descripcion)
            messagebox.showinfo("Creada", "Categoría creada correctamente.")
            self.cargar_categorias()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_categoria(self):
        sel = self.tree_cat.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona una categoría para editar.")
            return
        cat_id = sel[0]
        cat = self.service.obtener_categoria(cat_id)
        if not cat:
            messagebox.showerror("Error", "Categoría no encontrada.")
            return
        # abrir dialog con valores actuales
        dlg = CategoriaDialog(self.window, title="Editar Categoría", descripcion_init=cat.get("descripcion",""), slug_init=cat.get("nombre",""))
        self.window.wait_window(dlg.top)
        if not dlg.result:
            return
        descripcion, slug = dlg.result
        if not slug:
            slug = descripcion.lower().strip().replace(" ", "-")
        try:
            self.service.actualizar_categoria(cat_id, slug, descripcion, modificado_por=self.usuario["username"])
            self.aud.registrar_evento(self.usuario["username"], self.usuario.get("rol",""), "EDITAR_CATEGORIA", documento_id=cat_id, documento_nombre=descripcion)
            messagebox.showinfo("Actualizado", "Categoría actualizada.")
            self.cargar_categorias()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_categoria(self):
        sel = self.tree_cat.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona una categoría para eliminar.")
            return
        cat_id = sel[0]
        if not messagebox.askyesno("Confirmar", "¿Deseas desactivar (eliminar) la categoría seleccionada?"):
            return
        try:
            self.service.eliminar_categoria(cat_id, eliminado_por=self.usuario["username"])
            self.aud.registrar_evento(self.usuario["username"], self.usuario.get("rol",""), "ELIMINAR_CATEGORIA", documento_id=cat_id)
            messagebox.showinfo("Eliminada", "Categoría desactivada.")
            self.cargar_categorias()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Tipos ----------
    def mostrar_tipos(self, categoria_id):
        for i in self.tree_tipos.get_children():
            self.tree_tipos.delete(i)
        cat = self.service.obtener_categoria(categoria_id)
        if not cat:
            return
        for t in cat.get("tipos", []):
            if not t.get("activo", True):
                continue
            tid = t.get("id")
            nombre = t.get("nombre", "")
            desc = t.get("descripcion", "")
            activo = t.get("activo", True)
            self.tree_tipos.insert("", "end", iid=tid, values=(tid, nombre, desc, "Sí" if activo else "No"))

    def _limpiar_tipos(self):
        for i in self.tree_tipos.get_children():
            self.tree_tipos.delete(i)

    def agregar_tipo(self):
        sel = self.tree_cat.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona primero una categoría.")
            return
        cat_id = sel[0]
        dlg = TipoDialog(self.window, title="Nuevo Tipo")
        self.window.wait_window(dlg.top)
        if not dlg.result:
            return
        nombre, descripcion = dlg.result
        try:
            tipo_id = self.service.agregar_tipo(cat_id, nombre, descripcion, creado_por=self.usuario["username"])
            self.aud.registrar_evento(self.usuario["username"], self.usuario.get("rol",""), "AGREGAR_TIPO", documento_id=cat_id, extra={"tipo_id": tipo_id, "nombre": nombre})
            messagebox.showinfo("Agregado", "Tipo agregado correctamente.")
            self.mostrar_tipos(cat_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_tipo(self):
        sel_cat = self.tree_cat.selection()
        sel_tipo = self.tree_tipos.selection()
        if not sel_cat or not sel_tipo:
            messagebox.showwarning("Selecciona", "Selecciona categoría y tipo a editar.")
            return
        cat_id = sel_cat[0]
        tipo_id = sel_tipo[0]
        cat = self.service.obtener_categoria(cat_id)
        tipo = next((t for t in cat.get("tipos",[]) if t["id"]==tipo_id), None)
        if not tipo:
            messagebox.showerror("Error", "Tipo no encontrado.")
            return
        dlg = TipoDialog(self.window, title="Editar Tipo", nombre_init=tipo.get("nombre",""), descripcion_init=tipo.get("descripcion",""))
        self.window.wait_window(dlg.top)
        if not dlg.result:
            return
        nombre, descripcion = dlg.result
        try:
            self.service.editar_tipo(cat_id, tipo_id, nombre, descripcion, modificado_por=self.usuario["username"])
            self.aud.registrar_evento(self.usuario["username"], self.usuario.get("rol",""), "EDITAR_TIPO", documento_id=cat_id, extra={"tipo_id": tipo_id, "nombre": nombre})
            messagebox.showinfo("Actualizado", "Tipo actualizado.")
            self.mostrar_tipos(cat_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_tipo(self):
        sel_cat = self.tree_cat.selection()
        sel_tipo = self.tree_tipos.selection()
        if not sel_cat or not sel_tipo:
            messagebox.showwarning("Selecciona", "Selecciona categoría y tipo a eliminar.")
            return
        if not messagebox.askyesno("Confirmar", "¿Deseas desactivar (eliminar) el tipo seleccionado?"):
            return
        cat_id = sel_cat[0]
        tipo_id = sel_tipo[0]
        try:
            self.service.eliminar_tipo(cat_id, tipo_id, eliminado_por=self.usuario["username"])
            self.aud.registrar_evento(self.usuario["username"], self.usuario.get("rol",""), "ELIMINAR_TIPO", documento_id=cat_id, extra={"tipo_id": tipo_id})
            messagebox.showinfo("Eliminado", "Tipo desactivado.")
            self.mostrar_tipos(cat_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def volver_menu_principal(self):
        """Cierra esta ventana y regresa al menú principal."""
        self.window.destroy()


# ----------------- DIALOGS -----------------
class CategoriaDialog:
    def __init__(self, parent, title="Categoría", descripcion_init="", slug_init=""):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("420x160")
        self.top.transient(parent)
        self.top.grab_set()
        self.top.configure(bg=COLOR_FONDO)

        tk.Label(self.top, text="Nombre visible (descripción):", bg=COLOR_FONDO, fg="black", font=FUENTE_NORMAL).pack(anchor="w", padx=10, pady=(10,0))
        self.entry_desc = tk.Entry(self.top, width=60, font=FUENTE_NORMAL, relief="flat", bd=1)
        self.entry_desc.pack(padx=10, pady=3)
        self.entry_desc.insert(0, descripcion_init)

        tk.Label(self.top, text="Slug (opcional, p. ej. 'contratos'):", bg=COLOR_FONDO, fg="black", font=FUENTE_NORMAL).pack(anchor="w", padx=10, pady=(6,0))
        self.entry_slug = tk.Entry(self.top, width=60, font=FUENTE_NORMAL, relief="flat", bd=1)
        self.entry_slug.pack(padx=10, pady=3)
        self.entry_slug.insert(0, slug_init)

        btnf = tk.Frame(self.top, bg=COLOR_FONDO)
        btnf.pack(pady=10)
        tk.Button(btnf, text="Cancelar", command=self._cancel, bg="gray", fg="white", font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=0, padx=6)
        tk.Button(btnf, text="Guardar", command=self._ok, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=1, padx=6)

        self.result = None

    def _ok(self):
        desc = self.entry_desc.get().strip()
        slug = self.entry_slug.get().strip().lower().replace(" ", "-")
        if not desc:
            messagebox.showwarning("Falta nombre", "Debes escribir la descripción visible de la categoría.")
            return
        # si slug vacío, se generará fuera. guardamos los dos
        self.result = (desc, slug)
        self.top.destroy()

    def _cancel(self):
        self.result = None
        self.top.destroy()

class TipoDialog:
    def __init__(self, parent, title="Tipo", nombre_init="", descripcion_init=""):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("480x200")
        self.top.transient(parent)
        self.top.grab_set()
        self.top.configure(bg=COLOR_FONDO)

        tk.Label(self.top, text="Nombre del tipo:", bg=COLOR_FONDO, fg="black", font=FUENTE_NORMAL).pack(anchor="w", padx=10, pady=(10,0))
        self.entry_nombre = tk.Entry(self.top, width=70, font=FUENTE_NORMAL, relief="flat", bd=1)
        self.entry_nombre.pack(padx=10, pady=3)
        self.entry_nombre.insert(0, nombre_init)

        tk.Label(self.top, text="Descripción (opcional):", bg=COLOR_FONDO, fg="black", font=FUENTE_NORMAL).pack(anchor="w", padx=10, pady=(6,0))
        self.entry_desc = tk.Entry(self.top, width=70, font=FUENTE_NORMAL, relief="flat", bd=1)
        self.entry_desc.pack(padx=10, pady=3)
        self.entry_desc.insert(0, descripcion_init)

        btnf = tk.Frame(self.top, bg=COLOR_FONDO)
        btnf.pack(pady=10)
        tk.Button(btnf, text="Cancelar", command=self._cancel, bg="gray", fg="white", font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=0, padx=6)
        tk.Button(btnf, text="Guardar", command=self._ok, bg=COLOR_BTN, fg=COLOR_TEXTO_BTN, font=FUENTE_BTN, relief="flat", bd=0).grid(row=0, column=1, padx=6)

        self.result = None

    def _ok(self):
        nombre = self.entry_nombre.get().strip()
        desc = self.entry_desc.get().strip()
        if not nombre:
            messagebox.showwarning("Falta nombre", "Debes escribir el nombre del tipo.")
            return
        self.result = (nombre, desc)
        self.top.destroy()

    def _cancel(self):
        self.result = None
        self.top.destroy()