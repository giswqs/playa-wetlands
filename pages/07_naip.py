import ee
import geemap
import solara
import ipywidgets as widgets


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_basemap("Esri.WorldImagery", True)
        self.add_data()
        self._toolbar.toggle_layers(False)
        self.add_gui()

    def add_data(self):
        fc = ee.FeatureCollection("projects/ee-giswqs/assets/Playa/High_Plains")
        style = {
            "color": "000000ff",
            "width": 2,
            "lineType": "solid",
            "fillColor": "FF000000",
        }
        self.add_layer(fc.style(**style), {}, "Playa")
        convex = ee.FeatureCollection(
            "projects/ee-giswqs/assets/Playa/High_Plains_Convex_Hulls"
        )
        style = {
            "color": "ff0000ff",
            "width": 2,
            "lineType": "solid",
            "fillColor": "FF000000",
        }
        self.add_layer(convex.style(**style), {}, "Playa Convex Hulls")

    def add_gui(self):
        widget_width = "350px"
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left
        style = {"description_width": "initial"}
        button_width = "113px"

        text = widgets.Text(
            "Draw a rectangle on the map",
            layout=widgets.Layout(padding="0px", width="230px"),
        )

        bands = widgets.Dropdown(
            description="Bands:",
            options=[
                "Red/Green/Blue",
                "NIR/Red/Green",
            ],
            value="NIR/Red/Green",
            layout=widgets.Layout(width="230px", padding=padding),
            style=style,
        )

        apply_btn = widgets.Button(
            description="Time slider",
            button_style="primary",
            tooltip="Click to create timeseries",
            style=style,
            layout=widgets.Layout(padding="0px", width=button_width),
        )

        split_btn = widgets.Button(
            description="Split map",
            button_style="primary",
            tooltip="Click to create timeseries",
            style=style,
            layout=widgets.Layout(padding="0px", width=button_width),
        )
        widget = widgets.VBox([text, bands, widgets.HBox([apply_btn, split_btn])])
        self.add_widget(widget, position="topright")

        def apply_btn_click(b):
            if self.user_roi is not None:

                if bands.value == "NIR/Red/Green":
                    RGBN = True
                    vis_params = {"bands": ["N", "R", "G"], "min": 0, "max": 255}
                else:
                    RGBN = False
                    vis_params = {"bands": ["R", "G", "B"], "min": 0, "max": 255}
                collection = geemap.naip_timeseries(self.user_roi, RGBN=RGBN)
                if hasattr(self, "slider_ctrl") and self.slider_ctrl is not None:
                    self.remove(self.slider_ctrl)
                    delattr(self, "slider_ctrl")
                self.add_time_slider(
                    collection, vis_params=vis_params, date_format="YYYY"
                )

        apply_btn.on_click(apply_btn_click)

        def split_btn_click(b):
            if self.user_roi is not None:
                if bands.value == "NIR/Red/Green":
                    RGBN = True
                    vis_params = {"bands": ["N", "R", "G"], "min": 0, "max": 255}
                else:
                    RGBN = False
                    vis_params = {"bands": ["R", "G", "B"], "min": 0, "max": 255}
                collection = geemap.naip_timeseries(self.user_roi, RGBN=RGBN)

                self.ts_inspector(
                    collection,
                    left_vis=vis_params,
                    width="100px",
                    date_format="YYYY",
                    add_close_button=True,
                )

        split_btn.on_click(split_btn_click)


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        Map.element(
            center=[40, -100],
            zoom=4,
            height="750px",
            zoom_ctrl=False,
            measure_ctrl=False,
        )
