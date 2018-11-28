import pyomo.environ as pe

A = [[0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0]]

d = [4, 5, 6, 1, 8, 5]

# Create the model
model = pe.ConcreteModel()
model.dual = pe.Suffix(direction = pe.Suffix.IMPORT)
# ------ SETS ---------
model.dd = pe.Set(initialize = range(6))
# ------PARAMETERS--------
model.d = pe.Param(model.dd, initialize = lambda model, c: d[c])
model.A = pe.Param(model.dd, model.dd,\
                     initialize = lambda model, i, j: A[i][j])
# -------------VARIABLES------------
model.s = pe.Var(model.dd, domain = pe.NonNegativeReals)
# ------CONSTRAINTS-----------
def precedence_rule(model, i, j):
    if model.A[i,j] == 1:
        return model.s[i] + model.d[i] <= model.s[j]
    else:
        return pe.Constraint.Feasible
 
model.precedenceCons = pe.Constraint(model.dd,\
                 model.dd, rule = precedence_rule)
# ------OBJECTIVE-----------
def obj_rule(model):
    return model.s[5] + d[5]
    
model.OBJ = pe.Objective(rule = obj_rule, sense = pe.minimize)
model.OBJ.pprint()
#----------SOLVING----------
solver = pe.SolverFactory('gurobi') # Specify Solver
results = solver.solve(model, tee = False, keepfiles = False)
print()
print("Status:", results.solver.status)
print("Termination Condition:", \
                    results.solver.termination_condition)
# ---------POST-PROCESSING-------------------
print()
for c in model.s:
    print('s %d is %d'%(c+1, model.s[c].value))
print("\nObjective function value: ", model.OBJ())