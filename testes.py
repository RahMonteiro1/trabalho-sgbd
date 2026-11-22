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
    print(sum(total), "de", len(total), "testes passaram")


print("\n========== 21. CHAVES ESTRANGEIRAS ==========\n")

from sistema import Sistema

sistema_fk = Sistema()

print("\n--- 21.1. O óbvio ---")

verificar("Login do administrador",
          sistema_fk.login("Admin", "123456"), True)

verificar("Criar banco universidade_fk",
          sistema_fk.consulta("CREATE DATABASE universidade_fk"), [True])

verificar("Selecionar banco universidade_fk",
          sistema_fk.consulta("USE DATABASE universidade_fk"), [True])

verificar("Criar tabela alunos",
          sistema_fk.consulta("""
              CREATE TABLE alunos (
                  matricula INTEGER PRIMARY KEY,
                  nome STRING,
                  idade INTEGER
              )
          """), [True])

verificar("Criar tabela disciplinas",
          sistema_fk.consulta("""
              CREATE TABLE disciplinas (
                  codigo INTEGER PRIMARY KEY,
                  nome STRING
              )
          """), [True])

verificar("Criar tabela matriculas com duas FKs",
          sistema_fk.consulta("""
              CREATE TABLE matriculas (
                  id INTEGER PRIMARY KEY,
                  matricula INTEGER FOREIGN KEY REFERENCES alunos(matricula),
                  codigo_disciplina INTEGER FOREIGN KEY REFERENCES disciplinas(codigo),
                  nota FLOAT
              )
          """), [True])

verificar("Inserir aluno 1001",
          sistema_fk.consulta('INSERT INTO alunos VALUES (1001, "Ana", 22)'),
          [True])

verificar("Inserir aluno 1002",
          sistema_fk.consulta('INSERT INTO alunos VALUES (1002, "Carlos", 25)'),
          [True])

verificar("Inserir aluno 1003",
          sistema_fk.consulta('INSERT INTO alunos VALUES (1003, "Maria", 19)'),
          [True])

verificar("Inserir disciplina 1",
          sistema_fk.consulta('INSERT INTO disciplinas VALUES (1, "Programacao")'),
          [True])

verificar("Inserir disciplina 2",
          sistema_fk.consulta('INSERT INTO disciplinas VALUES (2, "Banco de Dados")'),
          [True])

verificar("Inserir matrícula com as duas FKs válidas",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (1, 1001, 1, 9.0)'),
          [True])

verificar("Inserir matrícula usando outros registros existentes",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (2, 1003, 2, 8.5)'),
          [True])

print("\n--- 21.2. O esperado ---")

verificar("Rejeitar FK para tabela inexistente",
          sistema_fk.consulta("""
              CREATE TABLE teste_tabela_inexistente (
                  id INTEGER PRIMARY KEY,
                  referencia INTEGER FOREIGN KEY REFERENCES fantasma(id)
              )
          """), [False])

verificar("Rejeitar FK para atributo inexistente",
          sistema_fk.consulta("""
              CREATE TABLE teste_atributo_inexistente (
                  id INTEGER PRIMARY KEY,
                  referencia INTEGER FOREIGN KEY REFERENCES alunos(codigo)
              )
          """), [False])

verificar("Rejeitar FK que aponta para atributo não PK",
          sistema_fk.consulta("""
              CREATE TABLE teste_atributo_nao_pk (
                  id INTEGER PRIMARY KEY,
                  referencia STRING FOREIGN KEY REFERENCES alunos(nome)
              )
          """), [False])

verificar("Rejeitar FK com tipo diferente do atributo referenciado",
          sistema_fk.consulta("""
              CREATE TABLE teste_tipo_diferente (
                  id INTEGER PRIMARY KEY,
                  referencia STRING FOREIGN KEY REFERENCES alunos(matricula)
              )
          """), [False])

verificar("Rejeitar inserção com matrícula inexistente (9999)",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (3, 9999, 1, 7.0)'),
          [False])

verificar("Rejeitar inserção com disciplina inexistente",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (3, 1001, 999, 7.0)'),
          [False])

verificar("Rejeitar PK repetida na tabela matriculas",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (1, 1002, 2, 8.0)'),
          [False])

verificar("Rejeitar PK repetida na tabela alunos (1001)",
          sistema_fk.consulta('INSERT INTO alunos VALUES (1001, "Pedro", 30)'),
          [False])

print("\n--- 21.3. Casos de borda ---")

