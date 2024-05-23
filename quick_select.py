from numba import jit
from multiprocessing import Process, Queue
import time

# Función que particiona el arreglo con optimización JIT
@jit(nopython=True)
def particionar(arr, izq, der):
    pivote = arr[der]
    i = izq
    for j in range(izq, der):
        if arr[j] <= pivote:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[der] = arr[der], arr[i]
    return i

# Función que implementa el algoritmo Quick Select con la optimización de JIT
@jit(nopython=True)
def quick_select(arr, izq, der, k):
    if izq == der:
        return arr[izq]

    indice_pivote = particionar(arr, izq, der)
    if k == indice_pivote:
        return arr[k]
    elif k < indice_pivote:
        return quick_select(arr, izq, indice_pivote - 1, k)
    else:
        return quick_select(arr, indice_pivote + 1, der, k)

# Función de quick select en paralelo
def quick_select_paralelo(arr, izq, der, k, cola):
    if izq == der:
        cola.put(arr[izq])
        return

    indice_pivote = particionar(arr, izq, der)

    if k == indice_pivote:
        cola.put(arr[k])
    else:
        cola_izq = Queue()
        cola_der = Queue()
        proceso_izq = None
        proceso_der = None
        
        if k < indice_pivote and izq < indice_pivote:
            proceso_izq = Process(target=quick_select_paralelo, args=(arr, izq, indice_pivote - 1, k, cola_izq))
            proceso_izq.start()
        elif k > indice_pivote and indice_pivote + 1 < der:
            proceso_der = Process(target=quick_select_paralelo, args=(arr, indice_pivote + 1, der, k, cola_der))
            proceso_der.start()

        if proceso_izq:
            proceso_izq.join()
            cola.put(cola_izq.get())
        elif proceso_der:
            proceso_der.join()
            cola.put(cola_der.get())

def main():
    lista_ejemplo = [7, 10, 4, 3, 20, 15, 5, 6, 7, 10, 70, 98, 41, 65, 1, 42, 54, 74, 8, 18, 26, 30]
    print("Lista :", lista_ejemplo)
    k = int(input("Ingresa el índice k que desea buscar en la lista: "))
    cola_resultado = Queue()
    
    tiempo_inicio = time.time()
    
    proceso = Process(target=quick_select_paralelo, args=(lista_ejemplo, 0, len(lista_ejemplo) - 1, k, cola_resultado))
    proceso.start()
    proceso.join()

    tiempo_fin = time.time()
    
    resultado = cola_resultado.get()
    print(f"El {k}-ésimo elemento más pequeño es: {resultado}")
    print(f"Tiempo total: {tiempo_fin - tiempo_inicio:.4f} segundos")

if __name__ == "__main__":
    main()
