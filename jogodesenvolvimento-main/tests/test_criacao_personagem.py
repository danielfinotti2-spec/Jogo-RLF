import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "game" / "python"))

import pygame
import joguinhoonline as jogo


def clique(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)


def tecla(key, mod=0):
    return pygame.event.Event(pygame.KEYDOWN, key=key, mod=mod)


def texto(valor):
    return pygame.event.Event(pygame.TEXTINPUT, text=valor)


class CriacaoPersonagemTests(unittest.TestCase):
    def setUp(self):
        jogo.preparar_janela()
        self.form = jogo.CriacaoPersonagem()

    def tearDown(self):
        pygame.quit()

    def test_validacao_dos_campos_obrigatorios(self):
        self.assertIsNone(self.form.confirmar())
        self.form.valores["nome"] = "   "
        self.assertIsNone(self.form.confirmar())
        self.form.valores["nome"] = " Éowyn "
        for idade in ("", "0", "17", "-1", "abc", "1000"):
            self.form.valores["idade"] = idade
            self.assertIsNone(self.form.confirmar())
        self.form.valores["idade"] = "27"
        self.assertIsNone(self.form.confirmar())
        self.form.classe = ("Guerreiro", "")
        self.assertEqual(self.form.confirmar(), {"nome": "Éowyn", "idade": 27, "classe": "Guerreiro"})

    def test_idade_minima_mesmo_com_classe_selecionada(self):
        self.form.valores["nome"] = "Arthur"
        self.form.classe = jogo.CLASSES_PERSONAGEM[0]
        for idade in range(18):
            self.form.valores["idade"] = str(idade)
            self.assertIsNone(self.form.confirmar())
        self.form.valores["idade"] = "18"
        self.assertEqual(self.form.confirmar()["idade"], 18)

    def test_digitacao_tab_backspace_e_busca_sem_acentos(self):
        for evento in (texto("João"), tecla(pygame.K_TAB), texto("2a7")):
            self.form.tratar_evento(evento)
        self.assertEqual(self.form.valores["nome"], "João")
        self.assertEqual(self.form.valores["idade"], "27")
        self.form.tratar_evento(tecla(pygame.K_BACKSPACE))
        self.assertEqual(self.form.valores["idade"], "2")
        self.form.tratar_evento(tecla(pygame.K_TAB))
        self.form.tratar_evento(texto("clerigo"))
        self.assertEqual([c[0] for c in self.form.classes_filtradas()], ["Clérigo"])
        self.form.tratar_evento(tecla(pygame.K_TAB, pygame.KMOD_SHIFT))
        self.assertEqual(self.form.campo_ativo, "idade")

    def test_todas_as_classes_sao_acessiveis_e_selecao_persiste(self):
        vistos = []
        _, total = self.form.paginacao()
        for pagina in range(total):
            self.form.pagina = pagina
            for botao in self.form.botoes_classes():
                vistos.append(botao.acao)
                self.form.tratar_evento(clique(botao.rect.center))
                self.assertEqual(self.form.classe[0], botao.acao)
        self.assertEqual(vistos, [c[0] for c in jogo.CLASSES_PERSONAGEM])
        selecionada = self.form.classe
        self.form.valores["busca"] = "classe inexistente"
        self.assertEqual(self.form.paginacao(), ([], 1))
        self.assertEqual(self.form.classe, selecionada)
        self.form.desenhar()

    def test_layout_em_janela_e_tela_menor(self):
        for tamanho in ((1280, 720), (1024, 768)):
            jogo.tela = pygame.display.set_mode(tamanho)
            botoes = self.form.botoes_classes() + self.form.botoes_acoes()
            for indice, botao in enumerate(botoes):
                self.assertTrue(jogo.tela.get_rect().contains(botao.rect))
                for outro in botoes[indice + 1:]:
                    self.assertFalse(botao.rect.colliderect(outro.rect))
            self.form.desenhar()

    def test_fluxo_novo_jogo_ate_ficha_e_reinicio(self):
        frames = iter([
            [clique((70, 200))],
            [texto("Éowyn"), tecla(pygame.K_TAB), texto("27"), tecla(pygame.K_TAB), texto("paladino")],
            [clique((450, 260))],
            [clique((250, 600))],
            [clique((1170, 680))],
            [clique((70, 345))],
            [clique((70, 200))],
            [tecla(pygame.K_RETURN)],
            [tecla(pygame.K_ESCAPE)],
            [pygame.event.Event(pygame.QUIT)],
        ])
        estados = []
        desenhos = jogo.CriacaoPersonagem.desenhar
        formularios = []

        def registrar_formulario(form):
            formularios.append(dict(form.valores))
            desenhos(form)

        def atualizar():
            estados.append(jogo.estado)

        with patch.object(pygame.event, "get", side_effect=lambda: next(frames)), \
             patch.object(pygame.display, "flip", side_effect=atualizar), \
             patch.object(jogo.CriacaoPersonagem, "desenhar", registrar_formulario), \
             patch.object(jogo.webbrowser, "open") as navegador:
            jogo.executar_jogo()
        self.assertIn("personagem_criado", estados)
        self.assertIn("introducao", estados)
        self.assertEqual(jogo.personagem_atual, {"nome": "Éowyn", "idade": 27, "classe": "Paladino"})
        self.assertEqual(formularios[-1], {"nome": "", "idade": "", "busca": ""})
        self.assertEqual(jogo.estado, "menu")
        self.assertFalse(pygame.get_init())
        navegador.assert_not_called()


if __name__ == "__main__":
    unittest.main()
