# Contém os testes e as demonstrações do sistema
total = list()

def verificar(rotulo, resultado, esperado):
    ok = resultado == esperado
    total.append(ok)
    
    if ok:
        print("Sucesso ", rotulo)
    else:
        print("Falha", resultado, "deveria ser ", esperado)
        
def resumo():
    print(sum(total), " de ", len(total), "testes passaram")


import unittest
import interpretador as it


# ============================================================
# 1. TESTES DO TOKENIZER
# ============================================================

class TestSepararTokens(unittest.TestCase):

    def test_comando_simples(self):
        resultado = it.separar_tokens("CREATE DATABASE universidade")
        esperado = [
            ("PAL", "CREATE"),
            ("PAL", "DATABASE"),
            ("PAL", "universidade")
        ]
        self.assertEqual(resultado, esperado)

    def test_parenteses_e_virgulas(self):
        resultado = it.separar_tokens("(1, 2, 3)")
        esperado = [
            ("SIM", "("),
            ("PAL", "1"),
            ("SIM", ","),
            ("PAL", "2"),
            ("SIM", ","),
            ("PAL", "3"),
            ("SIM", ")")
        ]
        self.assertEqual(resultado, esperado)

    def test_string_com_espacos(self):
        resultado = it.separar_tokens('"Ana Maria"')
        self.assertEqual(resultado, [("STR", "Ana Maria")])

    def test_numero_decimal(self):
        resultado = it.separar_tokens("8.5")
        self.assertEqual(resultado, [("PAL", "8.5")])

    def test_numero_negativo(self):
        resultado = it.separar_tokens("-10")
        self.assertEqual(resultado, [("PAL", "-10")])

    def test_string_nao_fechada(self):
        with self.assertRaises(ValueError):
            it.separar_tokens('"Ana Maria')


# ============================================================
# 2. TESTES DAS FUNCOES AUXILIARES
# ============================================================

class TestFuncoesAuxiliares(unittest.TestCase):

    def test_proximo(self):
        tokens = [("PAL", "CREATE"), ("PAL", "DATABASE")]
        resultado = it.proximo(tokens)

        self.assertEqual(resultado, ("PAL", "CREATE"))
        self.assertEqual(tokens, [("PAL", "DATABASE")])

    def test_proximo_lista_vazia(self):
        with self.assertRaises(ValueError):
            it.proximo([])

    def test_olhar(self):
        tokens = [("PAL", "CREATE")]
        resultado = it.olhar(tokens)

        self.assertEqual(resultado, ("PAL", "CREATE"))
        self.assertEqual(len(tokens), 1)

    def test_olhar_lista_vazia(self):
        self.assertIsNone(it.olhar([]))

    def test_esperar(self):
        tokens = [("PAL", "CREATE")]
        self.assertTrue(it.esperar(tokens, "CREATE"))
        self.assertEqual(tokens, [])

    def test_esperar_sem_diferenciar_maiusculas(self):
        tokens = [("PAL", "create")]
        self.assertTrue(it.esperar(tokens, "CREATE"))

    def test_esperar_palavra_incorreta(self):
        tokens = [("PAL", "INSERT")]

        with self.assertRaises(ValueError):
            it.esperar(tokens, "CREATE")


# ============================================================
# 3. TESTES DE CONVERSAO DE VALORES
# ============================================================

class TestLerValor(unittest.TestCase):

    def test_string(self):
        self.assertEqual(it.ler_valor(("STR", "Ana")), "Ana")

    def test_inteiro(self):
        self.assertEqual(it.ler_valor(("PAL", "25")), 25)

    def test_float(self):
        self.assertEqual(it.ler_valor(("PAL", "8.5")), 8.5)

    def test_booleanos(self):
        self.assertIs(it.ler_valor(("PAL", "TRUE")), True)
        self.assertIs(it.ler_valor(("PAL", "FALSE")), False)

    def test_booleanos_minusculos(self):
        self.assertIs(it.ler_valor(("PAL", "true")), True)
        self.assertIs(it.ler_valor(("PAL", "false")), False)

    def test_valor_invalido(self):
        with self.assertRaises(ValueError):
            it.ler_valor(("PAL", "abc"))

    def test_token_simbolo(self):
        with self.assertRaises(ValueError):
            it.ler_valor(("SIM", ","))


