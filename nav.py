import awpy.plot.nav
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pathlib import Path
import matplotlib.pyplot as plt
from loguru import logger
from matplotlib import patches

from awpy.data import NAVS_DIR



def plot_map_tiles(
    map_name: str,
    outpath: str | Path | None = None,
    dpi: int = 300,
    fill: str | None = None,
    figure_size: tuple[float, float] = (19, 21),
) -> tuple[Figure, Axes]:
    fig, axis = awpy.plot.plot(map_name=map_name)
    fig.set_size_inches(*figure_size)
    _plot_all_tiles(map_name, axis, default_fill=fill)

    # Handle outpath for both str and Path inputs
    if outpath is not None:
        outpath = Path(outpath)
        outpath.parent.mkdir(parents=True, exist_ok=True)  # Ensure parent directory exists
        plt.savefig(outpath, bbox_inches="tight", dpi=dpi)
        logger.debug(f"The visualization has been saved at {outpath.resolve()}")

    return fig, axis

def _plot_all_tiles(map_name: str, axis: Axes, default_fill: str = "None") -> None:
    map_nav = awpy.nav.Nav.from_json(awpy.data.NAVS_DIR / f"{map_name}.json")

    for area in map_nav.areas.values():
        polygon = _tile_polygon(area.corners, map_name)
        _plot_tile(axis, polygon, edgecolor="yellow", facecolor=default_fill)

    for area in map_nav.areas.keys():
        print(map_nav.areas[area])

def _tile_polygon(area_corners: list[awpy.vector.Vector3], map_name: str) -> list[tuple[float, float]]:
    return [awpy.plot.utils.game_to_pixel(map_name, (c.x, c.y, c.z))[0:2] for c in area_corners]


def _plot_tile(
    axis: Axes, polygon: list[tuple[float, float]], edgecolor: str, facecolor: str, linewidth: int = 1
) -> None:
    patch = patches.Polygon(polygon, linewidth=linewidth, edgecolor=edgecolor, facecolor=facecolor)

    axis.add_patch(patch)

if __name__ == "__main__":
    # plot_map_tiles(map_name="de_dust2", outpath="./images/de_dust2.png")

    print(NAVS_DIR)
