# Contém os testes e as demonstrações do sistema
from modelos import Atributo, Tabela, Banco

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




# Executa uma operação e verifica se ela lança a exceção esperada.
def esperar_erro(rotulo, operacao, erro_esperado):
    try:
        operacao()
    except erro_esperado:
        verificar(rotulo, True, True)
    except Exception as erro:
        verificar(rotulo, type(erro).__name__, erro_esperado.__name__)
    else:
        verificar(rotulo, False, True)


# --------------------------------------------------
# PREPARAÇÃO
# --------------------------------------------------

sala = Banco("teste")

id_aluno = Atributo("id", "INTEGER", pk=True)
idade = Atributo("idade", "INTEGER")
nome = Atributo("nome", "STRING")
ativo = Atributo("ativo", "BOOLEAN")
nota = Atributo("nota", "FLOAT")

sala.criar_tabela(
    "alunos",
    [id_aluno, idade, nome, ativo, nota]
)

alunos = sala.tabelas["alunos"]


# --------------------------------------------------
# 1. CRIAÇÃO DE TABELAS
# --------------------------------------------------

verificar(
    "Criação de tabela válida",
    "alunos" in sala.tabelas,
    True
)

esperar_erro(
    "Impedir tabela duplicada",
    lambda: sala.criar_tabela("alunos", [id_aluno, nome]),
    ValueError
)

esperar_erro(
    "Impedir tabela sem PK",
    lambda: sala.criar_tabela(
        "sem_pk",
        [Atributo("nome", "STRING")]
    ),
    ValueError
)

esperar_erro(
    "Impedir tabela com duas PKs",
    lambda: sala.criar_tabela(
        "duas_pks",
        [
            Atributo("id", "INTEGER", pk=True),
            Atributo("codigo", "INTEGER", pk=True)
        ]
    ),
    ValueError
)

esperar_erro(
    "Impedir atributos com nomes duplicados",
    lambda: sala.criar_tabela(
        "atributos_duplicados",
        [
            Atributo("id", "INTEGER", pk=True),
            Atributo("id", "STRING")
        ]
    ),
    ValueError
)

esperar_erro(
    "Impedir tipo de atributo inválido",
    lambda: sala.criar_tabela(
        "tipo_invalido",
        [
            Atributo("id", "DATE", pk=True)
        ]
    ),
    TypeError
)


# --------------------------------------------------
# 2. LOCALIZAÇÃO DE ATRIBUTOS
# --------------------------------------------------

verificar(
    "Encontrar atributo existente",
    alunos.indice("nome"),
    2
)

esperar_erro(
    "Impedir busca por atributo inexistente",
    lambda: alunos.indice("inexistente"),
    ValueError
)


# --------------------------------------------------
# 3. INSERÇÃO DE REGISTROS
# --------------------------------------------------

verificar(
    "Inserção válida",
    sala.inserir("alunos", [1, 20, "Armando", True, 8]),
    [True]
)

verificar(
    "Conversão de INTEGER para FLOAT",
    type(alunos.registros[0][4]),
    float
)

verificar(
    "Preservar registros como lista de listas",
    isinstance(alunos.registros, list)
    and all(isinstance(r, list) for r in alunos.registros),
    True
)

esperar_erro(
    "Impedir inserção com PK repetida",
    lambda: sala.inserir("alunos", [1, 25, "Outro", True, 9]),
    ValueError
)

esperar_erro(
    "Impedir inserção com PK nula",
    lambda: sala.inserir("alunos", [None, 25, "Outro", True, 9]),
    ValueError
)

verificar(
    "Permitir None em atributo não-PK",
    sala.inserir("alunos", [2, None, None, False, None]),
    [True]
)


# --------------------------------------------------
# 4. COMPATIBILIDADE DE TIPOS
# --------------------------------------------------

esperar_erro(
    "Impedir texto em INTEGER",
    lambda: sala.inserir("alunos", [3, "vinte", "Ana", True, 8]),
    TypeError
)

esperar_erro(
    "Impedir FLOAT em INTEGER",
    lambda: sala.inserir("alunos", [3, 20.5, "Ana", True, 8]),
    TypeError
)

esperar_erro(
    "Impedir BOOLEAN em INTEGER",
    lambda: sala.inserir("alunos", [3, True, "Ana", True, 8]),
    TypeError
)

esperar_erro(
    "Impedir BOOLEAN em FLOAT",
    lambda: sala.inserir("alunos", [3, 20, "Ana", True, False]),
    TypeError
)

esperar_erro(
    "Impedir número em STRING",
    lambda: sala.inserir("alunos", [3, 20, 123, True, 8]),
    TypeError
)

esperar_erro(
    "Impedir INTEGER em BOOLEAN",
    lambda: sala.inserir("alunos", [3, 20, "Ana", 1, 8]),
    TypeError
)


# --------------------------------------------------
# 5. QUANTIDADE DE VALORES
# --------------------------------------------------

esperar_erro(
    "Impedir registro com valores insuficientes",
    lambda: sala.inserir("alunos", [3, 20, "Ana"]),
    ValueError
)

esperar_erro(
    "Impedir registro com valores excedentes",
    lambda: sala.inserir("alunos", [3, 20, "Ana", True, 8, "extra"]),
    ValueError
)


# --------------------------------------------------
# 6. VALORES DE BORDA
# --------------------------------------------------

verificar(
    "Aceitar INTEGER igual a zero",
    sala.inserir("alunos", [0, 0, "", False, 0]),
    [True]
)

verificar(
    "Preservar BOOLEAN False",
    alunos.registros[-1][3],
    False
)

verificar(
    "Preservar STRING vazia",
    alunos.registros[-1][2],
    ""
)

verificar(
    "Converter FLOAT zero corretamente",
    alunos.registros[-1][4],
    0.0
)


# --------------------------------------------------
# 7. TABELA INEXISTENTE
# --------------------------------------------------

esperar_erro(
    "Impedir inserção em tabela inexistente",
    lambda: sala.inserir("inexistente", [1]),
    ValueError
)


# --------------------------------------------------
# 8. INTEGRIDADE APÓS ERROS
# --------------------------------------------------

verificar(
    "Quantidade final de registros",
    len(alunos.registros),
    3
)

verificar(
    "PKs dos registros permanecem únicas",
    len([r[0] for r in alunos.registros])
    == len(set(r[0] for r in alunos.registros)),
    True
)


# --------------------------------------------------
# RESULTADO
# --------------------------------------------------

resumo()
