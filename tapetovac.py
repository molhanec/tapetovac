
FINAL_WIDTH = 1920
FINAL_HEIGHT = 1200
BOTTOM_PADDING = 2 * 30
IMAGE_NET_HEIGHT = FINAL_HEIGHT - BOTTOM_PADDING

from PIL import Image
import sys

# Check for argument, print help if necessary
if len(sys.argv) != 2:
    print("Usage: picture.jpg", file=sys.stderr)
    sys.exit(-1)

# Load source image
src_image = Image.open(sys.argv[1])

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
final_image.save(sys.argv[1].replace(".", "-resized."), quality=95, optimize=True)
