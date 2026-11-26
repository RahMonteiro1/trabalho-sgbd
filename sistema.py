# Gerencia o banco de dados, as sessões e as operações

from modelos import *
from interpretador import interpretar
from motor_selects import executar_select

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
                        
                    elif cmd["op"] == "SELECT":
                        resultado = self.selecionar(cmd)
                        
                    elif cmd["op"] == "CREATE_USER":
                        resultado = self.criar_usuario(cmd)
                        
                    elif cmd["op"] == "GRANT":
                        resultado = self.conceder(cmd)
                    
                    elif cmd["op"] == "REVOKE":
                        resultado = self.revogar(cmd)
                        
                    elif cmd["op"] == "SHOW_USERS":
                        resultado = self.mostrar_usuarios()
                        
                    elif cmd["op"] == "SHOW_PERMISSIONS":
                        resultado = self.mostrar_permissoes(cmd)
                        
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
 
    def selecionar(self, cmd):
        self.exigir_banco()
        return executar_select(cmd, self.bc_atual.tabelas)
    
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
    
    def criar_usuario(self, cmd):
    # Lê um dicionário da forma abaixo e cria o usuário, de for possível
    # {
    #   'op': 'CREATE_USER',
    #   'nome': 'professor',
    #   'senha': 'senha_professor'
    # }
    
        self.exigir_adm()
        nome = cmd["nome"]
        senha = cmd["senha"]
        
        if nome in self.usuarios:
            raise ValueError("Usuário já existe")
        
        elif not senha:
            raise ValueError("Campo 'senha' está vazio")
        
        else:
            self.usuarios[nome] = Usuario(nome, senha, False)
            
    def conceder(self, cmd):
        self.exigir_adm()

        perm = cmd["perm"].upper()
        bc = cmd["banco"]
        tb = cmd["tabela"]
        us = cmd["usuario"]
        
        if us not in self.usuarios:
            raise ValueError("Usuário inexistente")
        
        if bc not in self.bancos:
            raise ValueError("Banco inexistente")
        
        if tb is not None:
            if tb not in self.bancos[bc].tabelas:
                raise ValueError("Tabela inexistente")
            
            if perm == "CREATE":
                raise ValueError("Operação inválida para tabelas")
            
            self.usuarios[us].conceder(bc, tb, perm)
                
        else:
            self.usuarios[us].conceder(bc, None, perm)
            
    def revogar(self, cmd):
            self.exigir_adm()
    
            perm = cmd["perm"].upper()
            bc = cmd["banco"]
            tb = cmd["tabela"]
            us = cmd["usuario"]
            
            if us not in self.usuarios:
                raise ValueError("Usuário inexistente")
            
            if bc not in self.bancos:
                raise ValueError("Banco inexistente")
            
            if tb is not None:
                if tb not in self.bancos[bc].tabelas:
                    raise ValueError("Tabela inexistente")  
            
            self.usuarios[us].revogar(bc, tb, perm)
                    
    def mostrar_usuarios(self):
        self.exigir_adm()
        
        saida = list()
        for c in self.usuarios:
            if self.usuarios[c].admin:
                saida.append((c, "admin")) 
            
            else:
                saida.append((c, "comum"))
                    
        return saida
    
    def mostrar_permissoes(self, cmd):
        self.exigir_adm()
        
        saida = list()
        try:
            us = self.usuarios[cmd["usuario"]]
        
        except KeyError:
            raise ValueError("O usuário informado não existe")
        
        for c in us.perm_banco:
            for p in us.perm_banco[c]:
                saida.append((c, "*", p))
            
        for c in us.perm_tabela:
            partes = c.split(".")
            for p in us.perm_tabela[c]:
                saida.append((partes[0], partes[1], p))
    
        return saida  
        
    def autorizar(self, banco, tabela, perm): # perm = PERMissão
        pass
