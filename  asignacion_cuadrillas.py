import sys
#importamos el modulo cplex
import cplex
from recordclass import recordclass

TOLERANCE =10e-6 
Orden = recordclass('Orden', 'id beneficio', 'cant_trab')

class InstanciaAsignacionCuadrillas:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        
    def leer_datos(self,nombre_archivo):

        # Se abre el archivo
        f = open(nombre_archivo)

        # Lectura cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Lectura cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Lectura de las ordenes
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            linea = f.readline().rstrip().split(' ')
            self.ordenes.append(Orden(linea[0],linea[1],linea[2]))
        
        # Lectura cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Lectura conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            linea = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Lectura ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            linea = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Lectura ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            linea = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,linea)))
        
        # Lectura cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Lectura ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            linea = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,linea)))
        
        # Se cierra el archivo de entrada
        f.close()


def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada 	
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaAsignacionCuadrillas()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob, instancia):
    # Definir y agregar las variables:
	# metodo 'add' de 'variables', con parametros:
	# obj: costos de la funcion objetivo
	# lb: cotas inferiores
    # ub: cotas superiores
    # types: tipo de las variables
    # names: nombre (como van a aparecer en el archivo .lp)

    ordenes = instancia.ordenes

    #Variables que determinan si un trabajador trabajó en un turno para cierta orden
    nombres = []
    for o in range(instancia.cantidad_ordenes):
        for w in range(1, instancia.cantidad_trabajadores + 1):
            for t in range(1, 31):
                nombre = "X" + str(ordenes[o][0]) + str(w) + str(t)
                nombres.append(nombre)
    largo = nombres.len()            
    prob.variables.add(obj= [0]*largo, lb = [0]*largo, ub = [1]*largo, types = ['B']*largo, names = nombres)

    #Variables que determinan si un trabajador trabajó cierto día
    nombres = []
    for i in range(1, instancia.cantidad_trabajadores + 1):
        for j in range(1, 7):
            nombres.append("W" + str(i) + str(j))
    largo = nombres.len()            
    prob.variables.add(obj= [0]*largo, lb = [0]*largo, ub = [1]*largo, types = ['B']*largo, names = nombres)

    #Variables que determinan si cierta orden fue realizada en cierto turno
    for i in range(instancia.cantidad_ordenes):
        for t in range(1, 31)
            prob.variables.add(obj = ordenes[i][1], lb = [0], ub = [1], types = ['B'], names = ["O" + str(ordenes[i][0]) + str(t)])

    #Variables que determinan cuanto hay que pagarle a cada trabajador
    for i in range(1, instancia.cantidad_trabajadores + 1):
        prob.variables.add(obj = [-1000, -200, -200, -100], lb = [0]*4, ub = [30]*4, types = ['I']*4, names = ["S" + str(i) + "1", "S" + str(i) + "2", "S" + str(i) + "3", "S" + str(i) + "4"])

