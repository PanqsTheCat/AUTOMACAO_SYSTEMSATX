from playwright.sync_api import sync_playwright
from time import sleep
import pandas as pd
from conexaoSQL import conectaSQL, fecharConexao
from datetime import datetime
import os


class botSSX:

    os_name = os.name

    path_name = os.getlogin()

    excluir = []

    relatorio = []

    def download_database(self):
        url = "LINK DO SEU FORMULARIO AQUI"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.click('xpath=//*[@id="docs-file-menu"]')
            page.keyboard.press("ArrowDown")
            page.keyboard.press("ArrowRight")
            page.keyboard.press("Enter")
            with page.expect_download() as file:
                download = file.value
                download.save_as(path=f"/home/{self.path_name}/projetos/{self.os_name}/dados_relatorio_web_auto/placas_para_tirar_relatorio.xlsx")

    def debug(self):
        df = pd.read_excel(f'/home/{self.path_name}/projetos/{self.os_name}/dados_relatorio_web_auto/placas_para_tirar_relatorio.xlsx')
        loc = df.loc[:,["Nome_do_Cliente", "Placa_do_Cliente"]]
        filtro = loc.sort_values(by=["Nome_do_Cliente"],ascending=True, na_position='first')
        for index,row in filtro.iterrows():
            placa = row[1].strip()
            cliente = row[0].strip()
            if len(self.analise_banco_placas(cliente,placa)) != 0:
                if len(self.verifica_excluido(placa)) == 0:
                    self.relatorio.append({cliente:placa})
                    self.excluir.append({cliente:placa})
                else:
                    continue
            else:
                if len(self.analise_banco_sem_rastreador(cliente,placa)) != 0:
                    if len(self.verifica_excluido(placa)) == 0:
                        self.relatorio.append({cliente:placa})
                        self.excluir.append({cliente:placa})
                    else:
                       continue
   
    def analise_banco_placas(self,cliente,placa):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "SELECT Cliente, Placa FROM placas WHERE Cliente = %s and Placa = %s"
        valor = (cliente,placa)
        cursor.execute(sql,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        return dados

    def analise_banco_sem_rastreador(self,cliente,placa):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "SELECT Cliente, Placa FROM placas_sem_rastreador WHERE Cliente = %s and Placa = %s"
        valor = (cliente,placa)
        cursor.execute(sql,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        return dados

    def verifica_relatorio(self,placa):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "SELECT Placa FROM placas_retiradas_web WHERE Placa = %s"
        valor = (placa,)
        cursor.execute(sql,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        return dados

    def verifica_excluido(self,placa):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "SELECT Placa FROM placas_excluidas WHERE Placa = %s"
        valor = (placa,)
        cursor.execute(sql,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        return dados
    
    def dataAno(self):
        data = datetime.today()
        data = data.isoformat()
        ano = data[0:4]
        return ano

    def dataHoraInicio(self):
        data = datetime.today()
        data = data.isoformat()
        ano = data[0:4]
        mes = data[5:7]
        dia = "01"
        dataInicio = dia + "/" + mes + "/" + ano
        return dataInicio

    def dataHoraFim(self):
        data = datetime.today()
        data = data.isoformat()
        ano = data[0:4]
        mes = data[5:7]
        dia = data[8:10]
        dataFinal = dia + "/" + mes + "/" + ano
        return dataFinal
    
    def dataHoraNow(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return dt_string
    
    def getLogin(self,cliente):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "SELECT Email, Senha FROM login WHERE Cliente = %s"
        valor = (cliente,)
        cursor.execute(sql,valor)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        return dados

    def registra_retirada(self,cliente,placa,mes,motivo):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "INSERT INTO placas_retiradas_web (Cliente,Placa,Mes,Motivo) VALUES(%s,%s,%s,%s)"
        valor = (cliente,placa,mes,str(motivo))
        cursor.execute(sql,valor)
        conexao.commit()
        fecharConexao(cursor,conexao)

    def registra_exclusao(self,cliente,placa):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "INSERT INTO placas_excluidas (Cliente,Placa) VALUES(%s,%s)"
        valor = (cliente,placa)
        cursor.execute(sql,valor)
        conexao.commit()
        fecharConexao(cursor,conexao)

    def download_relatorio(self,dados) -> list:
        """dados = list[{cliente:placa}]  recebe uma lista de dicionario contendo cliente e placa"""
        dataI = self.dataHoraInicio()
        dataF = self.dataHoraFim()
        data = dados
        if len(data) == 0:
            print("ALL DOWNLOAD'S DONE NOTHING TO DO", self.dataHoraNow())
        else:
            for i in data:
                print(i)
                cliente = list(i.keys())
                placa = list(i.values())
                login = self.getLogin(cliente[0])
                if len(login) == 0:
                    print('LOGIN ERROR', self.dataHoraNow(), 'CLIENTE:', cliente[0])
                    continue
                else:
                    email = str(login[0][0])
                    senha = str(login[0][1])
                    print("STARTING DOWNLOAD's:",cliente[0])
                    with sync_playwright() as p:
                        url = 'http://tracking.systemsatx.com.br/'
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page()
                        page.goto(url)
                        page.fill('xpath=//*[@id="txtUsername"]/div/div[1]/input', email)
                        page.fill('xpath=//*[@id="txtSenha"]/div/div[1]/input', senha)
                        page.click('xpath=//*[@id="btnSenha"]/div')
                        sleep(5)
                        if page.url == 'http://tracking.systemsatx.com.br/Login/Blocked':
                            print(cliente[0]," BLOQUED. SEND THIS TO SUP")
                            continue
                        elif page.url == 'http://tracking.systemsatx.com.br/?error=LoginInvalido':
                            print(cliente[0]," INVALID LOGIN. SEND THIS TO SUP")
                            continue
                        else:
                            page.click('xpath=//*[@id="Menu_4"]')
                            page.click('xpath=//*[@id="Menu_24"]')
                            page.locator('xpath=//*[@id="UnidadeRastreada"]/div[1]/div/div[1]/input').fill(placa[0])
                            sleep(1)
                            page.keyboard.press("Enter")
                            sleep(1)
                            page.click("xpath=/html/body/div[9]/div/div[2]/div/div[2]/div[1]/div/div/div")
                            sleep(1)
                            page.click('xpath=//*[@id="DataInicio"]/div/div/div[1]/input')
                            sleep(2)
                            page.keyboard.press("Control+A")
                            page.keyboard.press("Delete")
                            sleep(1)
                            page.keyboard.type(dataI + str("0000"))
                            sleep(1)
                            page.keyboard.press("Tab")
                            page.keyboard.press("Tab")
                            sleep(1)
                            page.keyboard.type(str(dataF) + str(" 00:00"))
                            sleep(1)
                            page.click('xpath=//*[@id="listaAcao-btnConsultar"]')
                            page.wait_for_load_state()
                            sleep(30)
                            page.click('xpath=//*[@id="ExportMenu"]')
                            mes = dataI[3] + dataI[4]
                            sleep(30)
                            with page.expect_download() as file:
                                sleep(20)
                                motivo = "Programa RelatWebSSX"
                                download = file.value
                                download.save_as(path=F"/media/RelatoriosSSX/" + cliente[0] + "/" + placa[0] + "/" + "01_" + str(mes)+ '_excluido' + "_" + self.dataAno() + ".xlsx")
                                self.registra_retirada(cliente[0],placa[0],str(mes),motivo)
                                self.excluir.append({cliente[0]:placa[0]})
                                print(f'PLATE: {placa[0]}, DONE WITH SUCCESS!')
                            page.click('xpath=//*[@id="Menu_4"]')
                            page.click('xpath=//*[@id="Menu_24"]')

    def excluir_placa(self,dados) -> list:
        """dados = list[{cliente:placa}]  recebe uma lista de dicionario contendo cliente e placa"""
        data = dados
        if len(data) == 0:
            print('ALL LICENSE PLATE ARE DELETED. NOTHING TO DO.', self.dataHoraNow())
        else:
            for i in data:
                cliente = list(i.keys())
                placa = list(i.values())
                if len(self.verifica_excluido(placa[0])) != 0:
                        continue
                else:
                    print(f'EXCLUDING THE LICENSE PLATE: {placa[0]} OF CLIENTE: {cliente[0]}')
                    url = "http://tracking.systemsatx.com.br/"
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page()
                        page.goto(url)
                        page.fill('xpath=//*[@id="txtUsername"]/div/div[1]/input',"SEU EMAIL AQUI")
                        page.fill('xpath=//*[@id="txtSenha"]/div/div[1]/input',"SUA SENHA AQUI")
                        page.click('xpath=//*[@id="btnSenha"]/div')
                        sleep(1)
                        page.click('xpath=//*[@id="Menu_7"]')
                        sleep(1)
                        page.click('xpath=//*[@id="Menu_79"]')
                        sleep(1)
                        page.fill('xpath=//*[@id="grid"]/div/div[5]/div/table/tbody/tr[2]/td[5]/div/div[2]/div/div/div[1]/input',placa[0])
                        sleep(2)
                        page.fill('xpath=//*[@id="grid"]/div/div[5]/div/table/tbody/tr[2]/td[4]/div/div[2]/div/div/div[1]/input',cliente[0])
                        sleep(2)
                        page.click('xpath=//*[@id="grid"]/div/div[4]/div/div/div[3]/div[2]/div')
                        sleep(2)
                        verifica_rastreador = page.text_content('xpath=//*[@id="grid"]/div/div[6]/div/div/div[1]/div/table/tbody/tr[1]/td[6]')
                        verifica_existe_dado = page.is_hidden('xpath=/html/body/div[1]/div/div[4]/div/div/div/div[6]/span')
                        if verifica_rastreador.isdecimal() is True:
                            print(f"{cliente[0]}, {placa[0]}, HAS TRACKER. SEND THIS TO SUP.")
                            continue
                        elif verifica_existe_dado == False:
                            print(f"{cliente[0]}, {placa[0]}, HAS BEEN DELETED.")
                            self.registra_exclusao(cliente[0],placa[0])
                            continue
                        else:
                            page.click('xpath=//*[@id="grid"]/div/div[6]/div/div/div[1]/div/table/tbody/tr[1]/td[1]')
                            sleep(2)
                            page.click('xpath=//*[@id="Veiculo_Delete"]')
                            sleep(2)
                            page.click('xpath=//*[@id="listaAcao-salvar--inline"]/div')
                            self.registra_exclusao(cliente[0],placa[0])
                            print(f'{placa[0]}, SECCESSFULY DELETED!')

    def run(self):
        print("\n")
        print("="*80)
        print("START",self.dataHoraNow())
        self.download_database()
        self.debug()
        self.download_relatorio(self.relatorio)
        self.excluir_placa(self.excluir)
        print("END",self.dataHoraNow())
        print("="*80)

if __name__ == "__main__":
    bot = botSSX()
    bot.run()