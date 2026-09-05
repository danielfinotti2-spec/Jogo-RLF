import pygame
import sys
import webbrowser
import unicodedata
from pathlib import Path
from historia import IntroducaoHistoria



TAMANHO_JANELA = (1280, 720)
FPS = 60
IDADE_MINIMA = 18

CLASSES_PERSONAGEM = [
    ("Guerreiro", "Combate corpo a corpo com armas e resistência."),
    ("Mago", "Lança feitiços e domina as artes mágicas."),
    ("Arqueiro", "Ataques à distância com arco e precisão."),
    ("Ladino", "Furtividade, agilidade e ataques surpresa."),
    ("Clérigo", "Cura e proteção com magia sagrada."),
    ("Paladino", "Combina combate, proteção e cura sagrada."),
    ("Alquimista", "Prepara poções e misturas mágicas."),
    ("Invocador", "Invoca criaturas para ajudar em combate."),
]

if getattr(sys, "frozen", False):
    PASTA_BASE = Path(sys._MEIPASS)
else:
    PASTA_BASE = Path(__file__).resolve().parent

PASTA_FONTES = PASTA_BASE / "fonts"
PASTA_HISTORIA = PASTA_BASE / "assets" / "historia"
FONTE_REGULAR = PASTA_FONTES / "PixelifySans-Regular.ttf"
FONTE_BOLD = PASTA_FONTES / "PixelifySans-Bold.ttf"

CORES = {
    "fundo": (8, 8, 9),
    "painel": (17, 17, 19),
    "painel_claro": (25, 25, 28),
    "linha": (42, 42, 46),
    "texto": (240, 240, 240),
    "texto_fraco": (128, 128, 134),
    "destaque": (240, 240, 240),
}

tela_cheia = False
tela = None
relogio = None
usuario_atual = None
personagem_atual = None
fonte_logo = None
fonte_titulo = None
fonte_botao = None
fonte_texto = None
fonte_pequena = None


def carregar_fonte(tamanho, negrito=False):
    caminho = FONTE_BOLD if negrito else FONTE_REGULAR
    return pygame.font.Font(str(caminho), tamanho)


class Botao:
    def __init__(self, texto, rect, acao, selecionado=False):
        self.texto = texto
        self.rect = pygame.Rect(rect)
        self.acao = acao
        self.selecionado = selecionado

    def desenhar(self, superficie):
        mouse_em_cima = self.rect.collidepoint(pygame.mouse.get_pos())

        cor_fundo = CORES["painel_claro"] if mouse_em_cima else CORES["painel"]
        espessura_linha = 2 if self.selecionado else 1
        cor_linha = CORES["destaque"] if (self.selecionado or mouse_em_cima) else CORES["linha"]

        pygame.draw.rect(superficie, cor_fundo, self.rect, border_radius=2)
        pygame.draw.rect(superficie, cor_linha, self.rect, espessura_linha, border_radius=2)

        texto = fonte_botao.render(self.texto, True, CORES["texto"])
        texto_rect = texto.get_rect(midleft=(self.rect.x + 18, self.rect.centery))
        superficie.blit(texto, texto_rect)

    def clicou(self, evento):
        return (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.rect.collidepoint(evento.pos)
        )


def normalizar_busca(texto):
    return "".join(
        letra for letra in unicodedata.normalize("NFD", texto.casefold())
        if not unicodedata.combining(letra)
    )


def desenhar_texto_quebrado(texto, posicao, largura):
    x, y = posicao
    linha = ""
    for palavra in texto.split():
        tentativa = f"{linha} {palavra}".strip()
        if linha and fonte_texto.size(tentativa)[0] > largura:
            desenhar_texto(linha, fonte_texto, CORES["texto_fraco"], (x, y))
            y += 26
            linha = palavra
        else:
            linha = tentativa
    if linha:
        desenhar_texto(linha, fonte_texto, CORES["texto_fraco"], (x, y))


