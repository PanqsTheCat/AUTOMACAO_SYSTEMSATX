import pandas as pd 
from playwright.sync_api import sync_playwright
from time import sleep
from conexaoSQL import conectaSQL,fecharConexao
from datetime import datetime


def getPlacas():
    url = 'http://tracking.systemsatx.com.br/'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.fill('xpath=//*[@id="txtUsername"]/div/div[1]/input','SEU EMAIL AQUI')
        page.fill('xpath=//*[@id="txtSenha"]/div/div[1]/input','SUA SENHA AKI')
        page.click('xpath=//*[@id="btnSenha"]/div')
        page.click('xpath=//*[@id="Menu_7"]')
        page.click('xpath=//*[@id="Menu_79"]')
        page.click('#grid > div > div.dx-datagrid-header-panel.ExibirDatagridPanel > div > div > div.dx-toolbar-after > div:nth-child(4) > div > div > div')
        with page.expect_download() as downloadfile:
            sleep(5)
            download = downloadfile.value
            download.save_as(path=r'./data/Placas.xlsx')

def getClientes():
    url = 'http://tracking.systemsatx.com.br/'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.fill('xpath=//*[@id="txtUsername"]/div/div[1]/input','SEU EMAIL AQUI')
        page.fill('xpath=//*[@id="txtSenha"]/div/div[1]/input','SUA SENHA AKI')
        page.click('xpath=//*[@id="btnSenha"]/div')
        page.click('xpath=//*[@id="Menu_7"]')
        page.click('xpath=//*[@id="Menu_102"]')
        page.click('#grid > div > div.dx-datagrid-header-panel.ExibirDatagridPanel > div > div > div.dx-toolbar-after > div:nth-child(4)')
        with page.expect_download() as downloadfile:
            sleep(5)
            download = downloadfile.value
            download.save_as(path=r'./data/Clientes.xlsx')

def dellPlacasDB():
    conexao = conectaSQL(1)
    cursor = conexao.cursor()
    sql = "DELETE FROM placas WHERE placa = placa"
    cursor.execute(sql)
    conexao.commit()
    fecharConexao(cursor,conexao)

def dellCLientesDB():
    conexao = conectaSQL(1)
    cursor = conexao.cursor()
    sql = "DELETE FROM dados_clientes WHERE Cliente = Cliente"
    cursor.execute(sql)
    conexao.commit()
    fecharConexao(cursor,conexao)

def addPlacasDB():
    df = pd.read_excel(r'./teste/Clientes.xlsx')
    loc = df.loc[:,['Nome','Family','Tracking','Ativo','Bloqueado']]
    ordemAlf = loc.sort_values(by=['Nome'],ascending=True,na_position='first')
    df2 = pd.read_excel(r'./teste/Placas.xlsx')
    loc2 = df2.loc[:,['Cliente','Identificação','Rastreador']]
    ordemAlf2 = loc2.sort_values(by=['Cliente'],ascending=True,na_position='first')
    for index,row in ordemAlf.iterrows():
        cliente = row['Nome']
        family = row['Family']
        tracking = row['Tracking']
        ativo = row['Ativo']
        block = row['Bloqueado']
        plataforma = 'SSX'
        if family == 'Ativado':
            continue
        elif family == 'Não ativado' and tracking == 'Não ativado':
            continue
        elif family == 'Ativado' and tracking == 'Ativado':
            continue
        elif ativo == 'Sim' and block == 'Sim' or ativo == 'Não' and block == 'Sim':
            for index,row in ordemAlf2.iterrows():
                cliente2 = row['Cliente']
                placa = row['Identificação']
                if cliente == cliente2:
                    print(cliente,placa,'Adionado.')
                    conexao = conectaSQL(1)
                    cursor = conexao.cursor()
                    sql = "INSERT INTO placas_clientes_bloqueados (Placa,Cliente,Plataforma) VALUES (%s,%s,%s)"
                    valores = (placa,cliente2,plataforma)
                    cursor.execute(sql,valores)
                    conexao.commit()
                    fecharConexao(cursor,conexao)
        else:
            for index,row in ordemAlf2.iterrows():
                cliente2 = row['Cliente']
                placa = row['Identificação']
                rastreador = row['Rastreador']
                validacao = str(rastreador)
                if cliente == cliente2 and validacao == 'nan':
                    conexao = conectaSQL(1)
                    cursor = conexao.cursor()
                    sql = "INSERT INTO placas_sem_rastreador (Cliente,Placa) VALUES (%s,%s)"
                    valores = (cliente2,placa)
                    cursor.execute(sql,valores)
                    conexao.commit()
                    fecharConexao(cursor,conexao)
                elif cliente == cliente2 and validacao != 'nan':
                    print(cliente,cliente2,placa,plataforma)
                    conexao = conectaSQL(1)
                    cursor = conexao.cursor()
                    sql = "INSERT INTO placas (Placa,Cliente,Plataforma) VALUES (%s,%s,%s)"
                    valores = (placa,cliente2,plataforma)
                    cursor.execute(sql,valores)
                    conexao.commit()
                    fecharConexao(cursor,conexao)
                else:
                    continue
    print('Placas Adicionadas com sucesso!!!')

