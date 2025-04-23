#!/usr/bin/env python

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28),
             ('.heap', 0x80, 0x1F),
             ('.stack', 0xC0, 0x22),
            ]

def procesar(segmentos, reqs, marcos_libres):
    tam_pag = 16  
    
    tabla_paginas = {}  
    marcos_usados = {}  
    uso_reciente = []  
    resultados = []    
    
    def validar_direccion(direccion):
        for nombre, base, limite in segmentos:
            if base <= direccion < base + limite:
                return True
        return False
    
    def calcular_direccion_fisica(marco, desplazamiento):
        return(marco * tam_pag) + desplazamiento
    
    for req in reqs:
        if not validar_direccion(req):
            resultados.append((req, 0x1FF, "Segmention Fault"))
            return resultados
        
        num_pagina = req // tam_pag
        desplazamiento = req % tam_pag
        
        if num_pagina in tabla_paginas:
            marco = tabla_paginas[num_pagina]
            dir_fisica = calcular_direccion_fisica(marco, desplazamiento)
            
            if num_pagina in uso_reciente:
                uso_reciente.remove(num_pagina)
            uso_reciente.append(num_pagina)
            
            resultados.append((req, dir_fisica, "Marco ya estaba asignado"))
        else:
            if marcos_libres:
                marco = marcos_libres.pop(0)
                tabla_paginas[num_pagina] = marco
                marcos_usados[marco] = num_pagina
                
                uso_reciente.append(num_pagina)
                
                dir_fisica = calcular_direccion_fisica(marco, desplazamiento)
                resultados.append((req, dir_fisica, "Marco libre asignado"))
            else:
                pagina_lru = uso_reciente.pop(0)  
                marco = tabla_paginas[pagina_lru]
                
                del tabla_paginas[pagina_lru]
                
                tabla_paginas[num_pagina] = marco
                marcos_usados[marco] = num_pagina
                
                uso_reciente.append(num_pagina)
                
                dir_fisica = calcular_direccion_fisica(marco, desplazamiento)
                resultados.append((req, dir_fisica, "Marco asignado"))
    
    return resultados
    
def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

