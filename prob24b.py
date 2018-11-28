import pyomo.environ as pe

tickets = [[20, 50, 200], [10, 25, 175], [5, 10, 150]]

Profits = [[3, 2, 1], [3, 2, 1], [3, 2, 1]]

Space = [2, 1.5, 1]

Section = [1, 2, 3]

o = len(Section)
e = len(Space)    

# Create the model
model = pe.ConcreteModel()

model.dual = pe.Suffix(direction = pe.Suffix.IMPORT)

# ------ SETS ---------
model.Section  = pe.Set(initialize = range(o))
model.classes  = pe.Set(initialize = range(e))

# ------PARAMETERS--------
def tickets_func(model, c, p): 
    return tickets[c][p]

model.tickets = pe.Param(model.Section, model.classes, initialize = tickets_func)

model.Space = pe.Param(model.classes, initialize = lambda model, sp: Space[sp])

def Profits_func(model, c, p):
    return Profits[c][p]

model.Profits = pe.Param(model.Section, model.classes, initialize = Profits_func)

# -------------VARIABLES------------
model.X = pe.Var(model.classes, domain = pe.NonNegativeReals)
model.Z = pe.Var(model.Section, model.classes, domain = pe.NonNegativeReals)

# ------CONSTRAINTS-----------
def tickets_rule(model, c, p):
    return (model.Z[c, p] <= model.tickets[c, p])
    
model.ticketsCons = pe.Constraint(model.Section, model.classes, rule = tickets_rule)

def seat_rule(model, c, p):
    return (model.Z[c, p] <= model.X[p])

model.seatCons = pe.Constraint(model.Section, model.classes, rule = seat_rule)

def Space_rule(model, c):
    return (sum(model.X[c] * model.Space[c] for c in model.classes) <= 200)

model.SpaceCons = pe.Constraint(model.classes, rule = Space_rule)

# ------OBJECTIVE-----------

def obj_rule(model):
    return sum(model.Profits[c,p] * model.Z[c,p] for c in model.Section for p in model.classes)
    
model.OBJ = pe.Objective(rule = obj_rule, sense = pe.maximize)

model.OBJ.pprint()

#----------SOLVING----------
solver = pe.SolverFactory('gurobi') # Specify Solver

results = solver.solve(model, tee = False, keepfiles = False)

print()
print("Status:", results.solver.status)
print("Termination Condition:", results.solver.termination_condition)


# ---------POST-PROCESSING-------------------
print()
for c in model.classes:
    print('The class %d has %d seats'%(c, model.X[c].value))

print("\nObjective function value: ", model.OBJ())