import math
import time

class Agent:
    def __init__(self, name, team, index):
        self.index = index

        # Contants
        self.dodge_time = 0.2

        # Controller inputs
        self.throttle = 0
        self.steer = 0
        self.pitch = 0
        self.yaw = 0
        self.roll = 0
        self.boost = False
        self.jump = False
        self.powerslide = False

        # Game values
        self.bot_pos = None
        self.bot_rot = None
        self.ball_rot = None
        self.bot_yaw = None

        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0

        self.dodge_interval = 0


    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.degrees(math.atan2(target_y - self.bot_pos.Y,
                                                               target_x - self.bot_pos.X))

        distance_bot_to_ball = math.sqrt(self.bot_pos.X**2 + self.bot_pos.Y**2)

        if distance_bot_to_ball > 5000:
            self.boost = True
        else:
            self.boost = False

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        # Correct the values
        if angle_front_to_target < -180:
            angle_front_to_target += 360
        if angle_front_to_target > 180:
            angle_front_to_target -= 360

        if angle_front_to_target < -10:
            # If the target is more than 10 degrees right from the centre, steer left
            self.steer = -1
        elif angle_front_to_target > 10:
            # If the target is more than 10 degrees left from the centre, steer right
            self.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.steer = 0

    def check_for_dodge(self, target_x, target_y):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.aim(target_x, target_y)
            self.jump = True
            self.pitch = -1

        if self.on_second_jump:
            self.on_second_jump = False
            self.should_dodge = False
        else:
            self.on_second_jump = True
            self.next_dodge_time = time.time() + self.dodge_time

    def get_output_vector(self, values):
        # Update game data variables
        self.bot_pos = values.gamecars[self.index].Location
        self.bot_rot = values.gamecars[self.index].Rotation
        self.ball_pos = values.gameball.Location

        # Get car's yaw and convert from Unreal Rotator units to degrees
        self.bot_yaw = abs(self.bot_rot.Yaw) % 65536 / 65536 * 360
        if self.bot_rot.Yaw < 0:
            self.bot_yaw *= -1

        if self.dodge_interval < time.time():
            self.should_dodge = True
            self.dodge_interval = time.time() + 3

        # This makes self.jump be only active for 1 frame
        self.jump = False

        self.check_for_dodge(self.ball_pos.X, self.ball_pos.Y)

        self.aim(self.ball_pos.X, self.ball_pos.Y)

        return [self.throttle, self.steer,
                self.pitch, self.yaw, self.roll,
                self.jump, self.boost, self.powerslide]