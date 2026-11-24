# Interpreta comandos SQL e os transforma em dicionários

simbolos = {"(", ")", ",", "*", ":", "<", ">", "="}
funcoes = {"MIN", "MAX", "AVG", "COUNT"}

def e_numero(x):
    # Lê um número com ou sem sinal e devolve um booleano, dizendo se é um número ou não
    if len(x) == 0:
        return False
    
    if x[0] == "-":
        x = x[1:]

    return x.isdigit()

def separar_tokens(texto):
    # Função principal do tokenizador. Lê um texto (comando) e devolve uma  lista de tuplas, na qual cada um representa um token  
    # Forma: ("tipo", "expressão") -> ("SIM", ","); ("PAL", "alunos")
    tokens = list()
    atual = ""
    string = False # se estou no modo de avaliacao de texto ou de estring
    asp = 0 # contador de aspas na string
    mrc = "" # MaRCador de qual das aspas abriu a string 
    
    for i in range(len(texto)):
        if texto[i] in ("'",'"') and (mrc == "" or texto[i] == mrc):
            mrc = texto[i]
            asp += 1
            
            if asp == 2:
                asp = 0
                tokens.append(("STR", atual))
                atual = ""
                mrc = ""
                string = not string
                continue    
                    
            string = not string
            
            if len(atual) != 0:
                tokens.append(("PAL", atual))
            atual = ""
            continue
        
        if string:
            atual += texto[i]
            
        else:
            if texto[i] in (" ", "\n", "\t", "\r"):
                
                if len(atual) != 0:
                    tokens.append(("PAL", atual))
                    atual = ""
                
            elif texto[i] in simbolos:
                if len(atual) != 0:
                    tokens.append(("PAL", atual))
                
                tokens.append(("SIM", texto[i]))
                atual = ""
                continue
                    
            elif texto[i] == ".":
                try:
                    if e_numero(atual) and texto[i + 1].isdigit() and "." not in atual:
                        atual += texto[i]       
                    
                    else:
                        if len(atual) != 0:
                            tokens.append(("PAL", atual))
                        
                        tokens.append(("SIM", texto[i]))
                        atual = ""
                
                except IndexError:
                    if len(atual) != 0:
                        tokens.append(("PAL", atual))
                                                
                    tokens.append(("SIM", texto[i]))
                    atual = ""
        
            else:
                atual += texto[i]
    
    if mrc != "":
        raise ValueError("String não fechada")
     
    if len(atual) != 0:
        tokens.append(("PAL", atual))
    
    return tokens

def proximo(tokens):
    # Pega o próximo token da lista, consumindo-o
    # Lê uma lista de tokens e devolve um token (tupla)
    if len(tokens) != 0:
        return tokens.pop(0)
   
    else:
        raise ValueError("Lista de tokens vazia")

def olhar(tokens):
    # Avalia o próximo token da lista sem consumí-lo
    # Lê uma lista de tokens e devolve um token (tupla) ou None
    if len(tokens) != 0:
        return tokens[0]

    else: 
        return None

def esperar(tokens, palavra):
    # Lê uma lista de tokens e um termo esperado, devolve True caso eles coincidam ou levanta um erro caso contrário
    a = proximo(tokens)
    
    if a[1].upper() == palavra.upper():
        return True
    
    else:
        raise ValueError("Comando inválido")

def ler_valor(token):
    # Lê um único token e devolve seu valor convertido em um tipo de dado, se possível
    tipo, valor = token
    
    if tipo == "STR":
        return str(valor)

    elif tipo == "PAL":
        if valor.upper() == "FALSE":
            return False
        
        if valor.upper() == "TRUE":
            return True
    
        try:
            return int(valor)
        
        except:
            try:
                return float(valor)
            
            except:
                raise ValueError(f"Termo {valor} não pode ser convertido para qualquer tipo conhecido")

    else:
        raise ValueError("Tokens que representam símbolos não possuem correspondência de tipo")

def validar_identificador(palavra):
    # Lê o nome de uma coluna/tabela e avalia sua validade
    # "_tabela" "tabela_1" "_1tabela" -> Válidos
    # "tabela-1" "1tabela" "*+tabela" -> inválidos
    if len(palavra) == 0:
        raise ValueError("Nome inválido")
    
    if (not palavra[0].isalpha()) and (not palavra[0] == "_"):
        raise ValueError("Nome inválido")
    
    for c in palavra[1:]:
        if (not c.isalnum()) and (not c == "_"):
            raise ValueError("Nome inválido")
        
    return True  

