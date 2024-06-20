import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, FixedFormatter
import numpy as np
bvhFile = open("dataset/bvh/noFaceNoHands/016_lookback.bvh")
jointInfo = dict()
hierarchyNames = []

"""Conseguir los datos de los joints"""

actualJoint = ""
initialJointPosition = []
whatDegreesOfFreedom = []
dof = 0
for line in bvhFile:
  splittedLine = line.split()
  if "JOINT" in splittedLine or "ROOT" in splittedLine:
    actualJoint = splittedLine[1]
    hierarchyNames.append(actualJoint)
  if "OFFSET" in splittedLine:
    initialJointPosition = splittedLine[1:]
  if "CHANNELS" in splittedLine:
    dof = splittedLine[1]
    whatDegreesOfFreedom = splittedLine[2:]
    allInfo = dict()
    allInfo["name"] = actualJoint
    allInfo["initialJointPosition"] = initialJointPosition
    allInfo["degreesOfFreedom"] = dof
    allInfo["whatDegreesOfFreedom"] = whatDegreesOfFreedom
    jointInfo[actualJoint] = allInfo
  if "Frame" in splittedLine: #en la siguiente linea empieza frame a frame las posiciones y rotaciones
    break

"""Extraer en cada frame las posiciones y rotaciones"""

frame = 1
for dataLine in bvhFile:
  splittedDataLine = dataLine.split()
  i = 0
  for key in hierarchyNames:
    allInfo = jointInfo[key]
    dof = int(allInfo["degreesOfFreedom"])

    if "positionDict" not in allInfo.keys() and dof == 6: 
      positionDict = dict()
      allInfo["positionDict"] = positionDict
    elif "positionDict" in allInfo.keys():
      positionDict = allInfo["positionDict"]
    if "rotationDict" not in allInfo.keys() and dof > 2:
      rotationDict = dict()
      allInfo["rotationDict"] =  rotationDict
    else:
        rotationDict = allInfo["rotationDict"]

    if dof == 3:
      rotation = splittedDataLine[i:dof+i]
      rotationDict[frame] = rotation
      allInfo["rotationDict"] = rotationDict
    else:

      position = splittedDataLine[i:dof+i-3]
      rotation = splittedDataLine[dof+i-3:i+dof]
      positionDict[frame] = position
      rotationDict[frame] = rotation
      allInfo["positionDict"] = positionDict
      allInfo["rotationDict"] = rotationDict


    i+=dof
    jointInfo[key] = allInfo

  frame+=1

"""Ahora que ya están los datos, preguntamos que gráficas y de qué joints se quieren dibujar"""

print("What joints would you like to visualize?")
for i, valor in enumerate(hierarchyNames):
    print(f"{i}. {valor}", end='      ') 
    # Verificar si es el décimo valor de la fila
    if (i + 1) % 5 == 0:
        print()  # Salto de línea

print()
answerJoints = input("Introduce the number of joints you want to visualize ej: 1,2,3,4 (all for all): ")

"""Ahora preguntamos sobre qué gráficas mostrar."""

print("Which data do you want to plot?")
print("1. Positions and rotations")
print("2. Positions")
print("3. Rotations")


answerPlots = input("Answer: ")

print("Which axis would you like to plot?")
print("1. All")
print("2. X")
print("3. Y")
print("4. Z")
print("You can select any combination like this: 2 4 | 2 3")
print("Note, there are joints that lack positional degrees of freedom, therefore the plot will be empty")

answerAxis = input("Axis: ")

"""Ahora procesamos la entrada del usuario"""

axisToDraw = []
splitAnswerAxis = answerAxis.split()
if len(splitAnswerAxis) > 0 and splitAnswerAxis[0] != "1":
  for axis in splitAnswerAxis:
    axisToDraw.append(int(axis) - 2)
elif splitAnswerAxis[0] == "1":
  axisToDraw = [0,1,2]
else:
  exit(1)

print(axisToDraw)

jointsSelected = []
splitAnswerJoints = answerJoints.split(",")
if len(splitAnswerJoints) > 0 and splitAnswerJoints[0] != "all":
  for joint in splitAnswerJoints:
    jointsSelected.append(hierarchyNames[int(joint)])
