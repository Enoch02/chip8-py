import pathlib
import random

import pygame
from constants import (
    FONT_SET,
    FONT_START_ADDRESS,
    PROGRAM_START_ADDRESS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class Emulator:

    def __init__(self, set_vx_to_vy=False) -> None:
        self.screen = None
        self.pixels = None
        self.display_height = None
        self.display_width = None
        self.internal_surface = None
        self.memory = [0] * 4096
        self.variable_register = [0] * 16
        self.index_register = 0
        self.program_counter = PROGRAM_START_ADDRESS
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.carry_flag = 0
        self.screen_array = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]
        self.memory[FONT_START_ADDRESS : FONT_START_ADDRESS + len(FONT_SET)] = FONT_SET
        self.draw_flag = False
        self.key_states = [0] * 16  # 1 is pressed state

        self.set_vx_to_vy = set_vx_to_vy
        self.running = True
        self.pause_execution = False

        pygame.init()
        self.beep = pygame.mixer.Sound("bleep-41488.mp3")
        self.clock = pygame.time.Clock()

    def stop(self):
        if self.running:
            self.running = False
        self.draw_flag = False

        # clear loaded content
        self.memory = [0] * 4096
        self.variable_register = [0] * 16
        self.index_register = 0
        self.program_counter = PROGRAM_START_ADDRESS
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.carry_flag = 0
        self.screen_array = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]
        self.key_states = [0] * 16  # 1 is pressed state

        pygame.display.quit()
        pygame.quit()

    def modify_memory(self, location: int, new_content: int):
        if location <= 4096:
            self.memory[location] = new_content
        else:
            raise IndexError

    def modify_var_register(self, location: int, new_content: int):
        if location <= 16:
            self.variable_register[location] = new_content
        else:
            raise IndexError

    def access_memory(self, location: int):
        if location <= 4096:
            return self.memory[location]
        else:
            raise IndexError

    def access_var_reg(self, location: int):
        if location <= 16:
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

    def run(self, filename: pathlib.Path):
        self.load_program(str(filename))
        self.setup_display()
        pygame.display.set_caption(filename.name)

        while self.running:
            if not self.pause_execution:
                for _ in range(30):  # TODO: make configurable
                    self.decode_and_execute(instruction=self.fetch())

            if self.sound_timer > 0:
                self.beep.play()

            if self.sound_timer == 0:
                self.beep.stop()

            self.handle_inputs()

            # TODO: not working fine
            if self.delay_timer > 0:
                self.delay_timer -= 1
            if self.sound_timer > 0:
                self.sound_timer -= 1

            if self.draw_flag:
                self.display()
                self.draw_flag = False

            self.clock.tick(60)

        self.stop()

    def fetch(self) -> int:
        first_opcode = self.access_memory(location=self.program_counter)
        second_opcode = self.access_memory(location=self.program_counter + 1)
        instruction = (first_opcode << 8) | second_opcode

        self.program_counter += 2

        return instruction

    def decode_and_execute(self, instruction: int):
        opcode = instruction & 0xF000
        x = (instruction & 0xF00) >> 8
        y = (instruction & 0x00F0) >> 4
        n = instruction & 0x000F
        nn = instruction & 0x00FF
        nnn = instruction & 0x0FFF

        # clear screen
        if instruction == 0x00E0:
            self.screen_array = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]

        # 1NNN - jump to nnn
        elif opcode == 0x1000:
            self.program_counter = nnn

        # 2NNN - call subroutine
        elif opcode == 0x2000:
            self.stack.append(self.program_counter)
            self.program_counter = nnn

        # 3XNN - skip one instruction if the value in vx is equal to NN
        elif opcode == 0x3000:
            if self.access_var_reg(location=x) == nn:
                self.program_counter += 2

        # 4XNN - skip one instruction if the value in vx is not equal to NN
        elif opcode == 0x4000:
            if self.access_var_reg(location=x) != nn:
                self.program_counter += 2

        # 5XY0 - skip if vx and vy are equal
        elif opcode == 0x5000:
            if self.access_var_reg(location=x) == self.access_var_reg(location=y):
                self.program_counter += 2

        # 9XY0 - skip if vx and vy are not equal
        elif opcode == 0x9000:
            if self.access_var_reg(location=x) != self.access_var_reg(location=y):
                self.program_counter += 2

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

        # 8xxx instructions:
        elif opcode == 0x8000:
            last_nibble = instruction & 0x000F

            # 8XY0 - set vx to the value of vy
            if last_nibble == 0x0:
                self.modify_var_register(
                    location=x, new_content=self.access_var_reg(location=y)
                )

            # 8XY1 - vx is set to the binary OR of vx and vy
            if last_nibble == 0x1:
                result = self.access_var_reg(x) | self.access_var_reg(y)
                self.modify_var_register(location=x, new_content=result)

            # 8XY2 - vx is set to the binary AND of vx and vy
            if last_nibble == 0x2:
                result = self.access_var_reg(x) & self.access_var_reg(y)
                self.modify_var_register(location=x, new_content=result)

            # 8XY3 - vx is set to the binary OR of vx and vy
            if last_nibble == 0x3:
                result = self.access_var_reg(x) ^ self.access_var_reg(y)
                self.modify_var_register(location=x, new_content=result)

            # 8XY4 - vx is set to the value of vx plus vy
            if last_nibble == 0x4:
                result = self.access_var_reg(x) + self.access_var_reg(y)
                self.carry_flag = 1 if result > 0xFF else 0
                self.modify_var_register(location=x, new_content=result & 0xFF)

            # 8XY5 - vx is set to the value of vx minus vy
            if last_nibble == 0x5:
                result = self.access_var_reg(x) - self.access_var_reg(y)
                self.carry_flag = (
                    1 if self.access_var_reg(x) >= self.access_var_reg(y) else 0
                )
                self.modify_var_register(location=x, new_content=result & 0xFF)

            # 8XY7 - vx is set to the value of vy minus vx
            if last_nibble == 0x7:
                result = self.access_var_reg(y) - self.access_var_reg(x)
                self.carry_flag = (
                    1 if self.access_var_reg(y) >= self.access_var_reg(x) else 0
                )
                self.modify_var_register(location=x, new_content=result)

            # 8XY6 - shift vy 1 bit to the right and store in vx #TODO: wrong impl
            if last_nibble == 0x6:
                if self.set_vx_to_vy:
                    self.modify_var_register(
                        location=x, new_content=self.access_var_reg(y)
                    )

                shifted_out_bit = self.access_var_reg(x) & 0x01
                self.carry_flag = shifted_out_bit
                self.modify_var_register(
                    location=x, new_content=self.access_var_reg(x) >> 1
                )

            # 8XYE - shift vx to the left
            if last_nibble == 0xE:
                shifted_out_bit_e = self.access_var_reg(x) & 0x80 >> 7
                self.carry_flag = shifted_out_bit_e

                shifted_e = (self.access_var_reg(y) << 1) & 0xFF
                self.modify_var_register(location=x, new_content=shifted_e)

        # ANNN - set index register to i
        elif opcode == 0xA000:
            self.index_register = nnn

        # BNNN - jump with offset (v0)
        elif opcode == 0xB000:
            self.program_counter = nnn + self.access_var_reg(0)

        # CXNN - generate a random number
        elif opcode == 0xC000:
            random_num = random.randint(0, 255)
            self.modify_var_register(location=x, new_content=random_num & nn)

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

        elif opcode == 0xE000:
            last_byte = instruction & 0x00FF

            # EX9E - skip if key vx is pressed
            if last_byte == 0x9E:
                if self.key_states[self.access_var_reg(x)] == 1:
                    self.program_counter += 2

            # EXA1 - skip if key vx is not pressed
            if last_byte == 0xA1:
                if self.key_states[self.access_var_reg(x)] == 0:
                    self.program_counter += 2

        elif opcode == 0xF000:
            last_byte = instruction & 0x00FF

            # FX07 - set vx to the current value of the delay timer
            if last_byte == 0x07:
                self.modify_var_register(location=x, new_content=self.delay_timer)

            elif last_byte == 0x15:
                self.delay_timer = self.access_var_reg(x)

            elif last_byte == 0x18:
                self.sound_timer = self.access_var_reg(x)

            # FX1E - add to index
            elif last_byte == 0x1E:
                self.index_register = (
                    self.index_register + self.access_var_reg(x) & 0xFFF
                )

            # FX0A - get key
            elif last_byte == 0x0A:
                for index, key_state in enumerate(self.key_states):
                    if key_state == 1:
                        self.modify_var_register(location=x, new_content=index)
                        break
                else:
                    self.program_counter -= 2

            # FX29 - font character
            elif last_byte == 0x29:
                self.index_register = FONT_START_ADDRESS + self.access_var_reg(x) * 5

            # FX33
            elif last_byte == 0x33:
                vx = self.access_var_reg(x)
                hundreds = (vx // 100) % 10
                tens = (vx // 10) % 10
                ones = vx % 10

                self.modify_memory(location=self.index_register, new_content=hundreds)
                self.modify_memory(location=self.index_register + 1, new_content=tens)
                self.modify_memory(location=self.index_register + 2, new_content=ones)

            # FX55 - store registers to memory
            elif last_byte == 0x55:
                for i in range(x + 1):
                    self.modify_memory(
                        location=self.index_register + i,
                        new_content=self.access_var_reg(i),
                    )
                self.index_register = x + 1

            # FX65 - load registers to memory
            elif last_byte == 0x65:
                for i in range(x + 1):
                    self.modify_var_register(
                        location=i,
                        new_content=self.access_memory(self.index_register + i),
                    )
                self.index_register = x + 1

        else:
            print(f"Unknown opcode: {opcode:04X}")

    def setup_display(self):
        self.internal_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        scale_factor = 15
        self.display_width, self.display_height = (
            SCREEN_WIDTH * scale_factor,
            SCREEN_HEIGHT * scale_factor,
        )
        self.pixels = pygame.surfarray.pixels3d(self.internal_surface)
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))

    def display(self):
        self.screen.fill((255, 255, 255))
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                try:
                    if self.screen_array[y][x] == 0:
                        self.pixels[x, y] = (0, 0, 0)
                    else:
                        self.pixels[x, y] = (255, 255, 255)
                except IndexError:
                    print(f"IndexError: Tried to access ({x}, {y})")

        scaled_surface = pygame.transform.scale(
            self.internal_surface, (self.display_width, self.display_height)
        )
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.key_states[0] = 1
                if event.key == pygame.K_2:
                    self.key_states[1] = 1
                if event.key == pygame.K_3:
                    self.key_states[2] = 1
                if event.key == pygame.K_4:
                    self.key_states[3] = 1
                if event.key == pygame.K_q:
                    self.key_states[4] = 1
                if event.key == pygame.K_w:
                    self.key_states[5] = 1
                if event.key == pygame.K_e:
                    self.key_states[6] = 1
                if event.key == pygame.K_r:
                    self.key_states[7] = 1
                if event.key == pygame.K_a:
                    self.key_states[8] = 1
                if event.key == pygame.K_s:
                    self.key_states[9] = 1
                if event.key == pygame.K_d:
                    self.key_states[10] = 1
                if event.key == pygame.K_f:
                    self.key_states[11] = 1
                if event.key == pygame.K_z:
                    self.key_states[12] = 1
                if event.key == pygame.K_x:
                    self.key_states[13] = 1
                if event.key == pygame.K_c:
                    self.key_states[14] = 1
                if event.key == pygame.K_v:
                    self.key_states[15] = 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    self.key_states[0] = 0
                if event.key == pygame.K_2:
                    self.key_states[1] = 0
                if event.key == pygame.K_3:
                    self.key_states[2] = 0
                if event.key == pygame.K_4:
                    self.key_states[3] = 0
                if event.key == pygame.K_q:
                    self.key_states[4] = 0
                if event.key == pygame.K_w:
                    self.key_states[5] = 0
                if event.key == pygame.K_e:
                    self.key_states[6] = 0
                if event.key == pygame.K_r:
                    self.key_states[7] = 0
                if event.key == pygame.K_a:
                    self.key_states[8] = 0
                if event.key == pygame.K_s:
                    self.key_states[9] = 0
                if event.key == pygame.K_d:
                    self.key_states[10] = 0
                if event.key == pygame.K_f:
                    self.key_states[11] = 0
                if event.key == pygame.K_z:
                    self.key_states[12] = 0
                if event.key == pygame.K_x:
                    self.key_states[13] = 0
                if event.key == pygame.K_c:
                    self.key_states[14] = 0
                if event.key == pygame.K_v:
                    self.key_states[15] = 0
