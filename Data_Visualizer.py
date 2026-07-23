import pygame
import random
import math

pygame.init()


class DrawInformation:
    # Basic color constants (RGB tuples)
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    GREEN = 0, 255, 0
    RED = 255, 0, 0
    BLUE = 0, 0, 255
    BACKGROUND_COLOR = WHITE

    # Shades of gray used to alternate bar colors so adjacent bars
    # are visually distinguishable when not actively highlighted.
    GRADIENTS = [
        (128, 128, 128),
        (160, 160, 160),
        (192, 192, 192)
    ]

    # Fonts used for the title/header text and the smaller instructional text
    FONT = pygame.font.SysFont('comicsans', 24)
    LARGE_FONT = pygame.font.SysFont('comicsans', 36)

    # Padding reserved on the sides (for bar margins) and at the top
    # (for the title/instructions text) of the window
    SIDE_PAD = 100
    TOP_PAD = 150

    def __init__(self, width, height, lst):
        self.width = width
        self.height = height

        # Create the actual pygame window surface
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sorting Algorithm Visualization")
        self.set_list(lst)

    def set_list(self, lst):
        self.lst = lst
        self.min_val = min(lst)
        self.max_val = max(lst)

        # Width of each bar so that all bars + side padding fit the window width
        self.block_width = round((self.width - self.SIDE_PAD) / len(lst))

        # Height "per unit value" so the tallest bar fits within the
        # vertical space available below the header/top padding
        self.block_height = math.floor((self.height - self.TOP_PAD) / (self.max_val - self.min_val + 1))

        # X coordinate where the first bar starts (centers the bars horizontally)
        self.start_x = self.SIDE_PAD // 2

    def bar_rect(self, index):
        x = self.start_x + index * self.block_width
        return pygame.Rect(x, self.TOP_PAD, self.block_width, self.height - self.TOP_PAD)


def draw(draw_info, algo_name, ascending, speed):
    draw_info.window.fill(draw_info.BACKGROUND_COLOR)

    # Title showing current algorithm and sort direction
    title = draw_info.LARGE_FONT.render(
        f"{algo_name} - {'Ascending' if ascending else 'Descending'}", 1, draw_info.GREEN)
    draw_info.window.blit(title, (draw_info.width / 2 - title.get_width() / 2, 5))

    # Line 1 of on-screen instructions (general controls)
    controls = draw_info.FONT.render(
        "R - Reset | SPACE - Start | A - Asc | D - Desc | +/- Speed", 1, draw_info.BLACK)
    draw_info.window.blit(controls, (draw_info.width / 2 - controls.get_width() / 2, 45))

    # Line 2 of on-screen instructions (algorithm hotkeys)
    sorting = draw_info.FONT.render(
        "I - Insertion | B - Bubble | S - Selection | M - Merge | Q - Quick", 1, draw_info.BLACK)
    draw_info.window.blit(sorting, (draw_info.width / 2 - sorting.get_width() / 2, 75))

    # Current playback speed multiplier
    speed_text = draw_info.FONT.render(f"Speed: {speed}x", 1, draw_info.BLACK)
    draw_info.window.blit(speed_text, (draw_info.width / 2 - speed_text.get_width() / 2, 105))

    draw_list(draw_info)
    pygame.display.update()


def draw_list(draw_info, color_positions=None, clear_bg=False):
    lst = draw_info.lst
    color_positions = color_positions or {}

    # If we're doing a partial/incremental redraw, only touch the indices
    # that changed; otherwise redraw every bar in the list.
    indices_to_draw = color_positions.keys() if (clear_bg and color_positions) else range(len(lst))

    dirty_rects = []  # regions that changed, used for a partial screen update

    for i in indices_to_draw:
        val = lst[i]
        x = draw_info.start_x + i * draw_info.block_width
        # y position of the top of the bar: taller values (relative to min_val)
        # push the top of the bar further up (smaller y)
        y = draw_info.height - (val - draw_info.min_val) * draw_info.block_height

        if clear_bg:
            # Erase the old bar in this column before drawing the new one
            rect = draw_info.bar_rect(i)
            pygame.draw.rect(draw_info.window, draw_info.BACKGROUND_COLOR, rect)
            dirty_rects.append(rect)

        # Use the highlight color if this index was passed in, otherwise
        # fall back to the alternating gray gradient based on index
        color = color_positions.get(i, draw_info.GRADIENTS[i % 3])
        pygame.draw.rect(draw_info.window, color, (x, y, draw_info.block_width, draw_info.height))

    if clear_bg:
        # Only update the changed regions of the screen (faster than a full redraw)
        pygame.display.update(dirty_rects)


