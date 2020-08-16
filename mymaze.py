import sys


class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():  # untuk algoritma DFS
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contain_state(self, state):
        return any(state == node.state for node in self.frontier)

    # mengecek apakah frontier kosong
    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("Frontier kosong")
        else:
            node = self.frontier[-1]  # mengambil elemen terakhir di frontier
            self.frontier = self.frontier[:-1]  # menghilangkan elemen terakhir
            return node


class QueueFrontier(StackFrontier):  # untuk algoritma BFS, hanya beda method remove
    def remove(self):
        if self.empty():
            raise Exception("Frontier kosong")
        else:
            node = self.frontier[0]  # mengambil elemen terdepan di frontier
            self.frontier = self.frontier[1:]  # menghilangkan elemen pertama
            return node


class Maze():

    def __init__(self, filename):
        with open(filename) as f:
            # mengambil isi file
            content = f.read()

        # cek start dan goal
        if content.count("A") != 1:
            raise Exception("Tidak ada titik mulai")
        if content.count("B") != 1:
            raise Exception("Tidak ada titik finish")

        # menentukan tinggi dan lebar maze
        content = content.splitlines()
        self.height = len(content)
        self.width = len(content[0])

        # membuat tembok, yang tembok diberi nilai True yang nantinya jika true akan ditampilkan karakter balok di layar
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if content[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif content[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif content[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None
        # akhir constructor

    # fungsi print solusi
    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    # fungsi mengekspan tetangga yang bukan blok dinding
    def neighbours(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        # cek tetangga
        for action, (r, c) in candidates:
            # cak apakah masih di dalam rentang tabel
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self):
        # mencatat state yang di eksplor
        self.num_explored = 0

        # inisialisasi frontier untuk menyimpan posisi awal
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()  # mau menggunakan algoritma apa
        frontier.add(start)

        # inisialisasi empty explored
        self.explored = set()

        # perulangan sampai solusi ditemukan
        while True:

            if frontier.empty():
                raise Exception("tidak ada solusi")

            # ambil satu state untuk di ekspan
            node = frontier.remove()
            self.num_explored += 1

            # jika ditemukan solusi maka rekam jejak solusi
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                # me-reverse urutan list
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # tandai node saat ini sebagai yang di explor
            self.explored.add(node.state)

            # tambahkan neighbor yang dapat di ekspan
            for action, state in self.neighbours(node.state):
                # cek apakah state sudah pernah di eksplor
                if not frontier.contain_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw  # module untuk membuat gambar
        cell_size = 50
        cell_border = 2

        # membuat canvas kosong dengan parameter mode, size (width, height), color
        img = Image.new("RGBA", (self.width * cell_size,
                                 self.height * cell_size), "black")
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # walls
                # nilai true berarti walls
                if col:
                    fill = (40, 40, 40)
                # titik start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                # titik goal atau end
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                # solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)
                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


# harus memberikan parameter kedua saat menjalankan program
if len(sys.argv) != 2:
    sys.exit("second parameter is missing \nUsage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solve()
print("States Explored:", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze.png", show_explored=True)