verificar("Rejeitar tabela que referencia a si mesma",
          sistema_fk.consulta("""
              CREATE TABLE categorias (
                  id INTEGER PRIMARY KEY,
                  superior INTEGER FOREIGN KEY REFERENCES categorias(id)
              )
          """), [False])

verificar("Criar tabela independente para testar referência vazia",
          sistema_fk.consulta("""
              CREATE TABLE orientadores (
                  id INTEGER PRIMARY KEY,
                  nome STRING
              )
          """), [True])

verificar("Criar tabela dependente de orientadores",
          sistema_fk.consulta("""
              CREATE TABLE projetos (
                  id INTEGER PRIMARY KEY,
                  orientador INTEGER FOREIGN KEY REFERENCES orientadores(id)
              )
          """), [True])

verificar("Rejeitar FK quando a tabela referenciada está vazia",
          sistema_fk.consulta('INSERT INTO projetos VALUES (1, 50)'),
          [False])

verificar("Inserir registro na tabela referenciada",
          sistema_fk.consulta('INSERT INTO orientadores VALUES (50, "Joao")'),
          [True])

verificar("Aceitar FK após cadastrar o registro referenciado",
          sistema_fk.consulta('INSERT INTO projetos VALUES (1, 50)'),
          [True])

verificar("Aceitar inserção em tabela sem FK",
          sistema_fk.consulta('INSERT INTO orientadores VALUES (51, "Marina")'),
          [True])

print("\n--- 21.4. Exemplos mais complexos ---")

verificar("Aceitar registro com primeira FK válida e segunda FK válida",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (4, 1002, 1, 8.0)'),
          [True])

verificar("Rejeitar registro com primeira FK inválida e segunda válida",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (5, 9999, 1, 7.0)'),
          [False])

verificar("Rejeitar registro com primeira FK válida e segunda inválida",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (5, 1001, 999, 7.0)'),
          [False])

verificar("Aceitar PK 5 após tentativas anteriores rejeitadas",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (5, 1003, 2, 9.5)'),
          [True])

verificar("Aceitar FK que referencia o último registro da tabela",
          sistema_fk.consulta('INSERT INTO matriculas VALUES (6, 1003, 1, 8.5)'),
          [True])

print("\n21.5 — Exemplos oficiais do roteiro")

sistema_exemplos = Sistema()

verificar(
    "Login do administrador",
    sistema_exemplos.login("Admin", "123456"),
    True
)

verificar(
    "4.1 - Criar banco universidade",
    sistema_exemplos.consulta("CREATE DATABASE universidade"),
    [True]
)

verificar(
    "4.1 - Selecionar banco universidade",
    sistema_exemplos.consulta("USE DATABASE universidade"),
    [True]
)

verificar(
    "4.1 - Criar tabela alunos",
    sistema_exemplos.consulta("""
        CREATE TABLE alunos (
            matricula INTEGER PRIMARY KEY,
            nome STRING,
            idade INTEGER,
            media FLOAT
        )
    """),
    [True]
)

verificar(
    "4.1 - Criar tabela disciplinas",
    sistema_exemplos.consulta("""
        CREATE TABLE disciplinas (
            codigo INTEGER PRIMARY KEY,
            nome STRING,
            creditos INTEGER
        )
    """),
    [True]
)

verificar(
    "4.1 - Criar tabela matriculas com duas FKs",
    sistema_exemplos.consulta("""
        CREATE TABLE matriculas (
            id INTEGER PRIMARY KEY,
            matricula INTEGER FOREIGN KEY REFERENCES alunos(matricula),
            codigo_disciplina INTEGER FOREIGN KEY REFERENCES disciplinas(codigo),
            nota FLOAT
        )
    """),
    [True]
)

verificar(
    "4.2 - Inserir Ana em alunos",
    sistema_exemplos.consulta(
        'INSERT INTO alunos VALUES (1001, "Ana", 22, 8.5)'
    ),
    [True]
)

verificar(
    "4.2 - Inserir Carlos em alunos",
    sistema_exemplos.consulta(
        'INSERT INTO alunos VALUES (1002, "Carlos", 25, 7.0)'
    ),
    [True]
)

verificar(
    "4.2 - Inserir Maria em alunos",
    sistema_exemplos.consulta(
        'INSERT INTO alunos VALUES (1003, "Maria", 19, 9.2)'
    ),
    [True]
)

verificar(
    "4.2 - Inserir Programacao em disciplinas",
    sistema_exemplos.consulta(
        'INSERT INTO disciplinas VALUES (1, "Programacao", 4)'
    ),
    [True]
)

verificar(
    "4.2 - Inserir Banco de Dados em disciplinas",
    sistema_exemplos.consulta(
        'INSERT INTO disciplinas VALUES (2, "Banco de Dados", 4)'
    ),
    [True]
)

