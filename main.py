# main.py

from modules.login_gui import VentanaLogin
from modules.menu_gui import MenuPrincipal


def main():
    login = VentanaLogin()
    login.mainloop()

    usuario = login.usuario_logueado
    if not usuario:
        return  # no hubo login

    app = MenuPrincipal(usuario)
    app.mainloop()


if __name__ == "__main__":
    main()
