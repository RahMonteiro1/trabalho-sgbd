# Interpreta comandos SQL e os transforma em dicionários

simbolos = {"(", ")", ",", "*", ":", "<", ">", "="}

def e_numero(x):
    if x[0] == "-":
        x = x[1:]

    return x.isdigit()

def separar_tokens(texto):
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
    if len(tokens) != 0:
        return tokens.pop(0)
   
    else:
        raise ValueError("Lista de tokens vazia")

def olhar(tokens):
    if len(tokens) != 0:
        return tokens[0]

    else: 
        return None

def esperar(tokens, palavra):
    a = proximo(tokens)
    
    if a[1].upper() == palavra.upper():
        return True
    
    else:
        raise ValueError("Comando inválido")

def ler_valor(token):
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
    if len(palavra) == 0:
        raise ValueError("Nome inválido")
    
    if (not palavra[0].isalpha()) and (not palavra[0] == "_"):
        raise ValueError("Nome inválido")
    
    for c in palavra[1:]:
        if (not c.isalnum()) and (not c == "_"):
            raise ValueError("Nome inválido")
        
    return True  

def interpretar_create_database(tokens):
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
    tokens = separar_tokens(comando)
    p = olhar(tokens)
    
    if (p is not None) and (p[0] == "PAL"):        
        if p[1].upper() == "USE":
            return interpretar_use_database(tokens)
            
        elif p[1].upper() == "INSERT":
            return interpretar_insert(tokens)
            
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