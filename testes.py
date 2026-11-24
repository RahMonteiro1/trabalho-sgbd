
import interpretador as it


resultados = []


def verificar(rotulo, obtido, esperado):
    if obtido == esperado:
        print(f"Sucesso: {rotulo}")
        resultados.append(True)
    else:
        print(f"FALHA: {rotulo}")
        print(f"  Obtido:   {obtido}")
        print(f"  Esperado: {esperado}")
        resultados.append(False)


def verificar_erro(rotulo, comando):
    try:
        it.interpretar(comando)
        print(f"FALHA: {rotulo} - erro não identificado")
        resultados.append(False)

    except ValueError:
        print(f"Sucesso: {rotulo}")
        resultados.append(True)


def resumo():
    total = len(resultados)
    aprovados = sum(resultados)

    print("\n" + "=" * 45)
    print(f"{aprovados} de {total} testes passaram.")
    print("=" * 45)


def testar_select_simples():
    print("\n--- SELECT simples ---")

    verificar(
        "Selecionar todos os atributos",
        it.interpretar("SELECT * FROM alunos"),
        {
            "op": "SELECT",
            "colunas": [{"tipo": "*"}],
            "tabelas": ["alunos"],
            "where": [],
            "group_by": None
        }
    )

    verificar(
        "Selecionar um atributo",
        it.interpretar("SELECT nome FROM alunos"),
        {
            "op": "SELECT",
            "colunas": [{"tipo": "atb", "nome": "nome"}],
            "tabelas": ["alunos"],
            "where": [],
            "group_by": None
        }
    )

    verificar(
        "Selecionar vários atributos",
        it.interpretar("SELECT nome, idade FROM alunos"),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "atb", "nome": "nome"},
                {"tipo": "atb", "nome": "idade"}
            ],
            "tabelas": ["alunos"],
            "where": [],
            "group_by": None
        }
    )


def testar_atributos_qualificados():
    print("\n--- Atributos qualificados e múltiplas tabelas ---")

    verificar(
        "Atributos qualificados",
        it.interpretar(
            "SELECT alunos.nome, matriculas.nota "
            "FROM alunos, matriculas"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "atb", "nome": "alunos.nome"},
                {"tipo": "atb", "nome": "matriculas.nota"}
            ],
            "tabelas": ["alunos", "matriculas"],
            "where": [],
            "group_by": None
        }
    )

    verificar(
        "Três tabelas no FROM",
        it.interpretar(
            "SELECT alunos.nome "
            "FROM alunos, disciplinas, matriculas"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "atb", "nome": "alunos.nome"}
            ],
            "tabelas": ["alunos", "disciplinas", "matriculas"],
            "where": [],
            "group_by": None
        }
    )


def testar_where():
    print("\n--- WHERE ---")

    verificar(
        "Comparação entre atributo e constante",
        it.interpretar(
            "SELECT nome FROM alunos WHERE idade > 18"
        ),
        {
            "op": "SELECT",
            "colunas": [{"tipo": "atb", "nome": "nome"}],
            "tabelas": ["alunos"],
            "where": [[
                {
                    "esq": {"tipo": "atb", "nome": "idade"},
                    "op": ">",
                    "dir": {"tipo": "const", "valor": 18}
                }
            ]],
            "group_by": None
        }
    )

    verificar(
        "Comparação entre dois atributos",
        it.interpretar(
            "SELECT alunos.nome "
            "FROM alunos, matriculas "
            "WHERE alunos.matricula = matriculas.matricula"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "atb", "nome": "alunos.nome"}
            ],
            "tabelas": ["alunos", "matriculas"],
            "where": [[
                {
                    "esq": {"tipo": "atb", "nome": "alunos.matricula"},
                    "op": "=",
                    "dir": {"tipo": "atb", "nome": "matriculas.matricula"}
                }
            ]],
            "group_by": None
        }
    )

    verificar(
        "Duas condições ligadas por AND",
        it.interpretar(
            "SELECT nome FROM alunos "
            "WHERE idade > 18 AND idade < 25"
        ),
        {
            "op": "SELECT",
            "colunas": [{"tipo": "atb", "nome": "nome"}],
            "tabelas": ["alunos"],
            "where": [[
                {
                    "esq": {"tipo": "atb", "nome": "idade"},
                    "op": ">",
                    "dir": {"tipo": "const", "valor": 18}
                },
                {
                    "esq": {"tipo": "atb", "nome": "idade"},
                    "op": "<",
                    "dir": {"tipo": "const", "valor": 25}
                }
            ]],
            "group_by": None
        }
    )

    verificar(
        "Duas condições ligadas por OR",
        it.interpretar(
            "SELECT nome FROM alunos "
            "WHERE idade < 20 OR idade > 25"
        ),
        {
            "op": "SELECT",
            "colunas": [{"tipo": "atb", "nome": "nome"}],
            "tabelas": ["alunos"],
            "where": [
                [{
                    "esq": {"tipo": "atb", "nome": "idade"},
                    "op": "<",
                    "dir": {"tipo": "const", "valor": 20}
                }],
                [{
                    "esq": {"tipo": "atb", "nome": "idade"},
                    "op": ">",
                    "dir": {"tipo": "const", "valor": 25}
                }]
            ],
            "group_by": None
        }
    )

    verificar(
        "Precedência de AND sobre OR",
        it.interpretar(
            "SELECT nome FROM alunos "
            "WHERE idade > 18 AND idade < 25 OR idade = 30"
        ),
        {
            "op": "SELECT",
            "colunas": [{"tipo": "atb", "nome": "nome"}],
            "tabelas": ["alunos"],
            "where": [
                [
                    {
                        "esq": {"tipo": "atb", "nome": "idade"},
                        "op": ">",
                        "dir": {"tipo": "const", "valor": 18}
                    },
                    {
                        "esq": {"tipo": "atb", "nome": "idade"},
                        "op": "<",
                        "dir": {"tipo": "const", "valor": 25}
                    }
                ],
                [{
                    "esq": {"tipo": "atb", "nome": "idade"},
                    "op": "=",
                    "dir": {"tipo": "const", "valor": 30}
                }]
            ],
            "group_by": None
        }
    )

    verificar(
        "Comparação com constante textual",
        it.interpretar(
            "SELECT nome FROM alunos WHERE nome = 'Ana'"
        ),
        {
            "op": "SELECT",
            "colunas": [{"tipo": "atb", "nome": "nome"}],
            "tabelas": ["alunos"],
            "where": [[
                {
                    "esq": {"tipo": "atb", "nome": "nome"},
                    "op": "=",
                    "dir": {"tipo": "const", "valor": "Ana"}
                }
            ]],
            "group_by": None
        }
    )


