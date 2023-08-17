from conexaoSQL import conectaSQL, fecharConexao
import pandas as pd

def tabela_dados_cliente_1():
    conexao = conectaSQL(1)
    cursor = conexao.cursor()
    sql = "SELECT Cliente FROM dados_clientes ORDER BY Cliente"
    cursor.execute(sql)
    results = cursor.fetchall()
    lista = []
    for i in results:
        cliente = i[0]
        lista.append(cliente)
    df = pd.DataFrame(lista,columns=['Cliente tabela'])
    fecharConexao(cursor,conexao)
    return df

def tabela_dados_cliente_2():
    conexao = conectaSQL(1)
    cursor = conexao.cursor()
    sql = "SELECT Cliente FROM login ORDER BY Cliente"
    cursor.execute(sql)
    results = cursor.fetchall()
    lista = []
    for i in results:
        cliente = i[0]
        lista.append(cliente)
    df = pd.DataFrame(lista,columns=['Cliente tabela'])
    fecharConexao(cursor,conexao)
    return df

def analise_das_duas_tabelas():
    df1 = tabela_dados_cliente_1()
    df2 = tabela_dados_cliente_2()
    df3 = df1.merge(df2, on=['Cliente tabela'], how='outer', suffixes=['','_'], indicator=True)
    df3.to_excel('./dados_sql_clienteXlogin/dados_das_2_tabelas.xlsx')

def gerar_excel_com_analise_completa():
    df = pd.read_excel('./dados_sql_clienteXlogin/dados_das_2_tabelas.xlsx')
    lista = []
    cliente_sem_login = 0
    for index,row in df.iterrows():
        cliente = row[1]
        validador = row[2]
        if validador == 'both':
            continue
        elif validador == 'left_only':
            cliente_sem_login += 1
            lista.append(cliente)
            
        elif validador == 'right_only':
            # verificar se não esta bloqueado
            conexao = conectaSQL(1)
            cursor = conexao.cursor()
            sql = 'SELECT DISTINCT Cliente FROM clientes_bloqueados WHERE Cliente = %s'
            valor = (cliente,)
            cursor.execute(sql,valor)
            verificacao = cursor.fetchall()
            fecharConexao(cursor,conexao)
            
            if len(verificacao) == 1:
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = "UPDATE login SET Ativação = 'BLOQ' WHERE Cliente = %s"
                valor = (str(cliente),)
                cursor.execute(sql,valor)
                fecharConexao(cursor,conexao)
            else: # deletar do banco login
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = 'DELETE FROM login WHERE Cliente = %s'
                valor = (cliente,)
                cursor.execute(sql,valor)
                fecharConexao(cursor,conexao)
        else: continue
    print('Total de Clientes sem Login:',cliente_sem_login)
    return lista

def bloqueio():
    df = pd.read_excel('./dados_sql_clienteXlogin/dados_das_2_tabelas.xlsx')
    for index,row in df.iterrows():
        cliente = row[1]
        validador = row[2]
        if validador == 'right_only':
            conexao = conectaSQL(1)
            cursor = conexao.cursor()
            sql = 'SELECT DISTINCT Cliente FROM clientes_bloqueados WHERE Cliente = %s'
            valor = (cliente,)
            cursor.execute(sql,valor)
            verificacao = cursor.fetchall()
            fecharConexao(cursor,conexao)
            if len(verificacao) >= 1:
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = "UPDATE login SET Ativação = 'BLOQ' WHERE Cliente = %s"
                valor = (cliente,)
                cursor.execute(sql,valor)
                verificacao = cursor.fetchall()
                fecharConexao(cursor,conexao)
            else: 
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = "DELETE FROM login WHERE Cliente = %s"
                valor = (cliente,)
                cursor.execute(sql,valor)
                fecharConexao(cursor,conexao)
        else:
            continue