# Contém os testes e demonstrações do sistema

from sistema import Sistema
from modelos import Atributo, Tabela, Banco, Usuario

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
