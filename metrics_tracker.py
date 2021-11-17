from enum import Enum
from types import SimpleNamespace
from typing import Any, Dict, List, Literal, Optional, Set, Tuple
import json

import matplotlib.pyplot as plt #type: ignore

import numpy as np
# ===============================================
# Colorama Filler
# ===============================================
try:
    from colorama import Fore  # type: ignore
except:
    colors = ["RED", "YELLOW", "GREEN", "BLUE", "ORANGE", "MAGENTA", "CYAN"]
    kwargs = {}
    for col in colors:
        kwargs[col] = ""
        kwargs[f"LIGHT{col}_EX"]
    Fore = SimpleNamespace(RESET="", **kwargs)

# ===============================================
# Data Types
# ===============================================
class DataType(Enum):
    DISTRIBUTION = "distribution"
    SEQUENTIAL = "sequential"
    MAP = "map"
    DISTRIBUTION_2D = "distribution_2d"

# ===============================================
# Metrics
# ===============================================
class Metrics:

    def __init__(self) -> None:
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self._auto_bins: List[str] = []

    def new_data(self, name: str, type: DataType, auto_bins: bool = False, **kwargs):
        entry = {
            "type": type.value,
            "data": [],
            **kwargs
        }
        self.metrics[name] = entry
        if auto_bins:
            self._auto_bins.append(name)

    def add(self, name: str, data: Any):
        self.metrics[name]["data"].append(data)

    def save(self, path: str = "metrics.json"):
        for name in self._auto_bins:
            self.auto_bins(name)
        with open(path, "w") as fd:
            json.dump(self.metrics, fd)

    def auto_bins(self, name: str):
        mini = min(self.metrics[name]["data"])
        maxi = max(self.metrics[name]["data"])
        self.metrics[name]["bins"] = list(range(mini, maxi + 2))


# ===============================================
# Globasl for Plotting
# ===============================================

StoredDataKey = Literal["data", "orientation", "type", "bins", "labels", "measure"]
StoredData = Dict[StoredDataKey, Any]

__OPTIONS_STR__ = "@"
__GRAPH_STR__ = "+"
__KWARGS_STR__ = "$"

__ALLOWED_KWARGS__ = ["logx", "logy", "loglog", "exp"]
__OPTIONS__ = ["sharex", "sharey", "sharexy", "grid"]

# ===============================================
# Utils for plotting
# ===============================================
def __optional_split__(text: str, split: str) -> List[str]:
    if split in text:
        return text.split(split)
    return [text]

def __find_metrics_for__(metrics: Dict[str, Dict[StoredDataKey, Any]], prefix: str) -> List[str]:
    candidates = list(metrics.keys())
    for i, l in enumerate(prefix):
        if l == "*":
            return candidates
        candidates = [cand for cand in candidates if len(
            cand) > i and cand[i] == l]
        if len(candidates) == 1:
            return candidates
    for cand in candidates:
        if len(cand) == len(prefix):
            return [cand]
    return candidates

def __to_nice_name__(name: str) -> str:
    return name.replace("_", " ").replace(".", " ").title()

def layout_for_subplots(nplots: int, screen_ratio: float = 16 / 9) -> Tuple[int, int]:
    """
    Find a good number of rows and columns for organizing the specified number of subplots.

    Parameters
    -----------
    - **nplots**: the number of subplots
    - **screen_ratio**: the ratio width/height of the screen

    Return
    -----------
    [nrows, ncols] for the sublopt layout.
    It is guaranteed that ```nplots <= nrows * ncols```.
    """
    nrows = int(np.floor(np.sqrt(nplots / screen_ratio)))
    ncols = int(np.floor(nrows * screen_ratio))
    # Increase size so that everything can fit
    while nrows * ncols < nplots:
        if nrows < ncols:
            nrows += 1
        elif ncols < nrows:
            ncols += 1
        else:
            if screen_ratio >= 1:
                ncols += 1
            else:
                nrows += 1
    # If we can reduce the space, reduce it
    while (nrows - 1) * ncols >= nplots and (ncols - 1) * nrows >= nplots:
        if nrows > ncols:
            nrows -= 1
        elif nrows < ncols:
            ncols -= 1
        else:
            if screen_ratio < 1:
                ncols -= 1
            else:
                nrows -= 1
    while (nrows - 1) * ncols >= nplots:
        nrows -= 1
    while (ncols - 1) * nrows >= nplots:
        ncols -= 1
    return nrows, ncols

