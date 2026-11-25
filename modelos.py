# Classes que representam dados no banco

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
                convertidos.append(tipos.get(self.atributos[i].tipo)(valores[i]))
                
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
        
            
            