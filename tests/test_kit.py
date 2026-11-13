import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pautas
import checa_sem_fonte

ROOT = Path(__file__).resolve().parents[1]
DADOS = ROOT / 'exemplos/dados-sintetico.json'


def video(**kw):
    v = dict(titulo='Tutorial fictício do zero', canal='Canal Inventado Alfa', channel_id='identidade_alfa', id='identificador_video', porte='pequeno', categoria='Conteúdo', fator_canal=3, views=1000, n_amostra=5, duracao=600, nichos=['chatgpt'], idade_h=24)
    v.update(kw)
    return v


class KitTests(unittest.TestCase):
    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / script), *map(str,args)], cwd=ROOT, text=True, capture_output=True)

    def test_filtro_limites_e_condicoes(self):
        self.assertEqual(len(pautas.filtrar([video()])), 1)
        for campo, valores in {'categoria':['Quem fala','Quem posta','Misto','Sem dados',None], 'porte':['grande',None], 'fator_canal':[2.99,None], 'views':[999,None], 'n_amostra':[4,None]}.items():
            for valor in valores:
                with self.subTest(campo=campo,valor=valor):
                    self.assertEqual(pautas.filtrar([video(**{campo:valor})]), [])
            v=video(); del v[campo]
            self.assertEqual(pautas.filtrar([v]), [])
        self.assertEqual(len(pautas.filtrar([video(porte='médio',categoria='Conteúdo + quem fala')])),1)
        self.assertEqual(pautas.filtrar([video()],piso_views=1001),[])
        self.assertEqual(pautas.filtrar([video()],fator=4),[])
        self.assertEqual(pautas.filtrar([video()],amostra=6),[])

    def test_temas(self):
        self.assertEqual(pautas.tema_de('AUTOMACAO')['rotulo'], 'automação e agentes')
        self.assertEqual(pautas.tema_de('quis construir')['rotulo'], 'geral do nicho')
        self.assertEqual(pautas.tema_de('UI: painel')['rotulo'], 'visual e interface')
        self.assertEqual(pautas.tema_de('um full course!')['rotulo'], 'curso ou guia completo do zero')
        self.assertTrue(pautas.tema_de('curso: fingi um teste')['evitar_sem_rosto'])
        self.assertTrue(pautas.tema_de('😱')['evitar_sem_rosto'])
        self.assertEqual(pautas.tema_de(None)['rotulo'], 'geral do nicho')

    def test_faixas(self):
        for segundos, indice in [(0,0),(479,0),(480,1),(1200,1),(1201,2),(3600,2),(3601,3),(None,4),(-1,4)]:
            self.assertEqual(pautas.faixa_de(segundos),pautas.FAIXAS[indice])

    def test_canais_e_nichos(self):
        vs=[video(nichos=['chatgpt','agentes de ia','chatgpt']),video(),video(channel_id='identidade_beta',canal='Canal Inventado Beta')]
        grupos=pautas.agrupar(vs)
        self.assertEqual(len(grupos),2)
        r=pautas.montar_pautas({'videos':vs})
        self.assertEqual(r['pautas'][0]['videos'],3)
        self.assertEqual(r['pautas'][0]['canais'],2)
        self.assertEqual(len(r['sinais_fracos']),1)
        self.assertEqual(pautas.canais_distintos([video(),video(channel_id=None)]),1)
        self.assertEqual(pautas.canais_distintos([video(canal=None,channel_id=None)]),0)
        self.assertEqual(pautas.agrupar([video(nichos=None)]),{})

    def test_fracos_humor_e_menos_de_n(self):
        r=pautas.montar_pautas({'videos':[video(),video(titulo='fingi uma conversa')]})
        self.assertEqual(r['pautas'],[])
        self.assertEqual(len(r['sinais_fracos']),1)
        self.assertEqual(len(r['fora_do_metodo']),1)
        self.assertIn('só 0 assuntos passaram',r['mensagem'])
        self.assertIn('Filtro:',pautas.render_md(r))

    def test_ordenacao_e_corte(self):
        vs=[]
        for nicho, canais, fator, views in [('A',3,3,1000),('B',2,9,1000),('C',2,4,2000),('D',2,4,1000)]:
            vs += [video(channel_id=f'canal_{i}',canal=f'Nome fictício {i}',nichos=[nicho],fator_canal=fator,views=views) for i in range(canais)]
        r=pautas.montar_pautas({'videos':vs},n=3)
        self.assertEqual([p['assunto'].rsplit(' ',1)[1] for p in r['pautas']],['A','B','C'])
        self.assertEqual(r['sinais_fracos'],[])

    def test_estatisticas(self):
        vs=[video(fator_canal=3,views=1000,idade_h=10,duracao=3900),video(channel_id='beta',fator_canal=7,views=3000,idade_h=30,duracao=4000)]
        p=pautas.montar_pautas({'videos':vs})['pautas'][0]
        self.assertEqual((p['fator_mediano'],p['fator_max'],p['views_somadas'],p['idade_mediana_h']),(5,7,4000,20))
        self.assertEqual(p['faixa_mais_comum'],pautas.FAIXAS[3])
        self.assertIn('capítulos',p['formato_sem_rosto'])

    def test_saida_forte_sem_fontes_e_detalhes(self):
        dados=pautas.carregar(DADOS)
        with tempfile.TemporaryDirectory() as tmp:
            proc=self.cli('pautas.py',DADOS,'--saida',tmp)
            self.assertEqual(proc.returncode,0,proc.stderr)
            publicos=[Path(tmp)/'pautas.md',Path(tmp)/'pautas.json']
            texto=proc.stdout+proc.stderr+''.join(p.read_text() for p in publicos)
            for v in dados['videos']:
                for campo in ['titulo','canal','id','channel_id','pessoa','descricao']:
                    self.assertNotIn(v[campo].casefold(),texto.casefold())
            self.assertEqual(checa_sem_fonte.verificar(dados,publicos),[])
            self.assertFalse((Path(tmp)/'detalhes-PRIVADO.md').exists())
            proc=self.cli('pautas.py',DADOS,'--saida',tmp,'--detalhes')
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn('não publique este arquivo',proc.stdout)
            privado=Path(tmp)/'detalhes-PRIVADO.md'
            self.assertIn(dados['videos'][0]['titulo'],privado.read_text())
            self.assertEqual(privado.stat().st_mode & 0o777,0o600)
            self.assertEqual(checa_sem_fonte.verificar(dados,[tmp]),[])

    def test_checker_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'teste.md'
            p.write_text('Um assunto com 3 canais.')
            proc=self.cli('checa_sem_fonte.py',DADOS,p)
            self.assertEqual(proc.returncode,0)
            self.assertIn('nenhuma fonte',proc.stdout)
            fonte=pautas.carregar(DADOS)['videos'][0]['titulo']
            p.write_text('limpo\n'+fonte.upper())
            proc=self.cli('checa_sem_fonte.py',DADOS,p)
            self.assertEqual(proc.returncode,1)
            self.assertIn(':2:',proc.stdout)
            self.assertNotIn(fonte.casefold(),proc.stdout.casefold())
            p.write_text('Canal Fictício')
            self.assertEqual(self.cli('checa_sem_fonte.py',DADOS,p).returncode,0)
            (Path(tmp)/'.git').mkdir()
            (Path(tmp)/'.git'/'privado.md').write_text(fonte)
            self.assertEqual(self.cli('checa_sem_fonte.py',DADOS,tmp).returncode,0)

    def test_comuns(self):
        self.assertEqual(checa_sem_fonte.termos_de({'videos':[dict(canal='curso',titulo='automação',id='abc',pessoa='sobre')]}),set())

    def test_faltantes_e_nulos(self):
        r=pautas.montar_pautas({'videos':[{},video(porte=None),video(fator_canal=None)],'porque':None})
        self.assertEqual(r['pautas'],[])
        self.assertEqual(r['gerado_em'],'sem data')
        r=pautas.montar_pautas({'videos':[video(duracao=None,idade_h=None),video(channel_id='beta',duracao=None,idade_h=None)]})
        self.assertIsNone(r['pautas'][0]['idade_mediana_h'])

    def test_inexistente_e_json_invalido(self):
        self.assertEqual(self.cli('pautas.py','/tmp/caminho-que-nao-existe-dados-725.json').returncode,2)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'dados.json'; p.write_text('{"titulo secreto":')
            proc=self.cli('pautas.py',p)
            self.assertEqual(proc.returncode,2)
            self.assertNotIn('titulo secreto',proc.stderr)

    def test_nicho_nao_vaza_fonte(self):
        v=video(nichos=['Canal Inventado Alfa'])
        r=pautas.montar_pautas({'videos':[v]})
        self.assertNotIn('Canal Inventado Alfa',json.dumps(r,ensure_ascii=False))

    def test_canal_com_nome_de_produto_nao_apaga_o_nicho(self):
        # Um canal chamado só "Produto" não pode mascarar o nicho "produto code" (o nicho é do usuário).
        vs=[video(id=f'v{i}',canal='Produto',channel_id=f'c{i}',nichos=['produto code']) for i in range(2)]
        vs[1]['canal']='Outro Canal Beta'
        r=pautas.montar_pautas({'videos':vs})
        texto=json.dumps(r,ensure_ascii=False)
        self.assertIn('produto code',texto)
        self.assertNotIn('Outro Canal Beta',texto)

    def test_pt_br(self):
        self.assertEqual(pautas.br(1234),'1.234')
        self.assertEqual(pautas.br(5.1,1),'5,1')
        r=pautas.montar_pautas(pautas.carregar(DADOS))
        self.assertIn('63,0%',pautas.render_md(r))


if __name__ == '__main__':
    unittest.main()
