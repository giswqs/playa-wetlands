import os
import ee
import geemap
import ipywidgets as widgets
from IPython.display import display
import solara


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_basemap("Esri.WorldImagery")
        self.add_gui("timelapse", basemap=None)
        self.add_ee_data()

    def add_ee_data(self):

        url = "https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/services/Wetlands/MapServer/WMSServer?"
        self.add_wms_layer(
            url,
            layers="1",
            format="image/png",
            transparent=True,
            opacity=0.7,
            name="NWI Wetlands",
        )

        style = {
            "color": "000000ff",
            "width": 2,
            "lineType": "solid",
            "fillColor": "FF000000",
        }
        states = ee.FeatureCollection("TIGER/2018/States")
        self.addLayer(states.style(**style), {}, "US States")

        fc = ee.FeatureCollection("projects/ee-giswqs/assets/Playa/High_Plains")

        style = {
            "color": "ff0000ff",
            "width": 2,
            "lineType": "solid",
            "fillColor": "FF000000",
        }
        self.add_layer(fc.style(**style), {}, "High Plains")

        self.add_legend(
            builtin_legend="NWI",
            position="bottomleft",
            add_header=False,
            title="Wetland Type",
        )


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        Map.element(
            center=[37.6045093, -102.414550],
            zoom=6,
            height="750px",
            zoom_ctrl=False,
            measure_ctrl=False,
        )
