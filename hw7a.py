from PIL import Image
import pyomo.environ as pe
import scipy

im = Image.open('tower.png').convert('L') #convert to grayscale

h = im.height
w = im.width

print('height is: %d \n'%(h)) # height is 120 pixels
print('width is: %d \n'%(w)) # width is 177 pixels

#grayscale values; list of size h*w , where each values is integer in range [0,255]
intensity = list(im.getdata()) # it follows by rows, (i,j) means intensity[120*(i-1) + j - 1]

print(len(intensity)) # the list has the length of 21240 (120 * w)

# YOUR CODE GOES HERE
pathfile = open('pathfile.txt','a')
for iteration in range(25):
    # Calculate the existed edges
    sourcenode = w * (1-1) + (50 - 1)
    targetnode = 1000000
    Startnode = list([sourcenode])
    Edges = list()

    for t in range(2, 122):
        tempEdges = list()
        if t != 121:
            for i in Startnode:
                icol = (i + 1)%w
                if icol != 1 and icol != w:
                    tempEdges.append([i, w * (t-1) + (icol - 2)])
                    tempEdges.append([i, w * (t-1) + (icol - 1)])
                    tempEdges.append([i, w * (t-1) + (icol)])
                elif icol == 1:
                    tempEdges.append([i, w * (t-1) + (icol - 1)])
                    tempEdges.append([i, w * (t-1) + (icol)])
                elif icol == w:
                    tempEdges.append([i, w * (t-1) + (icol - 2)])
                    tempEdges.append([i, w * (t-1) + (icol - 1)])
                
            Startnode = list()
            for j in tempEdges:
                Startnode.append(j[1])
            Startnode = list(set(Startnode))
            Startnode.sort()

        elif t == 121:
            for i in Startnode:
                tempEdges.append([i, targetnode])
        Edges = Edges + tempEdges

    print('The number of edges is %d'%(len(Edges)))

    # Calculate the cost for each edge
    CostEdges = []
    for edge in Edges:
        if edge[1] != targetnode:
            CostEdges.append(abs(intensity[edge[0]] - intensity[edge[1]]))
        else:
            CostEdges.append(0)
    print('The number of costs is %d'%(len(CostEdges)))
    # print(CostEdges)

    # Calculate the node can be arrived
    Nodes = [i for k in Edges for i in k]
    Nodes = list(set(Nodes))
    Nodes.sort()
    print('There are %d node can arrive.'%(len(Nodes)))
    # print('Node %d and %d'%(Nodes[len(Nodes)-1], Nodes[0]))
    
    # Create the model
    model = pe.ConcreteModel()

    model.dual = pe.Suffix(direction = pe.Suffix.IMPORT)

    # ------ SETS ---------
    model.nodes = pe.Set(initialize = range(len(Nodes)))
    model.edges = pe.Set(initialize = range(len(Edges)))
    model.lenintensity = pe.Set(initialize = range(len(intensity)))
    model.h = pe.Set(initialize = range(h))
    model.w = pe.Set(initialize = range(w))

    # ------PARAMETERS--------
    model.intensity = pe.Param(model.lenintensity, initialize = lambda model, t: intensity[t])

    # -------------VARIABLES------------
    model.x = pe.Var(model.edges, domain = pe.NonNegativeReals)

    # ------CONSTRAINTS-----------
    def sumentry(Edges, CostEdges, nodeid):
        entry = []
        for i in range(len(Edges)):
            edge = Edges[i]
            if edge[0] == nodeid:
                entry.append(i)
        return entry

    def sumleave(Edges, CostEdges, nodeid):
        leave = []
        for i in range(len(Edges)):
            edge = Edges[i]
            if edge[1] == nodeid:
                leave.append(i)
        return leave

    def enterleave_rule(model, nodeid):
        if nodeid%1000 == 0:
            print(nodeid)
        entry = sumentry(Edges, CostEdges, Nodes[nodeid])

        Xentry = sum(model.x[i] for i in entry)
        leave = sumleave(Edges, CostEdges, Nodes[nodeid])

        Xleave = sum(model.x[j] for j in leave)
        
        if Nodes[nodeid] == sourcenode:
            return (Xentry - Xleave == 1)
        elif Nodes[nodeid] == targetnode:
            return (Xentry - Xleave == -1)
        else:
            return (Xentry - Xleave == 0)

    model.callsCons = pe.Constraint(model.nodes, rule = enterleave_rule)

    # ------OBJECTIVE-----------

    def obj_rule(model):
        return sum(CostEdges[i] * model.x[i] for i in model.edges)
        
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
    optimalpath = list([])
    nodeofpath = []
    for i in range(len(Edges)):
        if model.x[i].value == 1:
            # nextnode = Edges[i][1]
            nownode = Edges[i][0]
            optimalpath.append([int(nownode/w) + 1, (nownode+1)%w])          
            nodeofpath.append(nownode)
            print(Edges[i])
    print(optimalpath)        
    print("\nObjective function value: ", model.OBJ())

    for i in nodeofpath:
        intensity[i] = 0
    arr = scipy.reshape(intensity,(h,w)).astype('uint8')
    temp_image = Image.fromarray(arr)
    temp_image.save('temp_img_before%d.png'%(iteration+1))
    
    pathfile.write('The number of edges is %d \n'%(len(Edges)))
    pathfile.write('The number of costs is %d \n'%(len(CostEdges)))
    pathfile.write('There are %d node can arrive. \n'%(len(Nodes)))
    pathfile.write('The optimal value for the %d th image is %d: \n'%(iteration+1, model.OBJ()))
    pathfile.write('The optimal path for the %d th image is: \n'%(iteration+1))
    pathfile.write(str(optimalpath))
    pathfile.write('  \n')

    for i in sorted(nodeofpath, reverse=True):
        del intensity[i]

    w = w - 1
    print('w = %d'%(w))
    arr = scipy.reshape(intensity,(h,w)).astype('uint8')
    temp_image = Image.fromarray(arr)
    temp_image.save('temp_image%d.png'%(iteration+1))
pathfile.close()

# resize final intensities and save as an image
arr = scipy.reshape(intensity,(h,w)).astype('uint8')
final_image = Image.fromarray(arr)
final_image.save('final_image.png')
