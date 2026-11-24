# Gerencia o banco de dados, as sessões e as operações

from modelos import *
from interpretador import interpretar

class Sistema:
    def __init__(self):
        self.bancos = dict()
        self.usuarios = {
            "Admin" : Usuario("Admin", "123456", True)
        }
        self.us_atual = None # Gerenciador de estado - USuário atual
        self.bc_atual = None # Gerenciador de estado - BanCo atual
        
    def consulta(self, texto):            
            try:
                if self.us_atual is None:
                    raise ValueError("Não existe usuário logado")
                
                else:
                    cmd = interpretar(texto)
                
                    if cmd["op"] == "CREATE_DATABASE":
                        resultado = self.criar_banco(cmd)
                    
                    elif cmd["op"] == "CREATE_TABLE":
                        resultado = self.criar_tabela(cmd)
        
                    elif cmd["op"] == "USE_DATABASE":
                        resultado = self.usar_banco(cmd)
                    
                    elif cmd["op"] == "INSERT":
                        resultado = self.inserir(cmd)
                        
                    else:
                        raise ValueError(f"Comando {cmd} não reconhecido") #esse erro cai no próprio catch
                    
                    if resultado is None:
                        return [True]
                    
                    else:
                        return resultado
                    
            except Exception as erro: # o programa pode gerar value, key, type e index error, que são subclasses de exception
                print(f"Operação inválida {erro}")
                return [False]
                
    def login(self, nome, senha):
        if self.us_atual is None:
            if nome not in self.usuarios.keys():
                return False
            
            else:
                u = self.usuarios[nome]
                if u.senha == senha:
                    self.us_atual = u
                    return True
                
                else:
                    return False
            
        else:
            return False
        
    def logout(self):
        if self.us_atual is None:
            return False
        
        else:
            self.us_atual = None
            self.bc_atual = None
            return True

    def salvar(self, path): # path = caminho dos arquivos
        pass
    
    def carregar(self, path):
        pass
        
    def criar_banco(self, cmd): # cmd = CoManDo SQL já interpretado (em dicionário)
        self.exigir_adm()
        
        nome = cmd["nome"]
        
        if nome in self.bancos:
            raise ValueError("Não são permitidos bancos com nomes duplicados")
        
        else:
            self.bancos[nome] = Banco(nome)
            return        
    
    def usar_banco(self, cmd):
        nome = cmd["nome"]
        
        if nome in self.bancos:
            self.bc_atual = self.bancos[nome]
            return
            
        else:
            raise ValueError(f"Banco {nome} não existe")
    
    def criar_tabela(self, cmd):
        self.exigir_banco()

        col = list()
        
        for dic in cmd["colunas"]:
            a = Atributo(dic["nome"], dic["tipo"], dic["pk"], dic["fk"])
            col.append(a)
        
        self.bc_atual.criar_tabela(cmd["nome"], col)
    
    def inserir(self, cmd):
        self.exigir_banco()
        
        self.bc_atual.inserir(cmd["tabela"], cmd["valores"])
    
    def exigir_adm(self):
        if self.us_atual is not None:
            if self.us_atual.admin:
                return
            
            else:
                raise ValueError("Operação restrita ao administrador")
        
        else:
            raise ValueError("Não existe usuário autenticado")
    
    def exigir_banco(self):
        if self.bc_atual is not None:
            return 
            
        else:
            raise ValueError("Nenhum banco de dados selecionado")
    
    def autorizar(self, banco, tabela, perm): # perm = PERMissão
        pass
    