# Classes que representam dados no banco

import math

tipos = {
    "INTEGER": int,
    "FLOAT": float,
    "STRING": str,
    "BOOLEAN": bool
}

permissoes = ["SELECT", "INSERT", "CREATE"]

def compativel(tipo, valor):
    if tipo not in tipos:
        return False
    
    if tipo == "BOOLEAN" and isinstance(valor, bool):
        return True
    
    elif tipo == "INTEGER" and isinstance(valor, int) and not isinstance(valor, bool):
        return True
    
    elif tipo == "STRING" and isinstance(valor, str):
        return True
    
    elif tipo == "FLOAT" and (isinstance(valor, float) or isinstance(valor, int)) and not isinstance(valor, bool):
        return True
    
    else: 
        return False

def cabe_formato(tipo, valor):
    if tipo == "STRING":
        if len(valor.encode("utf-8")) <= 1024:
            return True
        
        else:
            return False
        
    elif tipo == "INTEGER":
        if valor >= -(2 ** 63) and valor <= (2 ** 63) - 1:
            return True
        
        else:
            return False

    elif tipo == "FLOAT":
        if math.isfinite(valor):
            return True
        
        else:
            return False
    
    else:
        return True
    
class Atributo:
    def __init__(self, nome, tipo, pk = False, fk = None):
        self.nome = nome
        self.tipo = tipo     
        self.pk = pk
        self.fk = fk  
        
class Tabela:
    def __init__(self, nome, atributos):
        self.nome = nome
        self.atributos = atributos
        self.registros = []

        # Invalida nomes iguais
        vistos = set()
        for a in atributos:
            if a.nome not in vistos:
                vistos.add(a.nome)
            
            else:
                raise ValueError("Atributos devem possuir nomes distintos")
        
        # Invalida tipos que não existem
        for a in atributos:
            if a.tipo not in tipos:
                raise TypeError("Tipo de dado incompatível\nSão aceitos: INTEGER, FLOAT, BOOLEAN e STRING")
        
        # invalida se o número de PK's != 1
        cpk = 0
        for a in atributos:
            if a.pk:
                cpk += 1
        
        if cpk == 0:
            raise ValueError("A tabela atual possui 0 chaves primárias")
        
        elif cpk > 1:
            raise ValueError("A tabela atual possui mais de uma chave primária")
        
  
    # Descobre o índice da coluna alvo
    def indice(self, alvo):
        for i in range(len(self.atributos)):
            if self.atributos[i].nome == alvo:
                return i
                    
        raise ValueError(f"Coluna {alvo} não encontrada")
    
    # Cria uma nova lista de valores com seus tipos corretos
    def converter(self, valores):
        if len(valores) != len(self.atributos):
            raise ValueError("O número de valores a serem inseridos deve coincidir com o número de colunas na tabela")

        # Testa compatibildade entre um valor e um tipo; ex: 25 sem aspas e integer
        # À essa altura, as listas tem o mesmo tamanho, e as colunas vão ser avaliadas por ordem de inserção
        convertidos = []
        for i in range(len(valores)):
            if valores[i] is None:
                convertidos.append(valores[i])
            
            elif not compativel(self.atributos[i].tipo, valores[i]):
               raise TypeError(f"Tentativa de converter {valores[i]} para {self.atributos[i].tipo}")
            
            else:
                tipo = self.atributos[i].tipo
                novo = tipos.get(tipo)(valores[i])
                
                if not cabe_formato(tipo, novo):
                    raise ValueError(f"O valor não cabe no formato de armazenamento ({tipo})")
                
                else:
                    convertidos.append(novo)
                
        return convertidos           
        
    def unica_pk(self, valores):     
        # Descobre qual o índice da coluna pk
        ipk = None
        for i in range(len(self.atributos)):
            if self.atributos[i].pk:
                ipk = i
                break
        
        # Verifica nulidade
        if valores[ipk] is None:
            raise ValueError("A chave primária da tabela não pode ser nula")
        
        # percorre os registros e vê se o elemento armazenado na coluna de índice pk é igual ao valor
        for r in self.registros:
            if r[ipk] == valores[ipk]:
                raise ValueError(f"{valores[ipk]} já definido na tabela")
    
    def existe_pk(self, valor):
        # Descobre qual o índice da coluna pk
        ipk = None
        for i in range(len(self.atributos)):
            if self.atributos[i].pk:
                ipk = i
                break
        
        for reg in self.registros:
            if reg[ipk] == valor:
                return True
        
        return False
                         
