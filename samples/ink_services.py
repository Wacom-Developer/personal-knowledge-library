# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language_code governing permissions and
#  limitations under the License.
import argparse
from pathlib import Path

from knowledge.base.ink import (
    ExportFormat,
    HWRMode,
    PDFType,
    Priority,
    Provider,
    ProviderSettings,
    Schema,
    WritingOrientation,
    InkToXSettings,
)
from knowledge.base.language import EN_US
from knowledge.services.ink import InkServices

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument(
        "-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    parser.add_argument(
        "--text-uim",
        help="Path to a UIM file containing handwritten text",
    )
    parser.add_argument(
        "--math-uim",
        help="Path to a UIM file containing handwritten math.",
    )
    args = parser.parse_args()

    client: InkServices = InkServices(service_url=args.instance)
    client.login(args.tenant, args.user)

    text_uim_path: Path = Path(args.text_uim)
    math_uim_path: Path = Path(args.math_uim)

    # -----------------------------------------------------------------------
    # Handwriting Recognition — enriched UIM
    # -----------------------------------------------------------------------
    print("Handwriting Recognition  [ink_to_text]")
    print("=" * 120)
    text_uim: bytes = text_uim_path.read_bytes()
    enriched_uim: bytes = client.perform_ink_to_text(
        content=text_uim,
        locale=EN_US,
        hwr_mode=HWRMode.TEXT_MODE,
        priority=Priority.LOWEST,
        provider=Provider.MYSCRIPT,
        schema=Schema.SEGMENTATION_V03,
    )
    print(f"  Input  : {text_uim_path.name}  ({len(text_uim):,} bytes)")
    print(f"  Output : enriched UIM  ({len(enriched_uim):,} bytes)")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Handwriting Recognition — plain text
    # -----------------------------------------------------------------------
    print("Handwriting Recognition  [ink_to_text_plain]")
    print("=" * 120)
    recognized_text: str = client.perform_ink_to_text_plain(
        content=text_uim,
        locale=EN_US,
        hwr_mode=HWRMode.TEXT_MODE,
        priority=Priority.LOWEST,
        provider=Provider.MYSCRIPT,
        schema=Schema.SEGMENTATION_V03,
    )
    print(f"  Recognized text: {recognized_text!r}")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Named Entity Linking on ink content
    # -----------------------------------------------------------------------
    print("Named Entity Linking  [perform_named_entity_linking]")
    print("=" * 120)
    nel_uim: bytes = client.perform_named_entity_linking(content=enriched_uim, locale=EN_US)
    print(f"  Input  : enriched UIM  ({len(enriched_uim):,} bytes)")
    print(f"  Output : NEL-enriched UIM  ({len(nel_uim):,} bytes)")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Math Recognition
    # -----------------------------------------------------------------------
    print("Math Recognition  [perform_ink_to_math]")
    print("=" * 120)
    math_uim: bytes = math_uim_path.read_bytes()
    math_enriched: bytes = client.perform_ink_to_math(
        content=math_uim,
        schema=Schema.MATH_V06,
        provider=Provider.MYSCRIPT,
        priority=Priority.LOWEST,
    )
    print(f"  Input  : {math_uim_path.name}  ({len(math_uim):,} bytes)")
    print(f"  Output : math-enriched UIM  ({len(math_enriched):,} bytes)")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Ink-to-X pipeline (HWR + NEL in one pass)
    # -----------------------------------------------------------------------
    print("Ink-to-X pipeline  [ink_to_x]")
    print("=" * 120)
    settings: InkToXSettings = InkToXSettings(view_name="hwr")
    settings.add_provider_settings(
        ProviderSettings(
            locale=str(EN_US),
            mode=HWRMode.TEXT_MODE,
            provider=Provider.MYSCRIPT,
            schema=Schema.SEGMENTATION_V03,
            text_direction=WritingOrientation.HORIZONTAL,
            filter_brushes=[],
        )
    )
    ink_to_x_result: bytes = client.ink_to_x(content=text_uim, settings=settings, priority=Priority.LOWEST)
    print(f"  Input  : {text_uim_path.name}  ({len(text_uim):,} bytes)")
    print(f"  Output : Ink-to-X enriched UIM  ({len(ink_to_x_result):,} bytes)")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Format conversion — PNG
    # -----------------------------------------------------------------------
    print("Format Conversion  [convert_to PNG]")
    print("=" * 120)
    png_bytes: bytes = client.convert_to(content=text_uim, export_format=ExportFormat.PNG)
    print(f"  Output : PNG image  ({len(png_bytes):,} bytes)")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Format conversion — SVG
    # -----------------------------------------------------------------------
    print("Format Conversion  [convert_to SVG]")
    print("=" * 120)
    svg_bytes: bytes = client.convert_to(content=text_uim, export_format=ExportFormat.SVG)
    print(f"  Output : SVG image  ({len(svg_bytes):,} bytes)")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Format conversion — PDF (vector)
    # -----------------------------------------------------------------------
    print("Format Conversion  [convert_to_pdf VECTOR]")
    print("=" * 120)
    pdf_bytes: bytes = client.convert_to_pdf(content=text_uim, pdf_type=PDFType.VECTOR)
    print(f"  Output : PDF (vector)  ({len(pdf_bytes):,} bytes)")
    print("=" * 120)
