from playwright.sync_api import sync_playwright
from conexaoSQL import conectaSQL, fecharConexao

class BotBloqued:

    def get_clientes_bloqueados(self):
        conexao = conectaSQL(1)
        cursor = conexao.cursor()
        sql = "SELECT * FROM relatorio_clientes_bloqueados"
        cursor.execute(sql)
        dados = cursor.fetchall()
        fecharConexao(cursor,conexao)
        print(dados)


    def get_login_clientes(self):
        pass

    def get_placas_clientes(self):
        pass
    
    def registra_download(self):
        pass

    def download(self):
        pass

    def run(self):
        self.get_clientes_bloqueados()


if __name__ == '__main__':
    bot = BotBloqued()
    bot.run()