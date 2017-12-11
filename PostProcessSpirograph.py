jobName = 'Spirograph-1'
color = '#b777b7'
writePNG = True

from abaqus import *
from abaqusConstants import *
from odbAccess import *
import visualization
import numpy as np

# Postprocessing
viewport = session.viewports['Viewport: 1']
try:
    for odbName in session.odbs.keys():
        if jobName in odbName:
            session.odbs[odbName].close()
except:
    None

odb = openOdb(path=''.join((jobName, '.odb')), readOnly=True)
viewport.setValues(displayedObject=odb)
rMax = 0
for node in odb.rootAssembly.instances['BAR2'].nodes:
    if node.coordinates[0] > rMax:
        rMax = node.coordinates[0]

session.viewports['Viewport: 1'].view.setValues(height=2*rMax+20)
session.viewports['Viewport: 1'].view.setValues(cameraTarget=(0,0,0,))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(DEFORMED,))
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')

nodeLabel = 2
instance = odb.rootAssembly.instances['BAR2']
nodeSetName = ''.join((instance.name, str(nodeLabel)))
try:
    nodeSet = instance.NodeSetFromNodeLabels(name=nodeSetName, nodeLabels=(nodeLabel,))
except OdbError:
    nodeSet = instance.nodeSets[nodeSetName]
    None

session.graphicsOptions.setValues(backgroundColor='#333333')
session.printOptions.setValues(vpDecorations=OFF, vpBackground=ON)
stepRepo = odb.steps
s = 0
file = 0
lines=()
for stepKey in stepRepo.keys():
    step = stepRepo[stepKey]
    for f in range(0, len(step.frames)):
        displacements_0 = step.frames[f-1].fieldOutputs['U'].getSubset(region=nodeSet).values[0].data
        displacements_1 = step.frames[f].fieldOutputs['U'].getSubset(region=nodeSet).values[0].data
        if len(displacements_0) == 2:
            coordsCurrent_0 = nodeSet.nodes[0].coordinates + np.append(displacements_0,[0])
            coordsCurrent_1 = nodeSet.nodes[0].coordinates + np.append(displacements_1,[0])
        else:
            coordsCurrent_0 = nodeSet.nodes[0].coordinates + displacements_0
            coordsCurrent_1 = nodeSet.nodes[0].coordinates + displacements_1
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=s, frame=f)
        a=odb.userData.Arrow(name=''.join((stepKey, str(f))),
                             startAnchor=coordsCurrent_0, 
                             endAnchor=coordsCurrent_1,  
                             endHeadStyle=NONE, 
                             color=color)
        lines += (a,)
        for lineSeg in lines:
            session.viewports['Viewport: 1'].plotAnnotation(annotation=lineSeg)
        highlight(object=nodeSet.nodes[0])
        if writePNG:
            session.printToFile(fileName=str(file), format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
            file += 1
