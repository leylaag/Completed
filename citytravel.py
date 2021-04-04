import random
import copy

class town:
    """Reads and intializes town map
    initializes lights, traffic jams, taxis and player 
    At each time steps updates lights, positions, and state of each class
    updates map
    if error returns error string"""
    def __init__(self):
        self.num_steps = 0
        #Read grid file
        self.read_grid_file(self.max_row,self.max_col)
        global max_col 
        max_col = self.max_col
        global max_row
        max_row = self.max_row
        
        # initialize map
        self.puremap = []
        for i in range(self.max_row+1):
            self.puremap.append([])
            for j in range(self.max_col+1):
                self.puremap[i].append([""])      

        # add player
        self.p = player()

        # add lights
        self.lights = []
        for i in range(self.max_row+1):
            self.lights.append(light())

        # add traffic_jams at random positions
        self.traffic_jams = []
        tjrow = random.sample(range(self.max_row),self.num_traffic_jams)            
        tjcol = random.sample(range(self.max_col),self.num_traffic_jams)
        for i in range(self.num_traffic_jams):
            self.traffic_jams.append(traffic_jam(tjrow[i],tjcol[i]))
            
        # add taxis at random positions
        self.taxis = []
        self.taxis.append(taxi(0,0))
        trow = random.choices(range(self.max_row-1),k=self.num_taxis)            
        tcol = random.choices(range(self.max_col-1),k=self.num_taxis)
        for i in range(1,self.num_taxis):
            self.taxis.append(taxi(trow[i],tcol[i]))

        # draw map
        self.draw()

        return

    def read_grid_file(self,max_row,max_col):
        with open("grid.txt","r") as infile:
            raw_input = infile.readlines()
            self.grid = [datum.strip('\n') for datum in raw_input]
            self.max_row = int(len(raw_input)/2)
            self.max_col = int(len(self.grid[1])/6+1)
        return()
    
    def draw(self):
        """update positions of person and taxi; update state of Taxi and update traffic_jam"""
        newmap = copy.deepcopy(self.puremap)
        newmap[self.p.row][self.p.col] += self.p.symbol
        for i in range(len(self.taxis)):
            r = self.taxis[i].row
            c = self.taxis[i].col
            s = self.taxis[i].symbol
            newmap[r][c] += s
        for i in range(len(self.traffic_jams)):
            r = self.traffic_jams[i].row
            c = self.traffic_jams[i].col
            s = self.traffic_jams[i].symbol
            newmap[r][c] += s
        # draw grid
        newgrid = self.grid.copy()
        for i in range(self.max_row):
            for j in range(self.max_col):
                if len(newmap[i][j]) > 1:
                    col = int(j*6)
                    row = int((self.max_row - i)*2)-1
                    l = len(newmap[i][j])-1
                    col = max(0,col-int(l/2))
                    newgrid[row] = newgrid[row][0:col] + ''.join(newmap[i][j]) + newgrid[row][col+l:]
                    
        # add street directions and light colors
        top_heading = "      N     S     N     S     N     S     N     S     N     S     N"
        print(self.lights[0].color, top_heading)
        for row in range(self.max_row*2):
            if row % 4 == 1:
                print(self.lights[i].color,"East ",''.join(newgrid[row]))
            elif row % 4 == 3:
                print(self.lights[i].color,"West ",''.join(newgrid[row]))
            else:
                print(self.lights[i].color,"     ",''.join(newgrid[row]))

        return()

    def next_step(self, action):
        self.num_steps += 1
        # player to walk or find a taxi
        if action in "NSEW":
            self.p.next_step(action)
        elif action in "X":
            not_found = self.find_taxi(self.p.row,self.p.col)
            #if not found return with "not_found" code
            if not_found:
                return(0)

        for t in self.taxis:
            # taxis that reach the NE corner go back to the starting point
            # update taxis. first find out if they are in a traffic jam
            if t.row == self.max_row-1 and t.col == self.max_col-1:
                if not t.has_player:
                    t.row = 0
                    t.col = 0
                else:
                    self.p.row = t.row
                    self.p.col = t.col
                continue
                
            i = 0
            while i < self.num_traffic_jams:
                tj = self.traffic_jams[i]
                if tj.row == t.row and tj.col == t.col:
                    t.next_step(action, self.lights, tj.severity)
                    i = self.num_traffic_jams+1
                else:
                    i += 1
            if i == self.num_traffic_jams:
                t.next_step(action, self.lights, 0)
            if t.has_player:
                self.p.row = t.row
                self.p.col = t.col
            
        # update lights
        for i in range(len(self.lights)):
            self.lights[i].next_step()
        
        # update traffic jams randomly
        tjrow = random.sample(range(self.max_row),self.num_traffic_jams)            
        tjcol = random.sample(range(self.max_col),self.num_traffic_jams)        
        for i in range(len(self.traffic_jams)):
            self.traffic_jams[i].next_step(tjrow[i],tjcol[i])

        self.draw()
        #if has arrived return with "has_arrived" code
        if self.p.has_arrived:
            return(1)
        else:
            return(2)

        
    def find_taxi(self, row, col):
        not_found = True
        i = 0
        while i < self.num_taxis:
            t = self.taxis[i]
            if (t.row == row and t.col == col):
                t.has_player = True
                t.is_free = False
                t.symbol = "X"
                self.p.symbol = ""
                self.p.in_taxi = True
                i = self.num_taxis
                not_found = False
            else:
                i += 1
        return(not_found)
    
    def __str__(self):
        temp = str(grid[0])
        return(temp)
    def __repr__(self):
        return(self.__str__())
    
    puremap = []
    grid = []
    lights=[]
    p = None
    num_taxis = 6
    taxis=[]
    num_traffic_jams = 4
    traffic_jams=[]
    num_steps = 0
    max_row = 0
    max_col = 0
    
