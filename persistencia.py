# Grava e recupera os dados em arquivos binários
from modelos import *
import math
import struct
import os
 
tam_str = 1024
form_int = "<q"
form_float = "<d"
form_bool = "<?"
form_str = "<1024s"

def escrever_int(arq, valor):
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ValueError("O número informado deve ser um inteiro")
    
    if valor < -(2 ** 63) or valor > 2 ** 63 - 1:
        raise ValueError("Inteiro fora do intervalo de 64 bits")
    
    arq.write(struct.pack(form_int, valor))
 
def ler_int(arq):
    dados = arq.read(8)
    
    if len(dados) != 8:
        raise EOFError("Arquivo incompleto: esperados 8 bytes de um inteiro")
    
    return struct.unpack(form_int, dados)[0]
 
def escrever_float(arq, valor):
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        raise ValueError("FLOAT deve ser um número")
    
    try:
        valor = float(valor)
        
        if not math.isfinite(valor):
            raise ValueError("FLOAT deve ser um número finito")
        
        else: 
            arq.write(struct.pack(form_float, valor))
            
    except (OverflowError, struct.error):
        raise ValueError("Valor FLOAT fora do intervalo de 64 bits")
 
def ler_float(arq):
    dados = arq.read(8)
    
    if len(dados) != 8:
        raise EOFError("Arquivo incompleto: esperados 8 bytes de um float")
    
    valor = struct.unpack(form_float, dados)[0]
    
    if not math.isfinite(valor):
        raise ValueError("FLOAT inválido no arquivo: NaN ou infinito")
    
    return valor
 
def escrever_bool(arq, valor):
    if not isinstance(valor, bool):
        raise ValueError("BOOL deve ser True ou False")
    
    else:
        arq.write(struct.pack(form_bool, valor))
 
def ler_bool(arq):
    dados = arq.read(1)
    
    if len(dados) != 1:
        raise EOFError("Arquivo incompleto: esperado 1 byte para booleano")
    
    if dados not in (b"\x00", b"\x01"):
        raise ValueError("Marcador booleano inválido")
    
    return struct.unpack(form_bool, dados)[0]
 
def escrever_str(arq, texto):
    if not isinstance(texto, str):
        raise ValueError("STRING deve ser texto")
    
    dados = texto.encode("utf-8")
    
    if len(dados) > tam_str:
        raise ValueError("String maior que 1024 bytes")
    
    if dados.endswith(b"\x00"):
        raise ValueError("String não pode terminar com byte zero")
    
    arq.write(struct.pack(form_str, dados.ljust(tam_str, b"\x00")))
 
def ler_str(arq):
    dados = arq.read(tam_str)
    
    if len(dados) != tam_str:
        raise EOFError("Arquivo incompleto: esperado campo STRING de 1024 bytes")
    
    try:
        return dados.rstrip(b"\x00").decode("utf-8")
    
    except UnicodeDecodeError:
        raise ValueError("Decodificação incompleta, string inválida")
 
def ler_contagem(arq):
    quant = ler_int(arq)
    
    if quant < 0:
        raise ValueError("Quantidade negativa no arquivo")
    
    return quant
 
def escrever_registro(arq, tabela, registro):
    if len(registro) != len(tabela.atributos):
        raise ValueError("Registro com quantidade de valores diferente da quantidade de atributos")
    
    pos = 0
    
    for atributo in tabela.atributos:
        tipo = atributo.tipo
        valor = registro[pos]
        pos = pos + 1
        
        if valor is None: # O None é deixado como espaço vazio, mas sem valor (marcador)
            escrever_bool(arq, True)
            
            if tipo == "INTEGER" or tipo == "FLOAT":
                arq.write(b"\x00" * 8)
            
            elif tipo == "STRING":
                arq.write(b"\x00" * 1024)
            
            elif tipo == "BOOLEAN":
                arq.write(b"\x00")
            
            else:
                raise ValueError(f"Tipo de atributo desconhecido: {tipo}")
        
        else:
            escrever_bool(arq, False)
            
            if tipo == "INTEGER":
                escrever_int(arq, valor)
            
            elif tipo == "FLOAT":
                escrever_float(arq, valor)
            
            elif tipo == "STRING":
                escrever_str(arq, valor)
            
            elif tipo == "BOOLEAN":
                escrever_bool(arq, valor)
            
            else:
                raise ValueError(f"Tipo de atributo desconhecido: {tipo}")
 