# ===============================================
#  Main function called
# ===============================================
def interactive_plot(metrics: Dict[str, Dict[StoredDataKey, Any]]):
    while True:
        print("Available data:", ", ".join([Fore.LIGHTYELLOW_EX + s + Fore.RESET for s in metrics.keys()]))
        try:
            query = input("Which metric do you want to plot?\n>" + Fore.LIGHTGREEN_EX)
            print(Fore.RESET, end=" ")
        except EOFError:
            break

        global_options = __optional_split__(query.lower().strip(), __OPTIONS_STR__)
        choice = global_options.pop(0)
        elements = __optional_split__(choice, __GRAPH_STR__)
        things_with_options = [__get_graph_options__(x) for x in elements]
        metrics_with_str_options = [(__find_metrics_for__(metrics, x), y) for x,y in things_with_options]
        metrics_with_options = [(x, __parse_kwargs__(y))
                                for x, y in metrics_with_str_options if len(x) > 0]
        if len(metrics_with_options) == 0:
            print(Fore.RED + "No metrics found matching query:\'" +
                  Fore.LIGHTRED_EX + query + Fore.RED + "\'" + Fore.RESET)
            continue

        correctly_expanded_metrics_with_otpions: List[Tuple[List[str], Dict]] = []
        for x, y in metrics_with_options:
            if y["exp"]:
                for el in x:
                    correctly_expanded_metrics_with_otpions.append(([el], y))

            else:
                correctly_expanded_metrics_with_otpions.append((x, y))
        
        plt.figure()
        __plot_all__(metrics, correctly_expanded_metrics_with_otpions, global_options)
        plt.show()


# ===============================================
#  Plot a list of metrics on the same graph
# ===============================================
def __plot_sequential__(metrics: Dict[str, Dict[StoredDataKey, Any]], metrics_name: List[str], logx: bool = False, logy: bool = False):
    plt.xlabel("Time")
    if logx:
        if logy:
            plt.loglog()
        else:
            plt.semilogx()
    elif logy:
        plt.semilogy()
    for name in metrics_name:
        nice_name = __to_nice_name__(name)
        plt.plot(metrics[name]["data"], label=nice_name)
    if len(metrics_name) > 1:
        plt.legend()
    else:
        plt.ylabel(nice_name)

def __plot_distribution__(metrics: Dict[str, Dict[StoredDataKey, Any]], metrics_name: List[str], logx: bool = False, logy: bool = False):
    # This may also contain maps
    # We should convert distributions to maps
    new_metrics:  Dict[str, Dict[StoredDataKey, Any]] = {}
    for name in metrics_name:
        info = metrics[name]
        # If a MAP no need to convert
        if info["type"] == DataType.MAP:
            new_metrics[name] = metrics[name]
            continue
        # Compute histogram
        bins = info.get("bins", None) or "auto"
        hist, edges = np.histogram(metrics[name]["data"], bins=bins, density=True)
        # If we have labels
        if "labels" in info:
            data = list(zip(info["labels"], hist))
            orientation = "horizontal"
        else:
            data = sorted([((edges[i], edges[i+1]), hist[i] * (edges[i + 1] - edges[i])) for i in range(len(hist))], key=lambda x: x[0])
            orientation = "vertical"
        # New metric
        new_metrics[name] = {
            "data": data,
            "type": DataType.MAP,
            "measure": "Frequency",
            "orientation": orientation,
        }
    return __plot_map__(new_metrics, metrics_name, logx, logy)

