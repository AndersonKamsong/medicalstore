from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe


class CloudinaryImageWidget(ClearableFileInput):
    """
    Admin image widget showing a thumbnail, storage badge (Cloudinary vs local),
    and a URL link above the standard file input.
    """

    def render(self, name, value, attrs=None, renderer=None):
        parts = []

        if value and hasattr(value, 'url'):
            try:
                url = value.url
                is_cloudinary = 'cloudinary.com' in url

                parts.append(
                    f'<div style="margin-bottom:10px;">'
                    f'<img src="{url}" style="width:150px;height:150px;'
                    f'object-fit:cover;border-radius:6px;border:2px solid #ddd;display:block;" />'
                    f'</div>'
                )

                if is_cloudinary:
                    badge = (
                        '<span style="display:inline-block;background:#4CAF50;color:white;'
                        'padding:3px 10px;border-radius:12px;font-size:11px;font-weight:bold;'
                        'margin-bottom:6px;">&#9729; Current image stored on Cloudinary</span>'
                    )
                else:
                    badge = (
                        '<span style="display:inline-block;background:#FF9800;color:white;'
                        'padding:3px 10px;border-radius:12px;font-size:11px;font-weight:bold;'
                        'margin-bottom:6px;">&#9888; Stored locally</span>'
                    )
                parts.append(badge)

                display_url = url if len(url) <= 80 else url[:77] + '...'
                parts.append(
                    f'<br><a href="{url}" target="_blank" rel="noopener" '
                    f'style="font-size:11px;color:#4CAF50;word-break:break-all;">'
                    f'{display_url}</a><br><br>'
                )
            except Exception:
                pass

        parts.append(super().render(name, value, attrs, renderer=renderer))
        return mark_safe(''.join(parts))
