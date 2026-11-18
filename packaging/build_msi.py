"""Build the per-user Pixel Shelf MSI on Windows with CPython 3.12 (py -3.12)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import re
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET

import msilib as msi
from msilib import schema, sequence


ROOT = Path(__file__).resolve().parents[1]
UPGRADE_ID = uuid.UUID("b13d2a45-f798-4a93-bd14-2c60e1b67542")
VERSION = "1.0.0"


def guid(key):
    return "{" + str(uuid.uuid5(UPGRADE_ID, key)).upper() + "}"


def collect_payload(executable):
    files = {"PixelShelf.exe": executable, "Shelf.xml": ROOT / "Shelf.xml"}
    scenes = ET.parse(files["Shelf.xml"]).getroot().findall("scene")
    if not scenes:
        raise ValueError("Shelf.xml contains no scenes")
    for scene in scenes:
        filename = scene.attrib["frames"]
        player = scene.attrib["player"]
        if not re.fullmatch(r"(films/)?[A-Za-z0-9_]+\.frames", filename):
            raise ValueError(f"Invalid film path {filename}")
        if not re.fullmatch(r"[A-Za-z0-9_]+\.ps1", player):
            raise ValueError(f"Invalid player path {player}")
        film = ROOT / filename
        expected = int(scene.attrib["fps"]) * int(scene.attrib["seconds"]) * 832
        if film.stat().st_size != expected:
            raise ValueError(f"Incomplete film {filename}")
        files[filename] = film
        files[player] = ROOT / player
    return files


def add_interface(db):
    msi.add_data(db, "TextStyle", [
        ("Body", "Segoe UI", 9, 0, 0), ("Heading", "Segoe UI", 14, 0, 1)])
    msi.add_data(db, "Property", [("DefaultUIFont", "Body")])

    def dialog(name, heading, text, default, cancel="Cancel"):
        d = msi.Dialog(db, name, 50, 50, 300, 136, 7, "Pixel Shelf Setup",
                       default, default, cancel)
        d.text("Title", 14, 10, 270, 18, 3, "{\\Heading}" + heading)
        d.text("Details", 15, 38, 268, 53, 3, text)
        d.line("Separator", 0, 100, 300, 1)
        return d

    def button(d, name, x, title, following, result):
        ctrl = d.pushbutton(name, x, 111, 60, 17, 3, title, following)
        ctrl.event("EndDialog", result, ordering=10)
        return ctrl

    intro = dialog("Welcome", "Install Pixel Shelf",
                   "Install the OLED animation library for your Windows account. "
                   "SteelSeries GG with Engine running is required for headset playback.", "Install")
    button(intro, "Install", 153, "&Install", "Cancel", "Return")
    button(intro, "Cancel", 223, "Cancel", "Install", "Exit")

    manage = dialog("Maintain", "Manage Pixel Shelf",
                    "Repair the installed program and films, or remove them from this account. "
                    "Your saved playlist is kept.", "Repair")
    repair = button(manage, "Repair", 82, "&Repair", "Remove", "Return")
    repair.event("[REINSTALL]", "ALL", ordering=1)
    repair.event("[REINSTALLMODE]", "amus", ordering=2)
    remove = button(manage, "Remove", 153, "R&emove", "Cancel", "Return")
    remove.event("[REMOVE]", "ALL", ordering=1)
    button(manage, "Cancel", 223, "Cancel", "Repair", "Exit")

    done = dialog("Complete", "Setup complete",
                  "Pixel Shelf Setup finished successfully.", "Finish", "Finish")
    # Launch exclusively on a user's click in the interactive installer UI.
    open_button = button(done, "Launch", 150, "&Open shelf", "Finish", "Return")
    open_button.condition("Hide", 'REMOVE~="ALL"')
    open_button.event("DoAction", "LaunchShelf", ordering=1)
    button(done, "Finish", 223, "&Finish", "Launch", "Return")
    for name, heading, message in [
        ("Failure", "Setup failed", "Windows Installer could not finish this operation."),
        ("Cancelled", "Setup cancelled", "Pixel Shelf Setup was cancelled.")]:
        dlg = dialog(name, heading, message, "Close", "Close")
        button(dlg, "Close", 223, "&Close", "Close", "Return")

    msi.add_data(db, "InstallUISequence", [
        ("FindRelatedProducts", None, 25), ("LaunchConditions", None, 100),
        ("CostInitialize", None, 800), ("FileCost", None, 900), ("CostFinalize", None, 1000),
        ("Welcome", "NOT Installed", 1100),
        ("Maintain", "Installed AND NOT REMOVE AND NOT REINSTALL", 1101),
        ("ExecuteAction", None, 1300),
        ("Complete", None, -1), ("Cancelled", None, -2), ("Failure", None, -3)])
    msi.add_data(db, "CustomAction", [("LaunchShelf", 210, "F_PixelShelf.exe", None)])


def build(temp, output):
    executable = temp / "PixelShelf.exe"
    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(ROOT / "Build-App.ps1"), "-OutputPath", str(executable)], check=True)
    files = collect_payload(executable)
    package = temp / output.name
    db = msi.init_database(str(package), schema, "Pixel Shelf", guid("release/" + VERSION),
                           VERSION, "Pixel Shelf")
    info = db.GetSummaryInformation(20)
    info.SetProperty(msi.PID_TEMPLATE, "Intel;1033")  # The AnyCPU application also runs on x64.
    info.SetProperty(msi.PID_PAGECOUNT, 405)
    info.SetProperty(msi.PID_WORDCOUNT, 10)  # Compressed long filenames, limited user privileges.
    info.Persist()
    del info
    upgrade = "{" + str(UPGRADE_ID).upper() + "}"
    msi.add_data(db, "Property", [
        ("UpgradeCode", upgrade), ("INSTALLLEVEL", "1"),
        ("SecureCustomProperties", "EARLIERPRODUCTS;NEWERPRODUCTS"),
        ("ARPNOMODIFY", "1")])
    msi.add_data(db, "Upgrade", [
        (upgrade, None, VERSION, None, 0, None, "EARLIERPRODUCTS"),
        (upgrade, VERSION, None, None, 2, None, "NEWERPRODUCTS")])
    msi.add_data(db, "LaunchCondition", [
        ("Installed OR NOT NEWERPRODUCTS", "A newer version of Pixel Shelf is already installed.")])
    msi.add_data(db, "Directory", [
        ("TARGETDIR", None, "SourceDir"), ("LocalAppDataFolder", "TARGETDIR", "."),
        ("ProgramsDir", "LocalAppDataFolder", "Programs"), ("INSTALLDIR", "ProgramsDir", "PixelShelf"),
        ("FILMS", "INSTALLDIR", "films"), ("ProgramMenuFolder", "TARGETDIR", ".")])
    msi.add_data(db, "Feature", [("Library", None, "Pixel Shelf", "Player and animations",
                                  1, 1, "INSTALLDIR", 0)])
    cab = msi.CAB("PixelShelf.cab")
    for n, (path, src) in enumerate(sorted(files.items()), start=1):
        name = src.name
        directory = "FILMS" if path.startswith("films/") else "INSTALLDIR"
        ident = msi.make_id(path)
        component, reg, fileid = "C_" + ident, "R_" + ident, "F_" + ident
        msi.add_data(db, "Component", [(component, guid(path), directory, 4, None, reg)])
        msi.add_data(db, "FeatureComponents", [("Library", component)])
        msi.add_data(db, "Registry", [
            (reg, 1, r"Software\PixelShelf\Installer", ident, VERSION, component)])
        msi.add_data(db, "File", [
            (fileid, component, f"P{n:07d}.{src.suffix[1:4]}|{name}", src.stat().st_size,
             VERSION + ".0" if path == "PixelShelf.exe" else None, None, 512, n)])
        cab.append(str(src), name, fileid)

    msi.add_data(db, "Shortcut", [
        ("StartPixelShelf", "ProgramMenuFolder", "PIXELS~1|Pixel Shelf", "C_PixelShelf.exe",
         "[#F_PixelShelf.exe]", None, "Pixel Shelf OLED animation library", None, None,
         None, 1, "INSTALLDIR")])
    execute = list(sequence.InstallExecuteSequence)
    msi.change_sequence(execute, "FindRelatedProducts", 25)
    msi.change_sequence(execute, "RemoveExistingProducts", 1510)
    msi.add_data(db, "InstallExecuteSequence", execute)
    msi.add_data(db, "AdminExecuteSequence", sequence.AdminExecuteSequence)
    add_interface(db)
    cab.commit(db)
    db.Close()
    output.parent.mkdir(parents=True, exist_ok=True)
    # A Windows TemporaryDirectory has a private ACL. Create the distributable
    # in its destination directory so it inherits the normal release-file ACL.
    staged = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
    try:
        shutil.copyfile(package, staged)
        staged.replace(output)
    finally:
        staged.unlink(missing_ok=True)
    print(f"{output} ({len(files)} payload files)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / f"PixelShelf-{VERSION}.msi")
    output = parser.parse_args().output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".msibuild-", dir=output.parent) as scratch:
        build(Path(scratch), output)
