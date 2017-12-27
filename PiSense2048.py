from sense_hat import SenseHat
import evdev
from select import select
import random
import time
import sys

sh = SenseHat()

# Clear LEDs
sh.clear()


#Define the colours for each 'number' square
global colourClear
colourClear = [0,0,0]
global colour2
colour2 = [255,0,0]
global colour4
colour4 = [255,128,0]
global colour8
colour8 = [0,255,0]
global colour16
colour16 =  [255,255,0]
global colour32
colour32 = [0,255,128]
global colour64
colour64 = [255,0,128]
global colour128
colour128 = [128,0,255]
global colour256
colour256 = [225,128,55]
global colour512
colour512 = [0,0,255]
global colour1024
colour1024 = [134,55,10]
global colour2048
colour2048 = [255,255,255]

colours = {'_':colourClear,'2':colour2, '4':colour4,'8':colour8,'16':colour16,
           '32':colour32,'64':colour64,'128':colour128,'256':colour256,
           '512':colour512,'1024':colour1024,'2048':colour2048}

global score
score = 0


# check devices
ecodes = evdev.ecodes
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for dev in devices:
    print(dev.name)
    if dev.name == "Raspberry Pi Sense HAT Joystick":
        js=dev
        print('found')

def lightSquare(c, l, color):
    c = c*2
    l = l*2
    sh.set_pixel(l,c,color)
    sh.set_pixel(l+1,c+1,color)
    sh.set_pixel(l+1,c,color)
    sh.set_pixel(l,c+1,color)
    return
    

def renderBoard(listNbyN):
    for c in range(4):
        for l in range(4):
            lightSquare(c, l, colours[listNbyN[c][l]])
    return
            
            
    

def printBoard(listNbyN):
  #Print a two dimentional list of numbers visually as a matrix
  
  rowsList = []
  for row in listNbyN:
    rowsList.append("\t".join(row))
  print("\n" + "\n\n".join(rowsList) + "\n")   
    
def isBoardFull(list4by4):
  #Check if board is full of numbers
  
  for row in list4by4:
    for cell in row:
      if cell == "_":
        return(False)
  return(True)
  
def isFailure(list4by4):
  #Check if board is in a losing position
  
  if isBoardFull(list4by4) == False: return(False)
  #check left/right matches
  for i in range(1,3):
    for j in range(0,4):
      if list4by4[j][i] == list4by4[j][i-1] or \
      list4by4[j][i] == list4by4[j][i+1]:
        return(False)
  #check up/down matches
  for i in range(0,4):
    for j in range(1,3):
      if list4by4[j][i] == list4by4[j-1][i] or \
      list4by4[j][i] == list4by4[j+1][i]:
        return(False)
  return(True)
  
def isWinner(listNbyN):
  #Check if board is in winning position (if it contains a "2048")
  
  for row in listNbyN:
    for cell in row:
      if cell == "2048":
        return(True)
  return(False)
  
def fallDown(list4by4):
  #Cells "fall" one blank space down, but do not add
  
  results = list4by4
  for i in range(0,4):
    for j in [3, 2, 1]:
      if results[j][i] == "_":
        results[j][i] = results[j-1][i]
        results[j-1][i] = "_"
  return(results)

def addDown(list4by4):
  #Cells add into identical cell below, but do not fall otherwise
  
  results = list4by4
  for i in range(0,4):
    for j in [3, 2, 1]:
      if results[j][i] == results[j-1][i] and results[j][i] != "_":
        results[j][i] = str(int(results[j-1][i])*2)
        results[j-1][i] = "_"
  return(results)
  
