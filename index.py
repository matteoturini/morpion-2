from rich import console
import os
import sys
from readchar import readkey
from websockets.sync.client import connect
from websockets.sync.connection import Connection

c = console.Console()

# 0 - b
# 1 - 1
# 2 - 2
#jeu = [[random.randint(0, 2) for i in range(9)] for j in range(9)]
jeu = [[0 for i in range(9)] for j in range(9)]

tableau: list[int] | None = None
joueur = 1
tour = 1

clear_screen = lambda: os.system('cls' if os.name == 'nt' else 'clear')

def recevoir_touche(msg: str) -> str:
    c.print(msg, end='')
    return readkey()

def jeuGagne(tableau):
    if tableau == None:
        return None
    mJeu = [[jeu[x][y] for y in range(tableau[1] * 3, (tableau[1] + 1) * 3)] for x in range(tableau[0] * 3, (tableau[0] + 1) * 3)]
    if mJeu[0][0] == mJeu[1][0] and mJeu[1][0] == mJeu[2][0] and mJeu[0][0] != 0: return [[0, 0], [1, 0], [2, 0]]  # ligne 0
    elif mJeu[0][1] == mJeu[1][1] and mJeu[1][1] == mJeu[2][1] and mJeu[0][1] != 0: return [[0, 1], [1, 1], [2, 1]]  # ligne 1
    elif mJeu[0][2] == mJeu[1][2] and mJeu[1][2] == mJeu[2][2] and mJeu[0][2] != 0: return [[0, 2], [1, 2], [2, 2]]  # ligne 2
    elif mJeu[0][0] == mJeu[0][1] and mJeu[0][1] == mJeu[0][2] and mJeu[0][0] != 0: return [[0, 0], [0, 1], [0, 2]]  # colonne 0
    elif mJeu[1][0] == mJeu[1][1] and mJeu[1][1] == mJeu[1][2] and mJeu[1][0] != 0: return [[1, 0], [1, 1], [1, 2]]  # colonne 1
    elif mJeu[2][0] == mJeu[2][1] and mJeu[2][1] == mJeu[2][2] and mJeu[2][0] != 0: return [[2, 0], [2, 1], [2, 2]]  # colonne 2
    elif mJeu[0][0] == mJeu[1][1] and mJeu[1][1] == mJeu[2][2] and mJeu[0][0] != 0: return [[0, 0], [1, 1], [2, 2]]  # diagonale decroissante
    elif mJeu[2][0] == mJeu[1][1] and mJeu[1][1] == mJeu[0][2] and mJeu[2][0] != 0: return [[2, 0], [1, 1], [0, 2]]  # diagonale croissante
    return None  # aucun

def jeuGagneJoueur(tableau):
    mJeu = [[jeu[x][y] for y in range(tableau[1] * 3, (tableau[1] + 1) * 3)] for x in range(tableau[0] * 3, (tableau[0] + 1) * 3)]
    if mJeu[0][0] == mJeu[1][0] and mJeu[1][0] == mJeu[2][0] and mJeu[0][0] != 0: return mJeu[0][0]  # ligne 0
    elif mJeu[0][1] == mJeu[1][1] and mJeu[1][1] == mJeu[2][1] and mJeu[0][1] != 0: return mJeu[0][1]  # ligne 1
    elif mJeu[0][2] == mJeu[1][2] and mJeu[1][2] == mJeu[2][2] and mJeu[0][2] != 0: return mJeu[0][2]  # ligne 2
    elif mJeu[0][0] == mJeu[0][1] and mJeu[0][1] == mJeu[0][2] and mJeu[0][0] != 0: return mJeu[0][0]  # colonne 0
    elif mJeu[1][0] == mJeu[1][1] and mJeu[1][1] == mJeu[1][2] and mJeu[1][0] != 0: return mJeu[1][0]  # colonne 1
    elif mJeu[2][0] == mJeu[2][1] and mJeu[2][1] == mJeu[2][2] and mJeu[2][0] != 0: return mJeu[2][0]  # colonne 2
    elif mJeu[0][0] == mJeu[1][1] and mJeu[1][1] == mJeu[2][2] and mJeu[0][0] != 0: return mJeu[0][0]  # diagonale decroissante
    elif mJeu[2][0] == mJeu[1][1] and mJeu[1][1] == mJeu[0][2] and mJeu[2][0] != 0: return mJeu[2][0]  # diagonale croissante
    return None  # aucun

