# Import libs
import sys
import matplotlib.pyplot as plt
from docplex.mp.model import Model
from docplex.mp.relax_linear import LinearRelaxer

try:
    import docplex.mp
except:
    raise Exception('Please install docplex. See https://pypi.org/project/docplex/')

# Declaración de parámetros

D1, D2, D3 = 40, 30, 30
P1, P2, P3 = 100, 40, 40
# nombre, precio de venta, demanda minima
products = [("SILLAS", P1, D1),
            ("TAB4", P2, D2),
            ("TAB3", P3, D3)]

# elementos recuperados
good_parts = ("RS1", "AS1", "PS1",
              "AS2", "PS2",
              "AS3", "PS3")
A = 70
R = 80
P = 20
# elementos faltantes
# nombre, precio de compra
missing_parts = (("RC1", R), ("AC1", A), ("PC1", P),
                 ("AC2", A), ("PC2", P),
                 ("AC3", A), ("PC3", P))

# produccion
production = {"SILLAS" : {"R" : 1, "A" : 1, "P" : 4},
              "TAB4" : {"A" : 1, "P" : 4},
              "TAB3" : {"A" : 1, "P" : 3}}

# sillas rotas
broken_furniture = {"RR" : 30, "AR" : 30, "P1" : 20, "P2" : 10, "RR1P" : 30}
salvage = {"RS" : broken_furniture["AR"] + broken_furniture["P1"] + broken_furniture["P2"],
              "AS" : broken_furniture["RR"] + broken_furniture["P1"] + broken_furniture["P2"] + broken_furniture["RR1P"],
              "PS" : 4 * (broken_furniture["RR"] + broken_furniture["AR"]) + 3 * (broken_furniture["P1"] + broken_furniture["RR1P"])
               + 2 * broken_furniture["P2"]}

def create_model():
    mdl = Model(name="Ejercicio 2.32")

    produccion_vars = {}
    for p in products:
        produccion_vars[p[0]] = mdl.integer_var(name="produccion_" + p[0])
    for i in range(len(good_parts)):
        produccion_vars[good_parts[i]] = mdl.integer_var(name="Used_" + good_parts[i])
        produccion_vars[missing_parts[i][0]] = mdl.integer_var(name="Bought_" + missing_parts[i][0])

    # --- restricciones ---

    # --- produccion ---
    i = 1
    for product, parts in production.items():
        for key, num in parts.items():
            mdl.add_constraint(num*produccion_vars[product] == produccion_vars[key + "S" + str(i)] + produccion_vars[key + "C" + str(i)])
        i += 1

    # --- disponibilidad partes---
    mdl.add_constraint(produccion_vars["PS1"] + produccion_vars["PS2"] + produccion_vars["PS3"] <= salvage["PS"], "Disponibilidad_Patas")
    mdl.add_constraint(produccion_vars["RS1"] <= salvage["RS"], "Disponibilidad_Respaldos")
    mdl.add_constraint(produccion_vars["AS1"] + produccion_vars["AS2"] + produccion_vars["AS3"] <= salvage["AS"], "Disponibilidad_Asientos")
    
    # --- demanda ---
    for p in products:
        mdl.add_constraint(produccion_vars[p[0]] >= p[2])

    # --- print information ---
    mdl.print_information()
    
    # --- set the objective ---
    revenue = mdl.sum(produccion_vars[p[0]] * p[1] for p in products)
    costs = mdl.sum(produccion_vars[p[0]] * p[1] for p in missing_parts)
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
    for p in products:
        print(f"{p[0]} : {produccion_vars[p[0]].solution_value}")

# Crea el modelo
mdl, produccion_vars = create_model()

# Soluciona el modelo
solve_model(mdl)