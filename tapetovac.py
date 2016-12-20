
FINAL_WIDTH = 1920
FINAL_HEIGHT = 1200
BOTTOM_PADDING = 2 * 30
IMAGE_NET_HEIGHT = FINAL_HEIGHT - BOTTOM_PADDING

RESIZED_SUFFIX = "-resized"

from pathlib import Path
import sys

from PIL import Image


def main():
    filename = check_arguments_or_print_usage_and_exit()
    if filename == '--all':
        resize_all_images()
    else:
        resize_single_image(Path(filename))


def check_arguments_or_print_usage_and_exit():
    if len(sys.argv) != 2:
        print("""\
    Usage:
        tapetovac.py picture.jpg
      or
        tapetovac.py --all

      The second form will try to resize all found JPGs.
      It will skip any files ending with '{}' suffix or files where corresponding resized file exists.
      """.format(RESIZED_SUFFIX), file=sys.stderr)
        sys.exit(-1)
    return sys.argv[1]


def resize_all_images():
    print("Resizing all JPGs...")
    for filename in sorted(Path('.').glob("*.jpg")):
        resize_single_image(filename)


def resize_single_image(filename):
    try:
        real_resize_single_image(filename)
    except Exception as error:
        print(error)


def real_resize_single_image(filename):
    if is_already_converted(filename): return
    print("Resizing", filename)

    # Load source image
    src_image = Image.open(filename)

    # Create final canvas
    final_image = Image.new(src_image.mode, (FINAL_WIDTH, FINAL_HEIGHT))

    # Calculate the width for required height
    width_for_required_height = int(src_image.width * (IMAGE_NET_HEIGHT / src_image.height))

    # If the width is over maximum width
    if width_for_required_height > FINAL_WIDTH:
        # Scale the image to maximum width
        height_for_final_width = int(src_image.height * (FINAL_WIDTH / src_image.width))
        resized_image = src_image.resize((FINAL_WIDTH, height_for_final_width), Image.LANCZOS)

        # Put the rescaled image at vertical middle
        vertical_middle = (FINAL_HEIGHT - height_for_final_width) // 2
        final_image.paste(resized_image, (0, vertical_middle))

    else:
        # Scale the image to required height
        resized_image = src_image.resize((width_for_required_height, IMAGE_NET_HEIGHT), Image.LANCZOS)

    # Put the rescaled image at horizontal middle
    horizontal_middle = (FINAL_WIDTH - width_for_required_height) // 2
    final_image.paste(resized_image, (horizontal_middle, 0))

    # Save the final image
    final_image.save(resized_image_filename(filename), quality=95, optimize=True)


def is_already_converted(filename):
    return filename.stem.endswith(RESIZED_SUFFIX) or resized_image_filename(filename).exists()


def resized_image_filename(filename):
    return filename.with_name(filename.stem + RESIZED_SUFFIX + ".jpg")


if __name__ == '__main__':
    main()
