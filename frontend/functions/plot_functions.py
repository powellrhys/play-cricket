# Import python dependencies
import plotly.express as px
import pandas as pd

class PlotlyPlotter:
    def __init__(self, df: pd.DataFrame, **kwargs):
        self.df = df
        self.default_kwargs = kwargs
        self.fig = None

    def plot_scatter(self, **kwargs) -> px.line:
        """
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate line plot figure
        self.fig = px.scatter(self.df, **params)
        return self.fig

    def plot_line(self, **kwargs) -> px.line:
        """
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate line plot figure
        self.fig = px.line(self.df, **params)
        return self.fig

    def plot_bar(self, **kwargs) -> px.bar:
        """
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate bar plot figure
        self.fig = px.bar(self.df, **params)
        return self.fig

    def plot_area(self, **kwargs) -> px.area:
        """
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate area plot figure
        self.fig = px.area(self.df, **params)
        return self.fig

    def plot_pie(self, **kwargs) -> px.pie:
        """
        """
        # Define plot parameters
        params = {**self.default_kwargs, **kwargs}

        # Generate pie plot figure
        self.fig = px.pie(self.df, **params)
        return self.fig

    def group_x_axis(self,
                     groupby_metric: str):
        """
        """
        # Group x axis by groupby_metric variable
        self.fig.update_layout(xaxis=dict(type='category',
                                          categoryorder='array',
                                          categoryarray=sorted(self.df[groupby_metric])),
                               uniformtext_minsize=8,
                               uniformtext_mode='hide')

        return self.fig
