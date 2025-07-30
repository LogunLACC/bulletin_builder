from pathlib import Path
from PIL import Image


def optimize_image(src_path: str, dest_dir: str = "assets", max_width: int = 800, quality: int = 85) -> str:
    """Resize and compress an image, saving to dest_dir.

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
            ratio = max_width / float(img.width)
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        img.save(out_path, format="JPEG", quality=quality, optimize=True)
        return str(out_path)
    except Exception:
        # if anything goes wrong, fall back to original
        return str(src_path)

