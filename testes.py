
import interpretador as it
import sistema


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

def resumo():
    total = len(resultados)
    aprovados = sum(resultados)

    print("\n" + "=" * 45)
    print(f"{aprovados} de {total} testes passaram.")
    print("=" * 45)


s = sistema.Sistema()
s.login("Admin", "123456")
s.consulta("CREATE DATABASE universidade")
s.consulta("USE DATABASE universidade")
s.consulta("CREATE TABLE alunos (matricula INTEGER PRIMARY KEY, nome STRING, idade INTEGER, media FLOAT)")
s.consulta("CREATE TABLE disciplinas (codigo INTEGER PRIMARY KEY, nome STRING, creditos INTEGER)")
s.consulta("CREATE TABLE matriculas (id INTEGER PRIMARY KEY, matricula INTEGER FOREIGN KEY REFERENCES alunos(matricula), codigo_disciplina INTEGER FOREIGN KEY REFERENCES disciplinas(codigo), nota FLOAT)")
for c in ['INSERT INTO alunos VALUES (1001, "Ana", 22, 8.5)',
          'INSERT INTO alunos VALUES (1002, "Carlos", 25, 7.0)',
          'INSERT INTO alunos VALUES (1003, "Maria", 19, 9.2)',
          'INSERT INTO disciplinas VALUES (1, "Programacao", 4)',
          'INSERT INTO disciplinas VALUES (2, "Banco de Dados", 4)',
          'INSERT INTO matriculas VALUES (1, 1001, 1, 9.0)',
          'INSERT INTO matriculas VALUES (2, 1001, 2, 8.0)',
          'INSERT INTO matriculas VALUES (3, 1002, 1, 7.0)',
          'INSERT INTO matriculas VALUES (4, 1003, 2, 9.5)']:
    s.consulta(c)

verificar("C1", s.consulta("SELECT * FROM alunos"), [(1001, "Ana", 22, 8.5), (1002, "Carlos", 25, 7.0), (1003, "Maria", 19, 9.2)])
verificar("C2", s.consulta("SELECT nome, idade FROM alunos WHERE idade > 20"), [("Ana", 22), ("Carlos", 25)])
verificar("C3", s.consulta("SELECT nome, idade FROM alunos WHERE idade > 18 AND idade < 25"), [("Ana", 22), ("Maria", 19)])
verificar("C4", s.consulta("SELECT nome, idade FROM alunos WHERE idade < 20 OR idade > 25"), [("Maria", 19)])
verificar("C5", s.consulta("SELECT alunos.nome, matriculas.codigo_disciplina, matriculas.nota FROM alunos, matriculas WHERE alunos.matricula = matriculas.matricula"),
          [("Ana", 1, 9.0), ("Ana", 2, 8.0), ("Carlos", 1, 7.0), ("Maria", 2, 9.5)])
verificar("C6", s.consulta("SELECT alunos.nome, disciplinas.nome, matriculas.nota FROM alunos, disciplinas, matriculas WHERE alunos.matricula = matriculas.matricula AND disciplinas.codigo = matriculas.codigo_disciplina"),
          [("Ana", "Programacao", 9.0), ("Ana", "Banco de Dados", 8.0), ("Carlos", "Programacao", 7.0), ("Maria", "Banco de Dados", 9.5)])
verificar("C7", s.consulta("SELECT AVG(nota) FROM matriculas"), [(8.375,)])
verificar("C8", s.consulta("SELECT MAX(nota), MIN(nota) FROM matriculas"), [(9.5, 7.0)])
verificar("C9", s.consulta("SELECT codigo_disciplina, COUNT(*) FROM matriculas GROUP BY codigo_disciplina"), [(1, 2), (2, 2)])
verificar("C10", s.consulta("SELECT codigo_disciplina, MIN(nota), MAX(nota), AVG(nota), COUNT(*) FROM matriculas GROUP BY codigo_disciplina"),
          [(1, 7.0, 9.0, 8.0, 2), (2, 8.0, 9.5, 8.75, 2)])
verificar("C11", s.consulta("SELECT codigo_disciplina, AVG(nota) FROM matriculas WHERE nota > 7 GROUP BY codigo_disciplina"), [(1, 9.0), (2, 8.75)])
verificar("vazio", s.consulta("SELECT COUNT(*), MAX(nota) FROM matriculas WHERE nota > 100"), [(0, None)])
verificar("sem linhas", s.consulta("SELECT nome FROM alunos WHERE idade > 100"), [])
verificar("tabela inexistente", s.consulta("SELECT * FROM xyz"), [False])
verificar("atributo sem GROUP BY", s.consulta("SELECT nome, COUNT(*) FROM alunos"), [False])
verificar("AVG de texto", s.consulta("SELECT AVG(nome) FROM alunos"), [False])
verificar("tipo errado no WHERE", s.consulta("SELECT nome FROM alunos WHERE idade > 'a'"), [False])

verificar("atributo inexistente",
          s.consulta("SELECT inexistente FROM alunos"), [False])

verificar("atributo ambíguo",
          s.consulta("SELECT nome FROM alunos, disciplinas"), [False])

verificar("atributo qualificado inexistente",
          s.consulta("SELECT xyz.nome FROM alunos"), [False])

s.consulta("CREATE TABLE alunos_vazia (id INTEGER PRIMARY KEY, nome STRING)")

verificar("atributo inválido em tabela vazia",
          s.consulta("SELECT nome FROM alunos_vazia WHERE inexistente = 10"), [False])

verificar("comparação entre atributos incompatíveis",
          s.consulta("SELECT alunos.nome FROM alunos, matriculas WHERE alunos.nome = matriculas.nota"), [False])

resumo()