else:
  jointsSelected = "all"

print(jointsSelected)

"""Ahora dibujamos las gráficas"""

jointsToDraw = []
if jointsSelected == "all":
  jointsToDraw = jointInfo.keys()
else:
  jointsToDraw = jointsSelected

if answerPlots == "1" or answerPlots == "2": # dibujar gráficas de posición por lo menos
  fig, ax = plt.subplots()
  for joint in jointsToDraw:
    jInfo = jointInfo[joint]
    if "positionDict" not in jInfo.keys():
      continue
    pDict = jInfo["positionDict"]
    nFrames = pDict.keys()
    x_values = []
    y_values = []
    z_values = []
    for frame in pDict.keys():
      posFrame = pDict[frame]
      x_values.append(float(posFrame[0]))
      y_values.append(float(posFrame[1]))
      z_values.append(float(posFrame[2]))


    # Trazar las líneas para cada coordenada
    if 0 in axisToDraw:
      plt.plot(nFrames, x_values, label=f'{joint} - X', linewidth=2)
    if 1 in axisToDraw:
      plt.plot(nFrames, y_values, label=f'{joint} - Y', linewidth=2)
    if 2 in axisToDraw:
      plt.plot(nFrames, z_values, label=f'{joint} - Z', linewidth=2)

  # Personalización del gráfico
  # Personalización del gráfico
  plt.xlabel('Frame', color='white')
  plt.ylabel('Position', color='white')
  plt.title('Position value per frame', color='white')
  #plt.legend()

  # Cambiar el color de los ejes y las etiquetas
  """
  ax.tick_params(axis='x', colors='white')
  ax.tick_params(axis='y', colors='white')
  ax.spines['bottom'].set_color('white')
  ax.spines['left'].set_color('white')
  ax.set_facecolor('white')
  fig.set_facecolor('white')
  """
  #save the plot in the sabingdir
  #plt.legend()
  plt.grid(False)
  #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

  # Mostrar el gráfico
  plt.show()

if answerPlots == "1" or answerPlots == "3": # dibujar gráficas de rotacion por lo menos
  fig, ax = plt.subplots()
  for joint in jointsToDraw:
    jInfo = jointInfo[joint]
    if "rotationDict" not in jInfo.keys():
      continue
    rDict = jInfo["rotationDict"]
    nFrames = rDict.keys()
    x_values = []
    y_values = []
    z_values = []
    for frame in rDict.keys():
      posFrame = rDict[frame]
      x_values.append(float(posFrame[0]))
      y_values.append(float(posFrame[1]))
      z_values.append(float(posFrame[2]))

    # Trazar las líneas para cada coordenada
    if 0 in axisToDraw:
      plt.plot(nFrames, x_values, label=f'{joint} - RX', linewidth=2)
    if 1 in axisToDraw:
      plt.plot(nFrames, y_values, label=f'{joint} - RY', linewidth=2)
    if 2 in axisToDraw:
      plt.plot(nFrames, z_values, label=f'{joint} - RZ', linewidth=2)

  # Personalización del gráfico
  #plt.xlabel('Frame', color='white')
  #plt.ylabel('Rotation', color='white')
  plt.title('Rotation value per frame', color='white')
  #plt.legend()

  # Cambiar el color de los ejes y las etiquetas
  """
  ax.tick_params(axis='x', colors='white')
  ax.tick_params(axis='y', colors='white')
  ax.spines['bottom'].set_color('white')
  ax.spines['left'].set_color('white')
  """

  # Ajustar los ticks principales del eje Y en intervalos de pi/2
  #plt.gca().yaxis.set_major_locator(MultipleLocator(base=np.pi/2))
  #ax.set_facecolor('black')
  #fig.set_facecolor('black')
  #plt.legend()
  plt.grid(False)
  #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., ncol=4)
  # Mostrar el gráfico
  legend_path = f'{savingDir}legend.png'
  plt.legend()
  plt.savefig(legend_path)
  plt.show()
