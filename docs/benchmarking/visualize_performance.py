import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
from matplotlib.ticker import MaxNLocator
import pandas as pd
import yaml
import tabulate

# https://personal.sron.nl/~pault/
import tol_colors

# matplotlib.rc('text', usetex=True)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "figure.dpi": 300,
    }
)


bright = tol_colors.tol_cset("bright")
vibrant = tol_colors.tol_cset("vibrant")
color_realtime = "#BBCCEE"  # pale_blue
color_barrier = "#CCDDAA"  # pale_green
color_line = bright.grey
# graphical abstract uses:
# simulation banner: bright.grey
# data: pale and dark . dark cyan
# network construction: pale and dark . dark blue
# idle power: pale and dark . dark grey
# reference: bright.yellow
# energy: high-contrast . red

params = {
    "fig_width": 7.0,  # max 180 mm / 25.4 = 7.08661
    "technology_list": ["cpu", "gpu", "spinnaker", "fpga"],
    "simulator_list": ["nest_cpu", "nest_gpu", "genn", "spinnaker", "csnn", "neuroaix"],
    "technologies": {
        "cpu": [r"\textbf{CPU}", vibrant.orange],
        "gpu": [r"\textbf{GPU}", vibrant.magenta],
        "spinnaker": [r"\textbf{SpiNNaker}", vibrant.blue],
        "fpga": [r"\textbf{FPGA}", bright.green],
    },
    "simulators": {
        "nest_cpu": ["NEST", "cpu", "o"],
        "nest_gpu": ["NEST", "gpu", "H"],
        "genn": ["GeNN", "gpu", "^"],
        "spinnaker": ["SpiNNaker 1", "spinnaker", "D"],
        "csnn": ["CsNN", "fpga", "P"],
        "neuroaix": ["neuroAIx", "fpga", "X"],
    },
}


def export_latex(data):

    def revise_bibentry(entry):
        return r"\cite{" + entry + "}"

    def revise_simulator(entry):
        new = params["simulators"][entry][0]
        if entry == "nest_cpu":
            new += " CPU"
        elif entry == "nest_gpu":
            new += " GPU"
        return new

    df = data[
        [
            "key",
            # "bibentry",
            "authoryear",
            "rtf",
            "esyn_muJ",
            "simulator",
            "num_nodes",
            "system",
            "process_node_nm",
            "drive",
        ]
    ]
    # df.fillna('-', inplace=True)
    # df.bibentry = df.bibentry.apply(revise_bibentry)
    df.simulator = df.simulator.apply(revise_simulator)
    df.rtf = round(df.rtf, 3)
    df.esyn_muJ = round(df.esyn_muJ, 3)
    df.rename(
        columns={
            "key": r"Study",
            # "bibentry": r"",
            "authoryear": r"",
            "rtf": r"Real-time factor $q_\text{RTF}$",
            "esyn_muJ": r"Energy per synaptic event $E_\text{syn}$ ($\mu$J)",
            "simulator": r"Simulator",
            "num_nodes": r"\#Nodes",
            "system": r"System",
            "process_node_nm": r"Process node (nm)",
            "drive": r"External drive",
        },
        inplace=True,
    )

    os.system("mkdir -p figures")
    fname = "figures/performance_summary.tex"
    df.to_latex(
        index=False,
        float_format="%g",
        column_format=r"p{1.1cm}p{0.5cm}|S[table-format=3.2]|p{0.9cm}|p{1.6cm}|>{\raggedleft\arraybackslash}p{1cm}|p{3.2cm}|>{\raggedleft\arraybackslash}p{0.8cm}|p{1cm}",
        formatters={r"\#Nodes": int, r"Process size (nm)": int},
        buf=fname,
    )
    fname = "figures/performance_summary.md"
    df.to_markdown(
        index=False,
        # float_format="%g",
        # column_format=r"p{1.1cm}p{0.5cm}|S[table-format=3.2]|p{0.9cm}|p{1.6cm}|>{\raggedleft\arraybackslash}p{1cm}|p{3.2cm}|>{\raggedleft\arraybackslash}p{0.8cm}|p{1cm}",
        # formatters={r"\#Nodes": int, r"Process size (nm)": int},
        buf=fname,
    )

    # replace NaN
    with open(fname, "r") as file:
        file_contents = file.read()
    updated_contents = file_contents.replace("NaN", "--")
    with open(fname, "w") as file:
        file.write(updated_contents)
    return


