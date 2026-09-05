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
from historia import CENAS_INTRODUCAO, IntroducaoHistoria, quebrar_legenda


class HistoriaTests(unittest.TestCase):
    def setUp(self):
        jogo.preparar_janela()
        self.intro = IntroducaoHistoria("Éowyn", jogo.PASTA_HISTORIA, jogo.carregar_fonte(24), jogo.fonte_botao)

    def tearDown(self):
        pygame.quit()

    def test_imagens_legendas_e_nome_em_todas_as_cenas(self):
        for tamanho in ((1280, 720), (1024, 768)):
            jogo.tela = pygame.display.set_mode(tamanho)
            for indice, (arquivo, _, texto) in enumerate(CENAS_INTRODUCAO):
                self.intro.indice = indice
                self.intro.tempo = self.intro.tempo_digitacao + 100
                self.intro.desenhar(jogo.tela)
                self.assertTrue((jogo.PASTA_HISTORIA / arquivo).is_file())
                self.assertNotIn("(Name)", self.intro.legenda)
                if "(Name)" in texto:
                    self.assertIn("Éowyn", self.intro.legenda)
                linhas = quebrar_legenda(self.intro.legenda, self.intro.fonte, tamanho[0] - 96)
                self.assertEqual(" ".join(linhas), self.intro.legenda)
                for linha in linhas:
                    self.assertLessEqual(self.intro.fonte.size(linha)[0], tamanho[0] - 96)
                self.assertLess(len(linhas) * (self.intro.fonte.get_linesize() + 6) + 106, tamanho[1] // 2)

    def test_reproducao_automatica_ate_ficha(self):
        for indice in range(len(CENAS_INTRODUCAO)):
            self.assertEqual(self.intro.indice, indice)
            self.assertIsNone(self.intro.atualizar(self.intro.duracao - 1))
            resultado = self.intro.atualizar(1)
        self.assertEqual(resultado, "personagem_criado")

    def test_pausa_avanco_retorno_e_pular(self):
        def tecla(key):
            return self.intro.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=key), (1280, 720))
        tecla(pygame.K_p)
        self.intro.atualizar(999999)
        self.assertEqual(self.intro.tempo, 0)
        tecla(pygame.K_SPACE)
        self.assertEqual(self.intro.indice, 0)
        self.assertEqual(self.intro.tempo, self.intro.tempo_digitacao)
        tecla(pygame.K_SPACE)
        self.assertEqual(self.intro.indice, 1)
        tecla(pygame.K_LEFT)
        self.assertEqual(self.intro.indice, 0)
        tecla(pygame.K_p)
        self.assertFalse(self.intro.pausada)
        pular = next(rect for _, rect, acao in self.intro.botoes((1280, 720)) if acao == "pular")
        resultado = self.intro.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pular.center), (1280, 720))
        self.assertEqual(resultado, "personagem_criado")

    def test_menu_historia_volta_ao_menu(self):
        frames = iter([
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(70, 260))],
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(1170, 680))],
            [pygame.event.Event(pygame.QUIT)],
        ])
        estados = []
        with patch.object(pygame.event, "get", side_effect=lambda: next(frames)), \
             patch.object(pygame.display, "flip", side_effect=lambda: estados.append(jogo.estado)):
            jogo.executar_jogo()
        self.assertEqual(estados, ["introducao", "menu"])


if __name__ == "__main__":
    unittest.main()