class light:
    """Traffic light. I will assume that all traffic switch from red to green at each time step
    all lights in E/W directions are red/green at the same time
    color indicates the color in the east/west direction."""

    def __init__(self):
        self.color = 'green'
        self.colors = {"green":"red","red":"green"}
        return
        
    def next_step(self):
        self.color = self.colors[self.color]
        return()

    color = 'green'
    colors = {}
    
class traffic_jam:
    """Pop at random time steps and random positions. Can be severe or benign
        Benign would reduce speed of taxis by 75%, severe by 100%
        severity is randomly updated at every time step"""
    def __init__(self, row = 0, col = 0, severity = 0):                  
        self.row = row
        self.col = col
        self.severity = severity
        self.symbols = {0:"",1:"j",2:"J"}
        return
        
    def next_step(self,row,col):
        old_severity = self.severity
        self.severity = random.randint(0,2)
        if (old_severity == 0 and self.severity > 0):
            # new traffic jam. determine position
            self.row = row
            self.col = col
        elif (old_severity > 0 and self.severity == 0):
            # disperse old_severity; move it to origin for now
            self.row = 0
            self.col = 0
        # set severity symbol
        self.symbol = self.symbols[self.severity]
        return()
        
    row = 0
    col = 0
    severity = 0
    symbol = ""
    symbols = {}

class taxi:
    """describe position and other attributes of taxi"""
    def __init__(self, row=0, col=0, is_free=True):
        self.row = row
        self.col = col
        self.is_free = is_free
        self.symbols = {True: "t", False: "T",}
        self.symbol = self.symbols[self.is_free]
        self.factors = {0:1, 1:0.25, 2:0}
