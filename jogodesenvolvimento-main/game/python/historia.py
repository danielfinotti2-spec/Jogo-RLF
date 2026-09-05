import pygame


CENAS_INTRODUCAO = [
    ("01_aldania.png", "O reino de Aldania",
     "(Name) nasceu em Aldania, um grande reino cercado por muralhas e governado por uma família real poderosa. "
     "Apesar da riqueza da cidade, ele cresceu em uma pequena casa na região mais pobre do reino."),
    ("02_familia.png", "Uma família humilde",
     "Sua mãe e seu pai mal conseguiam colocar comida na mesa. Mesmo assim, faziam de tudo para cuidar do filho."),
    ("03_acusacao.png", "A injustiça do rei",
     "Um dia, seu pai foi acusado injustamente pelo rei de um crime que não cometeu. "
     "Guardas o levaram diante de toda a cidade, enquanto (Name) e sua mãe assistiam sem poder fazer nada."),
    ("04_perda.png", "A perda",
     "Sem o pai e sem dinheiro, a situação da família piorou. A comida acabou e, algum tempo depois, "
     "sua mãe morreu de fome, deixando (Name) completamente sozinho."),
    ("05_mercado.png", "Sobrevivendo em Aldania",
     "Desde então, ainda muito jovem, ele passou a sobreviver trabalhando no centro de Aldania. "
     "Todos os dias, recolhe batatas caídas no mercado, recebendo algumas poucas moedas em troca."),
    ("06_jornada.jpg", "Uma lembrança que permanece",
     "Mas enquanto trabalha olhando para o enorme castelo ao longe, (Name) nunca esquece o que aconteceu "
     "com sua família — e muito menos o homem responsável por tudo."),
]


def quebrar_legenda(texto, fonte, largura):
    linhas = []
    linha = ""
    for palavra in texto.split():
        tentativa = f"{linha} {palavra}".strip()
        if linha and fonte.size(tentativa)[0] > largura:
            linhas.append(linha)
            linha = ""
        for letra in palavra:
            tentativa = linha + letra
            if linha and fonte.size(tentativa)[0] > largura:
                linhas.append(linha)
                linha = ""
            linha += letra
        linha += " "
    if linha.strip():
        linhas.append(linha.rstrip())
    return [linha.rstrip() for linha in linhas]


