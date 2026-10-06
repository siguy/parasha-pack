"""next_version must not reuse the number of a version that was promoted to identity.png."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import generate_references as gr  # noqa: E402


def test_next_version_counts_accepted_version(tmp_path):
    folder = tmp_path / "chava"
    (folder / "alternates").mkdir(parents=True)
    (folder / "alternates" / "identity_v1.png").write_bytes(b"x")
    (folder / "identity.png").write_bytes(b"x")  # this used to be identity_v2.png
    (folder / "character.yaml").write_text("key: chava\nidentity: identity.png\nidentity_version: 2\n")
    assert gr.next_version(folder) == 3


def test_set_identity_version_adds_line(tmp_path):
    yaml_path = tmp_path / "character.yaml"
    yaml_path.write_text("key: adam\nidentity: identity.png\nname_en: Adam\n")
    gr.set_yaml_identity_version(yaml_path, 2)
    assert "identity: identity.png\nidentity_version: 2\n" in yaml_path.read_text()