#        ok_turns={}
        return
         
    def next_step(self, action, lights, jam_severity):
        if action in "X":
            return()
        if action in "NSEW":
            self.has_player = False        
        
        # taxi can move. determine legal turns (one ways) and action 
        if not self.has_player:
            #player not in taxi. set is_free and action randomly
            self.is_free = random.choice([True,False])
            self.symbol = self.symbols[self.is_free]
            turns = self.legal_turns(self.row,self.col)
            action = turns[random.randint(0,len(turns)-1)]
        else:
            # player is in taxi. Go all the way North then East
            if self.row < max_row-1:
                action = "N" 
            elif self.col < max_col-1:
                action = "E"
            else:
                return()
                
        # move        
        current_speed = self.factors[jam_severity]*self.speed
        if action in "N":
            if lights[self.row].color in ["red"]:               # taxi can go N/S
                self.row = int(min(self.row + current_speed, max_row-1))
            else:
                return()
        if action in "S":
            if lights[self.row].color in ["red"]:               # taxi can go N/S               
                self.row = int(min(self.row - current_speed, max_row-1))
            else:
                return()
        if action in "E":    
            if lights[self.row].color in ["green"]:                 # taxi can go E/W
                self.col = int(min(self.col + current_speed, max_col-1))
            else:
                return()
        if action in "W":    
            if lights[self.row].color in ["green"]:                 # taxi can go E/W
                self.col = int(max(self.col - current_speed, 0))
            else:
                return()
        return()
    
    def legal_turns(self, row, col):
        turns = []
        if (self.row % 2 == 0) and (self.col < max_col-1):
            turns.append("E")
        elif (self.row % 2 == 1) and (self.col > 0):
            turns.append("W")
        if (self.col % 2 == 0) and (self.row < max_row-1):
            turns.append("N")
        elif (self.col % 2 == 1) and (self.row > 0):
            turns.append("S")
        return(turns)
            
    is_free = True
    has_player = False
    speed = 4
    row = 0
    col = 1
    symbol = "t"
    directions = {}
    factors = {}
    symbols = {}

class player:
    """This is a player who can walk in the grid. If she takes a cab her position is dictated by the cab's"""
    def __init__(self):
        self.symbol = "P"
        self.taxi = None
        self.row = 0
        self.col = 0
        self.directions = {"N":[1,0], "S":[-1,0],"E":[0,1],"W":[0,-1]}
        return
    
    def next_step(self, action, in_taxi=False):  
        if action in "X" and in_taxi:
            self.symbol = ""
            self.in_taxi = True
            return()
        if action in "NSEW":
            self.symbol = "P"
            self.taxi = None
            self.row = max(min(self.row + self.directions[action][0], max_row-1),0)
            self.col = max(min(self.col + self.directions[action][1], max_col-1),0)
        return()

    def has_arrived(self):
        if (self.row == max_row-1) and (self.col == max_col-1):
            return(True)
        else:
            return(False)
    
    row = 0
    col = 0
    taxi = None
    in_taxi = False
    symbol = "P"
    total_time = 0
    directions = {}
    
class play_game:
    """ Prompts user for input until the extreme NE point is reached or player quits"""
    def __init__(self):
        m = town()           
        prompt1="Walk [E]ast \nWalk [W]est \nWalk [N]orth \nWalk [S]outh\nStay in [T]axi\n[Q]uit\n"
        prompt2="Walk [E]ast \nWalk [W]est \nWalk [N]orth \nWalk [S]outh\nTake Ta[x]i\n[Q]uit\n"
        while not m.p.has_arrived():
            get_input = True
            while get_input:
                if m.p.in_taxi:                                
                    action = input("What do you want to do next?\n"+ prompt1).upper()
                    if action in "EWNSTQ":
                        get_input= False
                    else:
                        print("Invalid entry. Try again.")
                else:
                    action = input("What do you want to do next?\n"+ prompt2).upper()
                    if action in "EWNSXQ":
                        get_input= False
                    else:
                        print("Invalid entry. Try again.")
                # input is valid character
            if action in "Q":
                    return
            else:              
                if m.next_step(action) == 0:
                    print ("No taxi available at this location.")

        
        print("\n\nCongratulation! You made it in", m.num_steps, "steps!")                    
        return
  
g = play_game()
