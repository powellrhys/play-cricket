# Import python dependencies
import plotly.express as px
import pandas as pd

class PlotlyPlotter:
    """
    A utility class for generating common Plotly visualizations from a pandas DataFrame.

    The PlotlyPlotter class provides methods to create various types of plots such as scatter,
    line, bar, area, and pie charts using Plotly Express, while supporting default and
    overrideable parameters.

    Attributes:
        df (pd.DataFrame): The data to be visualized.
        default_kwargs (dict): Default plotting keyword arguments used across all plots.
        fig (go.Figure): The most recently generated plotly figure.

    Methods:
        plot_scatter(**kwargs): Creates a scatter plot using Plotly Express.
        plot_line(**kwargs): Creates a line plot using Plotly Express.
        plot_bar(**kwargs): Creates a bar chart using Plotly Express.
        plot_area(**kwargs): Creates an area chart using Plotly Express.
        plot_pie(**kwargs): Creates a pie chart using Plotly Express.
        group_x_axis(groupby_metric): Sorts and groups the x-axis based on a column.
    """
    def __init__(self, df: pd.DataFrame, **kwargs):
        self.df = df
        self.default_kwargs = kwargs
        self.fig = None

    def plot_scatter(self, **kwargs) -> px.line:
        """
        Creates a scatter plot using Plotly Express.

        Args:
            **kwargs: Additional keyword arguments to override default plot settings.

        Returns:
            plotly.graph_objs._figure.Figure: The generated scatter plot figure.
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate line plot figure
        self.fig = px.scatter(self.df, **params)
        return self.fig

    def plot_line(self, **kwargs) -> px.line:
        """
        Creates a line plot using Plotly Express.

        Args:
            **kwargs: Additional keyword arguments to override default plot settings.

        Returns:
            plotly.graph_objs._figure.Figure: The generated line plot figure.
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate line plot figure
        self.fig = px.line(self.df, **params)
        return self.fig

    def plot_bar(self, **kwargs) -> px.bar:
        """
        Creates a bar chart using Plotly Express.

        Args:
            **kwargs: Additional keyword arguments to override default plot settings.

        Returns:
            plotly.graph_objs._figure.Figure: The generated bar chart figure.
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate bar plot figure
        self.fig = px.bar(self.df, **params)
        return self.fig

    def plot_area(self, **kwargs) -> px.area:
        """
        Creates an area chart using Plotly Express.

        Args:
            **kwargs: Additional keyword arguments to override default plot settings.

        Returns:
            plotly.graph_objs._figure.Figure: The generated area chart figure.
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate area plot figure
        self.fig = px.area(self.df, **params)
        return self.fig

    def plot_pie(self, **kwargs) -> px.pie:
        """
        Creates a pie chart using Plotly Express.

        Args:
            **kwargs: Additional keyword arguments to override default plot settings.

        Returns:
            plotly.graph_objs._figure.Figure: The generated pie chart figure.
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate pie plot figure
        self.fig = px.pie(self.df, **params)
        return self.fig

    def group_x_axis(
            self,
            groupby_metric: str):
        """
        Sorts and groups the x-axis categories based on a specified metric column.

        Args:
            groupby_metric (str): The name of the column used to sort and group x-axis categories.

        Returns:
            plotly.graph_objs._figure.Figure: The updated figure with grouped x-axis.
        """
        # Group x axis by groupby_metric variable
        self.fig.update_layout(xaxis=dict(type='category',
                                          categoryorder='array',
                                          categoryarray=sorted(self.df[groupby_metric])),
                               uniformtext_minsize=8,
                               uniformtext_mode='hide')

        return self.fig
