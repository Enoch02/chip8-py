import unittest
from emulator import Emulator

class TestEmulatorTimers(unittest.TestCase):
    def setUp(self):
        self.emulator = Emulator()
        # Mock beep to avoid needing actual audio device in headless test environment if possible
        # Actually pygame.mixer might fail if no audio device.
        
    def test_timer_decrement(self):
        self.emulator.delay_timer = 10
        self.emulator.sound_timer = 5
        
        self.emulator.decrement_timers()
        
        self.assertEqual(self.emulator.delay_timer, 9)
        self.assertEqual(self.emulator.sound_timer, 4)
        
    def test_timer_decrement_to_zero(self):
        self.emulator.delay_timer = 1
        self.emulator.sound_timer = 1
        
        self.emulator.decrement_timers()
        
        self.assertEqual(self.emulator.delay_timer, 0)
        self.assertEqual(self.emulator.sound_timer, 0)
        
        # Should stay at 0
        self.emulator.decrement_timers()
        self.assertEqual(self.emulator.delay_timer, 0)
        self.assertEqual(self.emulator.sound_timer, 0)

if __name__ == '__main__':
    unittest.main()
