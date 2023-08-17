from verifica_cliente_placa_sys import *

print('Iniciando analize de Clientes sem login no banco de dados!')
tabela_dados_cliente_1()
tabela_dados_cliente_2()
analise_das_duas_tabelas()
print('Gerando Relatorio...')
gerar_excel_com_analise_completa()
print('Fim do Programa!')