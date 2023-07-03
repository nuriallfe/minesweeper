import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8, board = None):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set() #cells with mines --> board's positions will be true and we add in this set the tuple (i, j)
        
        #initialize and empty field with no mines --> all position False
        #the board will be a list of lists
        self.board = board or [[False for _ in range(width)] for _ in range(height)]


        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]: #if this cell is False we add a mine --> if it is true it means that there is a mine
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell): #we want to know if the cell is a mine --> true - is a mine / false - it is not a mine
        i, j = cell
        if 0 <= i < self.height and 0 <= j < self.width:
            return self.board[i][j]
        else:
            return False

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines (neighbors)
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width: #if it is true --> there is a mine
                    if self.board[i][j]:
                        count += 1
        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count): 
        self.cells = set(cells) #cells --> cells that we want to discover if it is a mine or it is a safer cell 
        self.count = count # count --> number of mines

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        #algorisme 2
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #algorisme 1
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count` --> cell = cells that are mines
               and counnt = number of mines
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #1
        self.moves_made.add(cell)
        #2
        self.mark_safe(cell)
        #3 -> una sentence hem de passar una cell i els seus veïns, independentment de si son mines i no i el nombre de mines que hi ha de mines
        neighbors = []
        i, j = cell
        for x in range(i-1, i+2):
            for y in range(j-1, j+2):
                if (x,y) != (i,j) and 0<= x < self.height and 0<= j < self.width:
                    neighbors.append((x,y))
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)
        #4 --> marcar cel·les adicionals com segures o mines basant-nos en el coneixement actual del jugador
        #utilitzant les oracions existents (algoritme 1 i 2)
        known_mines = set()
        known_safes = set()
        for sentence in self.knowledge:
            if sentence.known_mines:
                known_mines.update(sentence.known_mines())
            if sentence.known_safes:
                known_safes.update(sentence.known_safes())
        
        for mine in known_mines:
            self.mark_mine(mine)
        for safe in known_safes:
            self.mark_safe(safe)

        new_sentences = []
        for sentence1, sentence2 in itertools.combinations(self.knowledge, 2):
            if sentence1.cells.issubset(sentence2.cells):
                inferred_sentence = Sentence(
                    sentence2.cells - sentence1.cells, sentence2.count - sentence1.count)
                if inferred_sentence not in self.knowledge:
                    new_sentences.append(inferred_sentence)

        self.knowledge.extend(new_sentences)
                
        #afegir noves oracions al coneixement del jugador basant-nos en el coneixement existent
        #inferir noves frases (algoritme 3)
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #comencem creant un set de totes les cel·les que hi ha possibles
        all_cells = set(itertools.product(range(self.height), range(self.width)))
        #en el cas anterior, intertools.product, agafa dos iterables, range(self.height) i range(self.width) 
        # i genera totes les combinacions possibles d'elements, en aquest cas totes les cel·les del tauler
        possible_moves = all_cells - self.moves_made - self.mines
        if possible_moves:
            return random.choice(list(possible_moves))
        return None
