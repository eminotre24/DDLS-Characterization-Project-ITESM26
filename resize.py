from pathlib import Path
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

input_root = Path("./DDLS_120.3_SN_57_circle_marked")
output_root = Path("./DDLS_120.3_SN_57_circle_marked_resized")

max_side_px = 3000
jpeg_quality = 85

image_extensions = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"
}

for input_path in input_root.rglob("*"):
    if not input_path.is_file():
        continue

    if input_path.suffix.lower() not in image_extensions:
        continue

    relative_path = input_path.relative_to(input_root)

    output_path = output_root / relative_path
    output_path = output_path.with_suffix(".jpg")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(input_path) as img:
            img = ImageOps.exif_transpose(img)

            width, height = img.size

            scale = min(max_side_px / width, max_side_px / height, 1.0)

            new_width = int(width * scale)
            new_height = int(height * scale)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if img.mode in ["RGBA", "P", "LA"]:
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert("RGB")

            img.save(
                output_path,
                quality=jpeg_quality,
                optimize=True,
                progressive=True
            )

            original_mb = input_path.stat().st_size / 1024 / 1024
            resized_mb = output_path.stat().st_size / 1024 / 1024

            print(f"{relative_path}")
            print(f"  {width}x{height} -> {new_width}x{new_height}")
            print(f"  {original_mb:.2f} MB -> {resized_mb:.2f} MB")
            print()

    except Exception as e:
        print(f"Error with {input_path}: {e}")

print("Done.")
print(f"Resized images saved in: {output_root}")