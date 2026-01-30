# Shiny app comparing Python vs R (tidyverse) data visualization using rpy2
# This is Shiny Core syntax. You can ask me to convert it to Shiny Express.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# rpy2 imports for R integration
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr
from rpy2.robjects.lib import grdevices

from shiny import App, render, ui

# Import R packages
ggplot2 = importr("ggplot2")
base = importr("base")

# Generate sample dataset
np.random.seed(42)
n = 100
sample_data = pd.DataFrame({
    "x": np.random.randn(n),
    "y": np.random.randn(n) * 2 + np.random.randn(n),
    "category": np.random.choice(["A", "B", "C"], n),
    "size": np.random.uniform(10, 100, n)
})

# Define plot types
plot_types = {
    "scatter": "Scatter Plot",
    "histogram": "Histogram",
    "boxplot": "Box Plot",
    "density": "Density Plot",
    "bar": "Bar Chart"
}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Visualization Options"),
        ui.input_select(
            "plot_type",
            "Select Plot Type",
            choices=plot_types,
            selected="scatter"
        ),
        ui.input_select(
            "color_var",
            "Color by Category",
            choices={"none": "None", "category": "Category"},
            selected="category"
        ),
        ui.hr(),
        ui.p("This app demonstrates the same visualization created with:"),
        ui.tags.ul(
            ui.tags.li(ui.strong("Python:"), " matplotlib/seaborn"),
            ui.tags.li(ui.strong("R:"), " ggplot2 (via rpy2)")
        ),
        width=300
    ),
    ui.h2("Python vs R Visualization Comparison"),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header(
                ui.tags.i(class_="fa-brands fa-python", style="margin-right: 8px;"),
                "Python (matplotlib/seaborn)"
            ),
            ui.output_plot("python_plot", height="400px"),
            ui.card_footer(ui.output_code("python_code"))
        ),
        ui.card(
            ui.card_header(
                ui.tags.i(class_="fa-brands fa-r-project", style="margin-right: 8px;"),
                "R (ggplot2 via rpy2)"
            ),
            ui.output_plot("r_plot", height="400px"),
            ui.card_footer(ui.output_code("r_code"))
        ),
        width="50%"
    ),
    ui.tags.link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.1/css/all.min.css"
    ),
    title="Python vs R Visualization"
)


