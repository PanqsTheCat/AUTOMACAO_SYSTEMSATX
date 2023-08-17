from conexaoSQL import conectaSQL, fecharConexao
from playwright.sync_api import sync_playwright
import concurrent.futures
from time import sleep

class speedBOT:

    def dados_login(self,cliente):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = 'SELECT Email, Senha FROM login WHERE Cliente = %s'
        valor = (cliente,)
        cursor.execute(sql,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        return dados
    
    def clientes(self):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = 'SELECT Cliente FROM dados_clientes ORDER BY Cliente ASC'
        cursor.execute(sql)
        dados = cursor.fetchall()
        lista = []
        for i in dados:
            lista.append(i[0])
        fecharConexao(cursor,conexao)
        return lista
    
    def placas(self,clientes):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = 'SELECT Placa FROM placas WHERE Cliente = %s ORDER BY Placa ASC'
        lista = []
        for cliente in clientes:
            dicio = {}
            valor = (cliente,)
            cursor.execute(sql,valor)
            dados = cursor.fetchall()
            if len(dados) == 0:
                continue
            else:
                dicio['Cliente'] = cliente
                dicio['Placa'] = dados
                lista.append(dicio)
        return lista

    def registra_senha_invalida(self,email,senha):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = 'INSERT INTO clientes_com_login_invalido (Cliente,Email,Senha) VALUES (%s,%s,%s)'
        valor = ('BOT',email,senha)
        cursor.execute(sql,valor)
        conexao.commit()
        fecharConexao(cursor,conexao)

    def valida_senha(self,email,senha):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = 'SELECT Email, Senha FROM clientes_com_login_invalido WHERE Email = %s and Senha = %s'
        valor = (email,senha)
        cursor.execute(sql,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        if len(dados) == 0:
            return False
        else:
            return True
        
    def registra_erro_download(self,cliente,placa):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = 'INSERT INTO logs_error_download_placa (Cliente,Placa) VALUES (%s,%s)'
        valor = (cliente,placa)
        cursor.execute(sql,valor)
        conexao.commit()
        fecharConexao(cursor,conexao)
        
    def playwright(self,dados):
        data_relatorio_inicio = str('01/07/2023')
        data_relatorio_fim = str('31/07/2023')
        placa = dados['Placa']
        cliente = dados['Cliente']
        url = 'https://tracking.systemsatx.com.br/'
        with sync_playwright() as p:
            login = self.dados_login(cliente)
            email = login[0][0]
            senha = login[0][1]
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.fill('xpath=//*[@id="txtUsername"]/div/div[1]/input',email)
            page.fill('xpath=//*[@id="txtSenha"]/div/div[1]/input',senha)
            page.click('xpath=//*[@id="btnSenha"]/div')
            if page.url == 'https://tracking.systemsatx.com.br/Login/Blocked':
                print("="*136)
                print(email," BLOQUED. SEND THIS TO SUP")
                print("="*136,'\n')
            elif page.url == 'https://tracking.systemsatx.com.br/?error=LoginInvalido':
                print("="*136)
                print(email," INVALID LOGIN. SEND THIS TO SUP")
                print("="*136,'\n')
            elif page.url == 'https://tracking.systemsatx.com.br/?error=LoginSenhaInvalido':
                valida = self.valida_senha(email,senha)
                if valida == False:
                    self.registra_senha_invalida(email,senha)
            elif page.url == 'https://tracking.systemsatx.com.br/Home':
                for plate in placa:
                    print("="*136)
                    print('STARTING DOWNLOAD OF CLIENT:', cliente,'AND PLATE: ',plate[0])
                    page.click('xpath=//*[@id="Menu_4"]')
                    page.click('xpath=//*[@id="Menu_24"]')
                    page.wait_for_url('https://tracking.systemsatx.com.br/Relatorios/Geral')
                    page.locator('xpath=/html/body/div[1]/div/div[3]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div/form/ul/li[5]/div/div/span/div[1]/div/div[1]/input').fill(plate[0])
                    sleep(1)
                    page.keyboard.press('Enter')
                    sleep(1)
                    page.click('xpath=/html/body/div[9]/div/div[2]/div/div[2]/div[1]/div/div/div')
                    sleep(1)
                    page.click('xpath=//*[@id="DataInicio"]/div/div/div[1]/input')
                    sleep(1)
                    page.keyboard.press('Control+A')
                    page.keyboard.press('Delete')
                    sleep(1)
                    page.keyboard.type(data_relatorio_inicio+str('0000'))
                    sleep(1)
                    page.keyboard.press('Tab')
                    sleep(1)
                    page.keyboard.press('Tab')
                    sleep(1)
                    page.keyboard.type(data_relatorio_fim+str(' 00:00'))
                    verifica_placa_in_input = page.is_hidden('xpath=/html/body/div[1]/div/div[3]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div/form/ul/li[5]/div/div/span/div[1]/div/div[1]/div[2]')
                    if verifica_placa_in_input == False:
                        print('WARNING ERROR PLATE: ',placa[0])
                        self.registra_erro_download(cliente,placa[0])
                    page.click('xpath=//*[@id="listaAcao-btnConsultar"]/div')
                    sleep(75)
                    page.click('xpath=//*[@id="ExportMenu"]')
                    mes = data_relatorio_inicio[3]+data_relatorio_inicio[4]
                    sleep(75)
                    with page.expect_download() as file:
                        sleep(75)
                        download = file.value
                        download.save_as(path='/media/RelatoriosSSX/'+cliente+'/'+plate[0]+'/'+'01_'+str(mes)+'_2023'+'.xlsx')
                        print(f'PLATE: {plate[0]}, SAVE WITH SUCCESS!')
                        self.registroDB(cliente,plate[0],mes)
                    page.click('xpath=//*[@id="Menu_4"]')
                    page.click('xpath=//*[@id="Menu_24"]')
                    print("="*136,'\n')
            else:
                print("="*136)
                print('Erro desconhecido',page.url,email)
                print("="*136,'\n')


    def registroDB(self,cliente,placa,mes):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = """INSERT INTO placas_retiradas_web (Cliente,Placa,Mes,Motivo) VALUES(%s,%s,%s,%s)"""
        motivo = 'Relatorio mensal'
        valor = (cliente,placa,mes,motivo)
        cursor.execute(sql,valor)
        conexao.commit()
        cursor.close()
        fecharConexao(cursor,conexao)

    def run(self):
        clientes = self.clientes()
        placas = self.placas(clientes)
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=4)
        results = executor.map(self.playwright,placas)
        

if __name__ == '__main__':
    bot = speedBOT()
    bot.run()