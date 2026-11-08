"""Archive a committed source snapshot after checking its public documentation."""
import argparse
import hashlib
import io
import re
import subprocess
import zipfile
from pathlib import Path
from check_release_docs import check_zip

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    version = subprocess.check_output(["git", "show", f"{commit}:VERSION"], cwd=ROOT, text=True).strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:_Test)?", version):
        raise ValueError("Invalid package version")
    name = f"Agmad_Silent_Cutter_Source_{version}"
    archive_path = args.output / (name + ".zip")
    checksum_path = archive_path.with_name(archive_path.name + ".sha256")
    if archive_path.exists() or checksum_path.exists():
        raise ValueError("Output exists; choose a fresh build folder")
    data = subprocess.check_output(
        ["git", "archive", "--format=zip", f"--prefix={name}/", commit], cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip():
            raise ValueError("ZIP integrity failure")
        failures = check_zip(archive)
    if failures:
        raise ValueError("Source documentation check failed:\n" + "\n".join(failures))
    args.output.mkdir(parents=True, exist_ok=True)
    with archive_path.open("xb") as output:
        output.write(data)
    with checksum_path.open("x", encoding="utf-8") as output:
        output.write(hashlib.sha256(data).hexdigest() + "  " + archive_path.name + "\n")
    print(f"Created {archive_path.name} from commit {commit}")

if __name__ == "__main__":
    main()
