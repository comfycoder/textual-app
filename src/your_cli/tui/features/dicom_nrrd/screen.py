"""Demo: DICOM → NRRD batch conversion metrics dashboard."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from your_cli.tui.widgets import (
    ActivityCard,
    AlertCard,
    KVCard,
    MetricCard,
    ProgressCard,
    SparklineCard,
    TimelineCard,
)


class DicomNrrdDemoScreen(Screen[None]):
    """DICOM → NRRD batch conversion metrics dashboard."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [Binding("escape", "go_back", "Back")]

    # Throughput samples (series / min) over the last 24 one-minute windows
    _THROUGHPUT: list[float] = [
        0.0, 1.2, 2.8, 3.4, 3.1, 2.9, 3.6, 4.1, 3.8, 3.5,
        3.2, 2.7, 3.9, 4.3, 4.0, 3.7, 3.4, 3.2, 3.0, 2.8,
        3.1, 3.3, 2.9, 2.4,
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="dn-body"):

            # ── Batch overview ────────────────────────────────────────────
            yield Static(
                "[b]Batch Overview[/b]  "
                "[dim]conv-20260524-001  ·  CT / MR import  ·  JHU PACS[/dim]",
                classes="dn-section",
            )
            with Horizontal(classes="dn-row"):
                yield MetricCard(
                    "Total series", "24",
                    trend="flat", detail="8.4 GB raw DICOM input",
                )
                yield MetricCard(
                    "Completed", "18",
                    trend="up",  detail="75 % of batch  ·  13.2 GB NRRD output",
                )
                yield MetricCard(
                    "Failed", "3",
                    trend="down", detail="DN-004, DN-007, DN-009",
                )
                yield MetricCard(
                    "Skipped", "1",
                    trend="flat", detail="unsupported transfer syntax",
                )

            # ── Progress & throughput ─────────────────────────────────────
            yield Static(
                "[b]Conversion Progress[/b]",
                classes="dn-section",
            )
            with Horizontal(classes="dn-row"):
                yield ProgressCard(
                    "Batch  (series completed)",
                    18, total=24,
                    subtitle="18 of 24 series  ·  2 active  ·  3 failed  ·  1 skipped",
                    footer="Elapsed: 6 m 14 s  ·  ETA ~2 m  ·  wall-clock",
                )
                yield SparklineCard(
                    "Throughput  (series / min, last 24 min)",
                    self._THROUGHPUT,
                    [("Peak", "4.3 / min"), ("Avg", "3.1 / min"), ("Now", "2.4 / min")],
                )
                yield ProgressCard(
                    "Active  ·  CT Chest Axial  (series 19)",
                    420, total=512,
                    subtitle="Slice 420 of 512  ·  pixel data extraction",
                    footer="Node: conv-worker-02  ·  ETA ~8 s",
                )

            # ── Active series detail ──────────────────────────────────────
            yield Static(
                "[b]Active Series Detail[/b]  "
                "[dim]CT Chest Axial  ·  1.2.840.10008.5.1.4.1.1.2  ·  series 19 of 24[/dim]",
                classes="dn-section",
            )
            with Horizontal(classes="dn-row"):
                yield TimelineCard("Pipeline stages", [
                    ("00:00", "DICOM header parse",       "done"),
                    ("00:01", "Header validation",        "done"),
                    ("00:03", "Slice ordering",           "done"),
                    ("00:04", "Pixel data extraction",    "active"),
                    ("—",     "NRRD encoding (gzip)",     "pending"),
                    ("—",     "Checksum & output write",  "pending"),
                ])
                yield KVCard("Volume metadata", [
                    ("Modality",      "CT"),
                    ("Dimensions",    "512 × 512 × 512 vx"),
                    ("Voxel spacing", "0.625 × 0.625 × 1.0 mm"),
                    ("Orientation",   "Axial (LPS)"),
                    ("Bit depth",     "16-bit signed int"),
                    ("HU range",      "−1024 → 3071"),
                    ("Body part",     "Chest"),
                    ("Series date",   "2026-05-20"),
                ])
                yield KVCard("File stats", [
                    ("DICOM files",     "412 files"),
                    ("Input size",      "387.4 MB"),
                    ("NRRD output",     "156.2 MB  (est.)"),
                    ("Compression",     "~59.7 %  saved"),
                    ("Encoding",        "gzip level 6"),
                    ("Transfer syntax", "Explicit VR LE"),
                    ("SOP class",       "CT Image Storage"),
                    ("Worker node",     "conv-worker-02"),
                ])

            # ── Validation issues ─────────────────────────────────────────
            yield Static(
                "[b]Validation Issues[/b]  [dim]4 issues across this batch[/dim]",
                classes="dn-section",
            )
            with Horizontal(classes="dn-row"):
                yield AlertCard(
                    "error",
                    "Missing slices  ·  series DN-007",
                    "Expected 256 slices; received 249. Gap detected at "
                    "positions 128–134. Output NRRD skipped — re-export required.",
                )
                yield AlertCard(
                    "warning",
                    "Irregular spacing  ·  series DN-015",
                    "Slice intervals vary from 0.9 mm to 1.3 mm (threshold 5 %). "
                    "Conversion proceeds; downstream tools should resample to isotropic.",
                )
                yield AlertCard(
                    "warning",
                    "Gantry tilt  ·  series DN-003",
                    "Gantry tilt angle 12.4°. NRRD written with corrected direction "
                    "cosines. Verify alignment with any atlas or segmentation model.",
                )
                yield AlertCard(
                    "info",
                    "Lossy source  ·  series DN-011",
                    "Source DICOM uses JPEG 2000 lossy compression (~8:1 ratio). "
                    "NRRD preserves decoded pixel values; original fidelity is not recoverable.",
                )

            # ── Completion log ────────────────────────────────────────────
            yield Static(
                "[b]Completion Log[/b]  [dim]most recent first[/dim]",
                classes="dn-section",
            )
            with Horizontal(classes="dn-row"):
                yield ActivityCard("Series events", [
                    ("success", "DN-018  CT Chest Ax    512×512×512  →  chest_018.nrrd",             "28 s ago"),
                    ("success", "DN-017  CT Abdomen Ax  512×512×368  →  abdomen_017.nrrd",           "1 m ago"),
                    ("error",   "DN-007  Export skipped — missing 7 slices (see warnings)",          "1 m ago"),
                    ("success", "DN-016  MR Brain FLAIR 256×256×176  →  brain_016.nrrd",             "2 m ago"),
                    ("warning", "DN-015  CT Pelvis Ax   512×512×280  →  pelvis_015.nrrd  [irreg. spacing]", "3 m ago"),
                    ("success", "DN-014  CT Chest Ax    512×512×420  →  chest_014.nrrd",             "4 m ago"),
                    ("error",   "DN-009  Header parse failed — mixed series UIDs detected",          "4 m ago"),
                    ("success", "DN-013  MR Spine Sag   512×512×144  →  spine_013.nrrd",             "5 m ago"),
                    ("error",   "DN-004  OOM — pixel buffer exceeded 2 GB worker limit",             "5 m ago"),
                    ("success", "DN-012  CT Head Ax     512×512×300  →  head_012.nrrd",              "6 m ago"),
                ])

        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()