def __plot_map__(metrics: Dict[str, Dict[StoredDataKey, Any]], metrics_name: List[str], logx: bool = False, logy: bool = False):
    higher_data : List[Tuple[str, Dict[Any, float], bool]] = []
    measure: Optional[str] = None
    # 1) Label homogeneization
    for name in metrics_name:
        nice_name = __to_nice_name__(name)
        data = metrics[name]["data"]
        out = {}
        for a, b in data:
            out[a] = b
        higher_data.append(
            (nice_name, out, metrics[name].get("orientation", "horizontal") == "vertical"))
        if "measure" in metrics[name]:
            measure = metrics[name]["measure"]
    # 2) Compute set of all labels
    all_labels: Set[Any] = set()
    for _, d, _ in higher_data:
        all_labels |= d.keys()
    # 3) Arrange x and sort labels
    vertical = all(v for _, _, v in higher_data)
    # If labels are tuples => labels are intervals
    if vertical and isinstance(list(all_labels)[0], tuple):
        query_labels = sorted(all_labels, key=lambda x:x[0])
        labels = sorted(set([x for x, _ in all_labels]) |  set([x for _, x in all_labels]))
        x = [(labels[i] + labels[i+1]) / 2 for i in range(len(labels) - 1)]
        height = [labels[i+1] - labels[i] for i in range(len(labels) - 1)]
    else:
        labels = sorted(all_labels)
        query_labels = labels
        x = list(range(len(labels)))
        height = 1

    # 4) Plot the bars
    for nice_name, d, _ in higher_data:
        widths = [d.get(s, 0) for s in query_labels]
        if vertical:
            plt.bar(x, widths, height, label=nice_name, log=logy)
        else:
            plt.barh(x, widths, height,label=nice_name, log=logx)
    # 5) Legend or axis name as metric name
    if len(metrics_name) > 1:
        plt.legend()
    else:
        if vertical:
            plt.xlabel(nice_name)
        else:
            plt.ylabel(nice_name)
    # 6) Ticks and others axis
    if vertical:
        if measure:
            plt.ylabel(measure)
        if len(labels) > len(query_labels):
            plt.xticks(labels, labels=labels, rotation=0)
            plt.xlim(left=labels[0], right=labels[-1])
        else:
            plt.xticks(np.array(range(len(labels))), labels=labels, rotation=0)
    else:
        if measure:
            plt.xlabel(measure)
        plt.yticks(np.array(range(len(labels))), labels=labels, rotation=0)


def __plot__(metrics: Dict[str, Dict[StoredDataKey, Any]], metrics_name: List[str], logx: bool = False, logy: bool = False, **kwargs):
    data_type = DataType(metrics[metrics_name[0]]["type"])
    if data_type == DataType.MAP and any(metrics[n]["type"] == DataType.DISTRIBUTION for n in metrics_name):
        data_type = DataType.DISTRIBUTION
    if data_type == DataType.SEQUENTIAL:
        __plot_sequential__(metrics_name, logx, logy)
    elif data_type == DataType.DISTRIBUTION:
       __plot_distribution__(metrics, metrics_name, logx, logy)
    else:
        __plot_map__(metrics, metrics_name, logx, logy)


            

# ===============================================
#  Parsing
# ===============================================
def __get_graph_options__(text: str) -> Tuple[str, List[str]]:
    el = __optional_split__(text, __KWARGS_STR__)
    return el.pop(0), el


def __parse_kwargs__(options: List[str]) -> Dict[str, Any]:
    kwargs = {}
    for el in __ALLOWED_KWARGS__:
        kwargs[el] = el in options
    kwargs["logx"] |= kwargs["loglog"]
    kwargs["logy"] |= kwargs["loglog"]
    return kwargs


def __plot_all__(metrics: Dict[str, Dict[StoredDataKey, Any]], elements: List[Tuple[List[str], Dict[str, Any]]], global_options: List[str]):
    ax_list = []

    nrows, ncols = 1, len(elements)
    if "grid" in global_options:
        nrows, ncols = layout_for_subplots(len(elements))

    for i, (metrics_to_plot, kwargs) in enumerate(elements):
        ax = plt.subplot(nrows, ncols, 1 + i)
        ax_list.append(ax)
        __plot__(metrics, metrics_to_plot, **kwargs)
    if "sharex" in global_options or "sharexy" in global_options:
        ax_list[0].get_shared_x_axes().join(*ax_list)
    if "sharey" in global_options or "sharexy" in global_options:
        ax_list[0].get_shared_y_axes().join(*ax_list)
    plt.show()


# ===============================================
#  Actual Main call
# ===============================================
if __name__ == "__main__":
    import sys
    import os
    import matplotlib
    if len(sys.argv) < 2:
        print(Fore.LIGHTGREEN_EX + "Usage:" +
              Fore.GREEN + sys.argv[0] + " <filename>" + Fore.RESET)
        sys.exit(0)
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(Fore.RED + "No such file:\'" +
              Fore.LIGHTRED_EX + filename + Fore.RED + "\'" + Fore.RESET)
        sys.exit(1)
    with open(filename) as fd:
        metrics = json.load(fd)

    matplotlib.rcParams.update({'font.size': 14})
    matplotlib.rcParams['mathtext.fontset'] = 'custom'
    matplotlib.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
    matplotlib.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
    matplotlib.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'
    matplotlib.rcParams['mathtext.fontset'] = 'cm'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    plt.style.use('seaborn-colorblind')
    interactive_plot(metrics)