def moveDown(list4by4):
  #Cells perform all falling and adding actions involved with a 'down' move.

  #To Do: what's a better way to take static snapshot of 2D list??
  boardSnapshot = [list4by4[0][:], list4by4[1][:], list4by4[2][:], 
  list4by4[3][:]]
  
  #Three "falls", one "addDown", and two more falls seem to mimic behavior of 
  # the game. 
  tempBoard = fallDown(list4by4)
  tempBoard = fallDown(tempBoard)
  tempBoard = fallDown(tempBoard)
  tempBoard = addDown(tempBoard)
  tempBoard = fallDown(tempBoard)
  tempBoard = fallDown(tempBoard)
  
  #only add a cell if board isn't full, and if a change has been made this turn.
  if isBoardFull(tempBoard) == False and tempBoard != boardSnapshot:
    #if board isn't full, pick a random cell and populate it
    #in worse case, this isn't efficient since it randomly picks with 
    # replacement until it finds blank, but it doesn't seem to slow performance
    # too much... To Do: fix this.
    while True:
      i = random.randint(0,3)
      j = random.randint(0,3)
      if tempBoard[j][i] == "_":
        #weight ones more than twos
        tempRand = random.random()
        if tempRand < 0.8:
          tempBoard[j][i] = "2"
        else:
          tempBoard[j][i] = "4"
        break
  return(tempBoard)

def rotateClock(list4by4):
  #Board rotates clockwise 90 degrees
  
  results = [["_", "_", "_", "_"], ["_", "_", "_", "_"], ["_", "_", "_", "_"], 
  ["_", "_", "_", "_"]]
  for i in range(0,4):
    for j in range(0,4):
      results[j][i] = list4by4[3-i][j]
  return(results)



def main():
  sh.show_message("2048",text_colour=[255,255,255],scroll_speed=0.1)
  #initialize blank board
  curBoard = [["_", "_", "_", "_"], ["_", "_", "_", "_"], ["_", "_", "_", "_"], 
  ["_", "_", "_", "_"]]
  
  #initialize first move
  i = random.randint(0,3)
  j = random.randint(0,3)
  
  #weight twos more than fours
  tempRand = random.random()
  if tempRand < 0.8:
    curBoard[j][i] = "2"
  else:
    curBoard[j][i] = "4"
  
  printBoard(curBoard)
  print("\n\n...\n\n")
  renderBoard(curBoard)
  
  #import msvcrt as m

  
  #Begin game: each loop is a move by the player.
  while True:

    # printBoard(curBoard)
    if isWinner(curBoard):
        sh.show_message("YOU WIN!",text_colour=[255,0,0],scroll_speed=0.1)
        print(":) :)  !!!YOU ARE A WINNER!!!  (: (:")
        break
    if isFailure(curBoard):
        sh.show_message("YOU LOSE!",text_colour=[255,0,0],scroll_speed=0.1)
        print("YOU LOSE!")
        break
    
    
    #Wait for user input
    r,w,x=select([js.fd],[],[],0.01)

    for fd in r:
        for event in js.read():
            if event.type == ecodes.EV_KEY and event.value==1:
                if event.code == ecodes.KEY_UP:

                  print("UP")
                  ##rotate 180 degress, move down, rotate 180 degress
                  curBoard = rotateClock(curBoard)
                  curBoard = rotateClock(curBoard)
                  curBoard = moveDown(curBoard)
                  curBoard = rotateClock(curBoard)
                  curBoard = rotateClock(curBoard)
                  renderBoard(curBoard)
                  printBoard(curBoard)
      
                elif event.code == ecodes.KEY_LEFT:

                  print("LEFT")
                  ##rotate 270 degress, move down, rotate 90 degress
                  curBoard = rotateClock(curBoard)
                  curBoard = rotateClock(curBoard)
                  curBoard = rotateClock(curBoard)
                  curBoard = moveDown(curBoard)
                  curBoard = rotateClock(curBoard)
                  renderBoard(curBoard)
                  printBoard(curBoard)
      
                elif event.code == ecodes.KEY_DOWN:





                  print("DOWN")
                  curBoard = moveDown(curBoard)
                  printBoard(curBoard)
                  renderBoard(curBoard)
                elif event.code == ecodes.KEY_RIGHT:

                    print("RIGHT")
                    ##rotate 90 degress, move down, rotate 270 degress
                    curBoard = rotateClock(curBoard)
                    curBoard = moveDown(curBoard)
                    curBoard = rotateClock(curBoard)
                    curBoard = rotateClock(curBoard)
                    curBoard = rotateClock(curBoard)
                    renderBoard(curBoard)
                    printBoard(curBoard)
                else:

                    print("enter")
 

#Kick off the 'main' function
if __name__ == '__main__':
  main()
