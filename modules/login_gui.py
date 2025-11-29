# modules/login_gui.py

import tkinter as tk
from tkinter import messagebox
from models.user_service import UserService


class VentanaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Gestor de Documentos")
        self.geometry("300x180")

        self.user_service = UserService()
        self.usuario_logueado = None  # aquí guardaremos el doc del usuario

        tk.Label(self, text="Usuario:").pack(pady=(10, 0))
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        tk.Label(self, text="Contraseña:").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        tk.Button(self, text="Entrar",
                  command=self.intentar_login).pack(pady=10)

    def intentar_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        user = self.user_service.autenticar(username, password)

        if user:
            self.usuario_logueado = user
            self.destroy()  # cerrar ventana y seguir al menú
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
