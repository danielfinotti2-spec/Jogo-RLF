import random
import os


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def gerar_personagem():
    print("Bem-vindo ao RPG MMO!")
    return random.randint(70, 100)


nome_personagem = input("Digite o nome do seu personagem: ")

Vida = gerar_personagem()
Mana = random.randint(30, 80)
Ataque = random.randint(5, 15)
Defesa = random.randint(1, 10)
Dinheiro = random.randint(0, 100)
Xp = random.randint(0, 50)
Nivel = 1


print(f"\nPersonagem: {nome_personagem}")
print(f"Vida: {Vida}")
print(f"Mana: {Mana}")
print(f"Ataque: {Ataque}")
print(f"Defesa: {Defesa}")
print(f"Dinheiro: {Dinheiro}")
print(f"XP: {Xp}")
print(f"Nível: {Nivel}")


def batalha():
    global Vida

    inimigo_vida = random.randint(20, 100)
    inimigo_ataque = random.randint(5, 15)
    inimigo_defesa = random.randint(1, 10)

    print("\n⚔️ Um inimigo apareceu!")
    print(f"Vida: {inimigo_vida}")
    print(f"Ataque: {inimigo_ataque}")
    print(f"Defesa: {inimigo_defesa}")

    while Vida > 0 and inimigo_vida > 0:

        print("\n1 - Atacar")
        print("2 - Defender")

        acao = input("Escolha sua ação: ").lower()

        defendendo = False

        match acao:

            case "1" | "atacar":

                dano_causado = max(Ataque - inimigo_defesa, 1)

                inimigo_vida -= dano_causado

                print(
                    f"\nVocê causou {dano_causado} de dano."
                )

                print(
                    f"Vida do inimigo: {max(inimigo_vida, 0)}"
                )

            case "2" | "defender":

                defendendo = True

                print("\n🛡️ Você se preparou para defender.")

            case _:

                print("\nAção inválida!")
                continue

        # inimigo só ataca se ainda estiver vivo
        if inimigo_vida > 0:

            dano_recebido = max(inimigo_ataque - Defesa, 1)

            if defendendo:
                dano_recebido //= 2

            Vida -= dano_recebido

            print(
                f"O inimigo causou {dano_recebido} de dano."
            )

            print(
                f"Sua vida: {max(Vida, 0)}"
            )

    if Vida <= 0:
        print("\n💀 Você foi derrotado!")

    else:
        print("\n🏆 Você derrotou o inimigo!")


batalha()