def verifica_cadastro(cliente):
    conexao = conectaSQL(1)
    cursor = conexao.cursor()
    sql = 'SELECT Cliente FROM relatorio_clientes_bloqueados WHERE Cliente = %s'
    valor = (cliente,)
    cursor.execute(sql,valor)
    dados = cursor.fetchall()
    fecharConexao(cursor,conexao)
    return len(dados)

def date_time():
    data = datetime.today()
    data = data.isoformat()
    ano = data[0:4]
    mes = data[5:7]
    dia = "01"
    data_formated = dia + "/" + mes + "/" + ano
    return data_formated

def addDadosClienteDB():
    df = pd.read_excel(r'./teste/Clientes.xlsx')
    loc = df.loc[:,['Nome','Family','Tracking','Tipo cliente','Ativo','Bloqueado']]
    loc1 = df.sort_values(by=['Nome'],ascending=True,na_position='first')
    for index,row in loc1.iterrows():
        cliente = row['Nome']
        family = row['Family']
        tracking = row['Tracking']
        tipoCliente = row['Tipo cliente'] # pessoa fisica ou juridica
        ativo = row['Ativo']
        block = row['Bloqueado']
        if family == 'Ativado':
            continue
        elif family == 'Não ativado' and tracking == 'Não ativado':
            continue
        elif family == 'Ativado' and tracking == 'Ativado':
            continue
        elif cliente == 'Teste Gado':
            continue
        elif cliente == 'TESTE EQUIP. ALESSANDRA':
            continue
        elif cliente == 'Cliente Teste SSX':
            continue
        elif cliente == 'ClienteTesteSystemSat':
            continue
        elif cliente == 'CLLICK SOLUTIONS':
            continue
        elif ativo == 'Sim' and block == 'Sim':
            # VERIFICAR SE JA ESTA CADASTRADO
            if verifica_cadastro(cliente) == 0:
                conexao = conectaSQL(1)
                cursor = conexao.cursor()
                sql = "INSERT INTO relatorio_clientes_bloqueados (cliente,meses_bloqueado,mes_1) VALUES(%s,%s,%s)"
                valores = (cliente,)
                cursor.execute(sql,valores)
                conexao.commit()
                fecharConexao(cursor,conexao)
                continue
            else:
                ''
        else:
            conexao = conectaSQL(1)
            cursor = conexao.cursor()
            sql = "INSERT INTO dados_clientes (Cliente,TipoCliente,Tracking) VALUES (%s,%s,%s)"
            valores = (cliente,tipoCliente,tracking)
            cursor.execute(sql,valores)
            conexao.commit()
            fecharConexao(cursor,conexao)
    print('Dados Adicionados com Sucesso!!!')