def generate_starting_list(n, min_val, max_val):
    return [random.randint(min_val, max_val) for _ in range(n)]


def bubble_sort(draw_info, ascending=True):
    lst = draw_info.lst

    for i in range(len(lst) - 1):
        for j in range(len(lst) - 1 - i):
            num1 = lst[j]
            num2 = lst[j + 1]

            if (num1 > num2 and ascending) or (num1 < num2 and not ascending):
                # Out of order: swap and highlight the swapped pair
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                draw_list(draw_info, {j: draw_info.GREEN, j + 1: draw_info.RED}, True)
                yield True
            else:
                # Already in order: just highlight the pair being compared
                draw_list(draw_info, {j: draw_info.BLUE, j + 1: draw_info.BLUE}, True)
                yield True

    return lst


def insertion_sort(draw_info, ascending=True):
    lst = draw_info.lst

    for i in range(1, len(lst)):
        current = lst[i]

        while True:
            # Determine whether the previous element is out of order
            # relative to `current`, for the chosen sort direction
            ascending_sort = i > 0 and lst[i - 1] > current and ascending
            descending_sort = i > 0 and lst[i - 1] < current and not ascending

            if not ascending_sort and not descending_sort:
                # `current` is now in its correct position
                break

            # Shift the previous element right and move current left one slot
            lst[i] = lst[i - 1]
            i = i - 1
            lst[i] = current
            draw_list(draw_info, {i - 1: draw_info.GREEN, i: draw_info.RED}, True)
            yield True

    return lst


def selection_sort(draw_info, ascending=True):
    lst = draw_info.lst
    n = len(lst)

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            # Highlight the current best candidate (red) vs the element
            # being compared against it (blue)
            draw_list(draw_info, {target_idx: draw_info.RED, j: draw_info.BLUE}, True)
            yield True

            if (lst[j] < lst[target_idx] and ascending) or (lst[j] > lst[target_idx] and not ascending):
                target_idx = j

        if target_idx != i:
            # Place the found min/max at position i
            lst[i], lst[target_idx] = lst[target_idx], lst[i]
            draw_list(draw_info, {i: draw_info.GREEN, target_idx: draw_info.GREEN}, True)
            yield True

    return lst


def merge_sort(draw_info, ascending=True):
    lst = draw_info.lst

    def merge(lo, mid, hi):
        # Copy out the two halves to merge back together in place
        left = lst[lo:mid + 1]
        right = lst[mid + 1:hi + 1]
        i = j = 0
        k = lo

        # Merge while both halves still have elements left
        while i < len(left) and j < len(right):
            take_left = (left[i] <= right[j]) if ascending else (left[i] >= right[j])
            lst[k] = left[i] if take_left else right[j]
            if take_left:
                i += 1
            else:
                j += 1
            draw_list(draw_info, {k: draw_info.GREEN}, True)
            yield True
            k += 1

        # Drain any remaining elements from the left half
        while i < len(left):
            lst[k] = left[i]
            draw_list(draw_info, {k: draw_info.GREEN}, True)
            yield True
            i += 1
            k += 1

        # Drain any remaining elements from the right half
        while j < len(right):
            lst[k] = right[j]
            draw_list(draw_info, {k: draw_info.GREEN}, True)
            yield True
            j += 1
            k += 1

    def sort(lo, hi):
        # Base case: a single element (or empty range) is already sorted
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        yield from sort(lo, mid)
        yield from sort(mid + 1, hi)
        yield from merge(lo, mid, hi)

    yield from sort(0, len(lst) - 1)
    return lst


