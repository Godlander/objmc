import re
import unittest
from math import atan2, cos, pi, sin
from pathlib import Path


SHADER_PATH = (
    Path(__file__).parents[1]
    / "objmc"
    / "assets"
    / "minecraft"
    / "shaders"
    / "include"
    / "objmc_main.glsl"
)
GENERATOR_PATH = Path(__file__).parents[1] / "objmc.py"


class AutorotateShaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shader = SHADER_PATH.read_text(encoding="utf-8")
        cls.generator = GENERATOR_PATH.read_text(encoding="utf-8")
        match = re.search(
            r"if \(any\(greaterThan\(autorotate,vec2\(0\)\)\)\) \{(?P<body>.*?)\n\s*\}",
            cls.shader,
            re.DOTALL,
        )
        if match is None:
            raise AssertionError("autorotate shader block was not found")
        cls.autorotate_body = match.group("body")

        decoder = re.search(
            r"vec2 autorotate = vec2\(getb\(t\[6\]\.r, (\d), 1\), "
            r"getb\(t\[6\]\.r, (\d), 1\)\);",
            cls.shader,
        )
        if decoder is None:
            raise AssertionError("autorotate metadata decoder was not found")
        cls.pitch_bit, cls.yaw_bit = map(int, decoder.groups())

        encoder = re.search(r"autorotate << (\d)", cls.generator)
        if encoder is None:
            raise AssertionError("autorotate metadata encoder was not found")
        cls.encoder_shift = int(encoder.group(1))

    @classmethod
    def decode_mode(cls, mode):
        metadata = mode << cls.encoder_shift
        return (
            (metadata >> cls.pitch_bit) & 1,
            (metadata >> cls.yaw_bit) & 1,
        )

    def test_metadata_modes_decode_to_expected_axis_masks(self):
        expected = {
            0: (0, 0),
            1: (0, 1),
            2: (1, 0),
            3: (1, 1),
        }
        self.assertEqual(
            {mode: self.decode_mode(mode) for mode in expected},
            expected,
        )

    def test_axis_masks_lock_the_unselected_angle(self):
        def tracked_angles(mode, pitch, yaw):
            pitch_mask, yaw_mask = self.decode_mode(mode)
            return pitch * pitch_mask, yaw * yaw_mask

        self.assertEqual(tracked_angles(1, 0.25, 1.0), tracked_angles(1, 0.75, 1.0))
        self.assertEqual(tracked_angles(2, 0.5, 0.25), tracked_angles(2, 0.5, 1.25))
        self.assertNotEqual(tracked_angles(3, 0.25, 1.0), tracked_angles(3, 0.75, 1.0))

    def test_autorotate_derives_facing_from_the_quad_basis(self):
        self.assertRegex(
            self.autorotate_body,
            r"vec3 facing\s*=\s*cross\(vPos2,\s*vPos1\)",
        )
        self.assertNotRegex(self.autorotate_body, r"\bNormal\b")

    def test_autorotate_masks_pitch_and_yaw_independently(self):
        self.assertRegex(
            self.autorotate_body,
            r"pitch\s*\*\s*autorotate\.x",
        )
        self.assertRegex(
            self.autorotate_body,
            r"yaw\s*\*\s*autorotate\.y",
        )

    def test_autorotate_preserves_color_rotation(self):
        self.assertRegex(
            self.autorotate_body,
            r"rotate\(trackedRotation\s*\+\s*rotation\)",
        )

    def test_autorotate_preserves_entity_scale(self):
        self.assertRegex(
            self.autorotate_body,
            r"entityScale\s*\*\s*rotate\(",
        )

    def test_off_and_autorotate_apply_the_same_entity_scale(self):
        self.assertRegex(
            self.shader,
            r"float\s+entityScale\s*=\s*distance\(vPos0,\s*vPos1\);"
            r"[\s\S]*?if\s*\(any\(greaterThan\(autorotate,vec2\(0\)\)\)\)"
            r"[\s\S]*?posoffset\s*=\s*entityScale\s*\*\s*"
            r"rotate\(trackedRotation\s*\+\s*rotation\)\s*\*\s*posoffset;"
            r"[\s\S]*?else\s*\{\s*posoffset\s*=\s*entityScale\s*\*\s*"
            r"rotate\(rotation\)\s*\*\s*posoffset;",
        )

    def test_vertical_facing_recovers_yaw_from_the_quad_axis(self):
        self.assertRegex(
            self.autorotate_body,
            r"float\s+yaw\s*=\s*horizontalLength\s*>\s*0\.000001\s*"
            r"\?\s*-atan\(facing\.x,\s*facing\.z\)\s*"
            r":\s*atan\(vPos2\.z,\s*vPos2\.x\)",
        )

        def extract_yaw(pitch, yaw):
            facing = (
                -cos(pitch) * sin(yaw),
                -sin(pitch),
                cos(pitch) * cos(yaw),
            )
            right = (cos(yaw), 0, sin(yaw))
            horizontal_length = (facing[0] ** 2 + facing[2] ** 2) ** 0.5
            if horizontal_length > 0.000001:
                return -atan2(facing[0], facing[2])
            return atan2(right[2], right[0])

        for pitch in (-pi / 2, pi / 2):
            for yaw in (-2.4, -0.75, 0.0, 1.2, 2.8):
                self.assertAlmostEqual(extract_yaw(pitch, yaw), yaw)


if __name__ == "__main__":
    unittest.main()