def ler_registro(arq, tabela):
    reg = []
    
    for atributo in tabela.atributos:
        tipo = atributo.tipo
        nulo = ler_bool(arq)
        
        if nulo:
            if tipo == "INTEGER" or tipo == "FLOAT":
                tam = 8
            
            elif tipo == "STRING":
                tam = 1024
            
            elif tipo == "BOOLEAN":
                tam = 1
            
            else:
                raise ValueError(f"Tipo de atributo desconhecido: {tipo}")
            
            dados = arq.read(tam)
            
            if len(dados) != tam:
                raise EOFError("Registro incompleto no valor nulo")
            
            reg.append(None)
        
        else:
            if tipo == "INTEGER":
                reg.append(ler_int(arq))
            
            elif tipo == "FLOAT":
                reg.append(ler_float(arq))
            
            elif tipo == "STRING":
                reg.append(ler_str(arq))
            
            elif tipo == "BOOLEAN":
                reg.append(ler_bool(arq))
            
            else:
                raise ValueError(f"Tipo de atributo desconhecido: {tipo}")
    
    return reg

def escrever_usuario(arq, usuario):
    
    escrever_str(arq, usuario.nome)
    escrever_str(arq, usuario.senha)
    escrever_bool(arq, usuario.admin)
    
    # Permissões do banco: {nomebanco: [permissoes]}
    t = 0 # total de permissões
    for lista in usuario.perm_banco.values():
        t += len(lista)
    
    escrever_int(arq, t)
    
    for nome_banco in usuario.perm_banco:
        for permissao in usuario.perm_banco[nome_banco]:
            escrever_str(arq, nome_banco)
            escrever_str(arq, permissao)
    
    # Permissões databela: {"banco.tabela": [permissoes]}
    t = 0 # total de permissões
    for lista in usuario.perm_tabela.values():
        t += len(lista)
    
    escrever_int(arq, t)
    
    for ch in usuario.perm_tabela:
        partes = ch.split(".", 1)
        
        if len(partes) != 2:
            raise ValueError(f"Chave inválida: {ch}")
        
        for perm in usuario.perm_tabela[ch]:
            escrever_str(arq, partes[0])
            escrever_str(arq, partes[1])
            escrever_str(arq, perm)
 
def ler_usuario(arq):
    nome = ler_str(arq)
    senha = ler_str(arq)
    adm = ler_bool(arq)
    
    us = Usuario(nome, senha, adm)
    
    quant = ler_contagem(arq)
    
    for i in range(quant):
        nome_banco = ler_str(arq)
        permissao = ler_str(arq)
        
        if nome_banco not in us.perm_banco:
            us.perm_banco[nome_banco] = []
        
        us.perm_banco[nome_banco].append(permissao)
    
    quant = ler_contagem(arq)
    
    for i in range(quant):
        nome_banco = ler_str(arq)
        nome_tabela = ler_str(arq)
        permissao = ler_str(arq)
        chave = nome_banco + "." + nome_tabela
        
        if chave not in us.perm_tabela:
            us.perm_tabela[chave] = []
        
        us.perm_tabela[chave].append(permissao)
    
    return us
  
def escrever_tabela(arq, tabela):
    escrever_str(arq, tabela.nome)
    escrever_int(arq, len(tabela.atributos))
    
    for atb in tabela.atributos:
        if atb.tipo not in ("INTEGER", "FLOAT", "STRING", "BOOLEAN"):
            raise ValueError(f"Tipo de atributo desconhecido: {atb.tipo}")
        
        else:
            escrever_str(arq, atb.nome)
            escrever_str(arq, atb.tipo)
    
    # A CHave Primária é o atributo com pk = True
    ch_prim = ""
    
    for atb in tabela.atributos:
        if atb.pk:
            ch_prim = atb.nome
    
    escrever_str(arq, ch_prim)
    
    # As CHaves Estrangeiras são os atributos com fk = (tabreferenciada, atbreferenciado)
    ch_est = []
    
    for atb in tabela.atributos:
        if atb.fk is not None:
            ch_est.append((atb.nome, atb.fk[0], atb.fk[1]))
    
    escrever_int(arq, len(ch_est))
    
    for ch in ch_est:
        escrever_str(arq, ch[0])
        escrever_str(arq, ch[1])
        escrever_str(arq, ch[2])
    
    escrever_int(arq, len(tabela.registros))
    
    for registro in tabela.registros:
        escrever_registro(arq, tabela, registro)
 
