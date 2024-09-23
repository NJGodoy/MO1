# Import libs
import sys
import random
import matplotlib.pyplot as plt
from docplex.mp.model import Model
from docplex.mp.relax_linear import LinearRelaxer

try:
    import docplex.mp
except:
    raise Exception('Please install docplex. See https://pypi.org/project/docplex/')

# Declaración de parámetros

D1, D2, D3 = 50, 80, 70
P1, P2, P3 = 100, 70, 50
# nombre, precio de venta, demanda minima
products = [("SILLAS", P1, D1),
            ("TAB4", P2, D2),
            ("TAB3", P3, D3)]

# elementos faltantes
# nombre, precio de compra
A = 40
R = 45
P = 20
missing_parts_prices = (("RC1", R), ("AC1", A), ("PC1", P),
                 ("AC2", A), ("PC2", P),
                 ("AC3", A), ("PC3", P))

# produccion
production = {"SILLAS" : {"R" : 1, "A" : 1, "P" : 4},
              "TAB4" : {"A" : 1, "P" : 4},
              "TAB3" : {"A" : 1, "P" : 3}}

# nexo
link = {"SILLAS" : {"R" : ("RS1", "RC1"), "A" : ("AS1", "AC1"), "P" : ("PS1", "PC1")},
              "TAB4" : {"A" : ("AS2", "AC2"), "P" : ("PS2", "PC2")},
              "TAB3" : {"A" : ("AS3", "AC3"), "P" : ("PS3", "PC3")}}

# sillas rotas
broken_furniture = {"RR" : 30, "AR" : 30, "P1" : 20, "P2" : 10, "RR1P" : 30}
salvage = {"RS" : broken_furniture["AR"] + broken_furniture["P1"] + broken_furniture["P2"],
              "AS" : broken_furniture["RR"] + broken_furniture["P1"] + broken_furniture["P2"] + broken_furniture["RR1P"],
              "PS" : 4 * (broken_furniture["RR"] + broken_furniture["AR"]) + 3 * (broken_furniture["P1"] + broken_furniture["RR1P"])
               + 2 * broken_furniture["P2"]}

def create_model():
    mdl = Model(name="Ejercicio 2.32")

    produccion_vars = {}
    for product, parts in link.items():
        produccion_vars[product] = mdl.continuous_var(name="Produccion_de_" + product)
        for type in parts.values():
            produccion_vars[type[0]] = mdl.continuous_var(name="Reusado_" + type[0])
            produccion_vars[type[1]] = mdl.continuous_var(name="Comprado_" + type[1])

    # --- restricciones ---

    # --- produccion ---
    for product, parts in link.items():
        for key, type in parts.items():
            mdl.add_constraint(production[product][key]*produccion_vars[product] == produccion_vars[type[0]] + produccion_vars[type[1]])

    # --- disponibilidad partes---
    mdl.add_constraint(produccion_vars["PS1"] + produccion_vars["PS2"] + produccion_vars["PS3"] <= salvage["PS"], "Disponibilidad_Patas")
    mdl.add_constraint(produccion_vars["RS1"] <= salvage["RS"], "Disponibilidad_Respaldos")
    mdl.add_constraint(produccion_vars["AS1"] + produccion_vars["AS2"] + produccion_vars["AS3"] <= salvage["AS"], "Disponibilidad_Asientos")
    
    # --- demanda ---
    for p in products:
        mdl.add_constraint(produccion_vars[p[0]] >= p[2], "Demanda_min_%s" % p[0])

    # --- imprimir info ---
    mdl.print_information()
    
    # --- establecer objetivos ---
    revenue = mdl.sum(produccion_vars[p[0]] * p[1] for p in products)
    costs = mdl.sum(produccion_vars[part[0]] * part[1] for part in missing_parts_prices)
    total_benefit = revenue - costs
    mdl.maximize(total_benefit)

    return mdl, produccion_vars

# Solucion del modelo
def solve_model(mdl):
    solution = mdl.solve()

    if not solution:
        print("Model cannot be solved.")
        sys.exit(1)

    obj = mdl.objective_value

    print("* Production model solved with objective: {:g}".format(obj))
    products_list = list()
    production_values = list()
    total = 0
    for p in products:
        production_value = produccion_vars[p[0]].solution_value
        print(f"{p[0]} : {production_value}")
        products_list.append(p[0])
        production_values.append(production_value)
        total += production_value
    
    graph = True
    if graph:
        plt_graph_model(products_list, production_values, total)

# Crear el gráfico de barras
def plt_graph_model(products_list, production_values, total_produced):
    plt.figure(figsize=(10, 6))
    
    colors = list()
    for i in range(len(products_list)):
        ran_color = (random.random(), random.random(), random.random())
        colors.append(ran_color)

    bars = plt.bar(products_list, production_values, color=colors)

    # Agregar una línea horizontal que representa el total de productos fabricados
    plt.axhline(y=total_produced, color='black', linestyle='--', label=f'Total fabricado: {total_produced}')

    # Etiquetas y título
    plt.xlabel('Productos')
    plt.ylabel('Cantidad Fabricada')
    plt.title('Producción de cada producto')
    plt.legend()

    # Mostrar el valor sobre cada barra
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}', ha='center', va='bottom')


    # Mostrar el gráfico
    plt.show()

# Crea el modelo
mdl, produccion_vars = create_model()

# Soluciona el modelo
solve_model(mdl)