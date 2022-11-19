import sys, pygame

from game_objects.cpu import Cpu
from game_objects.io_queue import IoQueue
from game_objects.label import Label
from game_objects.process import Process
from game_objects.process_slot import ProcessSlot
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self._game_objects = []

        self.setup()
        self.main_loop()

    def setup(self):
        size = width, height = 1024, 768
        self._screen = pygame.display.set_mode(size)

        cpu_list = [
            Cpu(1),
            Cpu(2),
            Cpu(3),
            Cpu(4),
        ]
        for i, cpu in enumerate(cpu_list):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.setXY(x, y)
        self._game_objects.extend(cpu_list)

        io_queue = IoQueue()
        io_queue.view.setXY(50, 10)
        self._game_objects.append(io_queue)       

        processes_label = Label('Processes:')
        processes_label.view.setXY(50, 120)
        processes_label.font = FONT_ARIAL_20
        self._game_objects.append(processes_label)

        process_slots = []
        for row in range(7):
            for column in range(6):
                process_slot = ProcessSlot()          
                x = 50 + column * process_slot.view.width + column * 5
                y = 150 + row * process_slot.view.height + row * 5
                process_slot.view.setXY(x, y)
                process_slots.append(process_slot)
        self._game_objects.extend(process_slots)

        terminated_processes_label = Label('Terminated By User :')
        terminated_processes_label.view.setXY(50, 644)
        terminated_processes_label.font = FONT_ARIAL_20
        self._game_objects.append(terminated_processes_label)

        terminated_process_slots = []
        for i in range(5):
            process_slot = ProcessSlot()
            x = 50 + i * process_slot.view.width + i * 5
            y = 644 + terminated_processes_label.view.height + 5
            process_slot.view.setXY(x, y)
            terminated_process_slots.append(process_slot)
        self._game_objects.extend(terminated_process_slots)

        for i in range(10):
            pid = i + 1
            process = Process(pid, cpu_list, process_slots, terminated_process_slots, io_queue)
            process_slot = process_slots[i]
            process_slot.process = process
            process.view.setXY(process_slot.view.x, process_slot.view.y)
            self._game_objects.append(process)

    def main_loop(self):
        while True:
            self.update(pygame.time.get_ticks())
            self.render()        

    def update(self, current_time):
        events = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1):
                    events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))

        for game_object in self._game_objects:
            game_object.update(current_time, events)

    def render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()