def ler_tabela(arq):
    nome = ler_str(arq)
    
    nomes_atb = [] # nomes dos atributos
    tipos_atb = [] # tipos dos atributos
    quant = ler_contagem(arq)
    
    for i in range(quant):
        n_atributo = ler_str(arq) # nome de um atributo, o que está sendo lido no momento
        tipo = ler_str(arq)
        
        if tipo not in ("INTEGER", "FLOAT", "STRING", "BOOLEAN"):
            raise ValueError(f"Tipo de atributo desconhecido: {tipo}")
        
        nomes_atb.append(n_atributo)
        tipos_atb.append(tipo)
    
    ch_prim = ler_str(arq)
    
    ch_est = []
    quantidade = ler_contagem(arq)
    
    for i in range(quantidade):
        atributo = ler_str(arq)
        tabela_ref = ler_str(arq)
        atributo_ref = ler_str(arq)
        ch_est.append((atributo, tabela_ref, atributo_ref))
    
    # Agora posso criar os atributos, pois já tenho de pk e fk
    atributos = []
    
    for i in range(len(nomes_atb)):
        fk = None
        
        for ch in ch_est:
            if ch[0] == nomes_atb[i]:
                fk = (ch[1], ch[2])
        
        pk = (nomes_atb[i] == ch_prim)
        atributos.append(Atributo(nomes_atb[i], tipos_atb[i], pk, fk))
    
    tabela = Tabela(nome, atributos)
    
    quantidade = ler_contagem(arq)
    
    for i in range(quantidade):
        tabela.registros.append(ler_registro(arq, tabela))
    
    return tabela
 
def escrever_banco(arq, banco):
    escrever_str(arq, banco.nome)
    escrever_int(arq, len(banco.tabelas))
    
    for tab in banco.tabelas.values():
        escrever_tabela(arq, tab)
 
def ler_banco(arq):
    nome = ler_str(arq)
    banco = Banco(nome)
    
    quant = ler_contagem(arq)
    
    for i in range(quant):
        tab = ler_tabela(arq)
        banco.tabelas[tab.nome] = tab
    
    return banco
 
def escrever_sistema(arq, bancos, usuarios):
    if not isinstance(usuarios, dict):
        raise ValueError("usuarios deve ser um dicionário")
    
    if not isinstance(bancos, dict):
        raise ValueError("bancos deve ser um dicionário")
    
    escrever_int(arq, len(usuarios))
    
    for us in usuarios.values():
        escrever_usuario(arq, us)
    
    escrever_int(arq, len(bancos))
    
    for bc in bancos.values():
        escrever_banco(arq, bc)
 
def ler_sistema(arq):
    usuarios = {}
    quant = ler_contagem(arq)
    
    for i in range(quant):
        us = ler_usuario(arq)
        usuarios[us.nome] = us
    
    bancos = {}
    quant = ler_contagem(arq)
    
    for i in range(quant):
        banco = ler_banco(arq)
        bancos[banco.nome] = banco
    
    return bancos, usuarios
 
def salvar_arquivo(caminho, bancos, usuarios):
    tmp = caminho + ".tmp"
    
    with open(tmp, "wb") as arq:
        escrever_sistema(arq, bancos, usuarios)   # se falhar, o original não foi tocado
    
    os.replace(tmp, caminho)  # substitui um pelo outro, com o tmp desaparecendo da existência ao final 
def carregar_arquivo(caminho):
    # Só devolve os dicionários novos se a leitura inteira der certo.
    # Quem chamar deve substituir o sistema atual somente depois disso:
    # bancos, usuarios = carregar_arquivo(caminho)
    with open(caminho, "rb") as arq:
        bancos, usuarios = ler_sistema(arq)
        
        if arq.read(1) != b"":
            raise ValueError("Arquivo contém bytes extras após os dados")
    
    return bancos, usuarios
 