def performance_summary_manuscript(data):

    plt.figure(figsize=(params["fig_width"], 5.0))
    gs = gridspec.GridSpec(1, 3)
    gs.update(left=0.08, right=0.99, bottom=0.1, top=0.95, wspace=0.15)

    ax0 = plt.subplot(gs[0])
    add_label(ax0, "a")
    quantity_vs_year(
        data,
        quantity="rtf",
        legend=True,
        legend_orientation="vertical",
        legend_offset=[-1, -0.57],
        axis=ax0,
    )
    ax0.spines[["right", "top"]].set_visible(False)

    ax1 = plt.subplot(gs[1])
    add_label(ax1, "b")
    rtf_vs_energy(perf_data, legend=False, axis=ax1)
    ax1.spines[["right", "top"]].set_visible(False)
    ax1.set_yticklabels([])
    ax1.set_ylabel("")

    ax2 = plt.subplot(gs[2])
    add_label(ax2, "c")
    rtf_vs_processnode(perf_data, legend=False, axis=ax2)
    ax2.spines[["right", "top"]].set_visible(False)
    ax2.set_yticklabels([])
    ax2.set_ylabel("")

    os.system("mkdir -p figures")
    # plt.savefig("figures/performance_summary.eps")
    plt.savefig("figures/performance_summary.png")


def quantity_vs_year(
    data,
    quantity="rtf",
    legend=True,
    legend_orientation="vertical",
    legend_offset=[0, 0],
    axis=False,
):
    """
    quantity
        "rtf" or "esyn_muJ"
    legend
        whether to show a legend
    ax
        if False, standalone figure is produced
    """

    if not axis:
        plt.figure(figsize=(5.0, 3.0))
        gs = gridspec.GridSpec(1, 1)
        gs.update(left=0.12, right=0.75, bottom=0.15, top=0.98)
        ax = plt.subplot(gs[0])
    else:
        ax = axis

    keys = data["key"]
    show_rtf_years = data["show_rtf_year"]
    years = data["year"].astype(int)
    quantities = data[quantity].astype(float)
    simulators = data["simulator"]

    xmin = np.min(years) - 0.5
    xmax = np.max(years) + 1.7

    # additional curves
    if quantity == "rtf":
        ax.hlines(y=1, xmin=xmin, xmax=xmax, color=color_realtime)
        # ax.hlines(y=0.05, xmin=xmin, xmax=xmax, color=color_barrier)
        ax.annotate(
            text="Real time", xy=(np.max(years), 1.2), color=color_realtime, va="center"
        )

    if quantity == "rtf":
        yoffset = {}
        for i in data.index:
            yoffset[keys[i]] = 0.0
        yoffset.update(
            {"Rho+19a": 0.1, "Rho+19b": -0.1, "Kni+21": 0.1, "Hei+22": -0.03}
        )

    for i in data.index:
        if show_rtf_years[i] and quantity == "rtf":
            tech = params["simulators"][simulators[i]][1]
            color = params["technologies"][tech][1]
            marker = params["simulators"][simulators[i]][2]
            ax.plot(years[i], quantities[i], color=color, marker=marker)
            ax.annotate(
                text=keys[i],
                xy=(years[i] + 0.25, quantities[i] + yoffset[keys[i]]),
                fontsize=matplotlib.rcParams["font.size"] * 0.75,
                va="center",
            )
    ax.set_yscale("log")
    ax.set_xlabel("Year")
    xticks = np.arange(np.min(years), np.max(years) + 2, 2)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # years as integers

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.01, 40)

    if quantity == "rtf":
        ax.set_ylabel(r"Real-time factor $q_\mathrm{RTF}$", labelpad=0)
    elif quantity == "energy_syn_event_muJ":
        ax.set_ylabel(r"Energy per synaptic event ($\mu$J)")

    if legend and legend_orientation == "vertical":
        ax.legend(
            handles=legend_patches(params),
            fontsize=matplotlib.rcParams["font.size"] * 0.75,
            frameon=True,
            loc="upper left",
            bbox_to_anchor=(1 + legend_offset[0], 1 + legend_offset[1]),
            labelcolor="linecolor",
            columnspacing=0,
            handletextpad=0,
            labelspacing=0.2,
            borderpad=0.5,
            handlelength=1.8,
            handleheight=0,
        )
    if legend and legend_orientation == "horizontal":
        ax.legend(
            handles=legend_patches(params, legend_orientation="horizontal"),
            fontsize=matplotlib.rcParams["font.size"] * 0.75,
            frameon=True,
            loc="upper left",
            bbox_to_anchor=(1 + legend_offset[0], 1 + legend_offset[1]),
            labelcolor="linecolor",
            ncols=2,
            columnspacing=0,
            handletextpad=0,
            labelspacing=0.2,
            borderpad=0.2,
            handlelength=1.8,
            handleheight=0,
        )

    if not axis:
        plt.savefig(quantity + "_vs_year.eps")

    return


