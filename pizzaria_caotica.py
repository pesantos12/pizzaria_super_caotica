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

'''

import threading
import queue
import time
from math import sqrt
import random
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import pandas as pd

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

def exibirGrafico(configuracao, tempos):
    plt.figure(figsize=(8, 5)) 
    plt.plot(configuracao, tempos, marker='o', linestyle='-', color='tab:blue')
    plt.xlabel('Número de duplas (chef + entregador)')
    plt.ylabel('Tempo total (s)')
    
    plt.xticks(configuracao)
    
    plt.grid(True, which='both', linestyle='--', alpha=0.6)
    plt.tight_layout() 
    plt.show()

def exibirGraficoSpeedup(configuracoes, speedups):
    plt.figure(figsize=(8, 5))
    
    plt.plot(configuracoes, speedups, marker='o', label='Speedup real')
    
    # Linha ideal (speedup linear)
    plt.plot(configuracoes, configuracoes, linestyle='--', label='Speedup ideal')
    
    plt.xlabel('Número de duplas (chef + entregador)')
    plt.ylabel('Speedup')
    plt.legend()
    plt.grid(True)
    plt.show()


def chef(pedidos_pendentes, pizzas_feitas, semaphoro, pedidos_completos_bool, n_thread):
    contador = 0
    while True:
        try:
            pizza = pedidos_pendentes.get(block=False)
        except:
            break

        semaphoro.acquire()
        contador += 1
        print(f'O chef {n_thread} está fazendo a sua {contador}ª pizza, pizza de número {pizza}. É primo? {eh_primo(pizza)}')
        time.sleep(random.uniform(0.1, 0.3))
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

def entregador(pizzas_feitas, pedidos_completos_bool, entregas_concluidas_bool, n_thread):
    while True:
        try:
            pizza = pizzas_feitas.get(block=False)
            print(f'O entregador {n_thread} está fazendo a entrega do pedido {pizza}')
            time.sleep(0.1)
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
    configuracoes_funcionarios = [1, 2, 4, 8, 16, 32]
    tamanho_fila = 50
    tempos = []

    for configuracao in configuracoes_funcionarios:
        print(f"\n{'='*50}")
        print(f"Executando com {configuracao} chef(s) e {configuracao} entregador(es)")
        print(f"{'='*50}")
        
        pedidos_pendentes = queue.Queue()
        pizzas_feitas = queue.Queue()
        pedidos_completos_bool = threading.Event()
        entregas_concluidas_bool = threading.Event()
        semaphoro = threading.Semaphore(3)
        
        inicio = timer()
        
        for _ in range(1, tamanho_fila + 1):
            pedidos_pendentes.put(pow(10, 13) + random.randint(0, pow(10, 12)))

        funcionario = []
        for n_thread in range(1, configuracao + 1):
            p = threading.Thread(target=chef, args=(pedidos_pendentes, pizzas_feitas, semaphoro, pedidos_completos_bool, n_thread))
            e = threading.Thread(target=entregador, args=(pizzas_feitas, pedidos_completos_bool, entregas_concluidas_bool, n_thread))
            funcionario.append(p)
            funcionario.append(e)
            p.start()
            e.start()

        for j in funcionario:
            j.join()

        fim = timer()
        tempo_gasto = fim - inicio
        print(f"\nTempo gasto para {configuracao} dupla(s): {tempo_gasto:.4f} segundos")
        tempos.append(tempo_gasto)
        
        time.sleep(1)
    
    print("\n" + "="*50)
    print("RESULTADOS FINAIS:")
    print("="*50)
    for i, config in enumerate(configuracoes_funcionarios):
        print(f"{config} dupla(s): {tempos[i]:.4f} segundos")
    
    tempo_base = tempos[0]

    speedups = [tempo_base / t for t in tempos]
    
    exibirGrafico(configuracoes_funcionarios, tempos)
    exibirGraficoSpeedup(configuracoes_funcionarios, speedups)
    
    n = configuracoes_funcionarios[-1]
    Tn = tempos[-1]

    S = tempo_base / Tn

    p = (1 - (1 / S)) / (1 - (1 / n))

    sequencial = 1 - p

    print("\n===== LEI DE AMDAHL =====")
    print(f"Speedup observado com {n} duplas: {S:.4f}")
    print(f"Parte paralelizável: {p:.4f} ({p*100:.2f}%)")
    print(f"Parte sequencial: {sequencial:.4f} ({sequencial*100:.2f}%)")

    # Speedup máximo teórico
    S_max = 1 / sequencial
    print(f"Speedup máximo teórico: {S_max:.2f}")


    tabela = pd.DataFrame({
        "Duplas": configuracoes_funcionarios,
        "Tempo (s)": tempos,
        "Speedup": speedups
    })

    print("\nTabela de Resultados:")
    print(tabela)
    tabela.to_csv("resultados.csv", index=False)