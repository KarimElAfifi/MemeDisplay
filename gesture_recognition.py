import math
from typing import Protocol, Sequence


class Landmark(Protocol):
    x: float
    y: float
    z: float


Hand = Sequence[Landmark]

FINGER_JOINTS = ((5, 6, 7), (9, 10, 11), (13, 14, 15), (17, 18, 19))


def joint_angle(hand: Hand, first: int, joint: int, last: int) -> float:
    vector_a = (
        hand[first].x - hand[joint].x,
        hand[first].y - hand[joint].y,
        hand[first].z - hand[joint].z,
    )
    vector_b = (
        hand[last].x - hand[joint].x,
        hand[last].y - hand[joint].y,
        hand[last].z - hand[joint].z,
    )
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    cosine = max(-1.0, min(1.0, dot_product / (magnitude_a * magnitude_b)))
    return math.degrees(math.acos(cosine))


def finger_is_extended(hand: Hand, mcp: int, pip: int, dip: int) -> bool:
    return joint_angle(hand, mcp, pip, dip) >= 155


def is_closed_fist(hand: Hand) -> bool:
    return all(
        not finger_is_extended(hand, mcp, pip, dip)
        for mcp, pip, dip in FINGER_JOINTS
    )


def thumb_is_extended(hand: Hand) -> bool:
    return joint_angle(hand, 1, 2, 3) >= 145


def palm_facing_camera(hand: Hand) -> float:
    wrist = hand[0]
    middle_mcp = hand[9]
    index_mcp = hand[5]
    pinky_mcp = hand[17]

    wrist_to_middle = (
        middle_mcp.x - wrist.x,
        middle_mcp.y - wrist.y,
        middle_mcp.z - wrist.z,
    )
    index_to_pinky = (
        pinky_mcp.x - index_mcp.x,
        pinky_mcp.y - index_mcp.y,
        pinky_mcp.z - index_mcp.z,
    )
    normal = (
        wrist_to_middle[1] * index_to_pinky[2] - wrist_to_middle[2] * index_to_pinky[1],
        wrist_to_middle[2] * index_to_pinky[0] - wrist_to_middle[0] * index_to_pinky[2],
        wrist_to_middle[0] * index_to_pinky[1] - wrist_to_middle[1] * index_to_pinky[0],
    )
    magnitude = math.sqrt(sum(component * component for component in normal))
    return abs(normal[2]) / magnitude if magnitude else 0


def is_pistol_hand(hand: Hand) -> bool:
    return (
        thumb_is_extended(hand)
        and finger_is_extended(hand, 5, 6, 7)
        and finger_is_extended(hand, 9, 10, 11)
        and not finger_is_extended(hand, 13, 14, 15)
        and not finger_is_extended(hand, 17, 18, 19)
    )


def is_open_hand(hand: Hand) -> bool:
    return all(
        finger_is_extended(hand, mcp, pip, dip)
        for mcp, pip, dip in FINGER_JOINTS
    )


def hand_points_vertically(hand: Hand) -> bool:
    return abs(hand[12].y - hand[0].y) > abs(hand[12].x - hand[0].x) * 1.2


def hands_are_together(hands: Sequence[Hand]) -> bool:
    landmark_indices = (0, 5, 9, 13, 17, 8, 12, 16, 20)
    average_distance = sum(
        math.sqrt(
            (hands[0][index].x - hands[1][index].x) ** 2
            + (hands[0][index].y - hands[1][index].y) ** 2
        )
        for index in landmark_indices
    ) / len(landmark_indices)
    return average_distance < 0.13


def detect_gesture(
    hands: Sequence[Hand],
    world_hands: Sequence[Hand],
) -> str | None:
    if len(hands) != len(world_hands):
        raise RuntimeError("MediaPipe hat unterschiedliche Hand-Landmarks geliefert")
    if not hands:
        return None

    if len(hands) >= 2:
        first, second = hands[0], hands[1]
        first_world, second_world = world_hands[0], world_hands[1]

        if (
            is_open_hand(first_world)
            and is_open_hand(second_world)
            and hand_points_vertically(first) != hand_points_vertically(second)
        ):
            return "Stopp"

        if is_pistol_hand(first_world) and is_pistol_hand(second_world):
            return "Pistolen"

        if (
            hand_points_vertically(first)
            and hand_points_vertically(second)
            and hands_are_together(hands)
        ):
            return "Beten"

    for hand in world_hands:
        if is_closed_fist(hand):
            if palm_facing_camera(hand) >= 0.5:
                return "Jerry"
            return "Baby-Dats-Crazy"

    return None