def rtf_vs_energy(
    data, legend=True, legend_orientation="vertical", legend_offset=[0, 0], axis=False
):
    """ """
    if not axis:
        plt.figure(figsize=(params["fig_width"], 3.0))
        gs = gridspec.GridSpec(1, 1)
        gs.update(left=0.12, right=0.75, bottom=0.15, top=0.98)
        ax = plt.subplot(gs[0])
    else:
        ax = axis

    keys = data["key"]
    show_esyn_rtfs = data["show_esyn_rtf"]
    years = data["year"].astype(int)
    rtfs = data["rtf"].astype(float)
    energies = data["esyn_muJ"].astype(float)
    simulators = data["simulator"]

    xmin = 0.6 * np.min(energies)
    xmax = 7 * np.max(energies)

    # additional curves
    ax.hlines(y=1, xmin=xmin, xmax=xmax, color=color_realtime)
    # ax.hlines(y=0.05, xmin=xmin, xmax=xmax, color=color_barrier)
    # ax.annotate(text='Real time', xy=(np.min(energies), 0.75),
    #            color=color_realtime,
    #            va='center')

    xfactor = {}
    for i in data.index:
        xfactor[keys[i]] = 1
    xfactor.update({"Gol+21": 0.8})

    yoffset = {}
    for i in data.index:
        yoffset[keys[i]] = 0.0
    yoffset.update({"Rho+19a": 0.1, "Rho+19b": -0.1, "Gol+21": 0.2, "Gol+23b": 0.02})

    # all data points
    xdata = []
    ydata = []
    for i in range(len(years)):
        if show_esyn_rtfs[i]:
            tech = params["simulators"][simulators[i]][1]
            color = params["technologies"][tech][1]
            marker = params["simulators"][simulators[i]][2]
            ax.plot(energies[i], rtfs[i], color=color, marker=marker)
            ax.annotate(
                text=keys[i],
                xy=(energies[i] * 1.4 * xfactor[keys[i]], rtfs[i] + yoffset[keys[i]]),
                fontsize=matplotlib.rcParams["font.size"] * 0.75,
                va="center",
            )
            xdata.append(energies[i])
            ydata.append(rtfs[i])

    # curve from linear fit in log-log space
    slope = 1
    intercept = np.nanmean(np.log(ydata) - slope * np.log(xdata))
    xs = [0.01, 50]
    ys = np.exp(intercept) * np.power(xs, slope)

    plt.plot(xs, ys, "--", color=color_line, zorder=0)
    ax.annotate(text=f"Slope={slope}", xy=(0.5, 10), color=color_line, va="top")

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.01, 40)
    ax.set_xlabel(r"Energy per synaptic event $E_\mathrm{syn}$ ($\mu$J)")
    ax.set_ylabel(r"Real-time factor $q_\mathrm{RTF}$", labelpad=0)

    if legend and legend_orientation == "vertical":
        ax.legend(
            handles=legend_patches(params),
            fontsize=matplotlib.rcParams["font.size"],
            frameon=False,
            loc="upper left",
            bbox_to_anchor=(1 + legend_offset[0], 1 + legend_offset[1]),
            labelcolor="linecolor",
        )

    if not axis:
        plt.savefig("rtf_vs_energy.eps")

    return


