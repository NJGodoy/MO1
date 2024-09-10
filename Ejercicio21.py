# Import libs
import sys
import matplotlib.pyplot as plt
from docplex.mp.model import Model
from docplex.mp.relax_linear import LinearRelaxer

try:
    import docplex.mp
except:
    raise Exception('Please install docplex. See https://pypi.org/project/docplex/')

# Declare the parameters

# name, benefit, max demand, min demand
products = [("A", 10),
            ("B1", 15),
            ("B2", 15),
            ("C", 18)]

# resources are a list of simple tuples (name, capacity)
resources = [("Maquina1", 80),
             ("Maquina2", 80),
             ("LanaNormal", 36),
             ("LanaMejorada", 20)]

consumptions = {("A", "Maquina1"): 5,
                ("B1", "Maquina1"): 6,
                ("B2", "Maquina1"): 0,
                ("C", "Maquina1"): 0,
                ("A", "Maquina2"): 0,
                ("B1", "Maquina2"): 0,
                ("B2", "Maquina2"): 4,
                ("C", "Maquina2"): 4,
                ("A", "LanaNormal"): 0,
                ("B1", "LanaNormal"): 1.8,
                ("B2", "LanaNormal"): 1.8,
                ("C", "LanaNormal"): 0,
                ("A", "LanaMejorada"): 1.6,
                ("B1", "LanaMejorada"): 0,
                ("B2", "LanaMejorada"): 0,
                ("C", "LanaMejorada"): 1.2}

# Create the model with constraints and objective
def create_model():
    mdl = Model(name="Ejercicio 2.1")

    produccion_vars = mdl.continuous_var_dict(products, name='produccion')

    # --- constraints ---

    # --- resources disp equipo ---
    mdl.add_constraints((mdl.sum(produccion_vars[p] * consumptions[p[0], res[0]] for p in products) <= res[1], 'Disp_%s' % res[0]) for res in resources)

    # --- print information ---
    mdl.print_information()

    total_benefit = mdl.sum(produccion_vars[p] * p[1] for p in products)

    # --- set the objective ---
    mdl.maximize(total_benefit)

    return mdl, produccion_vars, products

# Solve the model
def solve_model(mdl):
    solution = mdl.solve()

    if not solution:
        print("Model cannot be solved.")
        sys.exit(1)

    obj = mdl.objective_value

    print("* Production model solved with objective: {:g}".format(obj))
    print("* Total benefit=%g" % mdl.objective_value)
    for p in products:
        print("Production of {product}: {prod_var:.3f}".format(product=p[0], prod_var=produccion_vars[p].solution_value))

# Create the model with constraints and objective
mdl, produccion_vars, products = create_model()

# Solve the model
solve_model(mdl)