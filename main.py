# main.py
import tkinter as tk
from modules.auditoria_gui import VentanaAuditoria

def main():
    root = tk.Tk()
    root.title("Archivo de Documentos Legales Digitales")
    root.geometry("400x200")

    btn = tk.Button(
        root,
        text="Abrir Auditoría de Accesos (Admin)",
        command=lambda: VentanaAuditoria(root)
    )
    btn.pack(expand=True, padx=20, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()

