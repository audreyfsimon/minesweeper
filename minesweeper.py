from cmu_112_graphics import *
import random, string, math, time, copy

from cmu_112_graphics import *
import random
from dataclasses import make_dataclass
import pygame


#################################################
# Helper functions
#################################################

# Citation - Taken from 15-112 Website: 
# https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#dimensions

def make2dList(rows, cols, placement):
    return [ ([placement] * cols) for row in range(rows) ]

# https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#caching\
# PhotoImages

def getCachedImage(app,image):
    if ('cachedPhotoImage' not in image.__dict__):
        image.cachedPhotoImage = ImageTk.PhotoImage(image)
    return image.cachedPhotoImage

#################################################
# Main App
#################################################

def gameDimensions():
    rows = 20
    cols = 35
    cellSize = 40
    margin = 30
    return rows,cols,cellSize,margin

def playGame():
    rows,cols,cellSize,margin = gameDimensions()
    width = 2*margin+cellSize*cols
    height = 2*margin+cellSize*rows
    runApp(width=width, height=height)

#############################################
# Global Variables
#############################################

def appStarted(app):
    app.gameLevel = 'Easy'
    app.gameMode = "Play"
    app.timeRef = time.time()
    app.time = 0
    app.level = 0
    app.rows,app.cols,app.cellSize,app.margin = gameDimensions()
    app.terrain = createTerrain(app.rows,app.cols,app.level)
    app.copyTerrain = copy.deepcopy(app.terrain)
    app.guessingBoard = make2dList(app.rows,app.cols,'guess')
    app.clickMode = 'Normal'
    app.bombs =0
    app.foundBombs = 0
    app.foundBlanks = 0
    for row in range(len(app.copyTerrain)):
        for col in range(len(app.copyTerrain[0])):
            if app.copyTerrain[row][col]=='bomb':
                app.bombs += 1
    app.blanks = app.rows*app.cols-app.bombs
    print (app.bombs,app.blanks)

def makeBombs(terrain,rows,cols):
    for i in range(100):
        row = random.randint(0,rows-1)
        col = random.randint(0,cols-1)
        terrain[row][col]='bomb'
#############################################
# Key Pressed Functions
#############################################

def keyPressed(app,event):
    if event.key=='r':
        appStarted(app)
    if event.key=='b':
        if app.gameMode == 'Play':
            app.gameMode = 'Cheat'
        else:
            app.gameMode = 'Play'
    if event.key=='f':
        if app.clickMode == 'Normal':
            app.clickMode = 'Flag'
        else:
            app.clickMode = 'Normal'
    
    
def mousePressed(app,event):
    if app.clickMode == 'Normal':
        if clickedBox(event.x,event.y,app.width,app.height,app.margin):
            row,col = getCellBounds(app,event.x,event.y)
            app.copyTerrain[row][col]='G'
            if app.guessingBoard[row][col]!='Flagged':
                app.guessingBoard[row][col] = "Guessed"
                app.foundBlanks += 1
            if app.terrain[row][col]==0:
                selectNearby(row,col,app)
            elif app.terrain[row][col] == 'bomb':
                app.gameMode = "Over"
    elif app.clickMode == 'Flag':
        if clickedBox(event.x,event.y,app.width,app.height,app.margin):
            row,col = getCellBounds(app,event.x,event.y)
            if app.guessingBoard[row][col] == "Flagged":
                app.guessingBoard[row][col] = "guess"
                if app.copyTerrain[row][col]=='found':
                    app.copyTerrain[row][col]='bomb'
                    app.foundBombs-=1
            else:
                app.guessingBoard[row][col]='Flagged'
                if app.copyTerrain[row][col]=='bomb':
                    app.copyTerrain[row][col]='found'
                    app.foundBombs+=1
    if app.foundBombs == app.bombs and app.foundBlanks==app.blanks:
        app.gameMode = 'Winner'
    print (app.foundBombs,app.foundBlanks)
    

        


def clickedBox(x,y,width,height,margin):
    if margin<=x and x<=width-margin and margin<=y and height-margin>=y:
        return True

def selectNearby(row,col,app):
    moves = [(-1,0),(0,-1),(0,1),(1,0)]
    for (drow,dcol) in moves:
        testRow = row + drow
        testCol = col + dcol
        if moveIsLegal(testRow,testCol,app.terrain):
            if app.copyTerrain[testRow][testCol] == 0:
                app.copyTerrain[testRow][testCol] = 'G'
                if app.guessingBoard[row][col]!='Flagged':
                    app.guessingBoard[testRow][testCol] = "Guessed"
                    app.foundBlanks +=1
                selectNearby(testRow,testCol,app)
            elif type(app.copyTerrain[testRow][testCol]) == int:
                app.copyTerrain[testRow][testCol] = 'G'
                app.guessingBoard[testRow][testCol] = 'Guessed'
                app.foundBlanks += 1
    #print (app.terrain)
    

#############################################
# Timer Fired Functions
#############################################

