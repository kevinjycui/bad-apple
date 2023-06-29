# Turing Machine that plays Bad Apple!!
# Junferno 2023

from PIL import Image

import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
from matplotlib.animation import writers
import networkx as nx

from time import sleep

WIDTH = 28
HEIGHT = 14
FSTART = 555
FRAMES = 1666
FSKIP = 4
ENUMBITS = 9 # 2^ENDBITS > FRAMES/FSKIP

BASE_PNG_DIR = 'pngs'
BASE_PNG_PATH = BASE_PNG_DIR + '/png%d.png'

direction = {'L': -1, 'R': 1}
number_of_states = 0
state_set = []

class State:
    def __init__(self, name=-1):
        global number_of_states, state_set
        if name == -1:
            self.name = number_of_states
            number_of_states += 1
            state_set.append(self)
        else:
            self.name = name
        self.trfn = {}

    def add_transition(self, letter, state, nletter, d):
        self.trfn[letter] = (state, nletter, d)

    def __str__(self):
        return 'q' + str(self.name)

class TuringMachine:
    def __init__(self, qinit, qaccept, qreject, inp=''):
        self.head = 0
        self.tape = inp
        self.state = qinit
        self.accept = qaccept
        self.reject = qreject
        
    def tape_printable(self):
        trimmed = self.tape.rstrip('_')
        return trimmed + ('_' * max(0, self.head - len(trimmed) + 1))

    def tape_printable_as_display(self):
        trimmed = self.tape_printable()
        formatted = '' 
        for i in range(0, len(trimmed), WIDTH):
            formatted += '\n' + trimmed[i:i+WIDTH]
            if i <= self.head < i+WIDTH:
                formatted += '\n' + (' ' * (self.head-i)) + '^'
            else:
                formatted += '\n' 
        return formatted

    def __str__(self):
        return str(self.state) + '\n' + self.tape_printable_as_display()

    def accepted(self):
        return self.state.name == self.accept.name

    def rejected(self):
        return self.state.name == self.reject.name

    def step(self):
        if self.head >= len(self.tape):
            self.tape += '_' * (self.head - len(self.tape) + 1)

        if self.head < 0:
            print('ERROR: NEGATIVE INDEX', self.head)
            return 2

        letter = self.tape[self.head]
        if letter not in self.state.trfn:
            print('ERROR: INVALID TRANSITION')
            return 2

        self.state, nletter, d = self.state.trfn[letter]
        self.tape = self.tape[:self.head] + nletter + self.tape[self.head+1:]
        self.head += direction[d]

        if self.accepted() or self.rejected():
            print('HALT')
            return 0

        return 1

def generate_enumerator(qstate, rep='', depthmax=ENUMBITS, enumerator_map={}):
    # States form a decision tree reading a 13 bit binary integer
    if len(rep) >= depthmax:
        enumerator_map[int(rep, 2)] = qstate
        return enumerator_map

    if int(rep+'0', 2) > FRAMES+1:
        return enumerator_map

    qzero = State()
    qstate.add_transition('0', qzero, '0', 'R')
    enumerator_map = generate_enumerator(qzero, rep + '0', depthmax, enumerator_map)

    if int(rep+'1', 2) > FRAMES+1:
        return enumerator_map

    qone = State()
    qstate.add_transition('1', qone, '1', 'R')
    enumerator_map = generate_enumerator(qone, rep + '1', depthmax, enumerator_map)

    return enumerator_map

def generate_states_and_transitions():
    qinit = State()
    qone = State()
    qtwo = State()
    qthree = State()
    qfour = State()
    
    # Set first index to empty letter to prevent underflow 
    qinit.add_transition('1', qinit, '_', 'R')
    qinit.add_transition('0', qone, '_', 'R')

    # Replace separator with # letter to separate enumerator from display
    qone.add_transition('0', qone, '0', 'R')
    qone.add_transition('1', qtwo, '#', 'R')
    
    # Set end of display to # to prevent overflow 
    qtwo.add_transition('0', qtwo, '0', 'R')
    qtwo.add_transition('_', qthree, '#', 'L')
    
    # Return to first index
    qthree.add_transition('0', qthree, '0', 'L')
    qthree.add_transition('1', qthree, '1', 'L')
    qthree.add_transition('#', qthree, '#', 'L')
    qthree.add_transition('_', qfour, '_', 'R')

    # Generate enumerator states
    enumerator_map = generate_enumerator(qfour)

    qback = State()

    for i, frame in enumerate(range(1, FRAMES+1, FSKIP)):
        with Image.open(BASE_PNG_PATH % (FSTART + frame)).resize((WIDTH, HEIGHT)) as im:
            px = im.load()

        qbegin = State()
        index = qbegin.name

        enumerator_map[i].add_transition('#', qbegin, '#', 'R')
        
        # One state per pixel for each frame branching from integer in enumerator
        for x in range(HEIGHT):
            for y in range(WIDTH):
                qnext = State()
                qlast = state_set[index]

                if px[y,x][0] < 125:
                    qlast.add_transition('0', qnext, '0', 'R')
                    qlast.add_transition('1', qnext, '0', 'R')
                else:
                    qlast.add_transition('0', qnext, '1', 'R')
                    qlast.add_transition('1', qnext, '1', 'R')

                index = qnext.name

        state_set[index].add_transition('#', qback, '#', 'L')

    qinc = State()

    # Return to start of tape to reread enumerator
    qback.add_transition('0', qback, '0', 'L')
    qback.add_transition('1', qback, '1', 'L')
    qback.add_transition('#', qinc, '#', 'L')

    # Add binary 1 to enumerator
    qinc.add_transition('0', qthree, '1', 'L')
    qinc.add_transition('1', qinc, '0', 'L')

    qaccept = State()
    qreject = State()

    # Final frame halts at accept state
    enumerator_map[FRAMES//FSKIP].add_transition('#', qaccept, '#', 'R')

    for state in state_set:
        for letter in ('0', '1', '_', '#'):
            if letter not in state.trfn:
                state.add_transition(letter, qreject, letter, 'R')

    return qinit, qaccept, qreject

def save_graph(graph, edge_labels, file_name):
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.circular_layout(graph)
    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, verticalalignment='bottom')

    plt.savefig(file_name, bbox_inches='tight')
    pylab.close()

