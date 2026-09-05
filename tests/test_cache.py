import unittest
from pathlib import Path

from artifacter_image_gen.cache import CACHE_ENV, default_cache_dir


class DefaultCacheDirTests(unittest.TestCase):
    def test_explicit_override_wins(self):
        result = default_cache_dir({CACHE_ENV: "C:/custom/cache"}, "win32", Path("C:/home"))
        self.assertEqual(result, Path("C:/custom/cache"))

    def test_windows_uses_local_app_data(self):
        result = default_cache_dir(
            {"LOCALAPPDATA": "C:/Users/test/AppData/Local"},
            "win32",
            Path("C:/Users/test"),
        )
        self.assertEqual(result, Path("C:/Users/test/AppData/Local/artifacter-image-gen"))

    def test_linux_honors_xdg_cache_home(self):
        result = default_cache_dir(
            {"XDG_CACHE_HOME": "/var/cache/test"}, "linux", Path("/home/test")
        )
        self.assertEqual(result, Path("/var/cache/test/artifacter-image-gen"))


if __name__ == "__main__":
    unittest.main()
