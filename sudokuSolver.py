#!/usr/bin/env python
#coding:utf-8


import warnings
warnings.filterwarnings('ignore')
import argparse
import time
import numpy as np
import queue
import sys

"""
Each sudoku board is represented as a dictionary with string keys and
int values.
e.g. my_board['A1'] = 8
"""

ROW = "ABCDEFGHI"
COL = "123456789"


def print_board(board):
    """Helper function to print board in a square."""
    print("-----------------")
    for i in ROW:
        row = ''
        for j in COL:
            row += (str(board[i + j]) + " ")
        print(row)

class finder:

    def __init__(self,board):
        self.hassolution = False
        self.variables = []
        self.unchangeable = []
        self.backtrace = BackTrace()
        for i in board.keys():
            value = board[i]
            if value == 0:
                variable = Variable(i,list(range(1,10)))
                self.variables.append(variable)
            else:
                variable = Variable(i,[value])
                self.unchangeable.append(variable)
        self.basicCheck()

    def basicCheck(self):
        for var in self.variables:
            for unchange in self.unchangeable:
                if unchange.isNeibor(var):
                    var.removeValueFromDomain(unchange.getAssignment())

    def getNeighbors(self,var):
        neihobors = []
        for unchange in self.unchangeable:
            if var.isNeibor(unchange) and not var == unchange:
                neihobors.append(unchange)
        for variable in self.variables:
            if var.isNeibor(variable) and not var == variable:
                neihobors.append(variable)
        return neihobors

    def getMRV(self):
        minlen = 10
        result = None
        for var in self.variables:
            if not var.isAssigned():
                if len(var.getValues()) < minlen:
                    minlen = len(var.getValues())
                    result = var
        return result

    def getValuesLCVOrder(self,var):
        return var.getValues()

    def forwardChecking(self):
        for var in self.variables:
            if var.isAssigned() and not var.isFChecked():
                var.setFChecked(True)
                for n in self.getNeighbors(var):
                    if n.isAssigned() and n.getAssignment() == var.getAssignment():
                        var.setFChecked(False)
                        return False
                    self.backtrace.push(n)
                    n.removeValueFromDomain(var.getAssignment())
        return True

    def solve(self):
        if self.hassolution:
            return

        # Variable Selection
        v = self.getMRV()
        # check if the assigment is complete
        if v is None:
            for var in self.variables:
                # If all variables haven't been assigned
                if not var.isAssigned():
                    print("Error")
            # Success
            self.hassolution = True
            return
        # print(v.getName())
        # Attempt to assign a value
        for i in self.getValuesLCVOrder(v):

            # Store place in trail and push variable's state on trail
            self.backtrace.placeTrailMarker()
            self.backtrace.push(v)

            # Assign the value
            v.assignValue(i)

            # Propagate constraints, check consistency, recurse
            if self.forwardChecking():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.backtrace.undo()


    def to_dict(self):
        result = {}
        for var in self.unchangeable:
            result[var.getName()] = var.getAssignment()
        for var in self.variables:
            result[var.getName()] = var.getAssignment()
        sorted(result)
        return result

class BackTrace:

    def __init__(self):
        self.trailStack = []
        self.trailMarker = []

    # Places a marker in the trail
    def placeTrailMarker(self):
        self.trailMarker.append(len(self.trailStack))

    # Before assign a variable, save its initial domain on the backtrace.
    # When the path fails, it can restore propagated domains correctly.
    def push(self, v):
        vPair = (v, [i for i in v.getValues()])
        self.trailStack.append(vPair)

    # Pops and restores variables on the trail until the last trail marker
    def undo(self):
        targetSize = self.trailMarker.pop()  # targetSize target position on the trail to backtrack to
        size = len(self.trailStack)
        while size > targetSize:
            vPair = self.trailStack.pop()
            v = vPair[0]
            v.setValues(vPair[1])
            v.setFChecked(False)
            size -= 1

    # Clears the trail
    def clear(self):
        self.trailStack = []
        self.trailMarker = []

