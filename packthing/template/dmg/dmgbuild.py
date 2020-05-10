format = "UDZO"

files = [
    "${bundle_name}",
]

symlinks = {
    "Applications": "/Applications",
}

icon = "${icon_path}"

icon_locations = {"${bundle_name}": (105, 180), "Applications": (395, 180)}

background = "${background_path}"

window_rect = ((200, 400), (500, 375))

icon_size = 72
