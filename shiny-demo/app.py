from shiny import App, ui, render
import matplotlib.pyplot as plt
import numpy as np

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("Histogram Controls"),
        ui.input_slider(
            "bins",
            "Number of Bins",
            min=5, max=30, value=10, step=1
            ),
    ),
    ui.h3("Interactive Histogram"),
    ui.output_plot("hist_plot"),
)

def server(input, output, session):
    @render.plot(alt="A histogram of random data")
    def hist_plot():
        np.random.seed(123)
        x = 100 + 15 * np.random.randn(456)
        plt.hist(
            x,
            bins=input.bins(),
            density=True
        )
        plt.title("Histogram of Random Data")
        plt.xlabel("Value")
        plt.ylabel("Frequency")

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()