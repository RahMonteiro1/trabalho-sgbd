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

