from pathlib import Path
from PIL import Image


def optimize_image(
    src_path: str,
    dest_dir: str = "assets",
    max_width: int = 800,
    quality: int = 85,
    ratio: tuple[int, int] | None = None,
) -> str:
    """Resize, optionally crop, and compress an image.

    Args:
        src_path: Path to the original image file.
        dest_dir: Directory to store optimized images.
        max_width: Maximum width of the saved image.
        quality: JPEG quality for compression.

    Returns:
        Path to the optimized image file.
    """
    src = Path(src_path)
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    # determine output path
    out_name = src.stem + "_opt.jpg"
    out_path = Path(dest_dir) / out_name

    try:
        img = Image.open(src_path)
        # Convert to RGB to ensure JPEG compatibility
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        # resize if wider than max_width
        if img.width > max_width:
            scale = max_width / float(img.width)
            new_height = int(img.height * scale)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        # Crop to aspect ratio if requested
        if ratio:
            target_ratio = ratio[0] / ratio[1]
            current_ratio = img.width / img.height
            if abs(current_ratio - target_ratio) > 0.01:
                if current_ratio > target_ratio:
                    # too wide
                    new_width = int(img.height * target_ratio)
                    left = (img.width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, img.height))
                else:
                    # too tall
                    new_height = int(img.width / target_ratio)
                    top = (img.height - new_height) // 2
                    img = img.crop((0, top, img.width, top + new_height))
        img.save(out_path, format="JPEG", quality=quality, optimize=True)
        return str(out_path)
    except Exception:
        # if anything goes wrong, fall back to original
        return str(src_path)

