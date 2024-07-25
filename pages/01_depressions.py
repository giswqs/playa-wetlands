import ee
import geemap

import solara
import ipywidgets as widgets
import ipyleaflet

zoom = solara.reactive(4)
center = solara.reactive([40, -100])


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_layer_manager(opened=False)
        # self.add_layer_manager(opened=False)
        self.add_data()
        names = ["NED 10m", "Depressions", "NWI Vector"]
        # self.add_buttons()
        self.add_inspector(names=names, visible=False, opened=True)

    def add_data(self):

        url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        self.add_tile_layer(url, name="Google Satellite", attribution="Google")

        n_layers = 9

        self.setCenter(-99.00, 47.01, 8)

        ned = ee.Image("USGS/3DEP/10m")
        hillshade = ee.Terrain.hillshade(ned)
        # Map.addLayer(hillshade, {}, "CONUS Hillshade", False)

        conus = ee.Geometry.BBox(-127.18, 19.39, -62.75, 51.29)

        huc8 = ee.FeatureCollection("USGS/WBD/2017/HUC08").filterBounds(conus)
        pipestem_hu8 = ee.FeatureCollection("users/giswqs/Pipestem/Pipestem_HUC8")

        style = {"color": "00000088", "fillColor": "00000000", "width": 1}

        palette = ["006633", "E5FFCC", "662A00", "D8D8D8", "F5F5F5"]
        self.addLayer(
            ned, {"min": 0, "max": 4000, "palette": palette}, "NED 10m", False
        )
        self.addLayer(hillshade, {}, "NED Hillshade", False)

        states = ee.FeatureCollection("TIGER/2018/States")
        floodplain = ee.FeatureCollection("users/giswqs/floodplain/GFP250m")

        gfplain250 = ee.Image("projects/sat-io/open-datasets/GFPLAIN250/NA")
        states = ee.FeatureCollection("users/giswqs/public/us_states")
        fp_image = gfplain250.clipToCollection(states)
        self.addLayer(fp_image, {"palette": "#002B4D"}, "Floodplain raster", False)

        fp_style = {"fillColor": "0000ff88"}
        self.addLayer(floodplain.style(**fp_style), {}, "Floodplain vector", False)
        self.addLayer(huc8, {}, "NHD-HU8 Vector", False)
        self.addLayer(huc8.style(**style), {}, "NHD-HU8 Raster")
        self.addLayer(
            pipestem_hu8.style(
                **{"color": "ffff00ff", "fillColor": "00000000", "width": 2}
            ),
            {},
            "Pipestem HU8",
        )

        self.add_legend(
            builtin_legend="NWI", position="bottomleft", title="NWI Wetland Type"
        )

        def add_buttons(self, opened=True):

            widget_width = "250px"
            padding = "0px 0px 0px 5px"  # upper, right, bottom, left
            style = {"description_width": "initial"}

            toolbar_button = widgets.ToggleButton(
                value=False,
                tooltip="Toolbar",
                icon="hand-o-up",
                layout=widgets.Layout(
                    width="28px", height="28px", padding="0px 0px 0px 4px"
                ),
            )

            close_button = widgets.ToggleButton(
                value=False,
                tooltip="Close the tool",
                icon="times",
                button_style="primary",
                layout=widgets.Layout(
                    height="28px", width="28px", padding="0px 0px 0px 4px"
                ),
            )

            buttons = widgets.ToggleButtons(
                value=None,
                options=["Watershed", "Inspector", "Deactivate"],
                tooltips=["Apply", "Reset", "Close"],
                button_style="primary",
            )
            buttons.style.button_width = "87px"
            # buttons.value = "Watershed"

            label = widgets.Label(
                "Click on the map to select a watershed",
                padding="0px 0px 0px 4px",
                style=style,
            )

            output = widgets.Output(
                layout=widgets.Layout(width=widget_width, padding=padding)
            )
            toolbar_widget = widgets.VBox()
            toolbar_widget.children = [toolbar_button]
            toolbar_header = widgets.HBox()
            toolbar_header.children = [close_button, toolbar_button]
            toolbar_footer = widgets.VBox()
            toolbar_footer.children = [
                buttons,
                label,
                output,
            ]

            def toolbar_btn_click(change):
                if change["new"]:
                    close_button.value = False
                    toolbar_widget.children = [toolbar_header, toolbar_footer]
                else:
                    if not close_button.value:
                        toolbar_widget.children = [toolbar_button]

            toolbar_button.observe(toolbar_btn_click, "value")

            def close_btn_click(change):
                if change["new"]:
                    toolbar_button.value = False
                    self.toolbar_reset()
                    if (
                        self.tool_control is not None
                        and self.tool_control in self.controls
                    ):
                        self.remove_control(self.tool_control)
                        self.tool_control = None
                    toolbar_widget.close()

            close_button.observe(close_btn_click, "value")

            def button_clicked(change):
                if change["new"] == "Watershed":
                    label.value = "Click on the map to select a watershed"

                    def handle_interaction(**kwargs):
                        latlon = kwargs.get("coordinates")
                        if (
                            kwargs.get("type") == "click"
                            and buttons.value == "Watershed"
                        ):
                            self.layers = self.layers[:n_layers]
                            self.default_style = {"cursor": "wait"}
                            clicked_point = ee.Geometry.Point(latlon[::-1])
                            selected = huc8.filterBounds(clicked_point)
                            watershed_bbox = selected.geometry().bounds()
                            huc_id = selected.first().get("huc8").getInfo()
                            self.addLayer(
                                selected.style(
                                    **{"color": "ff0000ff", "fillColor": "00000000"}
                                ),
                                {},
                                "HU8-" + huc_id,
                            )

                            label.value = f"Watershed HU8: {huc_id}"

                            hillshade_clip = hillshade.clipToCollection(selected)
                            self.addLayer(hillshade_clip, {}, "Hillshade")
                            depression_id = "users/giswqs/depressions/" + huc_id
                            depressions = ee.FeatureCollection(depression_id)
                            try:
                                self.addLayer(depressions, {}, "Depressions")
                            except Exception as e:
                                print(e)
                            nwi_id = "users/giswqs/NWI-HU8/HU8_" + huc_id + "_Wetlands"
                            try:
                                nwi = ee.FeatureCollection(nwi_id)
                                self.addLayer(nwi, {}, "NWI Vector")
                            except Exception as e:
                                print(e)

                            types = [
                                "Freshwater Forested/Shrub Wetland",
                                "Freshwater Emergent Wetland",
                                "Freshwater Pond",
                                "Estuarine and Marine Wetland",
                                "Riverine",
                                "Lake",
                                "Estuarine and Marine Deepwater",
                                "Other",
                            ]

                            colors = [
                                "#008837",
                                "#7FC31C",
                                "#688CC0",
                                "#66C2A5",
                                "#0190BF",
                                "#13007C",
                                "#007C88",
                                "#B28653",
                            ]

                            fillColor = [c + "A8" for c in colors]
                            nwi_color = geemap.ee_vector_style(
                                nwi,
                                column="WETLAND_TY",
                                labels=types,
                                fillColor=fillColor,
                                color="00000000",
                            )

                            self.addLayer(nwi_color, {}, "NWI Raster")
                            # sel_state = states.filterBounds(clicked_point).first().get('STUSPS').getInfo()
                            # asset = 'projects/sat-io/open-datasets/NHD/NHD_' + sel_state + '/'
                            # nhd_water = ee.FeatureCollection(asset + 'NHDWaterbody')
                            # nhd_area = ee.FeatureCollection(asset + 'NHDArea')
                            # nhd_flowline = ee.FeatureCollection(asset + 'NHDFlowline')
                            # nhd_line = ee.FeatureCollection(asset + 'NHDLine')

                            self.default_style = {"cursor": "default"}

                    self.on_interaction(handle_interaction)

                    with output:
                        output.clear_output()
                        print("Running ...")
                elif change["new"] == "Inspector":
                    label.value = "Click on the map to inspect data"
                    output.clear_output()
                elif change["new"] == "Deactivate":
                    buttons.value = None
                    label.value = "Click on the map to select a watershed"

                # buttons.value = None

            buttons.observe(button_clicked, "value")
            buttons.value = "Watershed"

            toolbar_button.value = opened
            buttons_control = ipyleaflet.WidgetControl(
                widget=toolbar_widget, position="topright"
            )

            if buttons_control not in self.controls:
                self.add_control(buttons_control)
                self.tool_control = buttons_control

        add_buttons(self, opened=True)


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        Map.element(  # type: ignore
            zoom=zoom.value,
            on_zoom=zoom.set,
            center=center.value,
            on_center=center.set,
            height="750px",
            # scroll_wheel_zoom=True,
            # height="600px",
        )
