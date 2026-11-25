# Executa consultas SELECT sobre as tabelas

from modelos import compativel

def nome_colunas(lista):
    # Lê uma lista de objetos tabela e devolve uma lista de nomes longos das colunas de cada tabela. 
    # Ex: [Alunos, Curso] -> ["alunos.nome", "alunos.matricula", 
    #                          "curso.nome", "curso.grade"]
    nomes = list()
    
    for t in lista:
        m = str(t.nome) + "."
        
        for a in t.atributos:
            n = str(a.nome)
            nomes.append(m + n)
            
    return nomes

def resolver(nome, colunas):
    encontrados = list()
    
    for a in colunas:
        if "." in nome:
            if nome == a:
                encontrados.append(nome)
            
        else: 
            partes = a.split(".")
            if nome == partes[1]:
                encontrados.append(partes[0] + "." + nome)
            
    if len(encontrados) == 0:
        raise ValueError("Atributo inexistente")
    
    elif len(encontrados) == 1:
        return encontrados[0]
    
    else:
        raise ValueError("Atributo ambíguo")
              
def tipo_coluna(nome, tabelas):
    # Lê um nome longo de atributo (alunos.ra) e o dicionario de tabelas, retornando o tipo daquele atrubuto
    partes = nome.split(".")

    if partes[0] not in tabelas:
        raise ValueError("Tabela não encontrada")

    else:
        t = tabelas[partes[0]]

        for a in t.atributos:
            if a.nome == partes[1]:
                return a.tipo

        raise ValueError("Atributo não encontrado")
    
def validar_where(wh, col, tab):
    numericos = ("INTEGER", "FLOAT")
    for i in range(len(wh)):
        for j in range(len(wh[i])):
            cond = wh[i][j]

            esq = cond["esq"]
            di = cond["dir"]

            cesq = esq["tipo"]  # Categoria esquerda
            cdi = di["tipo"]  # Categoria direita

            tesq = None
            tdi = None

            if cesq == "atb":
                nesq = resolver(esq["nome"], col)
                tesq = tipo_coluna(nesq, tab)
                esq["nome"] = nesq

            if cdi == "atb":
                ndi = resolver(di["nome"], col)
                tdi = tipo_coluna(ndi, tab)
                di["nome"] = ndi

            if cesq == "atb" and cdi == "const":
                valor = di["valor"]

                if not (
                    compativel(tesq, valor)
                    or (
                        tesq in numericos
                        and isinstance(valor, (int, float))
                        and not isinstance(valor, bool)
                    )
                ):
                    raise TypeError("Valores incompatíveis estão sendo comparados")

            elif cesq == "const" and cdi == "atb":
                valor = esq["valor"]

                if not (
                    compativel(tdi, valor)
                    or (
                        tdi in numericos
                        and isinstance(valor, (int, float))
                        and not isinstance(valor, bool)
                    )
                ):
                    raise TypeError("Valores incompatíveis estão sendo comparados")

            elif cesq == "atb" and cdi == "atb":
                if not (
                    tdi == tesq
                    or (
                        tdi in numericos
                        and tesq in numericos
                    )
                ):
                    raise TypeError("Valores incompatíveis estão sendo comparados")

            elif cesq == "const" and cdi == "const":
                vesq = esq["valor"]
                vdi = di["valor"]

                num = (int, float)

                nesq = isinstance(vesq, num) and not isinstance(vesq, bool)
                ndi = isinstance(vdi, num) and not isinstance(vdi, bool)

                if not (type(vesq) == type(vdi) or (nesq and ndi)):
                    raise TypeError("Valores incompatíveis estão sendo comparados")
                
def gerar_linhas(tabelas):
    # produto cartesiano
    # Lê uma lista de tabelas e devolve uma lista de dicionários {'alunos.nome': 'Ana', cursos.nome = "Direito", etc}
    linhas = [{}]
    for tab in tabelas:
        novas = []
        
        for linha in linhas: # linha: combinação já feita
            for reg in tab.registros: # reg: registro da tabela atual
                nova = dict(linha)
                
                for i in range(len(reg)): 
                    nova[tab.nome + "." + tab.atributos[i].nome] = reg[i]
                
                novas.append(nova) # combinações novas + combinações anteriores
        
        linhas = novas # substitui pois o próximo vai acresscentar os dele
    
    return linhas
  
def mesmo_tipo(a, b):
    # Verifica se se a e b podem ser comparados (bool com bool, número com número, texto com texto)
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool)
    
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return True
    
    return isinstance(a, str) and isinstance(b, str)  
            
def comparar(a, op, b):
    if not mesmo_tipo(a, b):
        raise ValueError(f"Não é possível comparar {a} com {b}")
    
    if op == ">":
        return a > b
    
    elif op == "<":
        return a < b
    
    elif op == "=":
        return a == b
    
    else:
        raise ValueError("Operador não reconhecido")
    
