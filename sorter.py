"""
sorter.py — Face recognition logic for KinderSort.

PhotoSorter loads reference encodings and sorts event photos into per-student
output folders. All processing is CPU-only (no GPU required).
"""

import logging
from collections.abc import Callable
from pathlib import Path

import face_recognition
import numpy as np
from PIL import Image, UnidentifiedImageError

from utils import (
    build_output_filename,
    collect_event_images,
    is_image_file,
    safe_copy,
)


class PhotoSorter:
    """Encapsulates the full sort pipeline from reference loading to file copying."""

    # Maximum face distance to consider a match.
    DISTANCE_THRESHOLD = 0.55

    # Resize large images before face detection to reduce CPU/RAM usage.
    MAX_IMAGE_DIMENSION = 1000

    def __init__(
        self,
        reference_folder: Path,
        events_folder: Path,
        output_folder: Path,
        logger: logging.Logger,
    ) -> None:
        """Store folder paths and logger; initialise empty encoding dict."""
        self.reference_folder = reference_folder
        self.events_folder = events_folder
        self.output_folder = output_folder
        self.logger = logger
        self._student_encodings: dict[str, np.ndarray] = {}

    # ------------------------------------------------------------------
    # Reference loading
    # ------------------------------------------------------------------

    def load_references(
        self,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> list[str]:
        """Load and encode all reference photos."""

        no_face_names: list[str] = []

        reference_images = sorted(
            p
            for p in self.reference_folder.iterdir()
            if is_image_file(p)
        )

        if not reference_images:
            self.logger.warning(
                "No reference images found in %s",
                self.reference_folder,
            )
            return no_face_names

        total = len(reference_images)

        for current, ref_path in enumerate(
            reference_images,
            start=1,
        ):
            student_name = ref_path.stem

            if progress_callback:
                progress_callback(
                    current,
                    total,
                    student_name,
                )

            try:
                # Load reference image.
                image = face_recognition.load_image_file(
                    str(ref_path)
                )

                # CPU-friendly HOG face detection.
                locations = face_recognition.face_locations(
                    image,
                    model="hog",
                )

                # Lightweight face encoding.
                encodings = face_recognition.face_encodings(
                    image,
                    known_face_locations=locations,
                    num_jitters=1,
                    model="small",
                )

                if not encodings:
                    self.logger.warning(
                        "No face detected in reference photo for %s (%s)",
                        student_name,
                        ref_path.name,
                    )
                    no_face_names.append(student_name)
                    continue

                if len(encodings) > 1:
                    self.logger.warning(
                        "Multiple faces in reference photo for %s "
                        "— using first face only",
                        student_name,
                    )

                self._student_encodings[student_name] = encodings[0]

                self.logger.info(
                    "Loaded reference for %s",
                    student_name,
                )

            except Exception as exc:  # noqa: BLE001
                self.logger.error(
                    "Could not read reference photo %s: %s",
                    ref_path.name,
                    exc,
                )

        self.logger.info(
            "Loaded %d student reference(s)",
            len(self._student_encodings),
        )

        return no_face_names

    # ------------------------------------------------------------------
    # Main sort loop
    # ------------------------------------------------------------------

    def sort_all(
        self,
        progress_callback: Callable[[int, int, str], None],
        cancelled: Callable[[], bool],
    ) -> dict[str, int]:
        """Sort all event photos into per-student output folders."""

        images = collect_event_images(
            self.events_folder
        )

        total = len(images)

        counts = {
            "total": total,
            "matched": 0,
            "unmatched": 0,
            "skipped": 0,
        }

        self.logger.info(
            "Starting sort — %d images found",
            total,
        )

        for current, (
            image_path,
            event_name,
        ) in enumerate(
            images,
            start=1,
        ):
            # Allow user cancellation.
            if cancelled():
                self.logger.info(
                    "Sort cancelled by user at image %d/%d",
                    current,
                    total,
                )
                break

            # Update GUI progress.
            progress_callback(
                current,
                total,
                image_path.name,
            )

            output_filename = build_output_filename(
                event_name,
                image_path.name,
            )

            # ----------------------------------------------------------
            # Load and resize image
            # ----------------------------------------------------------

            try:
                rgb_image = self._load_and_resize(
                    image_path
                )

            except UnidentifiedImageError:
                self.logger.warning(
                    "Corrupted image, moving to _unmatched: %s",
                    image_path.name,
                )

                safe_copy(
                    image_path,
                    self.output_folder / "_unmatched",
                    output_filename,
                    self.logger,
                )

                counts["unmatched"] += 1
                continue

            except Exception as exc:  # noqa: BLE001
                self.logger.error(
                    "Could not open %s: %s — skipping",
                    image_path.name,
                    exc,
                )

                counts["skipped"] += 1
                continue

            # ----------------------------------------------------------
            # Face detection and encoding
            # ----------------------------------------------------------

            try:
                # HOG is CPU-friendly and does not require GPU.
                face_locations = face_recognition.face_locations(
                    rgb_image,
                    model="hog",
                )

                # Lightweight encoding.
                face_encodings = face_recognition.face_encodings(
                    rgb_image,
                    face_locations,
                    num_jitters=1,
                    model="small",
                )

            except Exception as exc:  # noqa: BLE001
                self.logger.error(
                    "Face detection failed for %s: %s",
                    image_path.name,
                    exc,
                )

                safe_copy(
                    image_path,
                    self.output_folder / "_unmatched",
                    output_filename,
                    self.logger,
                )

                counts["unmatched"] += 1
                continue

            # ----------------------------------------------------------
            # No face detected
            # ----------------------------------------------------------

            if not face_encodings:
                self.logger.info(
                    "No face detected: %s → _unmatched",
                    image_path.name,
                )

                safe_copy(
                    image_path,
                    self.output_folder / "_unmatched",
                    output_filename,
                    self.logger,
                )

                counts["unmatched"] += 1
                continue

            # ----------------------------------------------------------
            # Match detected faces to students
            # ----------------------------------------------------------

            matched_students: set[str] = set()

            for encoding in face_encodings:
                match = self._match_face(
                    encoding
                )

                if match:
                    matched_students.add(match)

            # ----------------------------------------------------------
            # Copy matched photo
            # ----------------------------------------------------------

            if matched_students:

                for student_name in matched_students:

                    dest_folder = (
                        self.output_folder
                        / student_name
                    )

                    safe_copy(
                        image_path,
                        dest_folder,
                        output_filename,
                        self.logger,
                    )

                    self.logger.info(
                        "Matched %s → %s",
                        image_path.name,
                        student_name,
                    )

                counts["matched"] += 1

            # ----------------------------------------------------------
            # No student match
            # ----------------------------------------------------------

            else:

                self.logger.info(
                    "No match: %s → _unmatched",
                    image_path.name,
                )

                safe_copy(
                    image_path,
                    self.output_folder / "_unmatched",
                    output_filename,
                    self.logger,
                )

                counts["unmatched"] += 1

        # --------------------------------------------------------------
        # Sorting completed
        # --------------------------------------------------------------

        self.logger.info(
            "Sort complete — total=%d matched=%d unmatched=%d skipped=%d",
            counts["total"],
            counts["matched"],
            counts["unmatched"],
            counts["skipped"],
        )

        return counts

    # ------------------------------------------------------------------
    # Image loading / resizing
    # ------------------------------------------------------------------

    def _load_and_resize(
        self,
        image_path: Path,
    ) -> np.ndarray:
        """Open image, resize if needed, and return RGB numpy array."""

        with Image.open(image_path) as img:

            img = img.convert("RGB")

            width, height = img.size

            longest = max(
                width,
                height,
            )

            if longest > self.MAX_IMAGE_DIMENSION:

                scale = (
                    self.MAX_IMAGE_DIMENSION
                    / longest
                )

                new_size = (
                    int(width * scale),
                    int(height * scale),
                )

                img = img.resize(
                    new_size,
                    Image.LANCZOS,
                )

            return np.array(img)

    # ------------------------------------------------------------------
    # Face matching
    # ------------------------------------------------------------------

    def _match_face(
        self,
        encoding: np.ndarray,
    ) -> str | None:
        """Find the closest student encoding within threshold."""

        if not self._student_encodings:
            return None

        names = list(
            self._student_encodings.keys()
        )

        known_encodings = np.array(
            list(
                self._student_encodings.values()
            )
        )

        distances = face_recognition.face_distance(
            known_encodings,
            encoding,
        )

        best_idx = int(
            np.argmin(distances)
        )

        best_distance = distances[
            best_idx
        ]

        if best_distance <= self.DISTANCE_THRESHOLD:

            self.logger.debug(
                "Face matched to %s (distance=%.4f)",
                names[best_idx],
                best_distance,
            )

            return names[best_idx]

        self.logger.debug(
            "No match — best distance=%.4f",
            best_distance,
        )

        return None