# ============================================================
# 4. TESTES DE IDENTIFICADORES
# ============================================================

class TestValidarIdentificador(unittest.TestCase):

    def test_identificadores_validos(self):
        validos = [
            "alunos",
            "alunos2026",
            "_alunos",
            "tabela_teste",
            "BancoDados"
        ]

        for nome in validos:
            with self.subTest(nome=nome):
                self.assertTrue(it.validar_identificador(nome))

    def test_identificadores_invalidos(self):
        invalidos = [
            "",
            "123alunos",
            "nome-tabela",
            "nome.tabela",
            "nome tabela"
        ]

        for nome in invalidos:
            with self.subTest(nome=nome):
                with self.assertRaises(ValueError):
                    it.validar_identificador(nome)


# ============================================================
# 5. TESTES DE CREATE DATABASE
# ============================================================

class TestInterpretarCreateDatabase(unittest.TestCase):

    def test_criacao_banco(self):
        resultado = it.interpretar(
            "CREATE DATABASE universidade"
        )

        esperado = {
            "op": "CREATE_DATABASE",
            "nome": "universidade"
        }

        self.assertEqual(resultado, esperado)

    def test_criacao_banco_minusculas(self):
        resultado = it.interpretar(
            "create database universidade"
        )

        self.assertEqual(resultado["op"], "CREATE_DATABASE")

    def test_sem_nome(self):
        with self.assertRaises(ValueError):
            it.interpretar("CREATE DATABASE")

    def test_com_termo_excedente(self):
        with self.assertRaises(ValueError):
            it.interpretar("CREATE DATABASE universidade extra")


# ============================================================
# 6. TESTES DE USE DATABASE
# ============================================================

class TestInterpretarUseDatabase(unittest.TestCase):

    def test_selecao_banco(self):
        resultado = it.interpretar(
            "USE DATABASE universidade"
        )

        esperado = {
            "op": "USE_DATABASE",
            "nome": "universidade"
        }

        self.assertEqual(resultado, esperado)

    def test_selecao_minusculas(self):
        resultado = it.interpretar(
            "use database universidade"
        )

        self.assertEqual(resultado["op"], "USE_DATABASE")

    def test_sem_nome(self):
        with self.assertRaises(ValueError):
            it.interpretar("USE DATABASE")

    def test_com_termo_excedente(self):
        with self.assertRaises(ValueError):
            it.interpretar("USE DATABASE universidade extra")


# ============================================================
# 7. TESTES DE CREATE TABLE
# ============================================================

class TestInterpretarCreateTable(unittest.TestCase):

    def test_criacao_tabela(self):
        comando = """
        CREATE TABLE alunos (
            matricula INTEGER PRIMARY KEY,
            nome STRING,
            idade INTEGER,
            media FLOAT
        )
        """

        resultado = it.interpretar(comando)

        esperado = {
            "op": "CREATE_TABLE",
            "nome": "alunos",
            "colunas": [
                {"nome": "matricula", "tipo": "INTEGER", "pk": True, "fk": None},
                {"nome": "nome", "tipo": "STRING", "pk": False, "fk": None},
                {"nome": "idade", "tipo": "INTEGER", "pk": False, "fk": None},
                {"nome": "media", "tipo": "FLOAT", "pk": False, "fk": None}
            ]
        }

        self.assertEqual(resultado, esperado)

    def test_criacao_tabela_minusculas(self):
        comando = """
        create table alunos (
            matricula integer primary key,
            nome string
        )
        """

        resultado = it.interpretar(comando)

        self.assertEqual(resultado["op"], "CREATE_TABLE")
        self.assertEqual(resultado["nome"], "alunos")
        self.assertTrue(resultado["colunas"][0]["pk"])

    def test_chave_estrangeira(self):
        comando = """
        CREATE TABLE matriculas (
            id INTEGER PRIMARY KEY,
            matricula INTEGER FOREIGN KEY REFERENCES alunos(matricula)
        )
        """

        resultado = it.interpretar(comando)

        esperado = ["alunos", "matricula"]

        self.assertEqual(
            resultado["colunas"][1]["fk"],
            esperado
        )

    def test_coluna_com_tipo_invalido(self):
        comando = """
        CREATE TABLE alunos (
            nome VARCHAR
        )
        """

        with self.assertRaises(ValueError):
            it.interpretar(comando)

    def test_coluna_sem_tipo(self):
        comando = """
        CREATE TABLE alunos (
            nome
        )
        """

        with self.assertRaises(ValueError):
            it.interpretar(comando)

    def test_tabela_sem_parenteses(self):
        with self.assertRaises(ValueError):
            it.interpretar(
                "CREATE TABLE alunos matricula INTEGER"
            )

    def test_tabela_sem_colunas(self):
        with self.assertRaises(ValueError):
            it.interpretar("CREATE TABLE alunos ()")

    def test_tabela_sem_nome(self):
        with self.assertRaises(ValueError):
            it.interpretar("CREATE TABLE (nome STRING)")

    def test_tabela_com_termo_excedente(self):
        comando = """
        CREATE TABLE alunos (
            nome STRING
        ) EXTRA
        """

        with self.assertRaises(ValueError):
            it.interpretar(comando)

    def test_fk_incompleta(self):
        comando = """
        CREATE TABLE matriculas (
            id INTEGER PRIMARY KEY,
            matricula INTEGER FOREIGN KEY REFERENCES
        )
        """

        with self.assertRaises((ValueError, IndexError)):
            it.interpretar(comando)


