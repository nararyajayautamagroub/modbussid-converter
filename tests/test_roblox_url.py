import pytest

from shared.roblox_url import asset_id_from_url


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("https://www.roblox.com/asset/?id=12345", 12345),
        ("https://www.roblox.com/library/12345", 12345),
        ("https://create.roblox.com/store/asset/12345/example", 12345),
        ("rbxassetid://12345", 12345),
    ],
)
def test_asset_id_variants(value, expected):
    assert asset_id_from_url(value) == expected


def test_asset_id_rejects_untrusted_host():
    with pytest.raises(ValueError):
        asset_id_from_url("https://example.com/asset/?id=12345")


def test_asset_id_rejects_non_https_url():
    with pytest.raises(ValueError):
        asset_id_from_url("http://www.roblox.com/asset/?id=12345")
