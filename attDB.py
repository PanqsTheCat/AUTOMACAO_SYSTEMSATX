import getPlacaBySiger as g
import traceback

try:
    print('Iniciando Programa....\nOperações de Download Iniciadas.')
    g.getPlacas()
    print('Operação de Download de placas concluido com sucesso.')
    g.getClientes()
    print('Operação de Download de dados de clientes concluido com sucesso.\nIniciando Operação de limpeza de Dados....')
    g.dellPlacasDB()
    print('Operação de limpeza de placas concluido com sucesso.')
    g.dellCLientesDB()
    print('Operação de limpeza de dados de clientes concluido com sucesso.\nIniciando Operação de incersão de Dados....')
    g.addPlacasDB()
    print('Operação de incersão de placas no banco de dados concluido com sucesso.')
    g.addDadosClienteDB()
    print('Operação de incersão de dados clientes no banco de dados concluido com sucesso.')
    print('Fim do Programa.')
except Exception:
    traceback.print_exc()
    print('Erro inesperado, favor contatar o desenvolvimento.\nInformar o erro acima ↑')