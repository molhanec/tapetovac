
DEFAULT_FINAL_WIDTH = 1920
DEFAULT_FINAL_HEIGHT = 1200
DEFAULT_BOTTOM_PADDING = 2 * 30

DEFAULT_RESIZED_SUFFIX = "-resized"

import sys
from pathlib import Path

from PIL import Image
from send2trash import send2trash


def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        print_usage()
        sys.exit(-1)

    tapetovac = Tapetovac(trash_after_resize=(filename == '--all-and-trash'))
    if filename in ['--all', '--all-and-trash']:
        tapetovac.resize_all_images()
    else:
        tapetovac.resize_single_image(Path(filename))


def print_usage():
    print("""\
    Usage:
        tapetovac.py picture.jpg
      or
        tapetovac.py --all
        tapetovac.py --all-and-trash

      The second form will try to resize all found JPGs.
      It will skip any files ending with '{}' suffix or files where corresponding resized file exists.
      If --all-and-trash is specified, the original file is send to trash/recycle bin after succesfull conversion.
      """.format(DEFAULT_RESIZED_SUFFIX), file=sys.stderr)


class Tapetovac:

    def __init__(self, final_width=DEFAULT_FINAL_WIDTH, final_height=DEFAULT_FINAL_HEIGHT, *,
                 bottom_padding=DEFAULT_BOTTOM_PADDING, trash_after_resize=False, resized_suffix=DEFAULT_RESIZED_SUFFIX):
        self.final_width = final_width
        self.final_height = final_height
        self.image_net_height = final_height - bottom_padding
        self.trash_after_resize = trash_after_resize
        self.resized_suffix = resized_suffix

    def resize_all_images(self, path="."):
        print("Resizing all JPGs...")
        for filename in sorted(Path(path).glob("*.jpg")):
            self.resize_single_image(filename)

    def resize_single_image(self, filename):
        try:
            resized = self.real_resize_single_image(filename)
            if resized and self.trash_after_resize:
                send2trash(str(filename))
        except Exception as error:
            print(error)

    def real_resize_single_image(self, filename):
        if self.is_already_converted(filename): return False
        print("Resizing", filename)

        # Load source image
        src_image = Image.open(filename)

        # Create final canvas
        final_image = Image.new(src_image.mode, (self.final_width, self.final_height))

        # Calculate the width for required height
        width_for_required_height = int(src_image.width * (self.image_net_height / src_image.height))

        # If the width is over maximum width
        if width_for_required_height > self.final_width:
            # Scale the image to maximum width
            height_for_final_width = int(src_image.height * (self.final_width / src_image.width))
            resized_image = src_image.resize((self.final_width, height_for_final_width), Image.LANCZOS)

            # Put the rescaled image at vertical middle
            vertical_middle = (self.final_height - height_for_final_width) // 2
            final_image.paste(resized_image, (0, vertical_middle))

        else:
            # Scale the image to required height
            resized_image = src_image.resize((width_for_required_height, self.image_net_height), Image.LANCZOS)

            # Put the rescaled image at horizontal middle
            horizontal_middle = (self.final_width - width_for_required_height) // 2
            final_image.paste(resized_image, (horizontal_middle, 0))

        # Save the final image
        final_image.save(resized_image_filename(filename), quality=95, optimize=True)

        return True

    def is_already_converted(self, filename):
        return filename.stem.endswith(self.resized_suffix) or resized_image_filename(filename).exists()

    def resized_image_filename(self, filename):
        return filename.with_name(filename.stem + self.resized_suffix + ".jpg")


if __name__ == '__main__':
    main()
