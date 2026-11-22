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

# ====================================================================== #


from sistema import Sistema


def testar_dia_20():
    # Testa a autenticação, a execução de comandos e a integração dos módulos.
    sistema = Sistema()

    # 1. Autenticação
    verificar(
        "Consulta sem usuário logado",
        sistema.consulta("CREATE DATABASE universidade"),
        [False]
    )

    verificar(
        "Login com senha incorreta",
        sistema.login("Admin", "senha_errada"),
        False
    )

    verificar(
        "Login do administrador",
        sistema.login("Admin", "123456"),
        True
    )

    # 2. Criação e seleção do banco
    verificar(
        "Criação do banco universidade",
        sistema.consulta("CREATE DATABASE universidade"),
        [True]
    )

    verificar(
        "Criação de banco duplicado",
        sistema.consulta("CREATE DATABASE universidade"),
        [False]
    )

    verificar(
        "Seleção do banco universidade",
        sistema.consulta("USE DATABASE universidade"),
        [True]
    )

    # 3. Criação das tabelas (exemplo 4.1)
    comandos_criacao = [
        (
            "Criação da tabela alunos",
            """
            CREATE TABLE alunos (
                matricula INTEGER PRIMARY KEY,
                nome STRING,
                idade INTEGER,
                media FLOAT
            )
            """
        ),
        (
            "Criação da tabela disciplinas",
            """
            CREATE TABLE disciplinas (
                codigo INTEGER PRIMARY KEY,
                nome STRING,
                creditos INTEGER
            )
            """
        ),
        (
            "Criação da tabela matriculas",
            """
            CREATE TABLE matriculas (
                id INTEGER PRIMARY KEY,
                matricula INTEGER FOREIGN KEY REFERENCES alunos(matricula),
                codigo_disciplina INTEGER FOREIGN KEY REFERENCES disciplinas(codigo),
                nota FLOAT
            )
            """
        )
    ]

    for rotulo, comando in comandos_criacao:
        verificar(rotulo, sistema.consulta(comando), [True])

    # 4. Inserção dos registros (exemplo 4.2)
    comandos_insercao = [
        ('INSERT INTO alunos VALUES (1001, "Ana", 22, 8.5)',
         "Inserção de Ana"),

        ('INSERT INTO alunos VALUES (1002, "Carlos", 25, 7.0)',
         "Inserção de Carlos"),

        ('INSERT INTO alunos VALUES (1003, "Maria", 19, 9.2)',
         "Inserção de Maria"),

        ('INSERT INTO disciplinas VALUES (1, "Programacao", 4)',
         "Inserção de Programacao"),

        ('INSERT INTO disciplinas VALUES (2, "Banco de Dados", 4)',
         "Inserção de Banco de Dados"),

        ('INSERT INTO matriculas VALUES (1, 1001, 1, 9.0)',
         "Inserção da matrícula 1"),

        ('INSERT INTO matriculas VALUES (2, 1001, 2, 8.0)',
         "Inserção da matrícula 2"),

        ('INSERT INTO matriculas VALUES (3, 1002, 1, 7.0)',
         "Inserção da matrícula 3"),

        ('INSERT INTO matriculas VALUES (4, 1003, 2, 9.5)',
         "Inserção da matrícula 4")
    ]

    for comando, rotulo in comandos_insercao:
        verificar(rotulo, sistema.consulta(comando), [True])

    # 5. Verificação do estado interno
    verificar(
        "Quantidade de bancos",
        len(sistema.bancos),
        1
    )

    verificar(
        "Quantidade de tabelas",
        len(sistema.bc_atual.tabelas),
        3
    )

    verificar(
        "Quantidade de alunos",
        len(sistema.bc_atual.tabelas["alunos"].registros),
        3
    )

    verificar(
        "Quantidade de disciplinas",
        len(sistema.bc_atual.tabelas["disciplinas"].registros),
        2
    )

    verificar(
        "Quantidade de matrículas",
        len(sistema.bc_atual.tabelas["matriculas"].registros),
        4
    )

    # 6. Encerramento da sessão
    verificar(
        "Logout",
        sistema.logout(),
        True
    )

    verificar(
        "Consulta após logout",
        sistema.consulta("USE DATABASE universidade"),
        [False]
    )


testar_dia_20()
resumo()