class IntroducaoHistoria:
    LETRAS_POR_SEGUNDO = 42

    def __init__(self, nome, pasta, fonte, fonte_controles, retorno="personagem_criado"):
        self.nome = nome
        self.pasta = pasta
        self.fonte = fonte
        self.fonte_controles = fonte_controles
        self.retorno = retorno
        self.indice = 0
        self.tempo = 0
        self.pausada = False
        self._imagem = None
        self._indice_imagem = None
        self._tamanho = None
        self._imagem_ajustada = None

    @property
    def legenda(self):
        return CENAS_INTRODUCAO[self.indice][2].replace("(Name)", self.nome)

    @property
    def tempo_digitacao(self):
        return len(self.legenda) * 1000 / self.LETRAS_POR_SEGUNDO

    @property
    def duracao(self):
        return self.tempo_digitacao + max(4000, len(self.legenda) * 35)

    def avancar(self):
        if self.indice == len(CENAS_INTRODUCAO) - 1:
            return self.retorno
        self.indice += 1
        self.tempo = 0
        return None

    def atualizar(self, milissegundos):
        if not self.pausada:
            self.tempo += max(0, milissegundos)
            if self.tempo >= self.duracao:
                return self.avancar()
        return None

    def botoes(self, tamanho):
        largura, altura = tamanho
        return [
            ("Anterior", pygame.Rect(40, altura - 58, 130, 38), "anterior"),
            ("Retomar" if self.pausada else "Pausar", pygame.Rect(184, altura - 58, 130, 38), "pausar"),
            ("Concluir" if self.indice == len(CENAS_INTRODUCAO) - 1 else "Próxima",
             pygame.Rect(largura - 314, altura - 58, 130, 38), "proxima"),
            ("Pular intro", pygame.Rect(largura - 170, altura - 58, 130, 38), "pular"),
        ]

    def tratar_evento(self, evento, tamanho):
        acao = None
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT):
                acao = "proxima"
            elif evento.key == pygame.K_LEFT:
                acao = "anterior"
            elif evento.key == pygame.K_p:
                acao = "pausar"
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            acao = next((acao for _, rect, acao in self.botoes(tamanho) if rect.collidepoint(evento.pos)), None)
        if acao == "pular":
            return self.retorno
        if acao == "pausar":
            self.pausada = not self.pausada
        elif acao == "anterior":
            self.indice = max(0, self.indice - 1)
            self.tempo = 0
        elif acao == "proxima":
            if self.tempo < self.tempo_digitacao:
                self.tempo = self.tempo_digitacao
            else:
                return self.avancar()
        return None

    def desenhar(self, tela):
        largura, altura = tela.get_size()
        if self._indice_imagem != self.indice:
            self._imagem = pygame.image.load(str(self.pasta / CENAS_INTRODUCAO[self.indice][0])).convert()
            self._indice_imagem = self.indice
            self._tamanho = None
        if self._tamanho != tela.get_size():
            fator = min(largura / self._imagem.get_width(), altura / self._imagem.get_height())
            tamanho = (max(1, round(self._imagem.get_width() * fator)), max(1, round(self._imagem.get_height() * fator)))
            self._imagem_ajustada = pygame.transform.scale(self._imagem, tamanho)
            self._tamanho = tela.get_size()
        tela.fill((0, 0, 0))
        tela.blit(self._imagem_ajustada, self._imagem_ajustada.get_rect(center=tela.get_rect().center))

        linhas = quebrar_legenda(self.legenda, self.fonte, largura - 96)
        passo = self.fonte.get_linesize() + 6
        altura_painel = len(linhas) * passo + 106
        topo = altura - altura_painel
        painel = pygame.Surface((largura, altura_painel), pygame.SRCALPHA)
        painel.fill((5, 8, 14, 225))
        tela.blit(painel, (0, topo))
        pygame.draw.line(tela, (181, 144, 80), (40, topo), (largura - 40, topo))
        visiveis = int(self.tempo * self.LETRAS_POR_SEGUNDO / 1000)
        for i, linha in enumerate(linhas):
            renderizado = self.fonte.render(linha[:max(0, visiveis)], True, (247, 239, 220))
            tela.blit(renderizado, (48, topo + 22 + i * passo))
            visiveis -= len(linha) + 1

        titulo = f"ALDANIA  ·  {self.indice + 1}/{len(CENAS_INTRODUCAO)}  ·  {CENAS_INTRODUCAO[self.indice][1]}"
        faixa = self.fonte_controles.render(titulo, True, (247, 239, 220))
        fundo_titulo = pygame.Surface((faixa.get_width() + 32, 42), pygame.SRCALPHA)
        fundo_titulo.fill((5, 8, 14, 210))
        tela.blit(fundo_titulo, (40, 24))
        tela.blit(faixa, (56, 35))
        for rotulo, rect, _ in self.botoes(tela.get_size()):
            cor = (50, 43, 31) if rect.collidepoint(pygame.mouse.get_pos()) else (21, 23, 28)
            pygame.draw.rect(tela, cor, rect, border_radius=3)
            pygame.draw.rect(tela, (126, 109, 78), rect, 1, border_radius=3)
            texto = self.fonte_controles.render(rotulo, True, (247, 239, 220))
            tela.blit(texto, texto.get_rect(center=rect.center))
        progresso = min(1, self.tempo / self.duracao)
        pygame.draw.rect(tela, (181, 144, 80), (0, altura - 3, round(largura * progresso), 3))
