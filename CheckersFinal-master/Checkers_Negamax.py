from graphics import *
import sys
from tkinter import messagebox as tkMessageBox
#+-added to be able to select a random number from a range of numbers
from random import randrange

debug_list = [
    False,
    False,
    False,
    False,
    False,
    False
]

'''
The revisions in the code are labelled by the prefix '#+-'
'''
class Checkers:
    
    EVEN_ROWS = 0x0F0F0F0F
    ODD_ROWS = 0xF0F0F0F0
    NE_SLIDE_MASK = 0x0F7F7F7F
    NW_SLIDE_MASK = 0x0EFEFEFE
    SE_SLIDE_MASK = 0x7F7F7F70
    SW_SLIDE_MASK = 0xFEFEFEF0
    NE_CAP_MASK = 0x00777777
    NW_CAP_MASK = 0x00EEEEEE
    SE_CAP_MASK = 0x77777700
    SW_CAP_MASK = 0xEEEEEE00
    N_PROMOTION_MASK = 0xF0000000
    S_PROMOTION_MASK = 0x0000000F
    
    def __init__(s):
        s.state = 'CustomSetup'
        s.is1P = False
        #+-added string
        s.compIsColour = 'not playing'    #computer not playing by default
        s.placeColour = 'White'
        s.placeRank = 'Pawn'
        s.placeType = 'Place'                   #Place or Delete (piece)
        s.pTurn = 'White'                       #White or Black (turn)
        
        s.comp_depth = 14
        
        s.N_SLIDES = [s.slide_ne, s.slide_nw]
        s.S_SLIDES = [s.slide_se, s.slide_sw]
        
        s.N_CAPTURES = [s.cap_ne, s.cap_nw]
        s.S_CAPTURES = [s.cap_se, s.cap_sw]
        
        s.SLIDES = s.N_SLIDES + s.S_SLIDES
        s.CAPTURES = s.N_CAPTURES + s.S_CAPTURES
        
        s.ANTI_SLIDES = {
            slide:s.anti_slide(slide) for slide in s.SLIDES
        }
        
        s.ANTI_CAPTURES = {
            capture:s.anti_cap(capture) for capture in s.CAPTURES
        }
        
        
        s.selectedTile = ''
        s.selectedTileAt = []
        s.hasMoved = False
        s.pieceCaptured = False

        s.BoardDimension = 8
        s.numPiecesAllowed = 12

        s.win = GraphWin('Checkers',600,600)    #draws screen
        s.win.setBackground('White')
        s.win.setCoords(-1,-3,11,9)              #creates a coordinate system for the window
        s.ClearBoard()
        
        s.tiles = [[Tile(s.win,i,j,False) for i in range(s.BoardDimension)] for j in range(s.BoardDimension)]  #creates the 2D list and initializes all 8x8 entries to an empty tile

        #+-added two lists
        s.moves = []
        s.badMoves = []

        gridLetters = ['A','B','C','D','E','F','G','H',]
        for i in range(s.BoardDimension):
            Text(Point(-0.5,i+0.5),i+1).draw(s.win)                 #left and right numbers for grid
            Text(Point(8.5,i+0.5),i+1).draw(s.win)
            Text(Point(i+0.5,-0.5),gridLetters[i]).draw(s.win)      #bottom and top letters
            Text(Point(i+0.5,8.5),gridLetters[i]).draw(s.win) 
        
        s.SetButtons()
        
        s.SetupBoard()
	####
    #handles the setup of the board (i.e. piece placement)
	####
    def SetupBoard(s):
        while s.state == 'CustomSetup':
            s.Click()
        if s.state == 'Play':
            s.Play()
	####
    #handles the general play of the game
	####
    def Play(s):
        while s.state == 'Play':
            #+-added if statement
            print('Playing')
            if s.is1P and s.compIsColour == s.pTurn:
                s.CompTurn()
            else:
                s.Click()
        if s.state == 'CustomSetup':
            s.SetupBoard()
	####
    #+-added to be able to control the computer's turn
	####
    def CompTurn(s):

        # Use the function to get the bitboards
        s.translate_to_bitboard()
    
        # Represent color as a bit, White = 1, Black = 0
        color = 1 if s.pTurn == 'White' else 0
        
        if color:
            pawns = s.bitboard['white_pawns']
            kings = s.bitboard['white_kings']
            opp_pawns = s.bitboard['black_pawns']
            opp_kings = s.bitboard['black_kings']
        else:
            pawns = s.bitboard['black_pawns']
            kings = s.bitboard['black_kings']
            opp_pawns = s.bitboard['white_pawns']
            opp_kings = s.bitboard['white_kings']
        
        max_eval, best_move = s.negamax(
            depth = s.comp_depth, 
            alpha = float('-inf'), 
            beta = float('inf'), 
            color = color, 
            pawns = pawns,
            kings = kings,
            opp_pawns = opp_pawns,
            opp_kings = opp_kings
        )
        
        print(f'Computer Evaluation: {max_eval}')
        
        s.bitboard['black_pawns'], s.bitboard['black_kings'], s.bitboard['white_pawns'], s.bitboard['white_kings'] = best_move
        s.translate_to_board()
        s.pTurn = s.opposite(s.pTurn)
        
        s.SetButtons()
        #+-added if statement to check defeat
        if s.movesAvailable() == [] and s.numColour(s.pTurn):
            tkMessageBox.showinfo("Defeat", str(s.pTurn) + ' has no available moves! ' + str(s.opposite(s.pTurn)) + ' wins!')
            s.state = 'CustomSetup'
            s.SetButtons()        
        
    def slide_ne(s, pieces):
        return ((pieces & s.NE_SLIDE_MASK & s.EVEN_ROWS) << 4) | ((pieces & s.NE_SLIDE_MASK & s.ODD_ROWS) << 5)
    
    def slide_nw(s, pieces):
        return ((pieces & s.NW_SLIDE_MASK & s.EVEN_ROWS) << 3) | ((pieces & s.NW_SLIDE_MASK & s.ODD_ROWS) << 4)
    
    def slide_se(s, pieces):
        return ((pieces & s.SE_SLIDE_MASK & s.EVEN_ROWS) >> 4) | ((pieces & s.SE_SLIDE_MASK & s.ODD_ROWS) >> 3)
    
    def slide_sw(s, pieces):
        return ((pieces & s.SW_SLIDE_MASK & s.EVEN_ROWS) >> 5) | ((pieces & s.SW_SLIDE_MASK & s.ODD_ROWS) >> 4)
    
    def cap_ne(s, pieces):
        return (pieces & s.NE_CAP_MASK) << 9
    
    def cap_nw(s, pieces):
        return (pieces & s.NW_CAP_MASK) << 7
    
    def cap_se(s, pieces):
        return (pieces & s.SE_CAP_MASK) >> 7
    
    def cap_sw(s, pieces):
        return (pieces & s.SW_CAP_MASK) >> 9

    def captures(s, pieces, pawns, kings, opp_pawns, opp_kings, captures, promotion_mask):
        opp_pieces = opp_pawns | opp_kings
        empty_sqs = ~(pawns | kings | opp_pieces)
        
        additional = False
        moves = set()
        for capture in captures:
            slide = getattr(s, capture.__name__.replace('cap', 'slide'))
            
            land_sqs = slide(opp_pieces) # Squares where a capturing piece would land
            cap_sqs = capture(pieces) & land_sqs & empty_sqs # Squares where pieces can capture
            
            while cap_sqs:
                additional = True
                
                lsb = cap_sqs & -cap_sqs # Least significant bit, represents a capture square
                start = s.ANTI_CAPTURES[capture](lsb) # Starting square of the capturing piece
                mid = s.ANTI_SLIDES[slide](lsb) # Middle square of the capture
                
                promoted_pawns = lsb & promotion_mask
                static_move = start | lsb
                
                # Check if the capturing piece is a pawn
                if start & pawns:
                    # Check if the pawn landed on a promote square
                    if promoted_pawns:
                        new_pawns = pawns ^ start # Remove the capturing pawn
                        new_kings = kings | lsb # Replace with a king
                    else:
                        new_pawns = pawns ^ static_move # Move the capturing pawn
                        new_kings = kings # No change in kings
                else:
                    new_pawns = pawns # No change in pawns
                    new_kings = kings ^ static_move # Move the capturing king
                
                new_opp_pawns = opp_pawns & ~(mid & opp_pawns) # Get the new opponent pawns
                new_opp_kings = opp_kings & ~(mid & opp_kings) # Get the new opponent kings
                
                new_captures = s.CAPTURES if promoted_pawns else captures
                
                moves.update(
                    s.captures(
                        pieces = lsb,
                        pawns = new_pawns,
                        kings = new_kings,
                        opp_pawns = new_opp_pawns,
                        opp_kings = new_opp_kings,
                        captures = new_captures,
                        promotion_mask = promotion_mask,
                    )
                )
                
                cap_sqs &= cap_sqs - 1 
                
        if additional:
            return moves
        else:
            return [(pawns, kings, opp_pawns, opp_kings)]

    def valid_moves(s, pawns, kings, opp_pawns, opp_kings, color):
        moves = set()
        
        if color:
            slides = s.N_SLIDES
            pawn_captures = s.N_CAPTURES
            promotion_mask = s.N_PROMOTION_MASK
        else:
            slides = s.S_SLIDES
            pawn_captures = s.S_CAPTURES
            promotion_mask = s.S_PROMOTION_MASK
        
        empty_sqs = ~(pawns | kings | opp_pawns | opp_kings)
        

        moves.update(
            s.captures(
                pieces = pawns,
                pawns = pawns,
                kings = kings,
                opp_pawns = opp_pawns,
                opp_kings = opp_kings, 
                captures = pawn_captures, 
                promotion_mask = promotion_mask
            )
        )
        
        moves.update(
            s.captures(
                pieces = kings,
                pawns = pawns,
                kings = kings,
                opp_pawns = opp_pawns,
                opp_kings = opp_kings, 
                captures = s.CAPTURES, 
                promotion_mask = promotion_mask
            )
        )
        
        moves = [move for move in moves if move != (pawns, kings, opp_pawns, opp_kings)]
        
        if not moves:
            if pawns:
                for slide in slides:

                    slide_sqs = slide(pawns) & empty_sqs
                    
                    while slide_sqs:
                        lsb = slide_sqs & -slide_sqs
                        moves.append((
                            (s.ANTI_SLIDES[slide](lsb) | (lsb & ~promotion_mask)) ^ pawns,
                            (lsb & promotion_mask) | kings,
                            opp_pawns,
                            opp_kings
                        ))
                        slide_sqs &= slide_sqs - 1 
                        

                
            if kings:
                for slide in s.SLIDES:
                    slide_sqs = slide(kings) & empty_sqs
                    while slide_sqs:
                        lsb = slide_sqs & -slide_sqs
                        moves.append((
                            pawns,
                            (s.ANTI_SLIDES[slide](lsb) | lsb) ^ kings,
                            opp_pawns,
                            opp_kings
                        ))
                        slide_sqs &= slide_sqs - 1
            


        return moves

    def evaluate_bitboards(s, pawns:int, kings:int, opp_pawns:int, opp_kings:int):
        return pawns.bit_count() + 3 * kings.bit_count() - (opp_pawns.bit_count() + 3 * opp_kings.bit_count())
    
    def negamax(s, depth:int, alpha:float, beta:float, color:int, pawns:int, kings:int, opp_pawns:int, opp_kings:int):
        valid_moves = s.valid_moves(pawns, kings, opp_pawns, opp_kings, color) # Obtain all valid moves for the evaluating color's pieces
        
        # If depth is 0, evaluate the position
        if not depth:

            return s.evaluate_bitboards(pawns, kings, opp_pawns, opp_kings), None
        
        best_move = None # Initialize the best move to None
        max_eval = float('-inf') # Initialize the evaluation lower bound to negative infinity

        # Check that there are valid moves
        if valid_moves:
            # Best move defaults to the first valid move to handle cases where all moves evaluate to -inf
            best_move = valid_moves[0]
            # Loop through all valid moves
            for pawns, kings, opp_pawns, opp_kings in valid_moves:
                       
                # Recursively call the negamax function at deiterated depth, swapping the alpha, beta, and color
                cur_eval, _ = s.negamax(
                    depth = depth - 1, 
                    alpha = -beta, 
                    beta = -alpha, 
                    color = ~color, 
                    pawns = opp_pawns,
                    kings = opp_kings,
                    opp_pawns = pawns,
                    opp_kings = kings
                )
                
                cur_eval *= -1
                
                # Check if the move evaluation is the current maximum evaluation
                if cur_eval > max_eval:
                    max_eval = cur_eval # Reassign the max evaluation
                    best_move = (pawns, kings, opp_pawns, opp_kings) # Reassign the best move
                
                alpha = max(alpha, cur_eval) # Adjust the alpha value
                
                # Alpha-beta pruning
                if alpha >= beta:
                    break

        return max_eval, best_move    
    
    def translate_to_board(s):
        # Clear the current board
        s.tiles = [[Tile(s.win, x, y, isPiece=False) for x in range(s.BoardDimension)] for y in range(s.BoardDimension)]

        # Iterate over the bitboards to update the board
        for bit_position in range(32):
            y, x = divmod(bit_position, 4)
            x*= 2
            x += bit_position // 4 % 2 
            if s.bitboard['white_pawns'] & (1 << bit_position):
                s.tiles[x][y] = Tile(s.win, x, y, isPiece=True, pieceColour='White', pieceRank='Pawn')
            elif s.bitboard['white_kings'] & (1 << bit_position):
                s.tiles[x][y] = Tile(s.win, x, y, isPiece=True, pieceColour='White', pieceRank='King')
            elif s.bitboard['black_pawns'] & (1 << bit_position):
                s.tiles[x][y] = Tile(s.win, x, y, isPiece=True, pieceColour='Black', pieceRank='Pawn')
            elif s.bitboard['black_kings'] & (1 << bit_position):
                s.tiles[x][y] = Tile(s.win, x, y, isPiece=True, pieceColour='Black', pieceRank='King')

    def translate_to_bitboard(s):
        s.bitboard = {
            'white_pawns': 0,
            'white_kings': 0,
            'black_pawns': 0,
            'black_kings': 0,
            'white_pieces': 0,
            'black_pieces': 0,
            'all_pieces': 0
        }


        # Iterate over the board to update bitboards
        for y in range(s.BoardDimension):
            for x in range(s.BoardDimension):
                if (x + y) % 2 == 0:  # Check only dark squares
                    tile = s.tiles[x][y]
                    if tile.isPiece:
                        # Calculate the bit position for the 32-bit representation (index 0 to 31)
                        bit_position = (y * 4) + (x // 2)
                        
                        # Update the corresponding bitboard based on piece type and color
                        if tile.pieceColour == 'White':
                            if tile.pieceRank == 'Pawn':
                                s.bitboard['white_pawns'] |= (1 << bit_position)
                            elif tile.pieceRank == 'King':
                                s.bitboard['white_kings'] |= (1 << bit_position)
                        elif tile.pieceColour == 'Black':
                            if tile.pieceRank == 'Pawn':
                                s.bitboard['black_pawns'] |= (1 << bit_position)
                            elif tile.pieceRank == 'King':
                                s.bitboard['black_kings'] |= (1 << bit_position)
                                
        s.bitboard['white_pieces'] = s.bitboard['white_pawns'] | s.bitboard['white_kings']
        s.bitboard['black_pieces'] = s.bitboard['black_pawns'] | s.bitboard['black_kings']
        s.bitboard['all_pieces'] = s.bitboard['white_pieces'] | s.bitboard['black_pieces']


    def debug_log(s, string):
        s.log_file.write(string + "\n")
        s.log_file.flush()  # Ensure immediate write to the file 

	#Resets the board to be empty
    def ClearBoard(s):
        s.tiles=[[Tile(s.win,i,j,False) for i in range(s.BoardDimension)] for j in range(s.BoardDimension)]  #creates the 2D list and initializes all 8x8 entries to an empty tile
        for i in range(s.BoardDimension):
            for j in range(s.BoardDimension):
                s.ColourButton(s.TileColour(i,j),i,j)
        s.state = 'CustomSetup'
        s.pTurn = 'White'
        s.SetButtons()

    def ColourButton(s,colour,X,Y,width=1,height=1):        #function to create a rectangle with a given colour, size, and location
        rect = Rectangle(Point(X,Y),Point(X+width,Y+height))
        rect.setFill(colour)
        rect.draw(s.win)
            
    def TileColour(s,x,y):
        if (x%2 == 0 and y%2 == 0) or (x%2 == 1 and y%2 == 1):
            return 'Red'   #sets every other square to red 
        else:
            return 'White' #every non red square to white

    ##########
    #Draws Buttons
    ##########    
    def SetButtons(s):
        s.ColourButton('White',-1,-3,12,2)
        s.ColourButton('White',9,-1,2,10)

        if s.state == 'CustomSetup':
            s.DrawStandard()
            s.DrawStart()
            s.DrawClear()
            s.Draw1P()
            s.Draw2P()
            s.DrawLoad()
            s.DrawSave()
            s.DrawTurn()
            s.DrawX()
            
            s.DrawW()
            s.DrawB()
            s.DrawK()
            s.DrawDel()

            s.DrawScore() #not actually a button
        elif s.state == 'Play':
            #+-updated method name
            s.DrawResign()
            s.DrawSave()
            s.DrawTurn()
            s.DrawX()

            s.DrawScore() #not actually a button


    def DrawStandard(s):
        s.ColourButton('White',-1,-2,2,1)    #Standard Setup button
        Text(Point(0,-1.3),'Standard').draw(s.win)
        Text(Point(0,-1.7),'Setup').draw(s.win)
    def DrawCustom(s):
        s.ColourButton('White',-1,-3,2,1)    #Custom Setup button
        Text(Point(0,-2.3),'Custom').draw(s.win)  
        Text(Point(0,-2.7),'Setup').draw(s.win)
    def DrawStart(s):
        s.ColourButton('Yellow',1,-2)    #Start! button
        Text(Point(1.5,-1.5),'Start!').draw(s.win)
    def DrawClear(s):
        s.ColourButton('White',-1,-3,2,1)    #Clear Board button
        Text(Point(0,-2.3),'Clear').draw(s.win)
        Text(Point(0,-2.7),'Board').draw(s.win)
    def Draw1P(s):
        col = 'Red'
        if s.is1P:
            s.DrawCompColour()
        else:
            s.ColourButton(col,3,-2,2,1)    #1Player   -- (1AI)
            Text(Point(4,-1.3),'1Player').draw(s.win)
            Text(Point(4,-1.7),'Game').draw(s.win)
    def DrawCompColour(s):
        s.ColourButton(s.compIsColour,3,-2,2,1)
        txt1 = Text(Point(4,-1.3),'Comp Is')
        txt2 = Text(Point(4,-1.7),s.compIsColour)
        txt1.draw(s.win)
        txt2.draw(s.win)
        txt1.setFill(s.opposite(s.compIsColour))
        txt2.setFill(s.opposite(s.compIsColour))
    def Draw2P(s):#2Player
        col = 'Green'
        if s.is1P:
            col = 'Red'
        s.ColourButton(col,3,-3,2,1)    
        Text(Point(4,-2.3),'2Player').draw(s.win)  
        Text(Point(4,-2.7),'Game').draw(s.win)
    def DrawLoad(s):#Load
        s.ColourButton('White',6,-3,2,1)    
        Text(Point(7,-2.5),'Load').draw(s.win)
    def DrawSave(s):    #Save
        s.ColourButton('White',8,-3,2,1)
        Text(Point(9,-2.5),'Save').draw(s.win)
    def DrawX(s):#X
        s.ColourButton('Red',10,-3)    
        Exit_txt = Text(Point(10.5,-2.5),'X')
        Exit_txt.draw(s.win)
        Exit_txt.setFill('White')
    def DrawW(s):#W
        col = 'Green'
        if s.placeColour != 'White':
            col = 'Red'
        s.ColourButton(col,6,-2)    
        Text(Point(6.5,-1.5),'W').draw(s.win)
    def DrawB(s):#B
        col = 'Red'
        if s.placeColour != 'White':
            col = 'Green'
        s.ColourButton(col,7,-2)    
        Text(Point(7.5,-1.5),'B').draw(s.win)
    def DrawK(s): #K
        col = 'Red'
        if s.placeRank == 'King':
            col = 'Green'
        s.ColourButton(col,8,-2) 
        Text(Point(8.5,-1.5),'K').draw(s.win)
    def DrawDel(s):#Del
        col1 = 'Black'#square colour
        col2 = 'White'#text colour
        if s.placeType == 'Delete':
            col1 = 'Green'
            col2 = 'Black'        
        s.ColourButton(col1,9,-2)    
        deleteTxt = Text(Point(9.5,-1.5),'Del')
        deleteTxt.draw(s.win)
        deleteTxt.setFill(col2)
    def DrawResign(s):
        s.ColourButton('White',6,-3,2,1)    #Load
        Text(Point(7,-2.5),'Resign').draw(s.win)
    def DrawTurn(s):
        col1 = 'White'
        col2 = 'Black'
        if s.pTurn == 'Black':
            col1 = 'Black'
            col2 = 'White'
        s.ColourButton(col1,9,8,2,1)    #Standard Setup button
        txt1 = Text(Point(10,8.7),col1)
        txt2 = Text(Point(10,8.3),'Turn')
        txt1.draw(s.win)
        txt2.draw(s.win)
        txt1.setFill(col2)
        txt2.setFill(col2)
    def DrawScore(s): # draw score
        Text(Point(10,7.5),'# White').draw(s.win)
        Text(Point(10,7.1),'Pieces:').draw(s.win)
        Text(Point(10,6.7),s.numColour('White')).draw(s.win)
        Text(Point(10,5.9),'# Black').draw(s.win)
        Text(Point(10,5.5),'Pieces').draw(s.win)
        Text(Point(10,5.1),s.numColour('Black')).draw(s.win)
                 
    def Click(s):
        click = s.win.getMouse()        #Perform mouse click
        X, Y = s.ClickedSquare(click)   #Gets click coords
        s.Action(X,Y)
        
    def Action(s,X,Y):      #performs action for the location X,Y --essentially means user clicked there or computer is 'clicked' there
        if s.state == 'CustomSetup':
            s.clickInCustom(X,Y)
        elif s.state == 'Play':
            s.clickInPlay(X,Y)
            
    def clickInCustom(s,X,Y):
        #+-added X button if statement
        if (10<=X<11 and -3<=Y<-2): #X clicked
            ExitGame(s.win)
        elif (-1<=X<1 and -2<=Y<-1): #Standard clicked
            s.StandardSetup()  
        elif (1<=X<2 and -2<=Y<-1): #Start! clicked
            num_wh = s.numColour('White')
            num_bl = s.numColour('Black')
            if ((num_wh == 0) and (num_bl == 0)): #This means there are no pieces on the board; this is a pointless setup.
                tkMessageBox.showinfo("Error", "No pieces have been placed!")
            else:
                s.state = 'Play'
                s.SetButtons()
        elif (-1<=X<1 and -3<=Y<-2): #Clear Board clicked
            s.ClearBoard()
        #+-added 1Player and Comp Is if statements
        elif (3<=X<5 and -2<=Y<-1 and not s.is1P): #1Player clicked
            s.is1P = True
            s.compIsColour = 'White'
            s.SetButtons()
        elif (3<=X<5 and -2<=Y<-1 and s.is1P): #'Comp Is' button clicked --requires the user to have already designated it to be a 1 player game, else the option is not available
            s.compIsColour = s.opposite(s.compIsColour)
            s.SetButtons()
        elif (3<=X<5 and -3<=Y<-2): #2Player clicked
            s.is1P = False
            s.SetButtons()
        elif (8<=X<10 and -3<=Y<-2): #Save clicked
            s.SaveSetupToFile()
        elif (6<=X<8 and -3<=Y<-2): #Load clicked
            s.LoadSetupFromFile()
        elif (9<=X<11 and 8<=Y<9): #pTurn button clicked during CustomSetup
            s.pTurn = s.opposite(s.pTurn)
            s.SetButtons()
        elif (6<=X<7 and -2<=Y<-1): #W clicked
            s.placeColour = 'White'
            s.placeType = 'Place'
            s.SetButtons()
        elif (7<=X<8 and -2<=Y<-1): #B clicked
            s.placeColour = 'Black'
            s.placeType = 'Place'
            s.SetButtons()
        elif (8<=X<9 and -2<=Y<-1): #K clicked
            s.placeRank = s.opposite(s.placeRank)
            s.placeType = 'Place'
            s.SetButtons()
        elif (9<=X<10 and -2<=Y<-1): #Del clicked
            s.placeType = s.opposite(s.placeType)
            s.SetButtons()
        elif (0<=X<8 and 0<=Y<8): #Tile clicked in CustomSetup
            if s.tiles[X][Y].TileColour(X,Y) == 'White': #Clicked tile is White
                tkMessageBox.showinfo("Error", "Illegal Placement")
            elif s.numColour(s.placeColour) >= s.numPiecesAllowed and s.placeType == 'Place': #clicked tile would result in too many of colour being placed
                tkMessageBox.showinfo("Error", "Illegal Placement")
            elif (Y == 7 and s.placeColour == 'White' and not(s.placeRank == 'King')) or (Y == 0 and s.placeColour == 'Black' and not(s.placeRank == 'King')): #placing a non-king on a king square
                tkMessageBox.showinfo("Error", "Illegal Placement")
            else: #Valid tile update action (i.e. piece placement or deletion)
                s.tiles[X][Y] = Tile(s.win,X,Y,s.placeType == 'Place',s.placeColour,s.placeRank)    #updates that square in array
                s.SetButtons()

    #+-added to calculate all the available valid moves
    def movesAvailable(s):
        moves=[]
        for j in range(8):
            for i in range(8):
                X1,Y1 = [i-1,i+1],[j-1,j+1]
                for a in range(2):
                    for b in range(2):
                        if 0<=X1[a]<8 and 0<=Y1[b]<8:
                            if s.moveIsValid(i,j,X1[a],Y1[b]):
                                moves.append([i,j,X1[a],Y1[b]])
        return moves

	#Handles mouse clicks
    def clickInPlay(s,X,Y):
        #+-added X and Save clicked if statements
        if (10<=X<11 and -3<=Y<-2): #X clicked
            ExitGame(s.win)
        elif (8<=X<10 and -3<=Y<-2): #Save clicked
            s.SaveSetupToFile()
        elif (6<=X<8 and -3<=Y<-2): #Resign clicked
        #+-added message box indicating which player had quit/resigned
            tkMessageBox.showinfo("Resignation", str(s.pTurn) + ' has resigned! ' + str(s.opposite(s.pTurn)) + ' wins!')
            s.state = 'CustomSetup'
            s.SetButtons()
        elif (0<=X<8 and 0<=Y<8): #Tile Clicked in Play
            if s.selectedTileAt != []: #move if able
                if s.selectedTileAt[0] == X and s.selectedTileAt[1] == Y and not s.pieceCaptured: #Re-Selecting the already selected piece de-selects it
                    s.selectedTileAt = []
                    s.tiles[X][Y] = Tile(s.win,X,Y,s.tiles[X][Y].isPiece,s.tiles[X][Y].pieceColour,s.tiles[X][Y].pieceRank)
                elif s.pTurn == s.tiles[X][Y].pieceColour and not s.pieceCaptured and (s.PieceCanCapture(X,Y) or not s.PlayerCanCapture()): 
                    s.tiles[s.selectedTileAt[0]][s.selectedTileAt[1]] = Tile(s.win,s.selectedTileAt[0],s.selectedTileAt[1],s.tiles[s.selectedTileAt[0]][s.selectedTileAt[1]].isPiece,s.tiles[s.selectedTileAt[0]][s.selectedTileAt[1]].pieceColour,s.tiles[s.selectedTileAt[0]][s.selectedTileAt[1]].pieceRank)
                    s.selectedTileAt = [X,Y]
                    s.tiles[X][Y] = Tile(s.win,X,Y,s.tiles[X][Y].isPiece,s.tiles[X][Y].pieceColour,s.tiles[X][Y].pieceRank,isSelected=True)
                elif s.moveIsValid(s.selectedTileAt[0],s.selectedTileAt[1],X,Y):
#####################+-added extra code here
                    if s.tiles[X][Y].isPiece:
                        X=X+(X-s.selectedTileAt[0])
                        Y=Y+(Y-s.selectedTileAt[1])
############################################################                        
                    s.move(s.selectedTileAt[0],s.selectedTileAt[1],X,Y)
                    if not (s.pieceCaptured and s.PieceCanCapture(X,Y)):
                        s.pieceCaptured = False
                        s.selectedTileAt = []
                        s.pTurn = s.opposite(s.pTurn)
                        s.SetButtons()
                        #+-added if statement to check defeat
                        if s.movesAvailable() == [] and s.numColour(s.pTurn):
                            tkMessageBox.showinfo("Defeat", str(s.pTurn) + ' has no available moves! ' + str(s.opposite(s.pTurn)) + ' wins!')
                            s.state = 'CustomSetup'
                            s.SetButtons()

                else:
                    tkMessageBox.showinfo("Error", "Cannot perform that action.")
            else: #Select a Piece to move
                if s.pTurn != s.tiles[X][Y].pieceColour:
                    tkMessageBox.showinfo("Error", "Select a piece of current player's colour")
                elif (not s.PieceCanCapture(X,Y)) and s.PlayerCanCapture():
                    tkMessageBox.showinfo("Error", "Invalid selection, current player must take a piece")
                else:
                    s.selectedTileAt = [X,Y]
                    s.tiles[X][Y] = Tile(s.win,X,Y,s.tiles[X][Y].isPiece,s.tiles[X][Y].pieceColour,s.tiles[X][Y].pieceRank,isSelected=True)

    #+-added to determine whether the tile attempting to be selected is valid
    def validTileSelect(s,X,Y):
        if (0<=X<8 and 0<=Y<8): #Tile Clicked in Play
            if s.selectedTileAt != []: #move if able
                if s.selectedTileAt[0] == X and s.selectedTileAt[1] == Y and not s.pieceCaptured: #Re-Selecting the already selected piece de-selects it
                    return False
                elif s.pTurn == s.tiles[X][Y].pieceColour and not s.pieceCaptured and (s.PieceCanCapture(X,Y) or not s.PlayerCanCapture()): 
                    return True
                elif s.moveIsValid(s.selectedTileAt[0],s.selectedTileAt[1],X,Y):
                    return False
                else:
                    return False
            else: #Select a Piece to move
                if s.pTurn != s.tiles[X][Y].pieceColour:
                    return False
                elif (not s.PieceCanCapture(X,Y)) and s.PlayerCanCapture():
                    return False
                else:
                    return True
        else:
            return False



    def moveIsValid(s,x,y,X,Y): #parameters -> self,starting x,starting y,final X,final Y
        #+-added if statement to ensure it the selected piece's turn
        if s.tiles[x][y].pieceColour == s.pTurn:
            if s.tiles[X][Y].pieceColour == s.opposite(s.pTurn): #valid if can jump target piece
                return s.PieceCanCapturePiece(x,y,X,Y)
            elif s.PieceCanJumpTo(x,y,X,Y): #valid if can jump to target location
                return True
            elif s.CanDoWalk(x,y,X,Y) and not s.PlayerCanCapture(): #valid if piece can travel to X,Y normally and PlayerCanCapture==False
                return True
            else:
                return False

########
# This Function Enables a Piece to move. Trace Back --> Requirement 1.3
########
    def move(s,x,y,X,Y): #parameters -> self,starting x,starting y,final X,final Y      assumes valid move as input           
        s.tiles[X][Y] = Tile(s.win,X,Y,True,s.tiles[x][y].pieceColour,s.tiles[x][y].pieceRank)

        if (Y==7 and s.tiles[X][Y].isWhite) or \
           (Y==0 and s.tiles[X][Y].isBlack):
            s.tiles[X][Y].pieceRank = 'King'

        s.tiles[X][Y] = Tile(s.win,X,Y,True,s.tiles[X][Y].pieceColour,s.tiles[X][Y].pieceRank)
        s.tiles[x][y] = Tile(s.win,x,y,isPiece=False)
        if X-x == 2 or X-x == -2:
            if s.numColour(s.tiles[int(x+(X-x)/2)][int(y+(Y-y)/2)].pieceColour) == 1:
                tkMessageBox.showinfo("Winner", str(s.tiles[X][Y].pieceColour) + ' Wins!')
                #+-updated to allow another game to be played after a winner is declared
                s.state = 'CustomSetup'
                s.SetButtons()
            s.tiles[int(x+(X-x)/2)][int(y+(Y-y)/2)] = Tile(s.win,x+(X-x)/2,y+(Y-y)/2,isPiece=False)

            s.tiles[X][Y] = Tile(s.win,X,Y,True,s.tiles[X][Y].pieceColour,s.tiles[X][Y].pieceRank)
            if s.PieceCanCapture(X,Y):
                s.tiles[X][Y] = Tile(s.win,X,Y,True,s.tiles[X][Y].pieceColour,s.tiles[X][Y].pieceRank,isSelected=True)

            s.selectedTileAt = [X,Y]
            s.pieceCaptured = True
        else:
            s.selectedTileAt = []
            
            s.tiles[X][Y] = Tile(s.win,X,Y,True,s.tiles[X][Y].pieceColour,s.tiles[X][Y].pieceRank)
            s.pieceCaptured = False
                 
#the below few functions need conditions added to handle out of bounds errors (for being off grid, i.e. 0<=X<8 or 0<=Y<8 doesn't hold)      <--- I think this is handled in PieceCanCapturePiece      
    def PlayerCanCapture(s):
        for i in range(s.BoardDimension):
            for j in range(s.BoardDimension):
                if s.pTurn == s.tiles[i][j].pieceColour: #Current piece belongs to current player
                    if s.PieceCanCapture(i,j):
                        return True
        return False

    def PieceCanCapture(s,x,y):
        X1,X2,Y1,Y2 = [x-1,x+1],[x-2,x+2],[y-1,y+1],[y-2,y+2]

        for i in range(2):
            for j in range(2):
                if s.PieceCanCapturePiece(x,y,X1[i],Y1[j]):
                    return True
        return False

#########
# This Function enables a tile to capture and remove an opponent piece. Trace Back --> Requirement 1.5
#########
    def PieceCanCapturePiece(s,x,y,X,Y):
        X1,X2,Y1,Y2 = [x-1,x+1],[x-2,x+2],[y-1,y+1],[y-2,y+2]
        #+-added first two if conditions
        if ((0<=X<8) and (0<=Y<8)) and ((0<=x<8) and (0<=y<8)):
            if (s.tiles[x][y].pieceColour == s.opposite(s.tiles[X][Y].pieceColour)):
                if s.CanDoWalk(x,y,X,Y,exception=True):
                    for i in range(2):
                        for j in range(2):
                            if X1[i]==X and Y1[j]==Y:
                                if (0<=X2[i]<8) and (0<=Y2[j]<8):
                                    if not (s.tiles[X2[i]][Y2[j]].isPiece):
                                        return True
        return False

############
# This Function enables a tile to jump over opponent piece. Trace Back --> Requirement 1.5
############
    def PieceCanJumpTo(s,x,y,X,Y):
        X1,X2,Y1,Y2 = [x-1,x+1],[x-2,x+2],[y-1,y+1],[y-2,y+2]
        for i in range(2):
            for j in range(2):
                if X2[i]==X and Y2[j]==Y:
                    if s.PieceCanCapturePiece(x,y,X1[i],Y1[j]):
                        return True
        return False

########
# This Function enables a king to move front and back. Trace Back --> Requirement 1.5
######## 
    def CanDoWalk(s,x,y,X,Y,exception=False): #The final parameter is to add a special case such that PieceCanCapturePiece may use this method
        X1,Y1 = [x-1,x+1],[y-1,y+1]

        for i in range(2):
            for j in range(2):
                if X1[i]==X and Y1[j]==Y:
                    if (0<=X<8) and (0<=Y<8):
                        if(s.tiles[x][y].isWhite and j==1) or \
                            (s.tiles[x][y].isBlack and j==0) or \
                            (s.tiles[x][y].isKing):
                            if not(exception or s.tiles[X][Y].isPiece) or \
                               (exception and s.tiles[X][Y].isPiece and \
                               (s.pTurn != s.tiles[X][Y].pieceColour)):
                                return True
        return False

##########
# This Function launches the standard/original setup of the board. Trace Back --> Requirement 1.1
##########
    def StandardSetup(s): #defines the standard button
        s.ClearBoard()
        s.state = 'CustomSetup' #in custom mode
        for i in range(s.BoardDimension):
            for j in range(s.BoardDimension):
                if s.tiles[i][j].TileColour(i,j) == 'Red' and (j < 3):
                    s.tiles[i][j] = Tile(s.win,i,j,True,'White','Pawn')
                if s.tiles[i][j].TileColour(i,j) == 'Red' and (j > 4):
                    s.tiles[i][j] = Tile(s.win,i,j,True,'Black','Pawn')
                    #places all the pieces in default checkers postitions

    def numColour(s,colour): #counts the number of pieces of a given colour
        c = 0 #initiate counter
        for i in range(s.BoardDimension):
            for j in range(s.BoardDimension):
                if colour=='White' and s.tiles[i][j].isWhite:
                    c += 1
                elif colour=='Black' and s.tiles[i][j].isBlack:
                    c += 1
        return c

    def anti_cap(s, cap):
        if cap == s.cap_nw:
            return s.cap_se
        elif cap == s.cap_ne:
            return s.cap_sw
        elif cap == s.cap_sw:
            return s.cap_ne
        elif cap == s.cap_se:
            return s.cap_nw

    def anti_slide(s, slide):
        if slide == s.slide_ne:
            return s.slide_sw
        elif slide == s.slide_sw:
            return s.slide_ne
        elif slide == s.slide_nw:
            return s.slide_se
        elif slide == s.slide_se:
            return s.slide_nw        

    def opposite(s,opp): #Returns the 'opposite' of a given parameter (only works for specific things)
        if opp == 'White':
            return 'Black'
        elif opp == 'Black':
            return 'White'
        
        elif opp == 'King':
            return 'Pawn'
        elif opp == 'Pawn':
            return 'King'

        elif opp == 'Place':
            return 'Delete'
        elif opp == 'Delete':
            return 'Place'
        

        
        else:
            #+-returns instead of printing error message
            return opp
        
    #####
    #function returns the bottom left coordinate of the square clicked
    #####
    def ClickedSquare(s,click):   
        try:
            clickX = click.getX()
            clickY = click.getY()
            if clickX < 0:
                clickX = int(clickX)-1
            else:
                clickX = int(clickX)
            if clickY < 0:
                clickY = int(clickY)-1
            else:
                clickY = int(clickY)
            return clickX, clickY
        except IndexError:          #some positions on the outskirts of the screen are invalid locations
            s.Click()

#######
# This Function Saves the game to be resumed later. Trace back --> Requirement 1.6
#######
    def SaveSetupToFile(s):   #method writes the tiles array to file checkers.txt
        # can have a dialog box to ask for the text file name to save to
        saveFile = open ('checkers.txt' , 'w') #opens file to write
        for i in range(s.BoardDimension):
            for j in range(s.BoardDimension):
                if (s.tiles[i][j].isPiece):
                    i_string = str(i)
                    j_string = str(j)
                    saveFile.write(i_string + j_string + str(s.tiles[i][j].pieceColour)[0] + \
                                   str(s.tiles[i][j].pieceRank)[0] + "\n")
        saveFile.write(s.pTurn[0]) #saves whose turn it is too
        tkMessageBox.showinfo("Saved Complete", "Game setup was saved to checkers.txt")
        saveFile.close()

##########################
#Function LoadSetupFromFile(s) corresponds to Requirement 1.2
##########################
    def LoadSetupFromFile(s): #method gets the setup saved and places pieces accordingly
        loadFile = open ('checkers.txt' , 'r') #opens file to read
        piece_list = loadFile.readlines()
        tkMessageBox.showinfo("Loading", "Will now clear the board and \nplace the saved setup")
        s.ClearBoard()
        for i in range(len(piece_list) - 1):
            tot_string = piece_list[i]
            x_var = int(tot_string[0])
            y_var = int(tot_string[1])
            #checks the text file, with these specific letters signifying what each piece is
            #first letter - 'W' is white, 'B' is black
            #second letter - 'K' is a King piece, 'P' is a pawn piece
            if (tot_string[2] == 'W'): #it is a white piece
                if (tot_string[3] == 'K'): #it is a white King piece
                    s.tiles[x_var][y_var] = Tile(s.win,x_var,y_var,True,'White','King')
                else : #piece is a white pawn
                    assert(tot_string[3] == 'P')
                    s.tiles[x_var][y_var] = Tile(s.win,x_var,y_var,True,'White','Pawn')
            else: #piece is black
                assert(tot_string[2] == 'B')
                if (tot_string[3] == 'K'): #piece is a black King
                    s.tiles[x_var][y_var] = Tile(s.win,x_var,y_var,True,'Black','King')
                else: #piece is a black pawn
                    assert(tot_string[3] == 'P')
                    s.tiles[x_var][y_var] = Tile(s.win,x_var,y_var,True,'Black','Pawn')
        #whose turn it was is restored
        if (piece_list[len(piece_list)-1] == 'W'): #it is white's turn
            s.pTurn = 'White'
        else: #it is black's turn
            s.pTurn = 'Black'
        s.SetButtons()
        loadFile.close()


'''
# We took out Class Piece from Checkers_v6 and implemented Class Tile in Checkers_v18.
    This was done to ensure a seamless transition for when the game actually ran.
'''
##########
#defines a tile and holds its current state
##########

class Tile:
    def __init__(s,win,X,Y,isPiece,pieceColour='',pieceRank='',isSelected=False):
        s.win = win
        s.x = X
        s.y = Y
        s.isPiece = isPiece
        s.isWhite = ('White' == pieceColour) and s.isPiece
        s.isBlack = ('Black' == pieceColour) and s.isPiece
        s.isKing = ('King' == pieceRank) and s.isPiece
        s.isPawn = ('Pawn' == pieceRank) and s.isPiece

        s.pieceColour=''
        s.pieceRank=''
        if s.isWhite:
            s.pieceColour = 'White'
        elif s.isBlack:
            s.pieceColour = 'Black'
        if s.isKing:
            s.pieceRank = 'King'
        elif s.isPawn:
            s.pieceRank = 'Pawn'

        s.c = Point(s.x+.5,s.y+.5)
        s.circ = Circle(s.c,0.4)

        if isSelected:
            s.circ.setOutline('Yellow')
        else:
            s.circ.setOutline('Black')
            s.circ.undraw()

        s.kingTxt = Text(s.c,'K')
        s.kingTxt.undraw()

        s.ColourButton(s.TileColour(s.x,s.y),s.x,s.y)
        if s.isPiece:
            s.DrawPiece()
##########
#function to create a rectangle with a given colour, size, and location
##########
    def ColourButton(s,colour,X,Y,width=1,height=1):
        rect = Rectangle(Point(X,Y),Point(X+width,Y+height))
        rect.setFill(colour)
        rect.draw(s.win)
        
##########
#Tiles on the board
##########        
    def TileColour(s,x,y):
        if (x%2 == 0 and y%2 == 0) or (x%2 == 1 and y%2 == 1):
            return 'Red'   #sets every other square to red 
        else:
            return 'White' #every non red square to white

##########
#Displays White or Black or King Pieces
##########
    def DrawPiece(s):
        s.circ.draw(s.win)

        if s.isWhite:
            col1,col2 = 'White','Black'
        elif s.isBlack:
            col1,col2 = 'Black','White'

        s.circ.setFill(col1)

        if s.isKing:
            s.kingTxt.draw(s.win)
            s.kingTxt.setFill(col2)

##########
#Quit
##########
def ExitGame(win):
    win.close()
    sys.exit()
    
game = Checkers()