def quick_sort(draw_info, ascending=True):
    lst = draw_info.lst

    def partition(lo, hi):
        pivot = lst[hi]
        i = lo - 1  # index of the last element known to be <= pivot (for ascending)

        for j in range(lo, hi):
            # Highlight the element being compared (blue) against the pivot (red)
            draw_list(draw_info, {j: draw_info.BLUE, hi: draw_info.RED}, True)
            yield True

            if (lst[j] <= pivot and ascending) or (lst[j] >= pivot and not ascending):
                i += 1
                lst[i], lst[j] = lst[j], lst[i]
                draw_list(draw_info, {i: draw_info.GREEN, j: draw_info.GREEN}, True)
                yield True

        # Move the pivot into its final sorted position
        lst[i + 1], lst[hi] = lst[hi], lst[i + 1]
        draw_list(draw_info, {i + 1: draw_info.GREEN, hi: draw_info.GREEN}, True)
        yield True
        # Stash the pivot's final index on the function object so `sort()`
        # can retrieve it after the generator finishes (since generators
        # can't easily "return" a value through `yield from`)
        partition.result = i + 1

    def sort(lo, hi):
        if lo < hi:
            yield from partition(lo, hi)
            p = partition.result
            yield from sort(lo, p - 1)
            yield from sort(p + 1, hi)

    yield from sort(0, len(lst) - 1)
    return lst


# Maps keyboard keys to (algorithm function, display name) pairs,
# used to switch the active sorting algorithm from a keypress.
ALGORITHMS = {
    pygame.K_b: (bubble_sort, "Bubble Sort"),
    pygame.K_i: (insertion_sort, "Insertion Sort"),
    pygame.K_s: (selection_sort, "Selection Sort"),
    pygame.K_m: (merge_sort, "Merge Sort"),
    pygame.K_q: (quick_sort, "Quick Sort"),
}


def main():
    run = True
    clock = pygame.time.Clock()

    # Configuration for the random list to visualize
    n = 50
    min_val = 0
    max_val = 100

    lst = generate_starting_list(n, min_val, max_val)
    draw_info = DrawInformation(800, 600, lst)
    sorting = False
    ascending = True

    # Currently selected algorithm (defaults to bubble sort) and its
    # active generator instance (created when sorting starts)
    sorting_algorithm, sorting_algo_name = bubble_sort, "Bubble Sort"
    sorting_algorithm_generator = None

    # Playback speed: number of generator steps advanced per frame
    speed = 1
    MIN_SPEED, MAX_SPEED = 1, 10

    while run:
        clock.tick(60)  # cap the loop at 60 FPS

        if sorting:
            try:
                # Advance the sorting generator by `speed` steps this frame
                for _ in range(speed):
                    next(sorting_algorithm_generator)
            except StopIteration:
                # Generator is exhausted: sorting is complete
                sorting = False
                draw(draw_info, sorting_algo_name, ascending, speed)
        else:
            # Not currently sorting: just redraw the static list/UI each frame
            draw(draw_info, sorting_algo_name, ascending, speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_r:
                # Reset: generate a fresh random list and stop any active sort
                lst = generate_starting_list(n, min_val, max_val)
                draw_info.set_list(lst)
                sorting = False

            elif event.key == pygame.K_SPACE and not sorting:
                # Start sorting with the currently selected algorithm/direction
                sorting = True
                sorting_algorithm_generator = sorting_algorithm(draw_info, ascending)

            elif event.key == pygame.K_a and not sorting:
                ascending = True

            elif event.key == pygame.K_d and not sorting:
                ascending = False

            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                # Increase playback speed, capped at MAX_SPEED
                speed = min(MAX_SPEED, speed + 1)

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                # Decrease playback speed, floored at MIN_SPEED
                speed = max(MIN_SPEED, speed - 1)

            elif event.key in ALGORITHMS and not sorting:
                # Switch to a different algorithm (only allowed while idle)
                sorting_algorithm, sorting_algo_name = ALGORITHMS[event.key]

    pygame.quit()


if __name__ == "__main__":
    main()
