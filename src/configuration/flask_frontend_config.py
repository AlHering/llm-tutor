# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
global_config = {
    "page_title": "Aura Cognitive Architecture",
    "page_icon_path": "img/icons/favicon.ico"
}
endpoint_config = {
    "endpoints": {
        "index": "",
        "docker": "",
        "models": "",
    }
}
# Note that icons are xlink or font-awesome references
menu_config = {
    "menus": {
        "docker_control": {
            "#meta": {
                "icon": "#real-estate-1",
                "type": "xl",
            },
            "Environment": {
                "icon": "#real-estate-1",
                "type": "xl",
                "href": "index"
            },
            "Blueprints": {
                "icon": "#browser-window-1",
                "type": "xl",
                "href": "#docker_control_blueprints_dropdown",
                "dropdown": {
                    "Environments": {
                        "href": "index"
                    },
                    "Agents": {
                        "href": "index"
                    },
                    "Interfaces": {
                        "href": "index"
                    }
                }
            }
        },
        "model_control": {
            "#meta": {
                "icon": "#real-estate-1",
                "type": "xl",
            },
            "Models Overview": {
                "icon": "bed",
                "type": "fa",
                "href": "index",
                "flag": {
                    "type": "warning",
                    "text": "6 New"
                }
            },
            "Sources": {
                "icon": "bed",
                "type": "fa",
                "href": "index"
            },
            "Utility": {
                "icon": "#browser-window-1",
                "type": "xl",
                "href": "#model_control_utility_dropdown",
                "dropdown": {
                    "Training": {
                        "href": "index"
                    },
                    "Finetuning": {
                        "href": "index"
                    },
                    "Embeddings": {
                        "href": "index"
                    }
                }
            }
        },
        "datasets": {
            "#meta": {
                "icon": "#real-estate-1",
                "type": "xl",
            },
            "Dataset Overview": {
                "icon": "bed",
                "type": "fa",
                "href": "index",
                "flag": {
                    "type": "warning",
                    "text": "6 New"
                }
            },
            "Pipelines": {
                "icon": "bed",
                "type": "fa",
                "href": "index"
            },
            "Utility": {
                "icon": "#browser-window-1",
                "type": "xl",
                "href": "#datasets_utility_dropdown",
                "dropdown": {
                    "Extractors": {
                        "href": "index"
                    },
                    "Transformers": {
                        "href": "index"
                    },
                    "Loaders": {
                        "href": "index"
                    }
                }
            }
        }
    }
}

for dictionary in [endpoint_config, menu_config]:
    global_config.update(dictionary)
