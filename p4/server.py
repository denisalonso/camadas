import time as t
from pacote import Pacote


class Server(object):
    pass

def main():
    # inicializacao de objetos
    s = Server()
    p = Pacote()

    # inicializacao
    print('#################################################')
    print('#####        Servidor inicializando         #####') 
    print('#################################################')
    t.sleep(1)
    print('Estabelecendo comunicação com o cliente...')


    print('Esperando o byte de sacrifício...')

if __name__ == '__main__':
    main()