import mysql.connector

def conectaSQL(local, banco='banco_automacao_systemsatx'):
    if local == 0:
        myHost = "localhost"
        myUser = "root"
        myPwd = "root"
        myDB = banco
        return mysql.connector.Connect(host=myHost, user=myUser, password=myPwd, database=myDB)
    
    elif local == 1:
        myHost = '0.0.0.0' # ip do banco
        myUser = 'root' # usuario
        myPwd = '' # senha
        myDB = banco
        return mysql.connector.Connect(host=myHost, user=myUser, password=myPwd, database=myDB)

def fecharConexao(cursor, connection):
    cursor.close()
    connection.close()
