# Import python dependencies
import plotly.express as px
import pandas as pd

class PlotlyPlotter:
    def __init__(self, df: pd.DataFrame, **kwargs):
        self.df = df
        self.default_kwargs = kwargs
        self.fig = None

    def plot_line(self, **kwargs) -> px.line:
        params = {**self.default_kwargs, **kwargs}
        self.fig = px.line(self.df, **params)

    def plot_bar(self, **kwargs) -> px.bar:
        params = {**self.default_kwargs, **kwargs}
        self.fig = px.bar(self.df, **params)

    def plot_area(self, **kwargs) -> px.area:
        params = {**self.default_kwargs, **kwargs}
        self.fig = px.area(self.df, **params)

    def group_x_axis(self,
                     groupby_metric: str):
        """
        """
        self.fig.update_layout(xaxis=dict(type='category',
                                          categoryorder='array',
                                          categoryarray=sorted(self.df[groupby_metric])),
                               uniformtext_minsize=8,
                               uniformtext_mode='hide')

    def render_figure(self):
        """
        """
        return self.fig
