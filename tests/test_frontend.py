"""The page and the shared images in assets/ are both served."""

import re
from pathlib import Path

from fastapi.testclient import TestClient

from api import app


def test_every_image_the_page_links_to_is_served():
    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        images = re.findall(r'href="(assets/images/[^"]+)"', page.text)
        assert len(images) == 3
        for path in images:
            response = client.get(f"/{path}")
            assert response.status_code == 200, path
            assert response.content == Path(path).read_bytes()
