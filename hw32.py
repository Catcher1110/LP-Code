import pyomo.environ as pe

FTEE = [15, 10, 9, 8, 8, 17,
        40, 55, 63, 70, 72, 69,
        48, 75, 80, 72, 71, 55,
        30, 20, 21, 18, 17, 16]

wage = [15.20, 12.95]

worktime = [8, 4]

nf = len(FTEE)    # number of FTEE
nw = len(worktime)
nwa = len(wage)

# Create the model
model = pe.ConcreteModel()

model.dual = pe.Suffix(direction = pe.Suffix.IMPORT)

# ------ SETS ---------
model.times = pe.Set(initialize = range(nf))
model.wage = pe.Set(initialize = range(nwa))
model.worktime = pe.Set(initialize = range(nw))

# ------PARAMETERS--------
def ftee_func(model, c): 
    return FTEE[c]

model.ftee = pe.Param(model.times, initialize = ftee_func)

model.worktime = pe.Param(model.worktime, initialize = lambda model, t: worktime[t])

def wage_func(model, c):
    return wage[c]

model.wage = pe.Param(model.wage, initialize = wage_func)

# -------------VARIABLES------------
model.full = pe.Var(model.times, domain = pe.NonNegativeReals)
model.part = pe.Var(model.times, domain = pe.NonNegativeReals)

# ------CONSTRAINTS-----------
def calls_rule(model, c):
    fullres = 0
    partres = 0
    for i in range(8):
        if c - i < 0:
            fullres = fullres + model.full[c-i+24]
        else:
            fullres = fullres + model.full[c-i]
    for j in range(4):
        if c - j < 0:
            partres = partres + model.part[c-j+24]
        else:
            partres = partres + model.part[c-j]
    res = 6 * fullres + 5 * partres
    return (res >= 6 * model.ftee[c])
    
model.callsCons = pe.Constraint(model.times, rule = calls_rule)

def twothirds_rule(model, c):
    fullres = 0
    partres = 0
    for i in range(8):
        if c - i < 0:
            fullres = fullres + model.full[c-i+24]
        else:
            fullres = fullres + model.full[c-i]
    for j in range(4):
        if c - j < 0:
            partres = partres + model.part[c-j+24]
        else:
            partres = partres + model.part[c-j]    
    return (fullres >= partres)

model.twothirdsCons = pe.Constraint(model.times, rule = twothirds_rule)

# ------OBJECTIVE-----------

def obj_rule(model):
    fulltimewage = model.worktime[0] * model.wage[0] * sum(model.full[i] for i in model.times)
    parttimewage = model.worktime[1] * model.wage[1] * sum(model.part[i] for i in model.times)
    return fulltimewage + parttimewage
    
model.OBJ = pe.Objective(rule = obj_rule, sense = pe.minimize)

model.OBJ.pprint()

#----------SOLVING----------
solver = pe.SolverFactory('gurobi') # Specify Solver

results = solver.solve(model, tee = False, keepfiles = False)

print()
print("Status:", results.solver.status)
print("Termination Condition:", results.solver.termination_condition)


# ---------POST-PROCESSING-------------------
print()
for c in model.times:
    print('At %d o\'clock %d full-time employee and %d part-time employee begin to work'%(c, model.full[c].value, model.part[c].value))
for c in model.times:
    fullres = 0
    partres = 0
    for i in range(8):
        if c - i < 0:
            fullres = fullres + model.full[c-i+24].value
        else:
            fullres = fullres + model.full[c-i].value
    for j in range(4):
        if c - j < 0:
            partres = partres + model.part[c-j+24].value
        else:
            partres = partres + model.part[c-j].value
    print('At %d o\'clock %d full-time employee and %d part-time employee currently working'%(c, fullres, partres)) 
print("\nObjective function value: ", model.OBJ())