def interpretar_create_database(tokens):
    # Lê uma lista de tokens e devolve um dicionário na forma
    # {
    #  "op": "CREATE_DATABASE"
    #   "nome": nomebanco
    # }
    comandos = dict()
    
    esperar(tokens, "CREATE")
    esperar(tokens, "DATABASE")        
        
    if olhar(tokens) is not None:
        a = proximo(tokens)
        
        if (a[0] == "PAL"):
            validar_identificador(a[1])            
            if olhar(tokens) is None:
                comandos["op"] = "CREATE_DATABASE"
                comandos["nome"] = a[1]
                return comandos
            
            else:
                raise ValueError("Excesso de parâmetros para a criação do banco")
                
        else:
            raise ValueError("Token não representa um termo válido")
        
    else:
        raise ValueError("Parâmetros insuficientes para a criação do banco")
       
def interpretar_use_database(tokens):
    # Lê uma lista de tokens e devolve um dicionário na forma
        # {
        #  "op": "USE_DATABASE"
        #   "nome": nomebanco
        # }
    comandos = dict()
    
    esperar(tokens, "USE")
    esperar(tokens, "DATABASE")        
        
    if olhar(tokens) is not None:
        a = proximo(tokens)
        
        if (a[0] == "PAL"):
            validar_identificador(a[1])            
            if olhar(tokens) is None:
                comandos["op"] = "USE_DATABASE"
                comandos["nome"] = a[1]
                return comandos
            
            else:
                raise ValueError("Excesso de parâmetros para a seleção do banco")
                
        else:
            raise ValueError("Token não representa um termo válido")
        
    else:
        raise ValueError("Parâmetros insuficientes para a seleção do banco")

def interpretar_create_table(tokens):
    # Lê uma lista de tokens e devolve um dicionário na forma
    # {
    #  "op": "CREATE_TABLE"
    #   "nome": nometabela
    #   "colunas" : [
    #                   { 
    #                       "nome": nomecoluna
    #                       "tipo": INTEGER/BOOLEAN/FLOAT/STRING
    #                       "pk": True/Flse
    #                       "fk": ["tabela referenciada", "atributo referenciado"]
    #                   }
    #
    #               ]
    # }
    comandos = dict()
    colunas = []
    
    esperar(tokens, "CREATE")
    esperar(tokens, "TABLE")
    
    if olhar(tokens) is not None:
        n = proximo(tokens)
        
        if n[0] == "PAL":
            validar_identificador(n[1])
            comandos["op"] = "CREATE_TABLE"
            comandos["nome"] = n[1]
            
            if olhar(tokens) is not None:
                s = proximo(tokens)
                
                if s[0] == "SIM" and s[1] == "(":
                    while True:
                        a = proximo(tokens)
                        
                        if a[0] != "PAL":
                            raise ValueError("Nome de coluna inválido")
                        
                        validar_identificador(a[1])

                        t = proximo(tokens)
                        if t[0] != "PAL" or t[1].upper() not in ("INTEGER", "BOOLEAN", "STRING", "FLOAT"):
                            raise ValueError("Tipo de dado inválido")

                        pk = False
                        fk = None
                        tk = olhar(tokens)
                        
                        if (tk is not None) and (tk[0] == "PAL") and (tk[1].upper() == "PRIMARY"):
                            proximo(tokens)
                            esperar(tokens, "KEY")
                            pk = True

                        tk = olhar(tokens)
                        
                        if (tk is not None) and (tk[0] == "PAL") and (tk[1].upper() == "FOREIGN"):
                            proximo(tokens)
                            esperar(tokens, "KEY")
                            esperar(tokens, "REFERENCES")

                            nt = proximo(tokens)
                            
                            if nt[0] != "PAL":
                                raise ValueError("Sintaxe incorreta")
                            
                            validar_identificador(nt[1])
                            esperar(tokens, "(")
                            
                            ar = proximo(tokens)
                            
                            if ar[0] != "PAL":
                                raise ValueError("Sintaxe incorreta")
                            
                            validar_identificador(ar[1])
                            esperar(tokens, ")")
                            
                            fk = [nt[1], ar[1]]

                        colunas.append({"nome": a[1], "tipo": t[1].upper(), "pk": pk, "fk": fk})

                        sep = proximo(tokens)
                        if sep == ("SIM", ")"):
                            break
                        
                        if sep != ("SIM", ","):
                            raise ValueError("Sintaxe incorreta")

                    if len(tokens) != 0:
                        raise ValueError("Excesso de termos para a criação de uma tabela")
                    
                    comandos["colunas"] = colunas
                    
                    return comandos
                else:
                    raise ValueError("Sintaxe incorreta")
            else:
                raise ValueError("Termos insuficientes para a criação de uma tabela")
        else:
            raise ValueError("Token não representa um termo válido")
    else:
        raise ValueError("Termos insuficientes para a criação de uma tabela")
    