def plot_tm(tm):
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')

    fig = plt.figure(1)
    fig.patch.set_facecolor((0.0, 0.0, 0.0))

    ax = fig.add_subplot(111)
    ax.set_box_aspect(1)

    steps = []

    while not (tm.accepted() or tm.rejected()):
        sig = tm.step()
        steps.append((tm.state, tm.head, tm.tape_printable()))
        if sig > 1:
            break

    text_color_code = {'0': 'white', '1': 'black', '_': 'black', '#': 'black'}
    color_code = {'0': 'black', '1': 'white', '_': 'grey', '#': 'grey'}

    # Compress steps for video (animates first 100 steps, then every 50)
    steps = steps[:100] + [steps[j] for j in range(101, len(steps), 50)]
    
    def animate(frame):
        ax.clear()
        ax.set_facecolor((0.0, 0.0, 0.0))
        ax.set_axis_off()

        plt.xlim([0, 60])
        plt.ylim([0, 60])

        state, head, tape = steps[frame]
        tape += '_' * 10

        for j in range(0, len(tape), WIDTH):
            for i in range(j, min(len(tape), j+WIDTH)):
                color = color_code[tape[i]]
                ec = 'white'
                if len(tape) - i <= 6:
                    hx = 0.5 * ((len(tape) - i)/6.0)
                    color = (hx, hx, hx)
                    ehx = 1.0 * ((len(tape) - i)/6.0)
                    ec = (ehx, ehx, ehx)
                square = Rectangle((0.5 + (i-j)*2, (HEIGHT - j//WIDTH)*3 + 3.5), 2, 2, color=color, ec=ec)
                rx, ry = square.get_xy()
                cx = rx + square.get_width()/2.0
                cy = ry + square.get_height()/2.0
                ax.add_patch(square)
                ax.annotate(tape[i], (cx, cy), color=text_color_code[tape[i]], fontsize=14, ha='center', va='center')
        for j in range(0, len(tape), WIDTH):
            for i in range(j, min(len(tape), j+WIDTH)):
                if i == head:
                    ax.add_patch(Rectangle((0.5 + (i-j)*2, (HEIGHT - j//WIDTH)*3 + 3.5), 2, 2, fc='none', lw=2.0, ec='yellow'))

        halt = ''
        if state == tm.accept:
            halt = ' - HALTED with ACCEPT STATE'
        if state == tm.reject:
            halt = ' - HALTED with REJECT STATE'

        ax.annotate('State: ' + str(state) + halt, (ENUMBITS-6, HEIGHT*3 + 12.5), color='white', fontsize=52, ha='left', va='center')
        adj, nletter, d = state.trfn[tape[head]]
        ax.annotate('%s → %s (%s, %s / %s)' % (str(state), str(adj), tape[head], nletter, d), (ENUMBITS-6, HEIGHT*3 + 9.5), color='yellow', fontsize=52, ha='left', va='center')

    ani = FuncAnimation(fig, animate, frames=len(steps), interval=1, repeat=False)

    '''
    plt.show()
    return
    '''
    
    Writer = writers['ffmpeg']
    writer = Writer(fps=24, metadata=dict(artist='Junferno'), bitrate=1800)

    ani.save('turing4.mp4', writer=writer, progress_callback=lambda i, n: print(f'Saving frame {i}/{n}', end='\r'))
    print('Animation saved')

    plt.close()

if __name__ == '__main__':
    inp = ('1' * (WIDTH-ENUMBITS-2)) + ('0' * (ENUMBITS+1)) + '1' + ('0' * (WIDTH * HEIGHT))
    qinit, qaccept, qreject = generate_states_and_transitions()

    '''
    state_graph = nx.DiGraph()
    state_graph.add_nodes_from(map(str, state_set))

    edge_labels = {}

    for state in state_set:
        for letter, tr in state.trfn.items():
            adj, nletter, d = tr
            state_graph.add_edge(str(state), str(adj))
            edge_labels[(str(state), str(adj))] = letter + '->' + str(nletter) + ',' + d

    save_graph(state_graph, edge_labels, 'graph2.pdf')
    '''

    tm = TuringMachine(qinit, qaccept, qreject, inp)
    plot_tm(tm)
