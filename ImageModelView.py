from flask import url_for
from markupsafe import Markup
from flask_admin.contrib.sqla import ModelView

class ImageModelView(ModelView):
    column_formatters = {
        'img_plate_url': lambda v, c, m, p: Markup(f"""
            <img src="{url_for("static", filename="uploads/" + m.img_plate_url)}" 
                 class="zoomable-img" 
                 data-full="{url_for("static", filename="uploads/" + m.img_plate_url)}"
                 style="max-height: 100px; cursor: zoom-in;">
        """) if m.img_plate_url else '',

        'img_car_url': lambda v, c, m, p: Markup(f"""
            <img src="{url_for("static", filename="uploads/" + m.img_car_url)}" 
                 class="zoomable-img" 
                 data-full="{url_for("static", filename="uploads/" + m.img_car_url)}"
                 style="max-height: 100px; cursor: zoom-in;">
        """) if m.img_car_url else '',
    }