def victoire():
    tab = [[jeuGagneJoueur([i, j]) for j in range(3)] for i in range(3)]
    if tab[0][0] == tab[1][0] and tab[1][0] == tab[2][0] and tab[0][0] != None: return tab[0][0]  # ligne 0
    elif tab[0][1] == tab[1][1] and tab[1][1] == tab[2][1] and tab[0][1] != None: return tab[0][1]  # ligne 1
    elif tab[0][2] == tab[1][2] and tab[1][2] == tab[2][2] and tab[0][2] != None: return tab[0][2]  # ligne 2
    elif tab[0][0] == tab[0][1] and tab[0][1] == tab[0][2] and tab[0][0] != None: return tab[0][0]  # colonne 0
    elif tab[1][0] == tab[1][1] and tab[1][1] == tab[1][2] and tab[1][0] != None: return tab[1][0]  # colonne 1
    elif tab[2][0] == tab[2][1] and tab[2][1] == tab[2][2] and tab[2][0] != None: return tab[2][0]  # colonne 2
    elif tab[0][0] == tab[1][1] and tab[1][1] == tab[2][2] and tab[0][0] != None: return tab[0][0]  # diagonale decroissante
    elif tab[2][0] == tab[1][1] and tab[1][1] == tab[0][2] and tab[2][0] != None: return tab[2][0]  # diagonale croissante
    return None  # aucun

def printJeu():
    txt = " "
    if tableau == None: t = [-1, -1]
    else: t = tableau
    for j in range(3):
        for y in range(j * 3, (j + 1) * 3):
            txt += "  "
            for i in range(3):
                resultat = jeuGagne([i, j])
                for x in range(i * 3, (i + 1) * 3):
                    if resultat != None:
                        if jeu[x][y] == 0: txt += " "
                        elif jeu[x][y] == 1 and [x - i * 3, y - j * 3] in resultat: txt += "[white on green]X[/white on green]"
                        elif jeu[x][y] == 2 and [x - i * 3, y - j * 3] in resultat: txt += "[white on blue]O[/white on blue]"
                        elif jeu[x][y] == 1: txt += "[green]X[/green]"
                        elif jeu[x][y] == 2: txt += "[blue]O[/blue]"
                    else:
                        if jeu[x][y] == 0: txt += " "
                        elif jeu[x][y] == 1: txt += "[green]X[/green]"
                        elif jeu[x][y] == 2: txt += "[blue]O[/blue]"
                    if [i, j] == t and tour == 1 and not (x == 2 or x == 5 or x == 8): txt += " [green]|[/green] "
                    elif [i, j] == t and tour == 2 and not (x == 2 or x == 5 or x == 8): txt += " [blue]|[/blue] "
                    elif not (x == 2 or x == 5 or x == 8): txt += " | "
                    else: txt += "  "
                if i != 2: txt += "||  "
            txt += "\n "
            if j == t[1] and not (y == 8 or y == 5 or y == 2):
                add = " "
                for k in range(3):
                    if k == t[0] and tour == 1 and k != 2:
                        add += "[green]---|---|---[/green] || "
                    elif k == t[0] and tour == 2 and k != 2:
                        add += "[blue]---|---|---[/blue] || "
                    elif k == t[0] and tour == 1:
                        add += "[green]---|---|---[/green]"
                    elif k == t[0] and tour == 2:
                        add += "[blue]---|---|---[/blue]"
                    else:
                        if k != 2:
                            add += "---|---|--- || "
                        else:
                            add += "---|---|---"
                txt += add + "\n "
            elif not (y == 8 or y == 5 or y == 2):
                txt += " ---|---|--- || ---|---|--- || ---|---|---\n "
        if j != 2:
            txt += " " + "="*12 + "||" + "="*13 + "||" + "="*12 + "\n "
    c.print(txt)


subgame = ""
symbol = "O"

def saisirCase(t):
    t = t.lower()
    keys = {
        "q": [0, 0],
        "w": [1, 0],
        "e": [2, 0],
        "a": [0, 1],
        "s": [1, 1],
        "d": [2, 1],
        "z": [0, 2],
        "x": [1, 2],
        "c": [2, 2]
    }
    if t in keys:
        return keys[t]
    else:
        return [0, 0]


