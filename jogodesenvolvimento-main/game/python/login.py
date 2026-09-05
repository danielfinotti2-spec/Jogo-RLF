import json
from pathlib import Path

from joguinhoonline import executar_jogo


PASTA_ATUAL = Path(__file__).resolve().parent
ARQUIVO_USUARIOS = PASTA_ATUAL / "users.json"


def criar_arquivo_usuarios():
    if ARQUIVO_USUARIOS.exists():
        return

    usuarios_padrao = [
        {
            "nome": "admin",
            "senha": "admin123",
            "nivel": 1,
        }
    ]

    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios_padrao, arquivo, indent=4, ensure_ascii=False)


def carregar_usuarios():
    with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def fazer_login(nome, senha):
    for usuario in carregar_usuarios():
        if usuario["nome"] == nome and usuario["senha"] == senha:
            return usuario

    return None


def pedir_login():
    print("===== RLF LOGIN =====")
    print("Usuario padrao: admin")
    print("Senha padrao: admin123")

    while True:
        nome = input("\nUsuario: ").strip()
        senha = input("Senha: ").strip()

        usuario = fazer_login(nome, senha)
        if usuario:
            print(f"\nLogin feito. Bem-vindo, {usuario['nome']}!")
            return usuario

        print("\nUsuario ou senha incorretos.")


def main():
    criar_arquivo_usuarios()
    usuario = pedir_login()
    executar_jogo(usuario)


if __name__ == "__main__":
    main()