class Banco:
    def __init__(self, nome):
        self.nome = nome
        self.tabelas = dict()
        
        # Ideia de estrutura do dicionário:
        # tabelas = {
        #     "alunos": objeto do tipo Tabela,
        #     "disciplinas": objeto do tipo Tabela
        # }
        
    def criar_tabela(self, nome, atributos):
        if nome in self.tabelas.keys():
            raise ValueError(f"A tabela {nome} já existe")
        
        # verificar fk
        for a in atributos:
            achou = False
            if a.fk is not None:
                ntref = a.fk[0] # Nome da Tabela REFerenciada 
                naref = a.fk[1] # Nome do Atributo REFerenciado
                
                if ntref not in self.tabelas:
                    raise ValueError("Chave estrangeira não referencia uma tabela existente")
                
                else:
                    tref = self.tabelas[ntref] # objeto Tabela REFerenciada
                    
                    for at in tref.atributos: # at = ATributo
                        if at.nome == naref:
                            aref = at # objeto Atributo REFerenciado
                            achou = True
                            
                            if not aref.pk:
                                raise ValueError("A chave estrangeira deve referenciar uma chave primária de outra tabela")

                            if aref.tipo != a.tipo:
                                raise ValueError("Os atributos possuem tipos incompatíveis")
        
                    if not achou:
                        raise ValueError("O atributo referenciado pela chave estrangeira não existe")
        
        self.tabelas[nome] = Tabela(nome, atributos)
        return None
                
    def inserir(self, nome_tabela, valores):
        if nome_tabela not in self.tabelas:
            raise ValueError(f"A tabela {nome_tabela} deve existir para receber valores")

        else:
            tabela = self.tabelas.get(nome_tabela)
            convertidos = tabela.converter(valores)
            tabela.unica_pk(convertidos)
            
            # Verifica se o valor da fk existe na tabela referenciada
            for atr in tabela.atributos:
                if atr.fk is not None:
                    ntref = atr.fk[0] # Nome da Tabela REFerenciada
                    tref = self.tabelas[ntref] # objeto Tabela REFerenciada
                    ifk = tabela.indice(atr.nome) 
                    
                    if not tref.existe_pk(convertidos[ifk]):
                        raise ValueError(f"Chave estrangeira {convertidos[ifk]} não encontrada na tabela {ntref}")
            
            tabela.registros.append(convertidos)
            return None

class Usuario:
    def __init__(self, nome, senha, admin=False):
        self.nome = nome
        self.senha = senha
        self.perm_banco = dict() # universidade: select  // nomebanco: permissoes
        self.perm_tabela = dict() # aluno: select       // nometabela : permissoes
        self.admin = admin
        
    def conceder(self, banco, tabela, perm): # tabela: nome da tabela ou None, caso seja para o banco inteiro
        perm = perm.upper()
        todos = False
        if perm == "ALL":
            todos = True
        
        if not todos and (perm not in permissoes):
            raise ValueError("Permissão inválida")
        
        else:
            if tabela is None:                
                if not todos and banco not in self.perm_banco:
                    self.perm_banco[banco] = [perm]
                
                elif not todos and perm not in self.perm_banco[banco]:
                    self.perm_banco[banco].append(perm)
                    
                elif todos:
                    self.perm_banco[banco] = ["SELECT", "INSERT", "CREATE"]
                
            else:
                ch = banco + "." + tabela
                if not todos and ch not in self.perm_tabela:
                    self.perm_tabela[ch] = [perm]
                    
                elif not todos and perm not in self.perm_tabela[ch]:
                    self.perm_tabela[ch].append(perm)
                
                elif todos:
                    self.perm_tabela[ch] = ["SELECT", "INSERT"]
            
    def revogar(self, banco, tabela, perm):
        perm = perm.upper()
        todos = False
        if perm == "ALL":
            todos = True
        
        if not todos and (perm not in permissoes):
            raise ValueError("Permissão inválida")
        
        else:
            if tabela is None:
                if banco not in self.perm_banco:
                    pass
                                
                elif not todos and perm in self.perm_banco[banco]:
                    self.perm_banco[banco].remove(perm)
                    
                    if len(self.perm_banco[banco]) == 0:
                        del self.perm_banco[banco]    
                    
                elif todos:
                    del self.perm_banco[banco]
                
            else:
                ch = banco + "." + tabela
                if ch not in self.perm_tabela:
                    pass
                
                elif not todos and perm in self.perm_tabela[ch]:
                    self.perm_tabela[ch].remove(perm)
                    
                    if len(self.perm_tabela[ch]) == 0:
                        del self.perm_tabela[ch]
                
                elif todos:
                    del self.perm_tabela[ch]
    
    def tem_permissao(self, banco, tabela, perm):
        if self.admin:
            return True
        
        if tabela is None:
            if (banco in self.perm_banco) and (perm in self.perm_banco[banco]):
                return True
                
            else:
                return False
       
        else:
            ch = banco + "." + tabela
            
            if (banco in self.perm_banco) and (perm in self.perm_banco[banco]): 
                # Se tenho determinada permissão no banco, tenho na tabela
                return True
            
            if (ch in self.perm_tabela) and (perm in self.perm_tabela[ch]):
                return True
                
            else:
                return False
               
    def acessa_banco(self, banco):
        if self.admin:
            return True
        
        if (banco in self.perm_banco) and len(self.perm_banco[banco]) != 0:
            return True
        
        for ch in self.perm_tabela.keys():
            if ch.startswith(banco + "."): 
                for lp in self.perm_tabela[ch]:
                    if len(lp) != 0:
                        return True
                
        return False