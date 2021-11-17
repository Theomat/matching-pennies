from typing import Any, Dict, List, Literal, Optional, Set, Tuple

from metrics_tracker import DataType

from colorama import Fore  # type: ignore

import matplotlib.pyplot as plt #type: ignore

import numpy as np

StoredDataKey = Literal["data", "orientation", "type", "bins", "labels", "measure"]
StoredData = Dict[StoredDataKey, Any]

__OPTIONS_STR__ = "@"
__GRAPH_STR__ = "+"
__KWARGS_STR__ = "$"

__ALLOWED_KWARGS__ = ["logx", "logy", "loglog", "exp"]
__OPTIONS__ = ["sharex", "sharey", "sharexy", "grid"]


def __optional_split__(text: str, split: str) -> List[str]:
    if split in text:
        return text.split(split)
    return [text]


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


# ------------------------------------------------
## Plot function
# ------------------------------------------------
def __plot__(metrics: Dict[str, Dict[StoredDataKey, Any]], metrics_name: List[str], logx: bool = False, logy: bool = False, **kwargs):
    data_type = DataType(metrics[metrics_name[0]]["type"])
    if data_type == DataType.MAP and any(metrics[n]["type"] == DataType.DISTRIBUTION for n in metrics_name):
        data_type = DataType.DISTRIBUTION
    if data_type == DataType.SEQUENTIAL:
        plt.xlabel("Time")
        if logx:
            if logy:
                plt.loglog()
            else:
                plt.semilogx()
        elif logy:
            plt.semilogy()
        for name in metrics_name:
            nice_name = name.replace("_", " ").replace(".", " ").title()
            plt.plot(metrics[name]["data"], label=nice_name)

        if len(metrics_name) > 1:
            plt.legend()
        else:
            plt.ylabel(nice_name)

    elif data_type == DataType.DISTRIBUTION:
        # This may also contain maps
        # We should convert distributions to maps
        new_metrics:  Dict[str, Dict[StoredDataKey, Any]] = {}
        for name in metrics_name:
            nice_name = name.replace("_", " ").replace(".", " ").title()
            info = metrics[name]
            if info["type"] == DataType.MAP:
                new_metrics[name] = metrics[name]
                continue
            bins = info.get("bins", None)
            hist, edges = np.histogram(metrics[name]["data"], bins=bins, density=True)
            if "labels" in info:
                labels = info["labels"]
                data = list(zip(labels, hist))
                orientation = "horizontal"
            else:
                data = sorted([((edges[i], edges[i+1]), hist[i]) for i in range(len(hist))], key=lambda x: x[0])
                orientation = "vertical"
            new_metrics[name] = {
                "data": data,
                "type": DataType.MAP,
                "measure": "Frequency",
                "orientation": orientation,
            }

        return __plot__(new_metrics, metrics_name, logx, logy, **kwargs)

    else:
        higher_data : List[Tuple[str, Dict[Any, float], bool]] = []
        measure: Optional[str] = None
        for name in metrics_name:
            nice_name = name.replace("_", " ").replace(".", " ").title()
            data = metrics[name]["data"]
            out = {}
            for a, b in data:
                out[a] = b
            higher_data.append(
                (nice_name, out, metrics[name].get("orientation", "horizontal") == "vertical"))
            if "measure" in metrics[name]:
                measure = metrics[name]["measure"]
        # Compute set of all labels
        all_labels: Set[Any] = set()
        for _, d, _ in higher_data:
            all_labels |= d.keys()
        # Plot
        vertical = all(v for _, _, v in higher_data)
        if vertical:
            if isinstance(list(all_labels)[0], tuple):
                query_labels = sorted(all_labels, key=lambda x:x[0])
                labels = list(set([x for x, y in all_labels]) |  set([y for x, y in all_labels]))
                labels = sorted(labels)
                x = [(labels[i] + labels[i+1])/2 for i in range(len(labels) - 1)]
            else:
                labels = sorted(all_labels, key=lambda x: int(x[1:x.index(";")]))
                query_labels = labels
                x = list(range(len(labels)))
        else:
            labels = sorted(all_labels)
            query_labels = labels
            x = list(range(len(labels)))

        for nice_name, d, _ in higher_data:
            widths = [d.get(s, 0) for s in query_labels]
            if vertical:
                plt.bar(x, widths, label=nice_name, log=logy)
            else:
                plt.barh(x, widths,
                         label=nice_name, log=logx)

        if len(metrics_name) > 1:
            plt.legend()
        else:
            if vertical:
                plt.xlabel(nice_name)
            else:
                plt.ylabel(nice_name)
        if vertical:
            if measure:
                plt.ylabel(measure)
            if len(labels) > len(query_labels):
                plt.xticks(labels, labels=labels, rotation=0)
            else:
                plt.xticks(np.array(range(len(labels))), labels=labels, rotation=0)
        else:
            if measure:
                plt.xlabel(measure)
            plt.yticks(np.array(range(len(labels))), labels=labels, rotation=0)


            

# ------------------------------------------------
## INTERACTION
# ------------------------------------------------
def __get_graph_options__(text: str) -> Tuple[str, List[str]]:
    el = __optional_split__(text, __KWARGS_STR__)
    return el.pop(0), el

def __find_metrics_for__(metrics: Dict[str, Dict[StoredDataKey, Any]], prefix: str) -> List[str]:
    candidates = list(metrics.keys())
    for i, l in enumerate(prefix):
        candidates = [cand for cand in candidates if len(
            cand) > i and cand[i] == l]
        if len(candidates) == 1:
            return candidates
    return candidates

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

    for i, (metrics_to_plot, kwargs) in enumerate(elements):
        ax = plt.subplot(nrows, ncols, 1 + i)
        ax_list.append(ax)
        __plot__(metrics, metrics_to_plot, **kwargs)
    if "sharex" in global_options or "sharexy" in global_options:
        ax_list[0].get_shared_x_axes().join(*ax_list)
    if "sharey" in global_options or "sharexy" in global_options:
        ax_list[0].get_shared_y_axes().join(*ax_list)
    plt.show()


# ------------------------------------------------
## Main
# ------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import json
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

    # helper.use_colorblind_palette()
    # helper.use_latex_style()
    interactive_plot(metrics)
