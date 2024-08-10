import sys
import pygame
from constants import (
    FONT_START_ADDRESS,
    FONT_SET,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PROGRAM_START_ADDRESS,
)


class Emulator:

    def __init__(self) -> None:
        pygame.init()
        self.memory = [0] * 4096
        self.variable_register = [0] * 12
        self.index_register = 0
        self.program_counter = PROGRAM_START_ADDRESS
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.carry_flag = 0
        self.screen_array = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]
        self.memory[FONT_START_ADDRESS : FONT_START_ADDRESS + len(FONT_SET)] = FONT_SET
        self.draw_flag = False

    def modify_memory(self, location: int, new_content: int):
        if location <= 4096:
            self.memory[location] = new_content
        else:
            raise IndexError

    def modify_var_register(self, location: int, new_content: int):
        if location <= 12:
            self.variable_register[location] = new_content
        else:
            raise IndexError

    def access_memory(self, location: int):
        if location <= 4096:
            return self.memory[location]
        else:
            raise IndexError

    def access_var_reg(self, location: int):
        if location <= 12:
            return self.variable_register[location]
        else:
            raise IndexError

    def load_program(self, filename: str):
        with open(filename, "rb") as file:
            program_data = file.read()
            # Check if program data fits in memory
            if len(program_data) + PROGRAM_START_ADDRESS > len(self.memory):
                raise ValueError("Program is too large to fit in memory.")
            # Load program data into memory starting at 0x200
            self.memory[
                PROGRAM_START_ADDRESS : PROGRAM_START_ADDRESS + len(program_data)
            ] = program_data

    def run(self, filename: str):
        self.load_program(filename)

        while True:
            for _ in range(10):
                self.decode_and_execute(instruction=self.fetch())

            if (self.draw_flag):
                self.display()
                self.draw_flag = False
            
            self.handle_inputs()

    def fetch(self) -> int:
        first_opcode = self.access_memory(location=self.program_counter)
        second_opcode = self.access_memory(location=self.program_counter + 1)
        instruction = (first_opcode << 8) | second_opcode

        self.program_counter += 2

        return instruction

    def decode_and_execute(self, instruction: int):
        opcode = (instruction & 0xF000)
        x = (instruction & 0xF00) >> 8
        y = (instruction & 0x00F0) >> 4
        n = instruction & 0x000F
        nn = instruction & 0x00FF
        nnn = instruction & 0x0FFF

        # clear screen
        if instruction == 0x00E0:
            # self.screen.fill((0, 0, 0))
            print("Clear")
            self.screen_array = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]

        # 1NNN - jump to nnn
        elif opcode == 0x1000:
            self.program_counter = nnn

        # 2NNN - call subroutine
        elif opcode == 0x2000:
            self.stack.append(self.program_counter)
            self.program_counter = nnn

        # 00EE - return from subroutine
        elif instruction == 0x00EE:
            if self.stack:
                self.program_counter = self.stack.pop()

        # 6XNN - set register vx
        elif opcode == 0x6000:
            # self.variable_register[x] = nn
            self.modify_var_register(location=x, new_content=nn)

        # 7XNN - add nn to vx
        elif opcode == 0x7000:
            # self.variable_register[x] = (self.variable_register[x] + nn) & 0xFF
            self.modify_var_register(
                location=x, new_content=(self.variable_register[x] + nn) & 0xFF
            )

        # ANNN - set index register to i
        elif opcode == 0xA000:
            self.index_register = nnn

        # DXYN - display / draw
        elif opcode == 0xD000:
            x_coord = self.access_var_reg(x)
            y_coord = self.access_var_reg(y)

            self.carry_flag = 0

            for row in range(n):
                pixel = self.access_memory(self.index_register + row)

                for col in range(8):
                    if (pixel & (0x80 >> col)) != 0:
                        screen_y = (y_coord + row) % 32
                        screen_x = (x_coord + col) % 64

                        if self.screen_array[screen_y][screen_x] == 1:
                            self.carry_flag = 1

                        self.screen_array[screen_y][screen_x] ^= 1

            self.draw_flag = True

        else:
            print(f"Unknown opcode: {opcode:04X}")

    def display(self):
        clock = pygame.time.Clock()
        internal_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        scale_factor = 10
        display_width, display_height = (
            SCREEN_WIDTH * scale_factor,
            SCREEN_HEIGHT * scale_factor,
        )
        pixels = pygame.surfarray.pixels3d(internal_surface)

        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                try:
                    if self.screen_array[y][x] == 0:
                        pixels[x, y] = (255, 255, 255)
                    else:
                        pixels[x, y] = (0, 0, 0)
                except IndexError:
                    print(f"IndexError: Tried to access ({x}, {y})")

        scaled_surface = pygame.transform.scale(
            internal_surface, (display_width, display_height)
        )
        screen = pygame.display.set_mode((display_width, display_height))
        screen.blit(scaled_surface, (0, 0))
        clock.tick(60)  # Limit frame rate to 60 FPS
        pygame.display.flip()

    def handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                ...


# TODO: remove
emulator = Emulator()
#emulator.run(filename="test_opcode.ch8")
#emulator.run(filename="Zero Demo [zeroZshadow, 2007].ch8")
emulator.run(filename="IBM Logo.ch8")
