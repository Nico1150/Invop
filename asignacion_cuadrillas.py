import sys
#importamos el modulo cplex
import cplex
from recordclass import recordclass

TOLERANCE =10e-8 
Orden = recordclass('Orden', 'id beneficio cant_trab')

conflictos = 0
repeticiones = 0
alpha_conflictos = 0
alpha_repeticiones = 0

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
                nombre = "X_" + ordenes[o].id + "_" + str(w) + "_" + str(t)
                nombres.append(nombre)
    largo = len(nombres)            
    prob.variables.add(obj= [0]*largo, lb = [0]*largo, ub = [1]*largo, types = ['B']*largo, names = nombres)

    #Variables que determinan si un trabajador trabajó cierto día
    nombres = []
    for i in range(1, instancia.cantidad_trabajadores + 1):
        for j in range(1, 7):
            nombres.append("W" + str(i)  + str(j))
    largo = len(nombres)           
    prob.variables.add(obj= [0]*largo, lb = [0]*largo, ub = [1]*largo, types = ['B']*largo, names = nombres)

    #Variables que determinan si cierta orden fue realizada en cierto turno
    for i in range(instancia.cantidad_ordenes):
        for t in range(1, 31):
            prob.variables.add(obj = [int(ordenes[i].beneficio)], lb = [0], ub = [1], types = ['B'], names = ["O_" + ordenes[i].id + "_" + str(t)])

    #Variables que determinan cuanto hay que pagarle a cada trabajador
    for i in range(1, instancia.cantidad_trabajadores + 1):
        prob.variables.add(obj = [-1000, -200, -200, -100], lb = [0]*4, ub = [30]*4, types = ['I']*4, names = ["S" + str(i) + "1", "S" + str(i) + "2", "S" + str(i) + "3", "S" + str(i) + "4"])

    if conflictos == 2:
    #Variables que penalizan por cada conflicto entre trabajadores
        for lista in instancia.conflictos_trabajadores:
            prob.variables.add(obj = [-alpha_conflictos], lb = [0], ub = [instancia.cantidad_ordenes], types = ['I'], names = ["CT_" + lista[0] + "_" + lista[1]])
            for o in instancia.ordenes:
                prob.variables.add(obj = [0], lb = [0], ub = [1], types = ['B'], names = ["OW_" + lista[0] + "_" + lista[1] + "_" + str(o)])     

    if repeticiones == 2:
    #Variables que penalizan por cada orden repetida por alguien
        for lista in instancia.ordenes_repetitivas:
            for w in range(1, instancia.cantidad_trabajadores + 1):
                prob.variables.add(obj = [-alpha_conflictos], lb = [0], ub = [len(instancia.ordenes_repetitivas)], types = ['I'], names = ["OR_" + lista[0] + "_" + lista[1] + "_" + str(w)])



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

    #Si una orden se realiza en un turno, no puede ser realizada en otro turno
    restricciones = []
    nombres = []
    for o in range(instancia.cantidad_ordenes):
        for t1 in range(1, 30):
            for t2 in range(t1 + 1, 31):
                restricciones.append([["O_" + ordenes[o].id + "_" + str(t1), "O_" + ordenes[o].id + "_" + str(t2)], [1, 1]])
                nombres.append("Mismo turno" + str(len(restricciones)))
    cantidad = len(restricciones)
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
                restriccion.append("X_" + ordenes[o].id + "_" + str(w) + "_" + str(t))
            restricciones.append([restriccion, [1]*instancia.cantidad_ordenes])
            nombres.append("Solo una orden" + str(len(restricciones)))
    cantidad = len(restricciones)
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)
    
    #Correctitud variables binarias de asignación
    nombres = []
    restricciones = []
    for w in range(1, instancia.cantidad_trabajadores + 1):
        for d in range(1, 7):
            restriccion = ["W" + str(w) + str(d)]
            for o in range(instancia.cantidad_ordenes):
                for t in range(1, 6):
                    restriccion.append("X_" + ordenes[o].id + "_" + str(w) + "_" + str(5*(d-1) + t))
            restricciones.append([restriccion, [-4] + [1]*(len(restriccion) - 1)])
            nombres.append("Correctitud asignación" + str(len(restricciones)))
    cantidad = len(restricciones)
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[0]*cantidad,
                               names=nombres)                


    #Correctitud variables binarias de realización
    nombres = []
    restricciones = []
    for o in range(instancia.cantidad_ordenes):
        for t in range(1, 31):
            restriccion = ["O_" + ordenes[o].id + "_" + str(t)]
            for w in range(1, instancia.cantidad_trabajadores + 1):
                restriccion.append("X_" + str(ordenes[o][0]) + "_" + str(w) + "_" + str(t))
            restricciones.append([restriccion, [int(ordenes[o].cant_trab)] + [-1]*(len(restriccion) - 1)])
            nombres.append("Correctitud realización" + str(len(restricciones)))
    cantidad = len(restricciones)
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[0]*cantidad,
                               names=nombres)
    
    #Correctitud salarios

    restricciones = []
    nombres = []
    for i in range(4):
        for w in range(1, instancia.cantidad_trabajadores + 1):
            restriccion = ["S" + str(w) + str(i + 1)]
            for t in range(1, 31):
                for o in range(instancia.cantidad_ordenes):
                    restriccion.append("X_" + ordenes[o].id + "_" + str(w) + "_" + str(t))
            restricciones.append([restriccion, [-1] + [1]*(len(restriccion) - 1)])
            nombres.append("Correctitud salario " + str(w) + str(i + 1))
    cantidad = len(restricciones)//4
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
    cantidad = len(restricciones)
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[5]*cantidad,
                               names=nombres)

    #Ningún trabajador puede trabajar los 5 turnos de 1 día
    restricciones = []
    nombres = []
    for w in range(1, instancia.cantidad_trabajadores + 1):
        for d in range(6):
            restriccion = []
            for o in range(instancia.cantidad_ordenes):
                for t in range(1, 6):
                    restriccion.append("X_" + ordenes[o].id + "_" + str(w) + "_" + str(5*d + t))
            restricciones.append([restriccion, [1]*len(restriccion)])
            nombres.append("No todos los turnos" + str(len(restricciones)))
    cantidad = len(restricciones)
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
                    restricciones.append([["X_" + str(lista[0]) + "_" + str(w) + "_" + str(5*d + t), "X_" + str(lista[0]) + "_" + str(w) + "_" + str(5*d + t + 1), "X_" + str(lista[1]) + "_" + str(w) + "_" + str(5*d + t), "X_" + str(lista[1]) + "_" + str(w) + "_" + str(5*d + t + 1)], [1]*4])
                    nombres.append("Ordenes consecutivas " + str(len(restricciones)))
    cantidad = len(restricciones)
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
            restriccion.append("O_" + ordenes[lista[1]].id + "_" + str(5*d + 5))
            for t in range(1, 5):
                restricciones.append([["O_" + ordenes[lista[0]].id + "_" + str(5*d + t), "O_" + ordenes[lista[1]].id + "_" + str(5*d + t + 1)], [1, -1]])
                nombres.append("Ordenes correlaticas " + str(len(restricciones)))
    restricciones.append([restriccion, [1]*len(restriccion)])
    nombres.append("Primera no puede ir último día")
    cantidad = len(restricciones)
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[0]*cantidad,
                               names=nombres)
    
    #Los trabajadores no pueden tener una diferencia de más de 8 asignaciones
    restricciones = []
    nombres = []
    for w1 in range(1, instancia.cantidad_trabajadores):
        for w2 in range(w1 + 1, instancia.cantidad_trabajadores + 1):
            restriccion = []
            for o in range(instancia.cantidad_ordenes):
                for t in range(1, 31):
                    restriccion += ["X_" + ordenes[o].id + "_" + str(w1) + "_" + str(t), "X_" + ordenes[o].id + "_" + str(w2) + "_" + str(t)]
            restricciones.append([restriccion, [1, -1]*(len(restriccion)//2)])
            restricciones.append([restriccion, [-1, 1]*(len(restriccion)//2)])
            nombres += ["Diferencia de 8 " + str(w1) + str(w2), "Diferencia de 8 " + str(w2) + str(w1)]
    cantidad = len(restricciones)
    prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[8]*cantidad,
                               names=nombres)

    if conflictos == 1:
        restricciones = []
        nombres = []
        for o in range(instancia.cantidad_ordenes):
            for t in range(1, 31):
                    for lista in instancia.conflictos_trabajadores:
                        restricciones.append([["X_" + ordenes[o].id + "_" + str(lista[0]) + "_" + str(t), "X_" + ordenes[o].id + "_" + str(lista[1]) + "_" + str(t)], [1, 1]])
                        nombres.append("Trabajadores en conflicto_" + str(lista[0]) + "_" + str(lista[1]))
        cantidad = len(restricciones)
        prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)
    
        restricciones = []
        nombres = []

    if repeticiones == 1:    

        restricciones = []
        nombres = []
        for lista in instancia.ordenes_repetitivas:
            for w in range(1, instancia.cantidad_trabajadores):
                restriccion = []
                for t in range(1, 31):
                    restriccion += ["X_" + lista[0] + "_" + str(w) + "_" + str(t), "X_" + lista[1] + "_" + str(w) + "_" + str(t)]
            restricciones.append(restriccion, [1]*len(restriccion))        
        cantidad = len(restricciones)
        prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)
    
        restricciones = []
        nombres = []

    if conflictos == 2:

        #Correctitud 2 trabajadores en conflicto misma orden
        
        restricciones = []
        nombres = []
        for o in instancia.ordenes:
                for lista in instancia.conflictos_trabajadores:
                    restriccion = ["OW_" + lista[0] + "_" + lista[1] + "_" + o.id]
                    for t in range(1, 31):
                        restriccion += ["X_" + o.id + "_" + lista[0] + "_" + str(t), "X_" + o.id + "_" + lista[1] + "_" + str(t)]
                    restricciones.append(restriccion, [-1] + [1]*(len(restriccion) - 1))    
                    nombres.append("Trabajadores en conflicto en orden" + str(lista[0]) + "_" + str(lista[1] + "_" + o.id))

        cantidad = len(restricciones)
        prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)
        
        #Penalizacion correcta
        
        restricciones = []
        nombres = []

        for lista in instancia.conflictos_trabajadores:
            restriccion = ["CT_" + lista[0] + "_" + lista[1]]
            for o in instancia.ordenes:
                restriccion.append("OW_" + lista[0] + "_" + lista[1] + "_" + o.id)
            restricciones.append(restriccion, [-1] + [1]*(len(restriccion) - 1))
            nombres.append("Cantidad turnos juntos" + lista[0] + lista[1] + o.id)
        cantidad = len(restricciones)
        prob.linear_constraints.add(lin_expr=restricciones,
                               senses=["L"]*cantidad,
                               rhs=[1]*cantidad,
                               names=nombres)              
        
    
        restricciones = []
        nombres = []

    if repeticiones == 2:
        






                                                 
    

def armar_lp(prob, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.maximize)

    # Escribir el lp a archivo
    prob.write('asignacionCuadrillas.lp')

def resolver_lp(prob):
    
    # Definir los parametros del solver
    prob.parameters.mip.tolerances.mipgap.set(1e-10)
       
    # Resolver el lp
    prob.solve()

def mostrar_solucion(prob,instancia):
    #Obtener informacion de la solucion a traves de 'solution'
    
    #Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')

    print(prob.solution)

    # Tomar los valores de las variables
    x  = prob.solution.get_values()
    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    i = 0
    for o in range(instancia.cantidad_ordenes):
        for w in range(1, instancia.cantidad_trabajadores + 1):
            for d in range(1, 7):
                for t in range(1, 6):
                    if x[i] > TOLERANCE:
                        print("El trabajador " + str(w) + " trabajó el día " + str(d) + " en el turno " + str(t) + " realizando la orden " + instancia.ordenes[o].id)
                    i += 1    

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