def rtf_vs_processnode(
    data, legend=True, legend_orientation="vertical", legend_offset=0.0, axis=False
):
    """ """
    if not axis:
        plt.figure(figsize=(params["fig_width"], 3.0))
        gs = gridspec.GridSpec(1, 1)
        gs.update(left=0.12, right=0.75, bottom=0.15, top=0.98)
        ax = plt.subplot(gs[0])
    else:
        ax = axis

    keys = data["key"]
    show_esyn_rtfs = data["show_esyn_rtf"]
    years = data["year"].astype(int)
    rtfs = data["rtf"].astype(float)
    pnodes = data["process_node_nm"].astype(float)
    simulators = data["simulator"]

    xmin = 0.5 * np.min(pnodes)
    xmax = 4 * np.max(pnodes)

    # additional curves
    ax.hlines(y=1, xmin=xmin, xmax=xmax, color=color_realtime)
    # ax.hlines(y=0.05, xmin=xmin, xmax=xmax, color=color_barrier)
    # ax.annotate(text='Real time', xy=(np.min(energies), 0.75),
    #            color=color_realtime,
    #            va='center')

    xfactor = {}
    for i in data.index:
        xfactor[keys[i]] = 1
    xfactor.update({"Kur+22b": 0.8})

    yoffset = {}
    for i in data.index:
        yoffset[keys[i]] = 0.0
    yoffset.update({"Rho+19a": 0.1, "Rho+19b": -0.1, "Kur+22b": 0.18})

    # all data points
    xdata = []
    ydata = []
    for i in range(len(years)):
        if show_esyn_rtfs[i]:
            tech = params["simulators"][simulators[i]][1]
            color = params["technologies"][tech][1]
            marker = params["simulators"][simulators[i]][2]
            ax.plot(pnodes[i], rtfs[i], color=color, marker=marker)
            ax.annotate(
                text=keys[i],
                xy=(pnodes[i] * 1.25 * xfactor[keys[i]], rtfs[i] + yoffset[keys[i]]),
                fontsize=matplotlib.rcParams["font.size"] * 0.75,
                va="center",
            )
            if tech == "cpu" or tech == "gpu":
                xdata.append(pnodes[i])
                ydata.append(rtfs[i])

    # curve from linear fit in log-log space
    slope = 2
    intercept = np.nanmean(np.log(ydata) - slope * np.log(xdata))
    xs = [0.1, 1000]
    ys = np.exp(intercept) * np.power(xs, slope)

    plt.plot(xs, ys, "--", color=color_line, zorder=0)
    ax.annotate(text=f"Slope={slope}", xy=(6.5, 10), color=color_line, va="top")

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.01, 40)
    # ax.set_ylim(ymin, ymax)
    ax.set_xlabel(r"Process node (nm)")
    ax.set_ylabel(r"Real-time factor $q_\mathrm{RTF}$", labelpad=0)

    if legend and legend_orientation == "vertical":
        ax.legend(
            handles=legend_patches(params),
            fontsize=matplotlib.rcParams["font.size"],
            frameon=False,
            loc="upper left",
            bbox_to_anchor=(1 + legend_offset[0], 1 + legend_offset[1]),
            labelcolor="linecolor",
        )

    if not axis:
        plt.savefig("rtf_vs_processsize.eps")

    return


def read_data(filename):
    with open(filename, "r") as stream:
        data = yaml.safe_load(stream)

    rows = []
    for entry in data:
        for key, details in entry.items():
            row = {"key": key}
            for d in details:
                row.update(d)
            rows.append(row)

    df = pd.DataFrame(rows)
    # print(df)
    return df


def legend_patches(params, legend_orientation="vertical"):
    patches = []

    for t in params["technology_list"]:
        count_sims = 0
        tech_label = params["technologies"][t][0]
        color = params["technologies"][t][1]
        patches.append(
            mlines.Line2D(
                [], [], marker="", linestyle="none", color=color, label=tech_label
            )
        )
        for s in params["simulator_list"]:
            if params["simulators"][s][1] == t:
                sim_label = params["simulators"][s][0]
                marker = params["simulators"][s][2]
                patches.append(
                    mlines.Line2D(
                        [],
                        [],
                        marker=marker,
                        linestyle="none",
                        color=color,
                        label=sim_label,
                    )
                )
                count_sims += 1

        # for horizontal orientation, make it two rows for all simulators
        # if legend_orientation == 'horizontal' and count_sims < 2:
        #    patches.append(mlines.Line2D(
        #        [], [], marker='', linestyle='none', color='k', label=''))

        # empty line
        patches.append(
            mlines.Line2D([], [], marker="", linestyle="none", color="k", label="")
        )
    return patches


def add_label(ax, label, offset=[0, 0], weight="bold", fontsize_scale=1.2):
    """
    Adds label to axis with given offset.

    Parameters
    ----------
    ax
        Axis to add label to.
    label
        Label should be a letter.
    offset
        x-,y-Offset.
    weight
        Weight of font.
    fontsize_scale
        Scaling factor for font size.
    """
    if weight == "bold" and matplotlib.rcParams["text.usetex"]:
        mylabel = r"\textbf{" + label + "}"
    else:
        mylabel = label
    label_pos = [0.0 + offset[0], 1.0 + offset[1]]
    ax.text(
        label_pos[0],
        label_pos[1],
        mylabel,
        ha="left",
        va="bottom",
        transform=ax.transAxes,
        weight=weight,
        fontsize=matplotlib.rcParams["font.size"] * fontsize_scale,
    )
    return


if __name__ == "__main__":

    perf_data = read_data("performance_data_raw.yaml")

    export_latex(perf_data)

    performance_summary_manuscript(perf_data)
