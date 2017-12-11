r1 = 57 # length of the inner bar
r2 = 48 # length of the outer bar
dr = 0.8  # ratio of radial distance of hole to r2
jobName = 'Spirograph-1'

from abaqus import *
from abaqusConstants import *
from caeModules import *
from fractions import gcd

# Create model
modelSpirograph = mdb.Model(name='Spirograph')

# Create parts

sketch = modelSpirograph.ConstrainedSketch(name='bar', sheetSize=r1)
partBar1 = modelSpirograph.Part(name='Bar-1', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
sketch.Line(point1=(0,0), point2=(r1,0))
partBar1.BaseWire(sketch=sketch)
vertice0 = partBar1.vertices[0]
partBar1.ReferencePoint(point=vertice0)

sketch = modelSpirograph.ConstrainedSketch(name='bar', sheetSize=r1+r2)
partBar2 = modelSpirograph.Part(name='Bar-2', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
sketch.Line(point1=(r1,0), point2=(r1+r2,0))
partBar2.BaseWire(sketch=sketch)
vertice0 = partBar2.vertices[0]
partBar2.ReferencePoint(point=vertice0)
if dr != 1.:
    edges = partBar2.edges[:]
    partBar2.PartitionEdgeByParam(edges=edges, parameter=dr)

# Create material and section
modelSpirograph.Material(name='Material-1')
modelSpirograph.materials['Material-1'].Elastic(table=((1.0, 0.0), ))
modelSpirograph.TrussSection(name='Section-1', material='Material-1', area=1.0)

# Assign section
set = partBar1.Set(name='bar',edges=partBar1.edges)
partBar1.SectionAssignment(region=set,sectionName='Section-1')
set = partBar2.Set(name='bar',edges=partBar2.edges[:])
partBar2.SectionAssignment(region=set,sectionName='Section-1')

# Create assembly
assemblySpirograph = modelSpirograph.rootAssembly
instanceBar1 = assemblySpirograph.Instance(name='Bar1', part=partBar1, dependent=ON)
instanceBar2 = assemblySpirograph.Instance(name='Bar2', part=partBar2, dependent=ON)

# Create connector and rigid constraints
modelSpirograph.ConnectorSection(name='ConnSect-1', translationalType=JOIN)
refPointBar2 = instanceBar2.referencePoints[instanceBar2.referencePoints.keys()[0]]
verticeRightBar1 = instanceBar1.vertices[1]
assemblySpirograph.WirePolyLine(points=((refPointBar2, verticeRightBar1),),
                                mergeType=IMPRINT, 
                                meshable=False)
wire = assemblySpirograph.edges[0:1]
set = assemblySpirograph.Set(name='Wire', edges=wire)
assemblySpirograph.SectionAssignment(sectionName='ConnSect-1', region=set)

refPointBar1 = instanceBar1.referencePoints[instanceBar1.referencePoints.keys()[0]]
regionRefPointBar1 = regionToolset.Region(referencePoints=(refPointBar1,))
edges = instanceBar1.edges[:]
region = assemblySpirograph.Set(name='Bar1', edges=edges)
modelSpirograph.RigidBody(name='RigidBar1', refPointRegion=regionRefPointBar1, 
                          bodyRegion=region)  
regionRefPointBar2 = regionToolset.Region(referencePoints=(refPointBar2,))
edges = instanceBar2.edges[:]
region = assemblySpirograph.Set(name='Bar2', edges=edges)
modelSpirograph.RigidBody(name='RigidBar2', refPointRegion=regionRefPointBar2, 
                          bodyRegion=region)  

# Create step
time = r2 / gcd(r1+r2, r2)
modelSpirograph.StaticStep(name='Step-1', 
                            previous='Initial', 
                            timePeriod=time, 
                            maxNumInc=1000000, 
                            nlgeom=ON)
modelSpirograph.FieldOutputRequest(name='FieldOutput',createStepName='Step-1')
modelSpirograph.fieldOutputRequests['FieldOutput'].setValues(variables=('U',),timeInterval=1/30.)

# Create BCs
modelSpirograph.DisplacementBC(name='Pin1', createStepName='Initial', region=regionRefPointBar1, u1=SET, u2=SET)
modelSpirograph.VelocityBC(name='w1', createStepName='Step-1', region=regionRefPointBar1, vr3=2*pi)
w2 = - 2 * pi * r1 / r2
modelSpirograph.VelocityBC(name='w2', createStepName='Step-1', region=regionRefPointBar2, vr3=w2)

# Create mesh
edge = partBar1.edges[:]
partBar1.seedEdgeByNumber(edges=edge, number=1)
edge = partBar2.edges[:]
partBar2.seedEdgeByNumber(edges=edge, number=1)
elemType = mesh.ElemType(elemCode=T2D2, elemLibrary=STANDARD)
edges = (partBar1.edges[:], )
partBar1.setElementType(regions=edges,  elemTypes=(elemType, ))
partBar1.generateMesh()
edges = (partBar2.edges[:], )
partBar2.setElementType(regions=edges,  elemTypes=(elemType, ))
partBar2.generateMesh()

# Create job
job=mdb.Job(name=jobName, model=modelSpirograph)
job.submit()
