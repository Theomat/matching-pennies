from typing import Any, Dict, List, Literal, Optional, Union
import matplotlib.pyplot as plt

import numpy as np

StoredDataKey = Union[Literal["data"], Literal["type"], 
                      Literal["bins"], Literal["labels"]]
StoredData = Dict[StoredDataKey, Any]


def interactive_plot(metrics: Dict[str, Dict[StoredDataKey, Any]]):
    while True:
        print("Available data:", ", ".join(metrics.keys()))
        try:
            choice = input("Which metric do you want to plot?\n>").lower().strip()
        except EOFError:
            break

        plt.figure()
        options = []
        if "@" in choice:
            tmp = choice.split("@")
            choice = tmp[0]
            options = tmp[1:]
        if "+" in choice:
            elements = choice.split("+")
        else:
            elements = [choice]
        __plot_all__(metrics, elements, options)
        plt.show()


# ------------------------------------------------
## Plot function
# ------------------------------------------------
def __plot__(metrics: Dict[str, Dict[StoredDataKey, Any]], metric_name: str, logx: bool = False, logy: bool = False, **kwargs):
    info: Dict = metrics[metric_name]
    metric_name = metric_name.replace("_", " ").title()
    data: List = info["data"]
    data_type: str = info["type"]
    if data_type == "batch":
        plt.plot(data)
        plt.xlabel("Batch")
        if logx:
            if logy:
                plt.loglog()
            else:
                plt.semilogx()
        elif logy:
            plt.semilogy()

        plt.ylabel(metric_name)
    elif data_type == "distribution":
        bins = info.get("bins", None)
        orientation = "horizontal" if "labels" in info else "vertical"
        plt.hist(data, bins=bins, density=True, align="left", orientation=orientation)
        plt.xlabel(metric_name)
        plt.ylabel("Frequency")
        if "labels" in info:
            plt.xlabel("Frequency")
            plt.ylabel(metric_name)
            plt.yticks(np.array(range(len(info["labels"]))), labels=info["labels"], rotation=0)

# ------------------------------------------------
## INTERACTION
# ------------------------------------------------


def __find_unique_metric_by_prefix__(metrics: Dict[str, Dict[StoredDataKey, Any]], prefix: str) -> Optional[str]:
    candidates = list(metrics.keys())
    for i, l in enumerate(prefix):
        candidates = [cand for cand in candidates if cand[i] == l]
        if len(candidates) == 1:
            return candidates[0]
    return None


def __parse_and_plot__(metrics: Dict[str, Dict[StoredDataKey, Any]], element: str) -> bool:
    kwargs = {}
    if "." in element:
        elements = element.split(".")
        element = elements.pop(0)
        for el in ["logx", "logy", "loglog"]:
            kwargs[el] = el in elements
        kwargs["logx"] |= kwargs["loglog"]
        kwargs["logy"] |= kwargs["loglog"]
    choice = __find_unique_metric_by_prefix__(metrics, element)
    if choice:
        __plot__(metrics, choice, **kwargs)
        return True
    return False


def __plot_all__(metrics: Dict[str, Dict[StoredDataKey, Any]], elements: List[str], options: List[str]):
    ax_list = []
    for i, element in enumerate(elements):
        ax = plt.subplot(1, len(elements), 1 + i)
        ax_list.append(ax)
        __parse_and_plot__(metrics, element)
    if "sharex" in options or "sharexy" in options:
        ax_list[0].get_shared_x_axes().join(*ax_list)
    if "sharey" in options or "sharexy" in options:
        ax_list[0].get_shared_y_axes().join(*ax_list)
    plt.show()


# ------------------------------------------------
## Main
# ------------------------------------------------
if __name__ == "__main__":
    import sys
    import json
    filename = sys.argv[1]
    with open(filename) as fd:
        metrics = json.load(fd)
    interactive_plot(metrics)