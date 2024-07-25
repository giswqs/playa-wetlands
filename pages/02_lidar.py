import geemap
import solara
import ee

zoom = solara.reactive(4)
center = solara.reactive((40, -100))


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add what you want below
        self.add_data()
        self.add_layer_manager(opened=False)

    def add_data(self, **kwargs):
        url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        self.add_tile_layer(url, name="Google Satellite", attribution="Google")

        dem_wms = "https://elevation.nationalmap.gov/arcgis/services/3DEPElevation/ImageServer/WMSServer"
        layer = "3DEPElevation:Hillshade Multidirectional"
        self.add_wms_layer(
            url=dem_wms, layers=layer, name="Hillshade", format="image/png", shown=True
        )

        huc12 = ee.FeatureCollection("USGS/WBD/2017/HUC12")
        collection = ee.ImageCollection("USGS/3DEP/1m")
        style = {"color": "0000ff88", "fillColor": "00000000", "width": 1}

        self.add_layer(
            collection, {"min": 0, "max": 4000, "palette": "terrain"}, "3DEP", True, 0.5
        )

        nwi_wms = "https://fwspublicservices.wiself.usgs.gov/wetlandsmapservice/services/Wetlands/MapServer/WMSServer"
        self.add_wms_layer(url=nwi_wms, layers="1", name="NWI", format="image/png")

        # self.add_layer(huc12, {}, "HU-12 Vector", False)
        self.add_layer(
            huc12.style(**style),
            {},
            "HU-12",
        )


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        # solara components support reactive variables
        # solara.SliderInt(label="Zoom level", value=zoom, min=1, max=20)
        # using 3rd party widget library require wiring up the events manually
        # using zoom.value and zoom.set
        Map.element(  # type: ignore
            zoom=zoom.value,
            on_zoom=zoom.set,
            center=center.value,
            on_center=center.set,
            scroll_wheel_zoom=True,
            height="750px",
        )
        # solara.Text(f"Zoom: {zoom.value}")
        # solara.Text(f"Center: {center.value}")