def valor_op(op, lin, col):
# Retorna a constante ou o valor do atb na linha em questão
    if op["tipo"] == "const":
        return op["valor"]

    else:
        return lin[resolver(op["nome"], col)]

def linha_passa(linha, wh, colunas):
    # Verifica se a linha satisfaz o where (lista de listas do or e do and)
    if len(wh) == 0:
        return True
    
    for grupo in wh:
        todas = True
        
        for cond in grupo:
            e = valor_op(cond["esq"], linha, colunas)
            d = valor_op(cond["dir"], linha, colunas)
            
            if not comparar(e, cond["op"], d): # se encontra uma falha dentro do and, interrompe o grupo
                todas = False
                break

        if todas: # se passa um grupo inteiro, o or já é satisfeito, então todos passam
            return True
            
    return False

def projetar(linhas, itens, colunas):
    # SELECT sem agregação: devolve uma tupla por linha com as colunas pedidas
    nomes = []
    for i in itens:
        if i["tipo"] == "*":
            if len(itens) != 1:
                raise ValueError("Sintaxe incorreta do operador *")
            
            else:
                nomes = list(colunas)
        
        else:
            nomes.append(resolver(i["nome"], colunas))

    resultado = []
    
    for linha in linhas:
        reg = []
        
        for n in nomes:
            reg.append(linha[n])
        
        resultado.append(tuple(reg))
    
    return resultado

def calcular(item, grupo, colunas):
    # calcula uma função de agregação sobre um grupo de linhas
    if item["nome"] is None: # COUNT(*)
        return len(grupo)

    n = resolver(item["nome"], colunas)
    valores = []
    
    for l in grupo:
        valores.append(l[n])

    func = item["funcao"]
    
    if func == "COUNT":
        return len(valores)
    
    if len(valores) == 0:
        return None
    
    if func == "MIN":
        return min(valores)
    
    if func == "MAX":
        return max(valores)
    
    if func == "AVG":
        return sum(valores) / len(valores)
    
    raise ValueError(f"Função desconhecida")

def agregar(linhas, itens, colunas, group_by, lista_tabelas):
    # SELECT com agregação e/ou GROUP BY: devolve uma tupla por grupo
    chave = None

    if group_by is not None:
        chave = resolver(group_by, colunas)
        apareceu = False
        
        for i in itens:
            if i["tipo"] == "*":
                raise ValueError("* não pode ser usado com GROUP BY")
            
            if i["tipo"] == "atb":
                if resolver(i["nome"], colunas) != chave:
                    raise ValueError("Atributo do SELECT diferente do atributo do GROUP BY")
                
                else:
                    apareceu = True
        
        if not apareceu:
            raise ValueError("O atributo do GROUP BY deve aparecer no SELECT")
    
    else:
        for it in itens:
            if it["tipo"] != "agg":
                raise ValueError("Atributos junto de agregações exigem GROUP BY")

    for ite in itens:
        if ite["tipo"] == "agg" and ite["nome"] is not None and ite["funcao"] != "COUNT":
            n = resolver(ite["nome"], colunas)
            if tipo_coluna(n, lista_tabelas) not in ("INTEGER", "FLOAT"):
                raise ValueError("MIN, MAX e AVG só aceitam atributos numéricos")

    # separa as linhas em grupos (sem GROUP BY: um grupo só, com todas)
    grupos = {}
    
    if chave is None:
        grupos[None] = linhas
    
    else:
        for linha in linhas:
            valor = linha[chave]
            if valor not in grupos:
                grupos[valor] = []
            grupos[valor].append(linha)

    resultado = []
    
    for valor in grupos:
        reg = []
        
        for item in itens:
            if item["tipo"] == "atb":
                reg.append(valor)
            
            else:
                reg.append(calcular(item, grupos[valor], colunas))
        
        resultado.append(tuple(reg))
    
    return resultado

def executar_select(cmd, tabelas):
    # Lê um dicionário de comandos do interpretador e um dicionário de tabelas.
    # Devolve uma lista de tuplas com os resultados
    lista = list()
    dic = dict()   # só as tabelas do FROM, por nome (tipo_coluna e validar_where esperam dicionário)

    for nome in cmd["tabelas"]:
        if nome not in tabelas:
            raise ValueError(f"A tabela {nome} não existe")

        if nome in dic:
            raise ValueError(f"A tabela {nome} está duplicada")

        lista.append(tabelas[nome])
        dic[nome] = tabelas[nome]

    col = nome_colunas(lista)
    validar_where(cmd["where"], col, dic)

    lin = []
    for l in gerar_linhas(lista):
        if linha_passa(l, cmd["where"], col):
            lin.append(l)

    agg = False # se tem agregação na operação ou não
    for i in cmd["colunas"]:
        if i["tipo"] == "agg":
            agg = True

    if agg or (cmd["group_by"] is not None):
        return agregar(lin, cmd["colunas"], col, cmd["group_by"], dic)
    
    return projetar(lin, cmd["colunas"], col)
