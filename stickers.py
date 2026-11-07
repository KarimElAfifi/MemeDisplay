from pathlib import Path

import cv2

GESTURE_STICKERS = {
    "Baby-Dats-Crazy": "baby dats crazy.jpg",
    "Jerry": "jerry look at this guy.png",
    "Pistolen": "sybau.jpg",
    "Stopp": "shaq stop.jpg",
    "Beten": "god pls.jpg",
}


def load_stickers(images_dir: Path) -> dict[str, cv2.typing.MatLike]:
    sticker_images = {
        gesture: cv2.imread(str(images_dir / filename))
        for gesture, filename in GESTURE_STICKERS.items()
    }

    for gesture, image in sticker_images.items():
        if image is None:
            filename = GESTURE_STICKERS[gesture]
            raise FileNotFoundError(
                f"Sticker konnte nicht geladen werden: {images_dir / filename}"
            )

    return sticker_images


def overlay_sticker(frame: cv2.typing.MatLike, sticker: cv2.typing.MatLike) -> None:
    height, width = frame.shape[:2]
    sticker_height, sticker_width = sticker.shape[:2]
    scale = min(width * 0.8 / sticker_width, height * 0.8 / sticker_height)
    sticker_width = max(1, int(sticker_width * scale))
    sticker_height = max(1, int(sticker_height * scale))
    resized_sticker = cv2.resize(
        sticker,
        (sticker_width, sticker_height),
        interpolation=cv2.INTER_AREA,
    )

    x = (width - sticker_width) // 2
    y = (height - sticker_height) // 2
    frame[y:y + sticker_height, x:x + sticker_width] = resized_sticker