def interpretar_insert(tokens):
    # Lê uma lista de tokens e devolve um dicionário na forma
        # {
        #  "op": "INSERT"
        #   "tabela": nometabela 
        #   "valores": [valores com tipos convertido]
        # }
    comandos = dict()
    valores = list()
    
    esperar(tokens, "INSERT")
    esperar(tokens, "INTO")
    
    if olhar(tokens) is not None:
        t = proximo(tokens)
        
        if t[0] == "PAL":
            validar_identificador(t[1])
            comandos["op"] = "INSERT"
            comandos["tabela"] = t[1]
            
            esperar(tokens, "VALUES")
            
            tk = olhar(tokens)
            if tk is not None:
                s = proximo(tokens)
                
                if s[0] == "SIM" and s[1] == "(":
                    while True:
                        a = proximo(tokens)                 
                        
                        if a[0] != "SIM":
                           v = ler_valor(a)
                           valores.append(v)
                           
                        else:
                            raise ValueError("Sintaxe incorreta")
                        
                        sep = olhar(tokens)
                        
                        if sep is None:
                            raise ValueError("Sintaxe incorreta")
                        
                        if sep == ("SIM", ")"):
                            proximo(tokens)
                            break
                        
                        elif sep == ("SIM", ","):
                            proximo(tokens)
                        
                        else:
                            raise ValueError("Sintaxe incorreta")
                    
                    comandos["valores"] = valores
                    
                    if len(tokens) != 0:
                        raise ValueError("Excesso de termos para a inserção em uma tabela")
                    
                    return comandos
                        
                else:
                    raise ValueError("Sintaxe incorreta")
            
            else:
                raise ValueError("Sintaxe incorreta")    
        
        else:
            raise ValueError("Token não representa um termo válido")
    
    else:
        raise ValueError("Termos insuficientes para a inserção em uma tabela")    

def interpretar(comando):
    # Centraliza as operações de interpretação, chamando as auxiliares correpondentes para cada comando
    # Lê uma lista de tokens e devolve um dicionário do comando correspondente
    tokens = separar_tokens(comando)
    p = olhar(tokens)
    
    if (p is not None) and (p[0] == "PAL"):        
        if p[1].upper() == "USE":
            return interpretar_use_database(tokens)
            
        elif p[1].upper() == "INSERT":
            return interpretar_insert(tokens)
        
        elif p[1].upper() == "SELECT":
            return interpretar_select(tokens)
            
        elif p[1].upper() == "CREATE":
            try:
                s = tokens[1]
                if (s is not None) and (s[0] == "PAL"):
                    if s[1].upper() == "TABLE":
                        return interpretar_create_table(tokens)
                    
                    elif s[1].upper() == "DATABASE":
                        return interpretar_create_database(tokens)
                        
                    else:
                        raise ValueError("Comando não reconhecido")
                
                else:
                    raise ValueError("Tipo inadequado para comando")
            
            except IndexError:
                raise ValueError("Comando incompleto")
               
        else:
            raise ValueError("Comando não reconhecido")
    
    else:
        raise ValueError("Tipo inadequado para comando")
    
def processar_atributo(tks):
    # lê um atributo simples (nome) ou composto (tabela.nome) e o devolve como String única
    # (alunos) (.) (nota) -> "alunos.nota"
    t = olhar(tks)
    if (t is not None) and (t[0] == "PAL") and (t[1].upper() not in funcoes):
        a = proximo(tks)
        p = olhar(tks)
        
        if (p is not None) and p == ("SIM", "."):
            proximo(tks)
            s = olhar(tks)
            if (s is not None) and (s[0] == "PAL") and (s[1].upper() not in funcoes):
                b = proximo(tks)
                
                return str(a[1]) + "." + str(b[1])
            
            else:
                raise ValueError("Sintaxe incorreta")
                
        else:
            return str(a[1])
                
    else:
        raise ValueError("O valor informado não representa um atributo válido")

