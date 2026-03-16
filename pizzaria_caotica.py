'''
• Use threading.Thread (pode herdar ou não)
• Use queue.Queue para fila de pedidos
• Use threading.Semaphore(3) para simular o forno (máximo 3 pizzas simultâneas)
• Use threading.Condition() ou threading.Event() para sincronizar a entrega de
pizzas prontas
• Cada chef gera números grandes (ex: 1013+ random) e verifica primalidade com a
função eh_primo da Unidade 02
• Cada entregador retira da fila e imprime mensagem clara (ex: “Entregue pizza premium 10000000000037”)
• Meça o tempo total com timeit.default_timer() para as seguintes configurações (mínimo):
    1 chef + 1 entregador
    2 chefs + 2 entregadores
    4 chefs + 4 entregadores
    8 chefs + 8 entregadores (ou o máximo que sua máquina suportar)

    falor com o professor de usar o with no semaphoro
'''

import threading
import queue
import time
from math import sqrt
import random
from timeit import default_timer

tamanho_fila = 50
numero_de_chefs_entregadores = 1
semaphoro = threading.Semaphore(3)
pedidos_pendentes = queue.Queue()
pizzas_feitas = queue.Queue()
pedidos_completos_bool = threading.Event()
entregas_concluidas_bool = threading.Event()

def eh_primo(x):
    if x < 2:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
        
    limit = int(sqrt(x)) + 1
    for i in range(3, limit, 2):
        if x % i == 0:
            return False
    return True

for i in range (1, tamanho_fila + 1):
    pedidos_pendentes.put(pow(10, 13) + random.randint(0, pow(10, 12)))

def chef(pedidos_pendentes, n_thread):
    contador = 0
    while True:
        if not pedidos_pendentes.empty():
            try:
                pizza = pedidos_pendentes.get(block=False)
            except:
                break

            semaphoro.acquire()
            contador += 1
            print(f'O chef {n_thread} está fazendo a sua {contador}ª pizza, pizza de número {pizza}. É primo? {eh_primo(pizza)}')
            #time.sleep(1)
            print(f'O chef {n_thread} finalizou a pizza de número {pizza}')
            pizzas_feitas.put(pizza)
            semaphoro.release()
            #time.sleep(1)

        if pedidos_completos_bool.is_set():
            break

        if pedidos_pendentes.empty() and (not pedidos_completos_bool.is_set()):
            pedidos_completos_bool.set()
            pedidos_pendentes.task_done()
            break

    


def entregador(n_thread):
    while True:
        try:
            pizza = pizzas_feitas.get(block=False)
            print(f'O entregador {n_thread} está fazendo a entrega do pedido {pizza}')
            #time.sleep(1)
            print(f'O entregador {n_thread} concluiu a entrega do pedido {pizza}')
        except queue.Empty:
            continue

    

        if entregas_concluidas_bool.is_set():
            break

        if (pedidos_completos_bool.is_set()) and (pizzas_feitas.empty()) and (not entregas_concluidas_bool.is_set()):
            entregas_concluidas_bool.set()
            pizzas_feitas.task_done()
            break

            
        
        


if __name__ == '__main__':
    inicio = default_timer()

    funcionario = []

    for n_thread in range (1, numero_de_chefs_entregadores + 1):
        p = threading.Thread(target=chef,  args=(pedidos_pendentes, n_thread))
        e = threading.Thread(target=entregador, args=(n_thread,))
        funcionario.append(p)
        funcionario.append(e)
        p.start()
        e.start()

    for j in funcionario:
        j.join()

    fim = default_timer()

    print(fim - inicio)
    
