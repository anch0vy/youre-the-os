import asyncio
import sys
from os import path
from random import random

import pygame

from game_info import TITLE
from game_objects.page import Page
from game_objects.process import Process
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
from scene_manager import scene_manager
from scenes.game import Game
from scenes.how_to_play import HowToPlay
from scenes.main_menu import MainMenu
from window_size import WINDOW_SIZE

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(WINDOW_SIZE)

icon = pygame.image.load(path.join("assets", "icon.png"))
pygame.display.set_caption(TITLE)
pygame.display.set_icon(icon)

scenes = {}

game_scene = Game(screen, scenes)
scenes["game"] = game_scene

main_menu_scene = MainMenu(screen, scenes)
scenes["main_menu"] = main_menu_scene

how_to_play_scene = HowToPlay(screen, scenes)
scenes["how_to_play"] = how_to_play_scene

main_menu_scene.start()

clock = pygame.time.Clock()

FPS = 60


def handle_process():
    stats = game_scene.process_manager.get_current_stats()
    in_use_cpu_number = sum(stats["active_process_count_by_starvation_level"])
    cpu_number = len(game_scene.process_manager.cpu_list)

    processes: list[Process] = [
        proc
        for proc in game_scene.process_manager.children
        if isinstance(proc, Process)
    ]
    tmpProcesses: list[Process] = []
    for process in processes:
        if (
            process.is_blocked
            or process.has_ended
            or (process.starvation_level == 0 and in_use_cpu_number == cpu_number)
        ):
            process._yield_cpu()
            continue

        tmpProcesses.append(process)

    for process in sorted(
        tmpProcesses, key=lambda proc: proc.starvation_level, reverse=True
    ):
        process._use_cpu()


def handle_io():
    io_queue = game_scene.process_manager.io_queue
    if io_queue is None:
        return

    io_queue._onClick()


def handle_page():
    page_manager = game_scene.page_manager
    if page_manager is None:
        return

    pages: list[Page] = [
        page for page in page_manager.children if isinstance(page, Page)
    ]
    for page in pages:
        if page.in_use and page.in_swap:
            page._on_click()
        elif not page.in_use and not page.in_swap:
            page._on_click()


def my_callback():
    if game_scene.process_manager is None:
        return

    handle_process()
    handle_io()
    handle_page()


async def main():
    mouse_down = False
    shift_down = False
    number_keys = list(map(str, range(0, 10)))

    while True:
        if random() < 0.1:
            my_callback()

        events = []

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
                events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))
            elif event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key).endswith('shift'):
                    shift_down = True
            elif event.type == pygame.KEYUP:
                if pygame.key.name(event.key).endswith('shift'):
                    shift_down = False
                events.append(GameEvent(GameEventType.KEY_UP, { 'key': pygame.key.name(event.key), 'shift': shift_down }))   
            elif event.type == pygame.MOUSEMOTION and mouse_down:
                events.append(GameEvent(GameEventType.MOUSE_LEFT_DRAG, { 'position': event.pos }))
                    
        scene_manager.current_scene.update(pygame.time.get_ticks(), events)
        scene_manager.current_scene.render()

        clock.tick(FPS)

        await asyncio.sleep(0)


asyncio.run(main())
