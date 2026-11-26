
import interpretador as it
from sistema import Sistema


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



# ============================================================
# 24/11 — Usuários e permissões
# ============================================================
s = Sistema()

# 1. Login administrativo
verificar("Login Admin", s.login("Admin", "123456"), True)

# 2. Preparação do banco
verificar(
    "Criar banco",
    s.consulta("CREATE DATABASE universidade"),
    [True]
)

verificar(
    "Selecionar banco",
    s.consulta("USE DATABASE universidade"),
    [True]
)

verificar(
    "Criar tabela",
    s.consulta("CREATE TABLE alunos (id INTEGER PRIMARY KEY, nome STRING)"),
    [True]
)

# 3. CREATE USER
verificar(
    "Criar professor",
    s.consulta("CREATE USER professor IDENTIFIED BY 'abc123'"),
    [True]
)

verificar(
    "Criar aluno",
    s.consulta("CREATE USER aluno IDENTIFIED BY 'aluno123'"),
    [True]
)

verificar(
    "Impedir usuário duplicado",
    s.consulta("CREATE USER aluno IDENTIFIED BY 'outra123'"),
    [False]
)

verificar(
    "Listar usuários",
    s.consulta("SHOW USERS"),
    [
        ("Admin", "admin"),
        ("professor", "comum"),
        ("aluno", "comum")
    ]
)

# 4. GRANT
verificar(
    "Conceder SELECT no banco",
    s.consulta("GRANT SELECT ON universidade TO professor"),
    [True]
)

verificar(
    "Conceder INSERT na tabela",
    s.consulta("GRANT INSERT ON universidade.alunos TO professor"),
    [True]
)

verificar(
    "Listar permissões do professor",
    s.consulta("SHOW PERMISSIONS professor"),
    [
        ("universidade", "*", "SELECT"),
        ("universidade", "alunos", "INSERT")
    ]
)

# 5. ALL no nível do banco
verificar(
    "Criar usuário gerente",
    s.consulta("CREATE USER gerente IDENTIFIED BY 'gerente123'"),
    [True]
)

verificar(
    "Conceder ALL no banco",
    s.consulta("GRANT ALL ON universidade TO gerente"),
    [True]
)

verificar(
    "ALL no banco",
    s.consulta("SHOW PERMISSIONS gerente"),
    [
        ("universidade", "*", "SELECT"),
        ("universidade", "*", "INSERT"),
        ("universidade", "*", "CREATE")
    ]
)

# 6. ALL no nível da tabela
verificar(
    "Criar usuário auxiliar",
    s.consulta("CREATE USER auxiliar IDENTIFIED BY 'auxiliar123'"),
    [True]
)

verificar(
    "Conceder ALL na tabela",
    s.consulta("GRANT ALL ON universidade.alunos TO auxiliar"),
    [True]
)

verificar(
    "ALL na tabela",
    s.consulta("SHOW PERMISSIONS auxiliar"),
    [
        ("universidade", "alunos", "SELECT"),
        ("universidade", "alunos", "INSERT")
    ]
)

# 7. REVOKE
verificar(
    "Revogar INSERT da tabela",
    s.consulta("REVOKE INSERT ON universidade.alunos FROM professor"),
    [True]
)

verificar(
    "Conferir permissões após REVOKE",
    s.consulta("SHOW PERMISSIONS professor"),
    [
        ("universidade", "*", "SELECT")
    ]
)

verificar(
    "Revogar permissão inexistente",
    s.consulta("REVOKE INSERT ON universidade.alunos FROM professor"),
    [True]
)

verificar(
    "Revogar SELECT do banco",
    s.consulta("REVOKE SELECT ON universidade FROM professor"),
    [True]
)

verificar(
    "Conferir permissões vazias",
    s.consulta("SHOW PERMISSIONS professor"),
    []
)

# 8. Restrições administrativas
verificar(
    "Logout Admin",
    s.logout(),
    True
)

verificar(
    "Login professor",
    s.login("professor", "abc123"),
    True
)

verificar(
    "Bloquear CREATE USER para não admin",
    s.consulta("CREATE USER invasor IDENTIFIED BY '123'"),
    [False]
)

verificar(
    "Bloquear GRANT para não admin",
    s.consulta("GRANT SELECT ON universidade TO aluno"),
    [False]
)

verificar(
    "Bloquear REVOKE para não admin",
    s.consulta("REVOKE SELECT ON universidade FROM aluno"),
    [False]
)

verificar(
    "Bloquear SHOW USERS para não admin",
    s.consulta("SHOW USERS"),
    [False]
)

verificar(
    "Bloquear SHOW PERMISSIONS para não admin",
    s.consulta("SHOW PERMISSIONS aluno"),
    [False]
)

# 9. Resumo
resumo()
