import requests
from bs4 import BeautifulSoup
from verifica_cliente_login_sys import *
from conexaoSQL import conectaSQL, fecharConexao

class scrapy:
    results = []

    data_list = []

    pandas_list = []

    def data_log_in(self,url):
        site = url
        valores = {'login':'','senha':''}
        with requests.Session() as s:
            r = s.post(site,data=valores)
            return s.get('http://www.cllick.com.br/')
            
    def parse(self,html):
        content = BeautifulSoup(html,'lxml')
        tabela = content.find('table', {'id':'tabela_dados'})
        tag = tabela.find_all(attrs={'valign':'middle'})
        for index,i in enumerate(tag):

            if i.string is None:
                i = 'dado não informado'
                self.results.append(i)
            elif index == index:
                self.results.append(i.string)
            else: continue

    def organizer_data_base(self,id):
        validador = id in self.results
        for i in self.results:
            if validador == False:
                continue
            else:
                request_data = self.results.index(str(id)) #id
                email = request_data - 1
                sistema = request_data + 1
                senha = request_data + 2
                return request_data,email,sistema,senha
        
    def clientes_sem_login(self):
        tabela_dados_cliente_1()
        tabela_dados_cliente_2()
        analise_das_duas_tabelas()
        bloqueio()
        lista = gerar_excel_com_analise_completa()
        return lista
    
    def dados_login(self):
        for x in self.clientes_sem_login():
            data = self.organizer_data_base(x)
            if data == None:
                continue
            else:
                self.data_list.append(data)

    def get_dados_from_list(self):
        dados_cliente = self.data_list
        for dado in dados_cliente:
            lista = []
            for elemento in dado:
                lista.append(self.results[elemento])
            self.pandas_list.append(lista)

    def append_db(self):
        dados_clientes = self.pandas_list
        for x in dados_clientes:
            cliente = x[0]
            email = x[1]
            plataforma = x[2].upper()
            senha = x[3]
            verifica_db = self.exist_sql_query(cliente)
            if verifica_db == True and plataforma != 'SSX-BLOQUEADO': #True = lista vazia não existe no banco de dados 
                status = 'ATIVO'
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = 'INSERT INTO login (Cliente,Email,Senha,Plataforma,Ativação) VALUES(%s,%s,%s,%s,%s)'
                valores = (cliente,email,senha,plataforma,status)
                cursor.execute(sql,valores)
                conexao.commit()
                conexao.close()
                fecharConexao(cursor,conexao)

            elif verifica_db == False and plataforma != 'SSX-BLOQUEADO': #False = lista que contem algo e existe no banco de dados
                status = 'ATIVO'
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = "UPDATE login SET Cliente = %s, Email = %s, Senha = %s, Plataforma = %s, Ativação = %s WHERE Cliente = %s"
                valores = (cliente,email,senha,plataforma,status,cliente)
                cursor.execute(sql,valores)
                conexao.commit()
                conexao.close()
                fecharConexao(cursor,conexao)

            elif verifica_db == False and plataforma == 'SSX-BLOQUEADO':
                status = 'BLOQ'
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = "UPDATE login SET Cliente = %s, Email = %s, Senha = %s, Plataforma = %s, Ativação = %s WHERE Cliente = %s"
                valores = (cliente,email,senha,plataforma,status,cliente)
                cursor.execute(sql,valores)
                conexao.commit()
                conexao.close()
                fecharConexao(cursor,conexao)

            else:
                status = 'BLOQ'
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = 'INSERT INTO login (Cliente,Email,Senha,Plataforma,Ativação) VALUES(%s,%s,%s,%s,%s)'
                valores = (cliente,email,senha,plataforma,status)
                cursor.execute(sql,valores)
                conexao.commit()
                conexao.close()
                fecharConexao(cursor,conexao)

    def exist_sql_query(self,cliente):
        sql_query = 'SELECT Cliente FROM login WHERE EXISTS (SELECT Cliente FROM login WHERE Cliente = %s)'
        valor = (str(cliente),)
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        cursor.execute(sql_query,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        return not dados

    def run(self): 
        response = self.data_log_in('http://www.cllick.com.br')
        self.parse(response.text)
        self.dados_login()
        self.get_dados_from_list()
        self.append_db()
   


   
if __name__ == '__main__':
    scraper = scrapy()
    scraper.run()