verificar(
    "4.2 - Inserir primeira matrícula",
    sistema_exemplos.consulta(
        "INSERT INTO matriculas VALUES (1, 1001, 1, 9.0)"
    ),
    [True]
)

verificar(
    "4.2 - Inserir segunda matrícula",
    sistema_exemplos.consulta(
        "INSERT INTO matriculas VALUES (2, 1001, 2, 8.0)"
    ),
    [True]
)

verificar(
    "4.2 - Inserir terceira matrícula",
    sistema_exemplos.consulta(
        "INSERT INTO matriculas VALUES (3, 1002, 1, 7.0)"
    ),
    [True]
)

verificar(
    "4.2 - Inserir quarta matrícula",
    sistema_exemplos.consulta(
        "INSERT INTO matriculas VALUES (4, 1003, 2, 9.5)"
    ),
    [True]
)

# 21.6 - Compatibilidade entre tipos numéricos

sistema_compatibilidade = Sistema()

sistema_compatibilidade.login("Admin", "123456")
sistema_compatibilidade.consulta("CREATE DATABASE compatibilidade")
sistema_compatibilidade.consulta("USE DATABASE compatibilidade")


# 1. INTEGER -> INTEGER: deve aceitar
verificar(
    "INTEGER referenciando INTEGER",
    sistema_compatibilidade.consulta("""
        CREATE TABLE pai_int (
            id INTEGER PRIMARY KEY
        )
    """),
    [True]
)

verificar(
    "FK INTEGER referenciando PK INTEGER",
    sistema_compatibilidade.consulta("""
        CREATE TABLE filho_int (
            id INTEGER PRIMARY KEY,
            referencia INTEGER FOREIGN KEY REFERENCES pai_int(id)
        )
    """),
    [True]
)


# 2. FLOAT -> FLOAT: deve aceitar
verificar(
    "FLOAT referenciando FLOAT",
    sistema_compatibilidade.consulta("""
        CREATE TABLE pai_float (
            id FLOAT PRIMARY KEY
        )
    """),
    [True]
)

verificar(
    "FK FLOAT referenciando PK FLOAT",
    sistema_compatibilidade.consulta("""
        CREATE TABLE filho_float (
            id INTEGER PRIMARY KEY,
            referencia FLOAT FOREIGN KEY REFERENCES pai_float(id)
        )
    """),
    [True]
)


# 3. FK FLOAT -> PK INTEGER: deve aceitar
verificar(
    "FK FLOAT referenciando PK INTEGER",
    sistema_compatibilidade.consulta("""
        CREATE TABLE filho_float_int (
            id INTEGER PRIMARY KEY,
            referencia FLOAT FOREIGN KEY REFERENCES pai_int(id)
        )
    """),
    [True]
)


# 4. FK INTEGER -> PK FLOAT: deve aceitar
verificar(
    "FK INTEGER referenciando PK FLOAT",
    sistema_compatibilidade.consulta("""
        CREATE TABLE filho_int_float (
            id INTEGER PRIMARY KEY,
            referencia INTEGER FOREIGN KEY REFERENCES pai_float(id)
        )
    """),
    [True]
)


# 5. STRING -> INTEGER: deve rejeitar
verificar(
    "FK STRING referenciando PK INTEGER",
    sistema_compatibilidade.consulta("""
        CREATE TABLE filho_string_int (
            id INTEGER PRIMARY KEY,
            referencia STRING FOREIGN KEY REFERENCES pai_int(id)
        )
    """),
    [False]
)


# 6. INTEGER -> STRING: deve rejeitar
verificar(
    "FK INTEGER referenciando PK STRING",
    sistema_compatibilidade.consulta("""
        CREATE TABLE pai_string (
            id STRING PRIMARY KEY
        )
    """),
    [True]
)

verificar(
    "FK INTEGER referenciando PK STRING",
    sistema_compatibilidade.consulta("""
        CREATE TABLE filho_int_string (
            id INTEGER PRIMARY KEY,
            referencia INTEGER FOREIGN KEY REFERENCES pai_string(id)
        )
    """),
    [False]
)


# 7. BOOLEAN -> FLOAT: deve rejeitar
verificar(
    "FK BOOLEAN referenciando PK FLOAT",
    sistema_compatibilidade.consulta("""
        CREATE TABLE filho_bool_float (
            id INTEGER PRIMARY KEY,
            referencia BOOLEAN FOREIGN KEY REFERENCES pai_float(id)
        )
    """),
    [False]
)

resumo()
