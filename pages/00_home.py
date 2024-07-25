import solara


@solara.component
def Page():
    markdown = """
    ## Solara for Geospatial Applications
    
    ### Introduction

    An interactive web app for mapping Playa wetlands.

    - Web App: <https://giswqs-playa-wetlands.hf.space>
    - GitHub: <https://github.com/giswqs/playa-wetlands>
    - Hugging Face: <https://huggingface.co/spaces/giswqs/playa-wetlands>

    """

    solara.Markdown(markdown)