def server(input, output, session):
    
    @render.plot
    def python_plot():
        fig, ax = plt.subplots(figsize=(8, 6))
        plot_type = input.plot_type()
        use_color = input.color_var() == "category"
        
        if plot_type == "scatter":
            if use_color:
                sns.scatterplot(data=sample_data, x="x", y="y", hue="category", 
                               size="size", sizes=(20, 200), ax=ax)
            else:
                ax.scatter(sample_data["x"], sample_data["y"], s=sample_data["size"])
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_title("Scatter Plot")
            
        elif plot_type == "histogram":
            if use_color:
                for cat in sample_data["category"].unique():
                    subset = sample_data[sample_data["category"] == cat]
                    ax.hist(subset["x"], alpha=0.6, label=cat, bins=15)
                ax.legend()
            else:
                ax.hist(sample_data["x"], bins=15, edgecolor="black")
            ax.set_xlabel("X")
            ax.set_ylabel("Count")
            ax.set_title("Histogram")
            
        elif plot_type == "boxplot":
            if use_color:
                sns.boxplot(data=sample_data, x="category", y="y", ax=ax)
            else:
                ax.boxplot(sample_data["y"])
            ax.set_ylabel("Y")
            ax.set_title("Box Plot")
            
        elif plot_type == "density":
            if use_color:
                for cat in sample_data["category"].unique():
                    subset = sample_data[sample_data["category"] == cat]
                    sns.kdeplot(subset["x"], label=cat, ax=ax)
                ax.legend()
            else:
                sns.kdeplot(sample_data["x"], ax=ax)
            ax.set_xlabel("X")
            ax.set_title("Density Plot")
            
        elif plot_type == "bar":
            counts = sample_data["category"].value_counts()
            if use_color:
                colors = sns.color_palette("husl", len(counts))
                ax.bar(counts.index, counts.values, color=colors)
            else:
                ax.bar(counts.index, counts.values)
            ax.set_xlabel("Category")
            ax.set_ylabel("Count")
            ax.set_title("Bar Chart")
        
        plt.tight_layout()
        return fig
    
    @render.plot
    def r_plot():
        plot_type = input.plot_type()
        use_color = input.color_var() == "category"
        
        # Convert pandas DataFrame to R dataframe using localconverter context
        with localconverter(ro.default_converter + pandas2ri.converter):
            r_df = ro.conversion.py2rpy(sample_data)
        ro.globalenv["df"] = r_df
        
        # Build ggplot2 code based on plot type
        if plot_type == "scatter":
            if use_color:
                r_code = """
                ggplot(df, aes(x = x, y = y, color = category, size = size)) +
                    geom_point(alpha = 0.7) +
                    labs(title = "Scatter Plot") +
                    theme_minimal()
                """
            else:
                r_code = """
                ggplot(df, aes(x = x, y = y)) +
                    geom_point(size = 3) +
                    labs(title = "Scatter Plot") +
                    theme_minimal()
                """
                
        elif plot_type == "histogram":
            if use_color:
                r_code = """
                ggplot(df, aes(x = x, fill = category)) +
                    geom_histogram(bins = 15, alpha = 0.6, position = "identity") +
                    labs(title = "Histogram") +
                    theme_minimal()
                """
            else:
                r_code = """
                ggplot(df, aes(x = x)) +
                    geom_histogram(bins = 15, fill = "steelblue", color = "black") +
                    labs(title = "Histogram") +
                    theme_minimal()
                """
                
        elif plot_type == "boxplot":
            if use_color:
                r_code = """
                ggplot(df, aes(x = category, y = y, fill = category)) +
                    geom_boxplot() +
                    labs(title = "Box Plot") +
                    theme_minimal()
                """
            else:
                r_code = """
                ggplot(df, aes(x = "", y = y)) +
                    geom_boxplot(fill = "steelblue") +
                    labs(title = "Box Plot", x = "") +
                    theme_minimal()
                """
                
        elif plot_type == "density":
            if use_color:
                r_code = """
                ggplot(df, aes(x = x, color = category, fill = category)) +
                    geom_density(alpha = 0.3) +
                    labs(title = "Density Plot") +
                    theme_minimal()
                """
            else:
                r_code = """
                ggplot(df, aes(x = x)) +
                    geom_density(fill = "steelblue", alpha = 0.5) +
                    labs(title = "Density Plot") +
                    theme_minimal()
                """
                
        elif plot_type == "bar":
            if use_color:
                r_code = """
                ggplot(df, aes(x = category, fill = category)) +
                    geom_bar() +
                    labs(title = "Bar Chart") +
                    theme_minimal()
                """
            else:
                r_code = """
                ggplot(df, aes(x = category)) +
                    geom_bar(fill = "steelblue") +
                    labs(title = "Bar Chart") +
                    theme_minimal()
                """
        
        # Execute R code and capture plot
        p = ro.r(r_code)
        
        # Use grdevices to render the ggplot
        with grdevices.render_to_bytesio(grdevices.png, 
                                          width=800, height=600, res=100) as img:
            ro.r.print(p)
        
        # Display using matplotlib
        from PIL import Image
        import io
        img_data = img.getvalue()
        image = Image.open(io.BytesIO(img_data))
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(image)
        ax.axis("off")
        plt.tight_layout()
        return fig
    
    @render.code
    def python_code():
        plot_type = input.plot_type()
        use_color = input.color_var() == "category"
        
        codes = {
            "scatter": (
                'sns.scatterplot(data=df, x="x", y="y", hue="category", size="size")'
                if use_color else
                'plt.scatter(df["x"], df["y"])'
            ),
            "histogram": (
                'sns.histplot(data=df, x="x", hue="category", bins=15)'
                if use_color else
                'plt.hist(df["x"], bins=15)'
            ),
            "boxplot": (
                'sns.boxplot(data=df, x="category", y="y")'
                if use_color else
                'plt.boxplot(df["y"])'
            ),
            "density": (
                'sns.kdeplot(data=df, x="x", hue="category")'
                if use_color else
                'sns.kdeplot(df["x"])'
            ),
            "bar": (
                'df["category"].value_counts().plot(kind="bar", color=palette)'
                if use_color else
                'df["category"].value_counts().plot(kind="bar")'
            )
        }
        return codes.get(plot_type, "")
    
    @render.code
    def r_code():
        plot_type = input.plot_type()
        use_color = input.color_var() == "category"
        
        codes = {
            "scatter": (
                'ggplot(df, aes(x, y, color=category)) + geom_point()'
                if use_color else
                'ggplot(df, aes(x, y)) + geom_point()'
            ),
            "histogram": (
                'ggplot(df, aes(x, fill=category)) + geom_histogram()'
                if use_color else
                'ggplot(df, aes(x)) + geom_histogram()'
            ),
            "boxplot": (
                'ggplot(df, aes(category, y, fill=category)) + geom_boxplot()'
                if use_color else
                'ggplot(df, aes(y=y)) + geom_boxplot()'
            ),
            "density": (
                'ggplot(df, aes(x, color=category)) + geom_density()'
                if use_color else
                'ggplot(df, aes(x)) + geom_density()'
            ),
            "bar": (
                'ggplot(df, aes(category, fill=category)) + geom_bar()'
                if use_color else
                'ggplot(df, aes(category)) + geom_bar()'
            )
        }
        return codes.get(plot_type, "")


app = App(app_ui, server)
