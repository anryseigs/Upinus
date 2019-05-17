# -*- coding: utf-8 -*-
"""
Author: TruongNV
Created Date: 17/05/2019
Describe:
"""
import re
import unittest

pointer_value = {
    0: "North",
    1: "East",
    2: "South",
    3: "West"
}


class UniBot(object):
    @staticmethod
    def parse_step(step_str):
        # validate input
        if not isinstance(step_str, str):
            raise ValueError("step_str should be string type, not {}".format(type(str)))

        # init setting
        pointer_facing = 0
        count_w = -1    # number W in for loop
        real_position = {
            "North": 0,
            "East": 0,
            "South": 0,
            "West": 0
        }

        # get all numberic value
        step = re.findall('\d+', step_str)
        step = list(map(int, step))

        for i in step_str:
            if i == "R":
                pointer_facing = (pointer_facing + 1) % 4
            if i == "L":
                pointer_facing = (pointer_facing - 1) % 4
            if i == "W":
                count_w += 1
                facing_direction = pointer_value[pointer_facing]
                last_poisition = real_position[facing_direction]
                now_poisition = last_poisition + step[count_w]
                real_position.update({facing_direction: now_poisition})

        # convert to {X:Y}
        x_value = real_position["East"] - real_position["West"]
        y_value = real_position["North"] - real_position["South"]
        real_direation = pointer_value[pointer_facing]

        # report
        report = "X: {}, Y: {}, Direction: {}".format(x_value, y_value, real_direation)
        print(report)

        return report


class Test001(unittest.TestCase):
    def test_insertion_sort(self):
        data_input = "RW15RW1"
        data_output = "X: 15, Y: -1, Direction: South"
        self.assertEqual(UniBot.parse_step(data_input), data_output)


if __name__ == '__main__':
    test_data = [
        "W5RW5RW2RW1R",
        "RRW11RLLW19RRW12LW1",
        "LLW100W50RW200W10",
        "LLLLLW99RRRRRW88LLLRL",
        "W55555RW555555W444444W1"
    ]
    for data in test_data:
        UniBot.parse_step(data)