class CriacaoPersonagem:
    def __init__(self):
        self.valores = {"nome": "", "idade": "", "busca": ""}
        self.campo_ativo = "nome"
        self.classe = None
        self.pagina = 0
        self.erro = ""

    def campos(self):
        largura, _ = tamanho_tela()
        coluna = min(340, int(largura * 0.30))
        direita = max(436, 56 + coluna + 40)
        return {
            "nome": pygame.Rect(56, 184, coluna, 44),
            "idade": pygame.Rect(56, 270, coluna, 44),
            "busca": pygame.Rect(direita, 184, largura - direita - 56, 44),
        }

    def classes_filtradas(self):
        busca = normalizar_busca(self.valores["busca"].strip())
        return [classe for classe in CLASSES_PERSONAGEM if busca in normalizar_busca(classe[0])]

    def paginacao(self):
        _, altura = tamanho_tela()
        por_pagina = max(1, (altura - 374) // 46)
        classes = self.classes_filtradas()
        total = max(1, (len(classes) + por_pagina - 1) // por_pagina)
        self.pagina = max(0, min(self.pagina, total - 1))
        inicio = self.pagina * por_pagina
        return classes[inicio:inicio + por_pagina], total

    def botoes_classes(self):
        campo = self.campos()["busca"]
        classes, _ = self.paginacao()
        return [
            Botao(nome, (campo.x, 244 + i * 46, campo.width, 40), nome,
                  self.classe is not None and self.classe[0] == nome)
            for i, (nome, _) in enumerate(classes)
        ]

    def botoes_acoes(self):
        _, altura = tamanho_tela()
        campo = self.campos()["busca"]
        return [
            Botao("Voltar", (56, altura - 134, 130, 42), "menu"),
            Botao("Criar personagem", (202, altura - 134, 220, 42), "criar"),
            Botao("Anterior", (campo.x, altura - 134, 130, 42), "anterior"),
            Botao("Próxima", (campo.right - 130, altura - 134, 130, 42), "proxima"),
        ]

    def confirmar(self):
        nome = self.valores["nome"].strip()
        idade = self.valores["idade"]
        if not nome:
            self.erro = "Digite o nome do personagem."
            self.campo_ativo = "nome"
        elif not idade or not idade.isascii() or not idade.isdecimal() or not IDADE_MINIMA <= int(idade) <= 999:
            self.erro = "A idade deve ser de 18 a 999 anos."
            self.campo_ativo = "idade"
        elif self.classe is None:
            self.erro = "Escolha uma classe na lista."
        else:
            self.erro = ""
            return {"nome": nome, "idade": int(idade), "classe": self.classe[0]}
        return None

    def tratar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.campo_ativo = next(
                (nome for nome, rect in self.campos().items() if rect.collidepoint(evento.pos)), None
            )
            for botao in self.botoes_classes():
                if botao.clicou(evento):
                    self.classe = next(classe for classe in CLASSES_PERSONAGEM if classe[0] == botao.acao)
                    self.erro = ""
                    return None
            for botao in self.botoes_acoes():
                if botao.clicou(evento):
                    if botao.acao in ("menu", "criar"):
                        return botao.acao
                    _, total = self.paginacao()
                    passo = -1 if botao.acao == "anterior" else 1
                    self.pagina = max(0, min(self.pagina + passo, total - 1))
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_TAB:
                campos = list(self.valores)
                indice = campos.index(self.campo_ativo) if self.campo_ativo in campos else -1
                passo = -1 if getattr(evento, "mod", 0) & pygame.KMOD_SHIFT else 1
                self.campo_ativo = campos[(indice + passo) % len(campos)]
            elif evento.key == pygame.K_BACKSPACE and self.campo_ativo:
                self.valores[self.campo_ativo] = self.valores[self.campo_ativo][:-1]
                self.erro = ""
                if self.campo_ativo == "busca":
                    self.pagina = 0
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "criar"
        elif evento.type == pygame.TEXTINPUT and self.campo_ativo:
            campo = self.campo_ativo
            texto = "".join(letra for letra in evento.text if letra.isprintable())
            if campo == "idade":
                texto = "".join(letra for letra in texto if letra in "0123456789")
            limite = 3 if campo == "idade" else 32
            self.valores[campo] = (self.valores[campo] + texto)[:limite]
            self.erro = ""
            if campo == "busca":
                self.pagina = 0
        return None

    def desenhar(self):
        desenhar_topo("Criação de personagem")
        campos = self.campos()
        rotulos = {"nome": "Nome do personagem", "idade": "Idade do personagem (18+)", "busca": "Escolha sua classe · Buscar"}
        dicas = {"nome": "Digite um nome", "idade": "Ex.: 25", "busca": "Digite para filtrar as classes"}
        for nome, rect in campos.items():
            desenhar_texto(rotulos[nome], fonte_texto, CORES["texto"], (rect.x, rect.y - 28))
            pygame.draw.rect(tela, CORES["painel"], rect)
            cor = CORES["destaque"] if self.campo_ativo == nome else CORES["linha"]
            pygame.draw.rect(tela, cor, rect, 2 if self.campo_ativo == nome else 1)
            valor = self.valores[nome]
            cursor = "|" if self.campo_ativo == nome and pygame.time.get_ticks() % 1000 < 500 else ""
            texto = valor + cursor if valor or self.campo_ativo == nome else dicas[nome]
            while texto and fonte_texto.size(texto)[0] > rect.width - 24:
                texto = texto[1:]
            desenhar_texto(texto, fonte_texto, CORES["texto"] if valor else CORES["texto_fraco"], (rect.x + 12, rect.y + 10))
        if self.campo_ativo:
            pygame.key.set_text_input_rect(campos[self.campo_ativo])
        desenhar_texto("Classe selecionada", fonte_texto, CORES["texto"], (56, 346))
        if self.classe:
            desenhar_texto_quebrado(self.classe[0] + ": " + self.classe[1], (56, 380), campos["nome"].width)
        else:
            desenhar_texto_quebrado("Selecione uma das opções ao lado para ver a descrição.", (56, 380), campos["nome"].width)
        for botao in self.botoes_classes():
            botao.desenhar(tela)
        _, total = self.paginacao()
        if not self.classes_filtradas():
            desenhar_texto("Nenhuma classe encontrada.", fonte_texto, CORES["texto_fraco"], (campos["busca"].x, 250))
        _, altura = tamanho_tela()
        desenhar_texto(f"Página {self.pagina + 1}/{total} · {len(self.classes_filtradas())} classes", fonte_pequena,
                       CORES["texto_fraco"], (campos["busca"].x, altura - 160))
        if self.erro:
            desenhar_texto(self.erro, fonte_pequena, (255, 150, 140), (56, altura - 160))
        for botao in self.botoes_acoes():
            botao.desenhar(tela)


def tamanho_tela():
    return tela.get_size()


def alternar_tela_cheia():
    global tela, tela_cheia

    tela_cheia = not tela_cheia
    if tela_cheia:
        tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        tela = pygame.display.set_mode(TAMANHO_JANELA)


def desenhar_fundo():
    largura, altura = tamanho_tela()
    tela.fill(CORES["fundo"])

    pygame.draw.line(tela, CORES["linha"], (0, altura - 76), (largura, altura - 76), 1)
    pygame.draw.rect(tela, CORES["fundo"], (0, altura - 75, largura, 75))


def desenhar_texto(texto, fonte, cor, posicao):
    renderizado = fonte.render(texto, True, cor)
    tela.blit(renderizado, posicao)


def desenhar_topo(titulo):
    largura, _ = tamanho_tela()
    pygame.draw.line(tela, CORES["linha"], (48, 98), (largura - 48, 98), 1)
    desenhar_texto("RLF", fonte_logo, CORES["texto"], (48, 30))
    desenhar_texto(titulo, fonte_titulo, CORES["texto_fraco"], (154, 49))

    if usuario_atual:
        texto_usuario = fonte_pequena.render(f"Logado: {usuario_atual['nome']}", True, CORES["texto_fraco"])
        tela.blit(texto_usuario, (largura - texto_usuario.get_width() - 48, 53))


def desenhar_rodape():
    _, altura = tamanho_tela()
    desenhar_texto("ESC volta ao menu   |   F11 alterna tela cheia", fonte_pequena, CORES["texto_fraco"], (48, altura - 45))


def criar_botoes_menu():
    x = 56
    y = 185
    largura = 240
    altura = 46
    espaco = 12

    return [
        Botao("Novo Jogo", (x, y, largura, altura), "criacao_personagem"),
        Botao("Historia", (x, y + (altura + espaco), largura, altura), "historia"),
        Botao("Opcoes", (x, y + (altura + espaco) * 2, largura, altura), "opcoes"),
        Botao("Apoiar", (x, y + (altura + espaco) * 3, largura, altura), "apoiar"),
    ]


def criar_botoes_opcoes():
    largura, _ = tamanho_tela()
    x = largura - 360
    return [
        Botao("Tela cheia: Sim" if tela_cheia else "Tela cheia: Nao", (x, 210, 260, 44), "tela_cheia", tela_cheia),
        Botao("Som: Ligado" if som_ligado else "Som: Desligado", (x, 266, 260, 44), "som", som_ligado),
        Botao("Voltar", (x, 342, 260, 44), "menu"),
    ]


def criar_botoes_apoio():
    return [
        Botao("Instagram", (56, 200, 240, 44), "https://instagram.com/euodeene"),
        Botao("WhatsApp", (56, 256, 240, 44), "https://wa.me/5521994856055"),
        Botao("Voltar", (56, 330, 180, 42), "menu"),
    ]


def desenhar_menu():
    desenhar_topo("Menu principal")

    desenhar_texto("Selecione uma opcao", fonte_titulo, CORES["texto"], (56, 135))
    desenhar_texto(
        "meinha 123 | teste 456 | teste 789 | teste 000",
        fonte_texto,
        CORES["texto_fraco"],
        (56, 430),
    )

    for botao in criar_botoes_menu():
        botao.desenhar(tela)


def desenhar_pagina(titulo, linhas):
    desenhar_topo(titulo)
    x = 56
    y = 150

    for linha in linhas:
        desenhar_texto(linha, fonte_texto, CORES["texto_fraco"], (x, y))
        y += 34

    Botao("Voltar", (56, 330, 180, 42), "menu").desenhar(tela)


def desenhar_opcoes():
    desenhar_topo("Opcoes")

    desenhar_texto("Video e interface", fonte_titulo, CORES["texto"], (56, 150))
    desenhar_texto("Use F11 ou o botao para alternar tela cheia.", fonte_texto, CORES["texto_fraco"], (56, 194))
    desenhar_texto("As opcoes ficam separadas do jogo para manter o projeto organizado.", fonte_texto, CORES["texto_fraco"], (56, 228))

    for botao in criar_botoes_opcoes():
        botao.desenhar(tela)


def preparar_janela():
    global tela, relogio, fonte_logo, fonte_titulo, fonte_botao, fonte_texto, fonte_pequena

    pygame.init()
    tela = pygame.display.set_mode(TAMANHO_JANELA)
    pygame.display.set_caption("RLF")
    relogio = pygame.time.Clock()

    fonte_logo = carregar_fonte(54, True)
    fonte_titulo = carregar_fonte(28, True)
    fonte_botao = carregar_fonte(19, True)
    fonte_texto = carregar_fonte(18)
    fonte_pequena = carregar_fonte(14)


def executar_jogo(usuario=None):
    global estado, rodando, som_ligado, usuario_atual, tela_cheia, personagem_atual

    usuario_atual = usuario
    estado = "menu"
    rodando = True
    som_ligado = True
    tela_cheia = False
    personagem_atual = None
    criacao = None
    introducao = None

    preparar_janela()
    pygame.key.stop_text_input()

    while rodando:
        tempo_frame = relogio.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                break

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    estado = "menu"
                    pygame.key.stop_text_input()
                    continue
                elif evento.key == pygame.K_F11 or (
                    evento.key == pygame.K_RETURN and evento.mod & pygame.KMOD_ALT
                ):
                    alternar_tela_cheia()
                    continue

            if estado == "menu":
                for botao in criar_botoes_menu():
                    if botao.clicou(evento):
                        estado = botao.acao
                        if estado == "criacao_personagem":
                            criacao = CriacaoPersonagem()
                            pygame.key.start_text_input()
                        elif estado == "historia":
                            nome = personagem_atual["nome"] if personagem_atual else "O herói"
                            introducao = IntroducaoHistoria(nome, PASTA_HISTORIA, carregar_fonte(24), fonte_botao, "menu")
                            estado = "introducao"

            elif estado == "criacao_personagem":
                acao = criacao.tratar_evento(evento)
                if acao == "menu":
                    estado = "menu"
                    pygame.key.stop_text_input()
                elif acao == "criar":
                    personagem = criacao.confirmar()
                    if personagem is not None:
                        personagem_atual = personagem
                        introducao = IntroducaoHistoria(personagem["nome"], PASTA_HISTORIA, carregar_fonte(24), fonte_botao)
                        estado = "introducao"
                        pygame.key.stop_text_input()

            elif estado == "introducao":
                destino = introducao.tratar_evento(evento, tamanho_tela())
                if destino:
                    estado = destino

            elif estado == "opcoes":
                for botao in criar_botoes_opcoes():
                    if botao.clicou(evento):
                        if botao.acao == "tela_cheia":
                            alternar_tela_cheia()
                        elif botao.acao == "som":
                            som_ligado = not som_ligado
                        else:
                            estado = botao.acao

            elif estado == "apoiar":
                for botao in criar_botoes_apoio():
                    if botao.clicou(evento):
                        if botao.acao == "menu":
                            estado = "menu"
                        else:
                            webbrowser.open(botao.acao)

            else:
                voltar = Botao("Voltar", (56, 330, 180, 42), "menu")
                if voltar.clicou(evento):
                    estado = "menu"

        if not rodando:
            break

        if estado == "introducao":
            destino = introducao.atualizar(tempo_frame)
            if destino:
                estado = destino

        desenhar_fundo()

        if estado == "menu":
            desenhar_menu()
        elif estado == "criacao_personagem":
            criacao.desenhar()
        elif estado == "introducao":
            introducao.desenhar(tela)
        elif estado == "personagem_criado":
            desenhar_pagina(
                "Personagem criado",
                [
                    f"Nome: {personagem_atual['nome']}",
                    f"Idade: {personagem_atual['idade']} anos",
                    f"Classe: {personagem_atual['classe']}",
                    "Personagem criado nesta sessão.",
                ],
            )
        elif estado == "opcoes":
            desenhar_opcoes()
        elif estado == "apoiar":
            desenhar_pagina(
                "Apoiar",
                [
                    "Se você gostou do jogo, considere apoiar o desenvolvedor!",
                ],
            )
            for botao in criar_botoes_apoio():
                botao.desenhar(tela)

        if estado != "introducao":
            desenhar_rodape()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    executar_jogo()
