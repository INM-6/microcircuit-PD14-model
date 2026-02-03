"""
Standalone script to generate PD14 publication charts.

This script extracts PD14 citation data from BibTeX files and generates
cumulative bar charts showing "All Citations" vs "Uses PD14" over time.
"""

import os
import re
import textwrap
from datetime import datetime

# Optional matplotlib import with fallback
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


def parse_bibtex_entries(bib_path):
    """Parse BibTeX file into individual entry strings."""
    if not os.path.exists(bib_path):
        return []

    with open(bib_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    entries = []
    current_entry = []
    brace_count = 0
    in_entry = False

    for line in content.split("\n"):
        if line.strip().startswith("@"):
            if current_entry:
                entries.append("\n".join(current_entry))
            current_entry = [line]
            in_entry = True
            brace_count = line.count("{") - line.count("}")
        elif in_entry:
            current_entry.append(line)
            brace_count += line.count("{") - line.count("}")
            if brace_count == 0:
                entries.append("\n".join(current_entry))
                current_entry = []
                in_entry = False

    if current_entry:
        entries.append("\n".join(current_entry))

    return entries


def extract_metadata(entry_text):
    """Extract year and uses_PD14 flag from BibTeX entry."""
    year_re = re.compile(r"year\s*=\s*[{\"]?(\d{4})", re.IGNORECASE)
    uses_re = re.compile(r"uses_PD14\s*=\s*[{\"]?(\w+)", re.IGNORECASE)

    metadata = {}
    for line in entry_text.split("\n"):
        line = line.strip()
        year_match = year_re.match(line)
        uses_match = uses_re.match(line)

        if year_match:
            metadata["year"] = year_match.group(1)
        if uses_match:
            metadata["uses_PD14"] = uses_match.group(1).lower()

    return metadata


def filter_preprints(entries):
    """Filter out preprint entries (Cold Spring Harbor Laboratory)."""
    filtered = []
    preprint_pattern = re.compile(
        r"publisher\s*=\s*[{\"].*Cold Spring Harbor Laboratory.*[}\"]", re.IGNORECASE
    )

    for entry in entries:
        if not preprint_pattern.search(entry):
            filtered.append(entry)

    return filtered


def load_and_process_data(bib_paths):
    """Load BibTeX files and extract citation data."""
    entries_data = []

    for bib_path in bib_paths:
        if not os.path.exists(bib_path):
            continue

        print(f"Loading {bib_path}...")
        entries = parse_bibtex_entries(bib_path)
        filtered = filter_preprints(entries)

        for entry_text in filtered:
            metadata = extract_metadata(entry_text)
            if metadata and "year" in metadata:
                entries_data.append(metadata)

    return entries_data


def get_last_two_entries(bib_path):
    """Extract the last two BibTeX entries from a file."""
    if not os.path.exists(bib_path):
        return []

    entries = parse_bibtex_entries(bib_path)
    filtered = filter_preprints(entries)

    # Return last two entries
    return filtered[-2:] if len(filtered) >= 2 else filtered


def format_bibtex_entry_for_display(entry_text):
    """Format a BibTeX entry for display, extracting key information."""
    lines = entry_text.strip().split("\n")
    if not lines:
        return ""

    # Extract entry type and key from first line
    first_line = lines[0].strip()
    entry_match = re.match(r"@(\w+)\s*{\s*([^,]+)", first_line)
    if not entry_match:
        return entry_text

    entry_type = entry_match.group(1)
    entry_key = entry_match.group(2).strip()

    # Format the entry
    formatted = f"@{entry_type}{{{entry_key},\n"

    # Add remaining lines with proper indentation
    for line in lines[1:]:
        formatted += line + "\n"

    return formatted.rstrip()


def calculate_cumulative_data(entries_data):
    """Calculate cumulative citation counts."""
    current_year = datetime.now().year
    year_range = range(2013, current_year + 1)

    # Initialize counts
    all_counts_dict = {y: 0 for y in year_range}
    uses_counts_dict = {y: 0 for y in year_range}

    # Count entries by year
    for item in entries_data:
        year = item.get("year")
        try:
            y = int(year)
        except (ValueError, TypeError):
            continue

        if y not in all_counts_dict:
            continue

        all_counts_dict[y] += 1
        if item.get("uses_PD14", "").lower() == "yes":
            uses_counts_dict[y] += 1

    # Calculate cumulative sums
    cumulative_all = {}
    cumulative_uses = {}
    sum_all = 0
    sum_uses = 0

    for year in year_range:
        sum_all += all_counts_dict[year]
        sum_uses += uses_counts_dict[year]
        cumulative_all[year] = sum_all
        cumulative_uses[year] = sum_uses

    return cumulative_all, cumulative_uses


def generate_cumulative_bar_chart(
    cumulative_all, cumulative_uses, output_dir, bib_entries=None
):
    """Generate cumulative stacked bar chart with optional BibTeX entries displayed."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available - skipping chart generation")
        return

    # Create figure with two subplots if we have entries to show
    if bib_entries:
        fig = plt.figure(figsize=(16, 7), facecolor="none")  # Transparent background
        # Left subplot for text (30% width)
        ax_text = plt.subplot2grid((1, 10), (0, 0), colspan=3)
        # Right subplot for chart (70% width)
        ax = plt.subplot2grid((1, 10), (0, 3), colspan=7)
    else:
        fig, ax = plt.subplots(
            figsize=(10, 7), facecolor="none"
        )  # Transparent background

    years = sorted(cumulative_all.keys())
    all_values = [cumulative_all[y] for y in years]
    uses_values = [cumulative_uses[y] for y in years]
    cites_only = [a - u for a, u in zip(all_values, uses_values)]

    # Create stacked bars
    bars1 = ax.bar(
        years,
        cites_only,
        label="Cites Only",
        color="lightgray",
        alpha=0.8,
        edgecolor="gray",
        linewidth=0.5,
    )
    bars2 = ax.bar(
        years,
        uses_values,
        bottom=cites_only,
        label="Uses PD14",
        color="tab:blue",
        alpha=0.8,
        edgecolor="navy",
        linewidth=0.5,
    )

    # Add value labels for "Cites Only" segment
    for i, (bar, value) in enumerate(zip(bars1, cites_only)):
        if value > 3:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() / 2,
                str(value),
                ha="center",
                va="center",
                fontsize=11,
                color="black",
                weight="bold",
            )

    # Add value labels for "Uses PD14" segment
    for i, (bar, value) in enumerate(zip(bars2, uses_values)):
        if value > 3:
            y_pos = cites_only[i] + value / 2
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos,
                str(value),
                ha="center",
                va="center",
                fontsize=11,
                color="white",
                weight="bold",
            )

    # Add total labels on top
    for i, year in enumerate(years):
        total = all_values[i]
        if total > 0:
            ax.text(
                year,
                total + max(all_values) * 0.01,
                str(total),
                ha="center",
                va="bottom",
                fontsize=13,
                weight="bold",
                color="black",
            )

    # Styling
    ax.set_xlabel("Year", fontsize=16, weight="bold")
    ax.set_title("PD14 Cumulative Citations", fontsize=18, weight="bold")
    ax.legend(fontsize=14, loc="upper left")
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Optimize Y-axis ticks
    max_val = max(all_values)
    if max_val <= 50:
        y_step = 5
    elif max_val <= 100:
        y_step = 10
    elif max_val <= 200:
        y_step = 20
    elif max_val <= 500:
        y_step = 50
    else:
        y_step = max(50, int(max_val / 10 / 50) * 50)

    ax.set_yticks(range(0, int(max_val) + y_step, y_step))
    ax.set_ylim(0, int(max_val) + y_step * 0.25)
    ax.tick_params(axis="y", labelsize=13)

    # X-axis ticks
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right", fontsize=13)
    ax.set_xlim(min(years) - 0.5, max(years) + 0.5)

    # Add BibTeX entries panel if provided
    if bib_entries:
        ax_text.axis("off")
        ax_text.set_xlim(0, 1)
        ax_text.set_ylim(0, 1)

        # Get the position of the main chart to match heights
        chart_pos = ax.get_position()
        text_pos = ax_text.get_position()

        # Calculate gray box height to match the chart's plotting area
        # The box should start where the chart starts and end where it ends
        box_bottom = (chart_pos.y0 - text_pos.y0) / text_pos.height
        box_height = chart_pos.height / text_pos.height

        # Add title above the gray box with same formatting as chart title
        title_y = box_bottom + box_height + 0.02
        ax_text.text(
            0.5,
            title_y,
            "Latest Publications",
            fontsize=18,
            weight="bold",
            horizontalalignment="center",
            verticalalignment="bottom",
            transform=ax_text.transAxes,
            zorder=1,
        )

        # Add light gray background that matches the graph axis height exactly
        from matplotlib.patches import Rectangle

        bg_rect = Rectangle(
            (-0.40, box_bottom),
            1.6,
            box_height,
            facecolor="#f0f0f0",
            edgecolor="#cccccc",
            linewidth=1,
            transform=ax_text.transAxes,
            zorder=-1,
            clip_on=False,
        )
        ax_text.add_patch(bg_rect)

        # Format and display entries - start just below the top of the box
        y_position = box_bottom + box_height - 0.01
        for i, entry in enumerate(bib_entries):
            # Extract entry type and key
            lines = entry.strip().split("\n")
            if not lines:
                continue

            first_line = lines[0].strip()
            entry_match = re.match(r"@(\w+)\s*{\s*([^,]+)", first_line)
            if not entry_match:
                continue

            entry_type = entry_match.group(1)
            entry_key = entry_match.group(2).strip()

            # Add entry header with colored formatting
            header_text = f"@{entry_type}"
            key_text = "{" + entry_key + "},"

            # Display @entrytype in red and bold
            ax_text.text(
                -0.37,
                y_position,
                header_text,
                fontfamily="monospace",
                fontsize=12,
                color="red",
                weight="bold",
                verticalalignment="top",
                transform=ax_text.transAxes,
                zorder=1,
            )

            # Display key in red
            ax_text.text(
                -0.37 + len(header_text) * 0.029,
                y_position,
                key_text,
                fontfamily="monospace",
                fontsize=12,
                color="red",
                verticalalignment="top",
                transform=ax_text.transAxes,
                zorder=1,
            )

            y_position -= 0.032

            # Add remaining lines (wrapped)
            for line in lines[1:]:
                line = line.strip()
                if not line or line == "}":
                    if line == "}":
                        ax_text.text(
                            -0.37,
                            y_position,
                            line,
                            fontfamily="monospace",
                            fontsize=10,
                            color="black",
                            verticalalignment="top",
                            transform=ax_text.transAxes,
                            zorder=1,
                        )
                        y_position -= 0.028
                    continue

                # Check if line contains a BibTeX key (word before =)
                if "=" in line:
                    key_match = re.match(r"^(\s*\w+\s*)(=.*)$", line)
                    if key_match:
                        key_part = key_match.group(1)  # e.g., "title "
                        rest_part = key_match.group(2)  # e.g., "= {value},"

                        # Check if line needs wrapping
                        full_line = key_part + rest_part
                        if len(full_line) > 60:
                            # Wrap the rest part if needed
                            wrapped_rest = textwrap.wrap(
                                rest_part, width=60 - len(key_part)
                            )

                            # Display first line with key in red and rest in black
                            ax_text.text(
                                -0.37,
                                y_position,
                                key_part,
                                fontfamily="monospace",
                                fontsize=10,
                                color="red",
                                verticalalignment="top",
                                transform=ax_text.transAxes,
                                zorder=1,
                            )

                            x_offset = len(key_part) * 0.03
                            ax_text.text(
                                -0.37 + x_offset,
                                y_position,
                                wrapped_rest[0] if wrapped_rest else rest_part,
                                fontfamily="monospace",
                                fontsize=10,
                                color="black",
                                verticalalignment="top",
                                transform=ax_text.transAxes,
                                zorder=1,
                            )
                            y_position -= 0.028

                            # Display continuation lines in black
                            for wrapped_line in wrapped_rest[1:]:
                                ax_text.text(
                                    -0.37,
                                    y_position,
                                    wrapped_line,
                                    fontfamily="monospace",
                                    fontsize=10,
                                    color="black",
                                    verticalalignment="top",
                                    transform=ax_text.transAxes,
                                    zorder=1,
                                )
                                y_position -= 0.028
                        else:
                            # Line fits, display key in red and rest in black
                            ax_text.text(
                                -0.37,
                                y_position,
                                key_part,
                                fontfamily="monospace",
                                fontsize=10,
                                color="red",
                                verticalalignment="top",
                                transform=ax_text.transAxes,
                                zorder=1,
                            )

                            x_offset = len(key_part) * 0.03
                            ax_text.text(
                                -0.37 + x_offset,
                                y_position,
                                rest_part,
                                fontfamily="monospace",
                                fontsize=10,
                                color="black",
                                verticalalignment="top",
                                transform=ax_text.transAxes,
                                zorder=1,
                            )
                            y_position -= 0.028
                        continue

                # Wrap long lines without keys
                wrapped_lines = textwrap.wrap(line, width=60)
                for wrapped_line in wrapped_lines:
                    ax_text.text(
                        -0.37,
                        y_position,
                        wrapped_line,
                        fontfamily="monospace",
                        fontsize=10,
                        color="black",
                        verticalalignment="top",
                        transform=ax_text.transAxes,
                        zorder=1,
                    )
                    y_position -= 0.028

            # Add spacing between entries
            y_position -= 0.01

    fig.tight_layout()

    # Save version without border first (with white background)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "PD14_pubs_cumulative_bar.svg")
    fig.savefig(output_path, bbox_inches="tight", facecolor="white")
    print(f"Saved: {output_path}")

    # Add white background with rounded corners and blue border for icon version
    from matplotlib.patches import FancyBboxPatch

    # Get the figure size in inches
    fig_width, fig_height = fig.get_size_inches()

    # Create white background patch (drawn first, behind everything)
    background_patch = FancyBboxPatch(
        (0.005, 0.005),  # Start slightly inside to account for border width
        0.99,
        0.99,  # Width and height (slightly less than full to account for border)
        boxstyle="round,pad=0.06",  # Rounded corners
        linewidth=0,  # No border on background
        edgecolor="none",
        facecolor="white",  # White fill
        transform=fig.transFigure,  # Use figure coordinates
        zorder=-1000,  # Draw behind everything
        clip_on=False,
    )
    fig.patches.append(background_patch)

    # Create blue border patch (drawn on top)
    border_patch = FancyBboxPatch(
        (0.005, 0.005),  # Start slightly inside to account for border width
        0.99,
        0.99,  # Width and height (slightly less than full to account for border)
        boxstyle="round,pad=0.06",  # Rounded corners
        linewidth=12,  # Border thickness
        edgecolor="#0969da",  # Blue color from publication_icon.png
        facecolor="none",  # Transparent fill
        transform=fig.transFigure,  # Use figure coordinates
        zorder=1000,  # Draw on top
        clip_on=False,
    )
    fig.patches.append(border_patch)

    # Save icon version with border
    output_path_icon = os.path.join(output_dir, "PD14_pubs_cumulative_bar_icon.svg")
    fig.savefig(output_path_icon, bbox_inches="tight", transparent=True)
    print(f"Saved: {output_path_icon}")

    plt.close(fig)


def main(input_paths=None, output_dir=None):
    """Main execution function."""
    # Define input paths
    if input_paths is None:
        project_root = os.path.dirname(os.path.abspath(__file__))
        docs_dir = os.path.dirname(project_root)
        input_paths = [
            os.path.join(docs_dir, "publications.bib"),
            os.path.join(docs_dir, "PD14_uses_only.bib"),
        ]

    # Define output directory
    if output_dir is None:
        project_root = os.path.dirname(os.path.abspath(__file__))
        docs_dir = os.path.dirname(project_root)
        parent_docs_dir = os.path.dirname(docs_dir)
        output_dir = os.path.join(parent_docs_dir, "_static", "images")

    print("=" * 60)
    print("PD14 Chart Generator")
    print("=" * 60)

    # Load and process data
    entries_data = load_and_process_data(input_paths)

    if not entries_data:
        print("Error: No valid citation data found")
        return 1

    print(f"Loaded {len(entries_data)} citation entries")

    # Calculate cumulative statistics
    cumulative_all, cumulative_uses = calculate_cumulative_data(entries_data)

    print(f"Total citations: {max(cumulative_all.values())}")
    print(f"Uses PD14: {max(cumulative_uses.values())}")

    # Get last two entries from publications.bib
    bib_path = input_paths[0] if input_paths else None
    last_entries = []
    if bib_path and os.path.exists(bib_path):
        last_entries = get_last_two_entries(bib_path)
        print(f"Loaded {len(last_entries)} latest entries for display")

    # Generate chart
    generate_cumulative_bar_chart(
        cumulative_all, cumulative_uses, output_dir, last_entries
    )

    print("=" * 60)
    print("Chart generation complete!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