def agregar_restricciones(prob, instancia):
    # Agregar las restricciones ax <= (>= ==) b:
	# funcion 'add' de 'linear_constraints' con parametros:
	# lin_expr: lista de listas de [ind,val] de a
    # sense: lista de 'L', 'G' o 'E'
    # rhs: lista de los b
    # names: nombre (como van a aparecer en el archivo .lp)
	
    # Notar que cplex espera "una matriz de restricciones", es decir, una
    # lista de restricciones del tipo ax <= b, [ax <= b]. Por lo tanto, aun cuando
    # agreguemos una unica restriccion, tenemos que hacerlo como una lista de un unico
    # elemento.

    # Restriccion generica

    ordenes = instancia.ordenes

    #Si un trabajador realiza una operación en un turno, ningún trabajador puede realizar la misma operación en otro turno
    restricciones = []
    nombres = []
    for o in range(1,instancia.cantidad_ordenes + 1):
        for t1 in range(1, 30):
            for t2 in range(t1 + 1, 31):
                for w1 in range(1, instancia.cantidad_trabajadores):
                    for w2 in range(w1, instancia.cantidad_trabajadores):
                        restricciones.append([["X" + str(ordenes[o][0]) + str(w1) + str(t1), "X" + str(ordenes[o][0]) + str(w2) + str(t2)], [1, 1]])
                        nombres.append["Mismo truno" + str(restricciones.len())]
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)
    
    #Ningún trabajador puede estar asignado a más de 1 orden en el mismo turno
    restricciones = []
    nombres = []
    for w in range(1,instancia.cantidad_trabajadores + 1):
        for t in range(1, 31):
            restriccion = []
            for o in range(instancia.cantidad_ordenes):
                restriccion.append("X" + str(ordenes[o][0]) + str(w) + str(t))
            restricciones.append([restriccion, [1]*instancia.cantidad_ordenes])
            nombres = ["Solo una orden" + str(restricciones.len())]
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)
    
    #Correctitud variables binarias de asignación
    nombres_1 = []
    nombres_2 = []
    restricciones_1 = []
    restricciones_2 = []
    for w in range(1, instancia.cantidad_trabajadores):
        for d in range(1, 7):
            restriccion = ["W" + str(w) + str(d)]
            for o in range(instancia.cantidad_operaciones):
                for t in range(1, 6):
                    restriccion.append("X" + str(ordenes[o][0]) + str(w) + str(5*d + t))
            restricciones_1.append([restriccion, [-4] + [1]*(restriccion.len() - 1)])
            restricciones_2.append([restriccion, [1] + [-1]*(restriccion.len() - 1)])
            nombres_1 = ["Correctitud asignación A" + str(restricciones.len())]
            nombres_2 = ["Correctitud asignación B" + str(restricciones.len())]
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones_1 + restricciones_2,
                               senses=["L"]*cantidad*2,
                               rhs=[0]*2*cantidad,
                               names=nombres_1 + nombres_2)                


    #Correctitud variables binarias de realización
    nombres_1 = []
    nombres_2 = []
    restricciones_1 = []
    restricciones_2 = []
    cantidades = []
    for o in range(instancia.cantidad_ordenes):
        cantidades.append(ordenes[o][2] - 1)
        for t in range(1, 31):
            restriccion = ["O" + str(ordenes[o][0])]
            for w in range(1, instancia.cantidad_trabajadores + 1):
                restriccion.append(["X" + str(ordenes[o][0]) + str(w) + str(t)])
            restricciones_1.append([restriccion, [ordenes[o][2]] + [-1]*(restriccion.len() - 1)])
            restricciones_2.append([restriccion, [-(instancia.cantidad_trabajadores + 1)] + [1]*(restriccion.len() - 1)])
            nombres_1 = ["Correctitud realización A" + str(restricciones.len())]
            nombres_2 = ["Correctitud realización B" + str(restricciones.len())]
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones_1 + restricciones_2,
                               senses=["L"]*cantidad*2,
                               rhs=[0]*cantidad + cantidades,
                               names=nombres_1 + nombres_2)
    
    #Correctitud salarios

    restricciones = []
    nombres = []
    for i in range(4):
        for w in range(instancia.cantidad_trabajadores + 1):
            restriccion = ["S" + str(w) + str(i + 1)]
            for t in range(1, 31):
                for o in range(instancia.cantidad_ordenes):
                    restriccion.append("X" + str(ordenes[o][0]) + str(w) + str(t))
            restricciones.append([restriccion, [-1] + [1]*(restriccion.len() - 1)])
            nombres = ["Correctitud salario " + str(w) + str(i + 1)]
    cantidad = restricciones.len()/4
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad*4,
                               rhs=[0]*cantidad + [5]*cantidad + [10]*cantidad + [15]*cantidad,
                               names=nombres)                
                    

    
    #Ningún trabajador puede trabajar los 6 días

    restricciones = []
    nombres = []
    for w in range(1, instancia.cantidad_trabajadores + 1):
        restricciones.append([["W" + str(w) + "1", "W" + str(w) + "2", "W" + str(w) + "3", "W" + str(w) + "4", "W" + str(w) + "5", "W" + str(w) + "6"], [1]*6])
        nombres.append("No todos los días " + str(w))
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[5]*cantidad,
                               names=nombres)

    #Ningún trabajador puede trabajar los 5 turnos de 1 día
    restricciones = []
    nombres = []
    for w in range(1, instancia.cantidad_trabajadores + 1):
        restriccion = []
        for o in range(instancia.cantidad_ordenes):
           for d in range(6):
                for t in range(1, 6):
                    restriccion.append("X" + str(ordenes[o][0]) + str(w) + str(5*d + t))
        restricciones.append([restriccion, [1]*restriccion.len()])
        nombres.append("No todos los turnos" + str(restricciones.len()))
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[4]*cantidad,
                               names=nombres)

    #Órdenes conflictivas
    restricciones = []
    nombres = []
    for w in range(1, instancia.cantidad_trabajadores + 1):
        for d in range(6):
            for t in range(1, 5):
                for lista in instancia.ordenes_conflictivas:
                    restricciones.append([["X" + str(lista[0]) + str(w) + str(5*d + t), "X" + str(lista[0]) + str(w) + str(5*d + t + 1), "X" + str(lista[1]) + str(w) + str(5*d + t), "X" + str(lista[1]) + str(w) + str(5*d + t + 1)], [1]*4])
                    nombres.append("Ordenes consecutivas " + str(restricciones.len()))
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)
    
    #Órdenes correlativas
    restricciones = []
    restriccion = []
    nombres = []
    for lista in instancia.ordenes_correlativas:
        for d in range(6):
            for t in range(1, 5):
                restricciones.append([["O" + str(ordenes[lista[0]]) + str(5*d + t), "O" + str(ordenes[lista[1]]) + str(5*d + t + 1)], [1, -1]])
                nombres.append("Ordenes correlaticas " + str(restricciones.len()))
                restriccion.append("O" + str(ordenes[lista[1]]) + str(5*d + 5))
    restricciones.append([restriccion, [1]*restricciones.len()])
    nombres.len("Primera no puede ir último día")
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[0]*cantidad,
                               names=nombres)
    
    #Los trabajadores no pueden tener una diferencia de más de 8 asignaciones
    restricciones = []
    nombres = []
    for w1 in range(1, instancia.cantidad_trabajadores):
        for w2 in range(w1 + 1, instancia.cantidad_trabajadores + 1):
            restriccion
            for o in range(instancia.cantidad_ordenes):
                for t in range(1, 31):
                    restriccion += ["X" + str(lista[0]) + str(w1) + str(t), "X" + str(lista[0]) + str(w1) + str(t)]
            restricciones.append[restriccion, [1, -1]*restriccion.len()/2]
            restricciones.append[restriccion, [-1, 1]*restriccion.len()/2]
            nombres += ["Diferencia de 8 " + str(w1) + str(w2), "Diferencia de 8 " + str(w2) + str(w1)]
    cantidad = restricciones.len()
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[8]*cantidad,
                               names=nombres)        




                                                 
    

def armar_lp(prob, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.....)

    # Escribir el lp a archivo
    prob.write('asignacionCuadrillas.lp')

def resolver_lp(prob):
    
    # Definir los parametros del solver
    prob.parameters....
       
    # Resolver el lp
    prob.solve()

#def mostrar_solucion(prob,instancia):
    # Obtener informacion de la solucion a traves de 'solution'
    
    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    
    # Tomar los valores de las variables
    x  = prob.solution.get_values()
    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    .....

def main():
    
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()
    
    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp(prob,instancia)

    # Resolucion del modelo
    resolver_lp(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob,instancia)

if __name__ == '__main__':
    main()