c.print("Bienvenu(e) sur Morpion² [REGLES]")
c.print("""Le saissisement de cases et de tableau se fait en appuyant sur une touche correspondante a la case:
      Q W E
      A S D
      Z X C
      """)

def game():
    with connect("ws://localhost:8000") as ws:
        c.print("Voulez vous créer une partie ou en rejoindre une?")
        c.print("[1] Créer")
        c.print("[2] Rejoindre")
        c.print("[3] Quitter")
        t = recevoir_touche("Saisissez votre choix: ")
        if t == "1":
            c.print("Attente de la création de la partie...")
            ws.send("create")
            msg = ws.recv()
            c.print(f"Le code est [cyan]{msg}[/cyan]. Donnez le a votre adversaire pour qu'il puisse rejoindre la partie.")
            c.print("Attente de l'adversaire...")
            msg = ws.recv()
            if msg == "joined":
                # Son de notification
                print('\a')
                c.print("L'adversaire a rejoint la partie.")
                c.print("La partie va commencer.")
                main_loop(ws, 1)
                sys.exit()
            else:
                print('\a')
                c.print("Le temps d'attente est écoulé. Merci de relancer l'application quand votre adversaire ira jouer.")
                sys.exit()
        elif t == "2":
            while True:
                c.print("Saisissez le code de la partie, ou [cyan]Q[/cyan] pour quitter: ")
                code = input("> ")
                if code == "Q" or code == "q":
                    sys.exit()
                ws.send(code)
                msg = ws.recv()
                if msg == "joined":
                    # Son de notification
                    print('\a')
                    c.print("Vous avez rejoint la partie.")
                    c.print("La partie va commencer.")
                    main_loop(ws, 2)
                    sys.exit()
        elif t == "3":
            exit()

def receive_move(ws: Connection):
    global tableau
    c.print("En attente du jet de l'adversaire...")
    msg = str(ws.recv())
    c.print(msg)
    if msg == "quit":
        c.print("L'adversaire a quitté la partie.")
        sys.exit()
        raise Exception()
    else:
        spl = msg.split(sep=',', maxsplit=-1) # type: ignore
        return list(map(int, spl))

def main_loop(ws: Connection, player: int = 1):
    resetJeu = 0
    global tableau
    retour = None
    if player == 2:
        joueur = 2
        tour = 1
    else:
        joueur = 1
        tour = 1
    while True:

        printJeu()


        if tour != joueur:
            move = receive_move(ws)
            jeu[move[0]][move[1]] = move[2]
            tableau = [move[0] % 3, move[1] % 3] if not jeuGagne(tableau) else None
            if move[3] == 1: tableau = None
            tour = 1 if tour == 2 else 2
            clear_screen()
            printJeu()

        if tableau == None:
            while True:
                tableau = saisirCase(recevoir_touche("Saisissez le jeu a jouer: "))
                if jeuGagne(tableau) != None:
                    c.print("Jeu invalide!")
                else:
                    clear_screen()
                    printJeu()
                    break

        case = None
        while True:
            case = saisirCase(recevoir_touche("Saisissez la case a jouer: "))
            if jeu[tableau[0] * 3 + case[0]][tableau[1] * 3 + case[1]] != 0:
                c.print("Case invalide!")
            else:
                jeu[tableau[0] * 3 + case[0]][tableau[1] * 3+ case[1]] = joueur
                resetJeu = 0
                if jeuGagne(tableau) != None: resetJeu = 1
                clear_screen()
                printJeu()
                ws.send(f"{tableau[0] * 3 + case[0]},{tableau[1] * 3 + case[1]},{joueur},{resetJeu}")
                break

        if jeuGagneJoueur(tableau) != None:
            c.print(jeuGagneJoueur(tableau))
            tableau = None
            victorious = victoire()
            if victorious != None:
                c.print(f"Joueur {victorious} a gagne!!!")
        else:
            tableau = case


        tour = 1 if tour == 2 else 2

        move = receive_move(ws)
        jeu[move[0]][move[1]] = move[2]
        tableau = [move[0] % 3, move[1] % 3] if not jeuGagne(tableau) else None
        if move[3] == 1: tableau = None
        clear_screen()
        printJeu()

        clear_screen()
        printJeu()

        tour = 1 if tour == 2 else 2

        clear_screen()

game()