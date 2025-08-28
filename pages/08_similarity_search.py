import solara
import leafmap.maplibregl as leafmap
import geemap

geemap.ee_initialize()


def create_map():

    m = leafmap.Map(
        projection="globe",
        sidebar_visible=True,
        center=[-100, 40],
        zoom=2,
        height="750px",
    )
    google_hybrid = "https://mt1.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}"
    m.add_tile_layer(google_hybrid, name="Google Hybrid", attribution="Google")
    layer_name = "NWI Wetlands"
    m.add_nwi_basemap(name=layer_name, opacity=0.5)
    m.add_similarity_search(
        before_id=layer_name,
        default_year=2024,
        default_color="#0000ff",
        default_threshold=0.8,
    )
    m.add_draw_control(controls=["point", "trash"])
    return m


@solara.component
def Page():
    m = create_map()
    return m.to_solara()
