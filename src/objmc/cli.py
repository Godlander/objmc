from argparse import ArgumentParser

from .models import Args


class ArgumentParserError(Exception):
    ...


class ThrowingArgumentParser(ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


def create_parser():
    parser = ThrowingArgumentParser(
        description=(
            "python script to convert .OBJ files into Minecraft,"
            " rendering them in game with a core shader.\n"
            "Github: https://github.com/Godlander/objmc"
        )
    )
    args = Args()

    parser.add_argument(
        "--objs",
        help="List of object files",
        nargs="*",
        default=args.objs,
    )
    parser.add_argument(
        "--texs",
        help="Specify a texture file",
        nargs="*",
        default=args.texs,
    )
    parser.add_argument(
        "--out",
        type=str,
        help="Output json and png",
        nargs=2,
        default=args.out,
    )
    parser.add_argument(
        "--offset",
        type=float,
        help="Offset of model in xyz",
        nargs=3,
        default=args.offset,
    )
    parser.add_argument(
        "--scale",
        type=float,
        help="Scale of model",
        default=args.scale,
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Duration of the animation in ticks",
        default=args.duration,
    )
    parser.add_argument(
        "--easing",
        type=int,
        help="Animation easing, 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier",
        default=args.easing,
    )
    parser.add_argument(
        "--interpolation",
        type=int,
        help="Texture interpolation, 0: none, 1: fade",
        default=args.interpolation,
    )
    parser.add_argument(
        "--colorbehavior",
        type=str,
        help=(
            "Item color overlay behavior, \"xyz\": rotate"
            ", 't': animation time offset, 'o': overlay hue"
        ),
        default=args.colorbehavior,
    )
    parser.add_argument(
        "--autorotate",
        type=int,
        help=(
            "Attempt to estimate rotation with Normals"
            "0: off, 1: yaw, 2: pitch, 3: both"
        ),
        default=args.autorotate,
    )
    parser.add_argument(
        "--autoplay",
        action="store_true",
        dest="autoplay",
        help='Always interpolate animation, colorbehavior="ttt" overrides this',
        default=args.autoplay,
    )
    parser.add_argument(
        "--visibility",
        type=int,
        help="Determines where the model is visible",
        default=args.visibility,
    )
    parser.add_argument(
        "--flipuv",
        action="store_true",
        dest="flipuv",
        help="Invert the texture to compensate for flipped UV",
    )
    parser.add_argument(
        "--noshadow",
        action="store_true",
        dest="noshadow",
        help="Disable shadows from face normals",
    )
    parser.add_argument(
        "--nopow",
        action="store_true",
        dest="nopow",
        help="Disable power of two textures",
    )
    parser.add_argument(
        "--join", nargs="*", dest="join", help="Joins multiple json models into one"
    )

    return parser


def args():
    parser = create_parser()
    return parser.parse_args(namespace=Args())