# ============================================================
# 8. TESTES DE INSERT
# ============================================================

class TestInterpretarInsert(unittest.TestCase):

    def test_insert_simples(self):
        resultado = it.interpretar(
            'INSERT INTO alunos VALUES (1001, "Ana", 22, 8.5)'
        )

        esperado = {
            "op": "INSERT",
            "tabela": "alunos",
            "valores": [1001, "Ana", 22, 8.5]
        }

        self.assertEqual(resultado, esperado)

    def test_insert_minusculas(self):
        resultado = it.interpretar(
            'insert into alunos values (1001, "Ana")'
        )

        self.assertEqual(resultado["op"], "INSERT")
        self.assertEqual(resultado["tabela"], "alunos")
        self.assertEqual(resultado["valores"], [1001, "Ana"])

    def test_insert_com_booleanos(self):
        resultado = it.interpretar(
            "INSERT INTO alunos VALUES (1, TRUE, FALSE)"
        )

        self.assertEqual(
            resultado["valores"],
            [1, True, False]
        )

    def test_insert_sem_tabela(self):
        with self.assertRaises(ValueError):
            it.interpretar("INSERT INTO VALUES (1)")

    def test_insert_sem_values(self):
        with self.assertRaises(ValueError):
            it.interpretar("INSERT INTO alunos (1)")

    def test_insert_sem_parenteses(self):
        with self.assertRaises(ValueError):
            it.interpretar("INSERT INTO alunos VALUES 1")

    def test_insert_com_virgula_excedente(self):
        with self.assertRaises(ValueError):
            it.interpretar("INSERT INTO alunos VALUES (1,)")

    def test_insert_com_valor_invalido(self):
        with self.assertRaises(ValueError):
            it.interpretar("INSERT INTO alunos VALUES (abc)")

    def test_insert_com_termo_excedente(self):
        with self.assertRaises(ValueError):
            it.interpretar("INSERT INTO alunos VALUES (1) extra")


# ============================================================
# 9. TESTES DA FUNCAO CENTRAL INTERPRETAR
# ============================================================

class TestInterpretarCentral(unittest.TestCase):

    def test_comando_vazio(self):
        with self.assertRaises(ValueError):
            it.interpretar("")

    def test_comando_apenas_espacos(self):
        with self.assertRaises(ValueError):
            it.interpretar("     ")

    def test_comando_desconhecido(self):
        with self.assertRaises(ValueError):
            it.interpretar("DELETE FROM alunos")

    def test_create_incompleto(self):
        with self.assertRaises(ValueError):
            it.interpretar("CREATE")

    def test_create_sem_tipo(self):
        with self.assertRaises(ValueError):
            it.interpretar("CREATE INDEX")

    def test_create_com_simbolo_no_segundo_token(self):
        with self.assertRaises(ValueError):
            it.interpretar("CREATE ( DATABASE teste")

    def test_use_incompleto(self):
        with self.assertRaises(ValueError):
            it.interpretar("USE")

    def test_insert_incompleto(self):
        with self.assertRaises(ValueError):
            it.interpretar("INSERT")


# ============================================================
# EXECUCAO
# ============================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