def testar_agregacoes():
    print("\n--- Funções de agregação ---")

    verificar(
        "AVG",
        it.interpretar(
            "SELECT AVG(nota) FROM matriculas"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "agg", "funcao": "AVG", "nome": "nota"}
            ],
            "tabelas": ["matriculas"],
            "where": [],
            "group_by": None
        }
    )

    verificar(
        "MAX e MIN",
        it.interpretar(
            "SELECT MAX(nota), MIN(nota) FROM matriculas"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "agg", "funcao": "MAX", "nome": "nota"},
                {"tipo": "agg", "funcao": "MIN", "nome": "nota"}
            ],
            "tabelas": ["matriculas"],
            "where": [],
            "group_by": None
        }
    )

    verificar(
        "COUNT(*)",
        it.interpretar(
            "SELECT COUNT(*) FROM matriculas"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "agg", "funcao": "COUNT", "nome": None}
            ],
            "tabelas": ["matriculas"],
            "where": [],
            "group_by": None
        }
    )

    verificar(
        "COUNT de um atributo",
        it.interpretar(
            "SELECT COUNT(nota) FROM matriculas"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "agg", "funcao": "COUNT", "nome": "nota"}
            ],
            "tabelas": ["matriculas"],
            "where": [],
            "group_by": None
        }
    )


def testar_group_by():
    print("\n--- GROUP BY ---")

    verificar(
        "Agrupamento com COUNT",
        it.interpretar(
            "SELECT codigo_disciplina, COUNT(*) "
            "FROM matriculas GROUP BY codigo_disciplina"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "atb", "nome": "codigo_disciplina"},
                {"tipo": "agg", "funcao": "COUNT", "nome": None}
            ],
            "tabelas": ["matriculas"],
            "where": [],
            "group_by": "codigo_disciplina"
        }
    )

    verificar(
        "Múltiplas agregações com GROUP BY",
        it.interpretar(
            "SELECT codigo_disciplina, MIN(nota), MAX(nota), "
            "AVG(nota), COUNT(*) "
            "FROM matriculas GROUP BY codigo_disciplina"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "atb", "nome": "codigo_disciplina"},
                {"tipo": "agg", "funcao": "MIN", "nome": "nota"},
                {"tipo": "agg", "funcao": "MAX", "nome": "nota"},
                {"tipo": "agg", "funcao": "AVG", "nome": "nota"},
                {"tipo": "agg", "funcao": "COUNT", "nome": None}
            ],
            "tabelas": ["matriculas"],
            "where": [],
            "group_by": "codigo_disciplina"
        }
    )

    verificar(
        "WHERE combinado com GROUP BY",
        it.interpretar(
            "SELECT codigo_disciplina, AVG(nota) "
            "FROM matriculas WHERE nota > 7 "
            "GROUP BY codigo_disciplina"
        ),
        {
            "op": "SELECT",
            "colunas": [
                {"tipo": "atb", "nome": "codigo_disciplina"},
                {"tipo": "agg", "funcao": "AVG", "nome": "nota"}
            ],
            "tabelas": ["matriculas"],
            "where": [[
                {
                    "esq": {"tipo": "atb", "nome": "nota"},
                    "op": ">",
                    "dir": {"tipo": "const", "valor": 7}
                }
            ]],
            "group_by": "codigo_disciplina"
        }
    )


def testar_erros():
    print("\n--- Consultas inválidas ---")

    verificar_erro(
        "SELECT sem itens",
        "SELECT FROM alunos"
    )

    verificar_erro(
        "Agregação com * inválida",
        "SELECT AVG(*) FROM matriculas"
    )

    verificar_erro(
        "WHERE sem operando direito",
        "SELECT nome FROM alunos WHERE idade >"
    )

    verificar_erro(
        "GROUP BY sem atributo",
        "SELECT nome FROM alunos GROUP BY"
    )

    verificar_erro(
        "Termos excedentes",
        "SELECT nome FROM alunos extra"
    )


def testar_select():
    testar_select_simples()
    testar_atributos_qualificados()
    testar_where()
    testar_agregacoes()
    testar_group_by()
    testar_erros()


testar_select()
resumo()