class Variable:
    def __init__(self, name, values):
        self.name = name
        self.values = values
        if len(values) == 1:
            self.fchecked = True
            self.changeable = False
        else:
            self.fchecked = False
            self.changeable = True

    def copy(self, v):
        self.name = v.name
        self.values = v.values
        self.fchecked = v.fchecked
        self.changeable = v.changeable

    def isChangeable(self):
        return self.changeable

    def isAssigned(self):
        return len(self.values) == 1

    def isFChecked(self):
        return self.fchecked

    # Returns the assigned value or 0 if unassigned
    def getAssignment(self):
        if not self.isAssigned():
            return 0
        else:
            return self.values[0]

    def getName(self):
        return self.name

    def getValues(self):
        return self.values

    def setFChecked(self, mod):
        self.fchecked = mod

    def setValues(self, values):
        self.values = values
    # Assign a value to the 
    def assignValue(self, val):
        if not self.changeable:
            return
        self.values = [val]

    # Removes a value from the domain
    def removeValueFromDomain(self, val):
        if not self.changeable:
            return
        if val not in self.getValues():
            return
        self.values.remove(val)

    def isNeibor(self, var):
        sameColumn = self.name[0] == var.getName()[0]
        sameRow = self.name[1] == var.getName()[1]

        selfblockcol = (ord(self.name[0]) - ord('A')) // 3
        selfblockrow = (ord(self.name[1]) - ord('1')) // 3
        varblockcol = (ord(var.getName()[0]) - ord('A')) // 3
        varblockrow = (ord(var.getName()[1]) - ord('1')) // 3

        sameBlock = selfblockcol == varblockcol and selfblockrow == varblockrow


        return sameRow or sameBlock or sameColumn


def board_to_string(board):
    """Helper function to convert board dictionary to string for writing."""
    ordered_vals = []
    for r in ROW:
        for c in COL:
            ordered_vals.append(str(board[r + c]))
    return ''.join(ordered_vals)


def backtracking(board):
    """Takes a board and returns solved board."""
    # TODO: implement this
    solve = finder(board)
    solve.solve()
    solved_board = solve.to_dict()
    return solved_board


if __name__ == '__main__':
    #  Read boards from source.
    ReamMe = 'ReadMe.txt'
    ReamMe = open(ReamMe, "w")
    ReamMe.write("This is a sudoku Solver, You can just write python sudoku.py 'board' ")
    ReamMe.write('\n')
    ReamMe.write("Also, If you want to solve all the puzzels in the file (400) you can run only python sudoku.py")
    ReamMe.write('\n')

    if len(sys.argv) == 1:

        src_filename = 'sudokus_start.txt'
        try:
            srcfile = open(src_filename, "r")
            sudoku_list = srcfile.read()
        except:
            print("Error reading the sudoku file %s" % src_filename)
            exit()

        # Setup output file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")
        times = []
        # Solve each board using backtracking
        for line in sudoku_list.split("\n"):

            if len(line) < 9:
                continue

            # Parse boards to dict representation, scanning board L to R, Up to Down
            board = { ROW[r] + COL[c]: int(line[9*r+c])
                    for r in range(9) for c in range(9)}

            # Print starting board. TODO: Comment this out when timing runs.
            #print_board(board)
            start_time = time.time()
            # Solve with backtracking
            solved_board = backtracking(board)
            end_time = time.time()

            # Print solved board. TODO: Comment this out when timing runs.
            #print_board(solved_board)

            # Write board to file
            outfile.write(board_to_string(solved_board))
            outfile.write('\n')
            times.append(end_time-start_time)

        outfile.close()
        print("Finishing all boards in file.")
        print("running time statistics:")
        print("min: ",min(times))
        print("max: ",max(times))
        print("mean: ",np.mean(times))
        print("standard deviation: ",np.std(times))
        ReamMe.write("Finishing all boards in file.")
        ReamMe.write('\n')
        ReamMe.write("min: {}".format(min(times)))
        ReamMe.write('\n')
        ReamMe.write("max: {}".format(max(times)))
        ReamMe.write('\n')
        ReamMe.write("mean: {}".format(np.mean(times)))
        ReamMe.write('\n')
        ReamMe.write("standard deviation: {}".format(np.std(times)))
        ReamMe.write('\n')

    else:
        parser = argparse.ArgumentParser(description='Suduku Solver...')
        parser.add_argument('Unsolved', type=str)
        args = parser.parse_args()
        line=args.Unsolved
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")
        times = []
        # Parse boards to dict representation, scanning board L to R, Up to Down
        board = { ROW[r] + COL[c]: int(line[9*r+c])
                for r in range(9) for c in range(9)}

        # Print starting board. TODO: Comment this out when timing runs.
        #print_board(board)
        start_time = time.time()
        # Solve with backtracking
        solved_board = backtracking(board)
        end_time = time.time()

        # Print solved board. TODO: Comment this out when timing runs.
        #print_board(solved_board)

        # Write board to file
        outfile.write(board_to_string(solved_board))
        outfile.write('\n')
        outfile.close()
        times.append(end_time-start_time)
        print("Finishing solved one puzzle")
        print("Solved in : ",min(times))
        ReamMe.write("Finishing solved one puzzle")
        ReamMe.write('\n')
        ReamMe.write("Solved in : {}".format(min(times)))
        ReamMe.close()




    