def proc_item_select(tks):
    # lê um item do SELECT: *, função de agregação ou atributo. Devolve um dicionário
    t = olhar(tks)

    if t is None:
        raise ValueError("Item ausente")

    if t == ("SIM", "*"):
        proximo(tks)
        return {"tipo": "*"}

    if t[0] == "PAL" and t[1].upper() in funcoes:
        proximo(tks)
        esperar(tks, "(")

        if olhar(tks) == ("SIM", "*"):
            if t[1].upper() != "COUNT":
                raise ValueError("Apenas COUNT aceita *")
            
            proximo(tks)
            nome = None
        
        else:
            nome = processar_atributo(tks)

        esperar(tks, ")")
        return {"tipo": "agg", "funcao": t[1].upper(), "nome": nome}

    return {"tipo": "atb", "nome": processar_atributo(tks)}

def listar_itens(tks):
    # lê os itens separados por vírgula e devolve uma lista de dicionários
    itens = []
    
    while True:
        itens.append(proc_item_select(tks))
        
        if olhar(tks) == ("SIM", ","):
            proximo(tks)
        
        else:
            break
    
    return itens

def listar_tabelas(tks):
    # lê os nomes de tabela separados por vírgula. Devolve uma lista de textos
    tabelas = []
    
    while True:
        t = proximo(tks)
        
        if t[0] != "PAL":
            raise ValueError("Nome de tabela inválido")
        
        validar_identificador(t[1])
        tabelas.append(t[1])
        
        if olhar(tks) == ("SIM", ","):
            proximo(tks)
        
        else:
            break
    
    return tabelas

def ler_operando(tks):
    # lê um operando do where, seja um valor constante ou um atributo
    # Devolve um dicionário na forma
        # {
        #  "tipo": "const"/"atb"
        #   "valor"/"nome": valorconst/nomeatributo
        # }
    t = olhar(tks)
    
    if t is None:
        raise ValueError("Operando ausente")

    if t[0] == "STR":
        proximo(tks)
        return {"tipo": "const", "valor": t[1]}

    if t[0] == "PAL":
        v = t[1]
        
        if v[0].isdigit() or v[0] == "-" or v.upper() in ("TRUE", "FALSE"):
            proximo(tks)
            return {"tipo": "const", "valor": ler_valor(t)}
        
        else:
            return {"tipo": "atb", "nome": processar_atributo(tks)}

    raise ValueError("Operando inválido")

def ler_operador(tks):
    # lê um operador de comparação (=, > ou <) e identifica se ele é válido
    t = proximo(tks)
    
    if t[0] == "SIM" and t[1] in ("=", ">", "<"):
        return t[1]
    
    else:
        raise ValueError("Operador de comparação inválido")

def ler_where(tks):
    # lê as condições do where. 
    # Devolve lista de listas (OR entre as listas, AND dentro de cada uma)
    where = [[]]
    
    while True:
        e = ler_operando(tks)
        op = ler_operador(tks)
        d = ler_operando(tks)
        where[-1].append({"esq": e, "op": op, "dir": d})

        t = olhar(tks)
        if (t is not None) and (t[0] == "PAL") and (t[1].upper() == "AND"):
            proximo(tks)
        
        elif (t is not None) and (t[0] == "PAL") and (t[1].upper() == "OR"):
            proximo(tks)
            where.append([])
        
        else:
            break
    
    return where

def interpretar_select(tokens):
    # Usa das funções auiliares acima para transformar uma lista de tokens em um dicionário
    esperar(tokens, "SELECT")
    cmd = {"op": "SELECT", "colunas": listar_itens(tokens), "tabelas": [], "where": [], "group_by": None}

    esperar(tokens, "FROM")
    cmd["tabelas"] = listar_tabelas(tokens)

    t = olhar(tokens)
    if (t is not None) and (t[0] == "PAL") and (t[1].upper() == "WHERE"):
        proximo(tokens)
        cmd["where"] = ler_where(tokens)

    t = olhar(tokens)
    if (t is not None) and (t[0] == "PAL") and (t[1].upper() == "GROUP"):
        proximo(tokens)
        esperar(tokens, "BY")
        cmd["group_by"] = processar_atributo(tokens)

    if len(tokens) != 0:
        raise ValueError("Excesso de termos")

    return cmd