def timerFired(app):  
    app.time = int((time.time()-app.timeRef))

'''def makeBombs(terrain,rows,cols):
    for i in range(200):
        row = random.randint(0,rows-1)
        col = random.randint(0,cols-1)
        terrain[row][col]='bomb'''

def makeNums(terrain,rows,cols):
    for row in range(len(terrain)):
        for col in range(len(terrain[0])):
            '''if (terrain[row][col])==1:
                return'''
            moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
            for (drow,dcol) in moves:
                testRow = row + drow
                testCol = col + dcol
                if moveIsLegal(testRow,testCol,terrain) and \
                    terrain[row][col]!='bomb':
                    if terrain[testRow][testCol] == 'bomb':
                        terrain[row][col] += 1

def moveIsLegal(row,col,terrain):
    if row >= len(terrain) or row<0 or col>=len(terrain[0]) or col<0:
        return False
    return True

def createTerrain(rows,cols,level):
    terrain = make2dList(rows,cols,0)
    makeBombs(terrain,rows,cols)
    makeNums(terrain,rows,cols)
    return terrain

def getCellBounds(app,row,col):
    x0 = app.margin+app.cellSize*col+app.mapX+app.distance*app.cellSize
    x1 = x0+app.cellSize
    y0 = app.cellSize*row+app.margin
    y1 = y0+app.cellSize
    return x0,x1,y0,y1

def getCellBounds(app,x,y):
    col = (x-app.margin)//app.cellSize
    row = (y-app.margin)//app.cellSize
    return row,col

def drawCell(app,canvas,row,col,num):
    #x = app.margin+app.cellSize*col+app.mapX+app.cellSize/2
    #IMG = getCachedImage(app,IMG)
    #canvas.create_image(x+app.distance*app.cellSize,
    #app.cellSize*row+app.margin+app.cellSize/2,image=IMG)
    if num == 'guess':
        color = 'light grey'
    elif num == 'Guessed':
        color = None
    elif num == 'Flagged':
        color = 'purple'
    elif num == 'bomb':
        color = 'red'
    elif type(num)==int and num>0:
        color = 'light blue'
    elif type(num)==int and num==0:
        color = 'light green'
    else:
        color = 'purple'
    canvas.create_rectangle(app.margin+col*app.cellSize,
    app.margin+row*app.cellSize,
    app.margin+(col+1)*app.cellSize,app.margin+(row+1)*app.cellSize,fill=color)
    if type(num)==int and num>0:
        canvas.create_text(app.margin+col*app.cellSize+app.cellSize//2,
        app.margin+row*app.cellSize+app.cellSize//2,text=num)

def drawBoard(app,canvas):
    for row in range(len(app.terrain)):
        for col in range(len(app.terrain[0])):
            drawCell(app,canvas,row,col,app.terrain[row][col])

def drawGuessingBoard(app,canvas):
    for row in range(len(app.guessingBoard)):
        for col in range(len(app.guessingBoard[0])):
            drawCell(app,canvas,row,col,app.guessingBoard[row][col])

def drawGameOver(app,canvas):
    canvas.create_rectangle(app.width//2-200,app.height//2-100,
    app.width//2+200,app.height//2+100,
    fill='Black')
    canvas.create_text(app.width//2,app.height//2-10,text='Game Over!',
    fill='White',
    font='Arial 50')
    canvas.create_text(app.width//2,app.height//2+40,text='Press R to restart.',
    fill='White',
    font='Arial 20')

def drawWinner(app,canvas):
    canvas.create_rectangle(app.width//2-200,app.height//2-100,
    app.width//2+200,app.height//2+100,
    fill='Pink')
    canvas.create_text(app.width//2,app.height//2,text='You Won!!!',
    fill='White',
    font='Arial 50')

def drawStart(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height,fill='Grey')
    canvas.create_text(app.width//2,app.height//5,
    text='Welcome to Minesweeper!')

def drawFlagMode(app,canvas):
    if app.clickMode == 'Flag':
        canvas.create_rectangle(app.width//2-100,10,app.width//2+100,30,
        fill='light green',width=0)
        canvas.create_text(app.width//2,20,text="FLAG MODE ON",font='Arial 18')
    else:
        canvas.create_rectangle(app.width//2-100,10,app.width//2+100,30,
        fill='red',width=0)
        canvas.create_text(app.width//2,20,text="FLAG MODE OFF",font='Arial 18')
#############################################
# Run Game
#############################################
def redrawAll(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height,fill='pink')
    drawBoard(app,canvas)
    if app.gameMode == 'Play':
       drawGuessingBoard(app,canvas)
    if app.gameMode == 'Over':
        drawGameOver(app,canvas)
    if app.gameMode == 'Winner':
        drawWinner(app,canvas)
    drawFlagMode(app,canvas)
    if app.gameMode == 'Start':
        drawStart(app,canvas)
    #canvas.create_triangle(0,0,20,20)
    #canvas.create_rectangle(100,100,300,300,)

if (__name__ == '__main__'):
    playGame()


