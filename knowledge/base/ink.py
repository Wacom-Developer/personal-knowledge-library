# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
from enum import Enum
from typing import Optional, Literal, List

__all__ = [
    "WritingOrientation",
    "Priority",
    "HWRMode",
    "Schema",
    "ExportFormat",
    "PDFType",
    "Provider",
    "ProviderSettings",
    "InkToXSettings",
    "DEFAULT_INK_TO_X",
]


class WritingOrientation(str, Enum):
    """
    The WritingOrientation enumeration defines the possible orientations in which
    text can be written. It is a subclass of `str` and `Enum`, enabling the
    values to be used both as enumeration members and as raw string values.
    The three members are:
        AUTO: automatically select the orientation based on context.
        HORIZONTAL: text is laid out horizontally.
        VERTICAL: text is laid out vertically.

    This enumeration can be used wherever a string representing the orientation
    is required, while still providing the safety and clarity of an enum.

    Attributes
    ----------
    AUTO : str
        Value representing automatic orientation selection.
    HORIZONTAL : str
        Value representing horizontal text orientation.
    VERTICAL : str
        Value representing vertical text orientation.
    """

    AUTO = "auto"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Priority(str, Enum):
    """
    Priority levels for handwriting recognition providers.
    The priority determines the order in which the providers will be used for recognition.

    Attributes
    ----------
    LOWEST : str
        The lowest priority level.
    LOW : str
        The low-priority level.
    NORMAL : str
        The normal priority level.
    HIGH : str
        The high-priority level.
    HIGHEST : str
        The highest priority level.
    """

    LOWEST = "Lowest"
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    HIGHEST = "Highest"


class HWRMode(str, Enum):
    """
    Defines the different modes of handwriting recognition.

    Detailed description of the class, its purpose, and usage.

    Attributes
    ----------
    TEXT_MODE : str
        Mode for handling handwritten text.
    DIAGRAM_MODE : str
        Mode for handling diagrams and shapes.
    MATH_MODE : str
        Mode for handling mathematical expressions.
    """

    TEXT_MODE = "Text"
    DIAGRAM_MODE = "TextAndShapes"
    MATH_MODE = "Math"


class Schema(str, Enum):
    """Represent the various Universal Ink Model schema identifiers used in the system.

    Attributes
    ----------
    SEGMENTATION_V03 : str
        Identifier for segmentation schema version 0.3.
    SIMPLE_SEGMENTATION_V01 : str
        Identifier for simple segmentation schema version 0.1.
    MATH_STRUCTURES_V01 : str
        Identifier for math structures schema version 0.1.
    MATH_V06 : str
        Identifier for math schema version 0.6.
    """

    SEGMENTATION_V03 = "seg_0.3"
    SIMPLE_SEGMENTATION_V01 = "simple-seg_0.1"
    MATH_STRUCTURES_V01 = "math-structures_0.1"
    MATH_V06 = "math_0.6"


class ExportFormat(str, Enum):
    """
    Represents image export formats as an enumeration.

    The ExportFormat enumeration defines supported image export
    formats. Each member is a string representing the format name,
    for example, 'SVG', 'PNG', or 'JPG'. This enum can be used to
    specify the desired format when exporting graphical data.

    Attributes
    ----------
    SVG : str
        Represents the SVG (Scalable Vector Graphics) format.
    PNG : str
        Represents the PNG (Portable Network Graphics) format.
    JPG : str
        Represents the JPG (Joint Photographic Experts Group) format.
    """

    SVG = "SVG"
    PNG = "PNG"
    JPG = "JPG"


class PDFType(str, Enum):
    """
    Represents the type of PDF document.

    Attributes
    ----------
    RASTER : str
        The ink is represented as raster images.
    VECTOR : str
        The ink is represented as vector graphics.
    """

    RASTER = "raster"
    VECTOR = "vector"


class Provider(str, Enum):
    """
    Provider of handwriting recognition technology.

    Attributes
    ----------
    MYSCRIPT : str
        The provider is MyScript.
    ILABO : str
        The provider is ILABO.
    """

    MYSCRIPT = "myscript"
    ILABO = "ilabo"


class ProviderSettings:
    """
    Provider settings
    -----------------
    Settings for the provider.

    Parameters
    ----------
    locale: str
        Locale for language and country
    mode: HWRMode
        Handwriting recognition mode
    provider: Provider
        HWR Technology provider
    schema: Schema
        The schema for representing the results of the recognition
    text_direction: WritingOrientation
        Writing orientation
    filter_brushes: List[str]
        List of brushes that should be filtered out from the recognition process
    """

    def __init__(
        self,
        locale: str,
        mode: HWRMode,
        provider: Provider,
        schema: Schema,
        text_direction: WritingOrientation,
        filter_brushes: List[str],
    ):
        self.__locale: str = locale
        self.__mode: HWRMode = mode
        self.__provider: Provider = provider
        self.__schema: Schema = schema
        self.__textDirection: WritingOrientation = text_direction
        self.__filterBrushes: List[str] = filter_brushes

    @property
    def locale(self) -> str:
        """
        Locale for language and country
        """
        return self.__locale

    @property
    def mode(self) -> HWRMode:
        """
        Handwriting recognition mode.
        """
        return self.__mode

    @property
    def provider(self) -> Provider:
        """
        HWR Technology provider.
        """
        return self.__provider

    @property
    def schema(self) -> Schema:
        """
        Schema for representing the results of the recognition.
        """
        return self.__schema

    @property
    def text_direction(self) -> WritingOrientation:
        """
        Writing orientation.
        """
        return self.__textDirection

    @property
    def filter_brushes(self) -> List[str]:
        """
        List of brushes that should be filtered out from the recognition process.
        """
        return self.__filterBrushes


class InkToXSettings:
    """
    Ink to X settings
    -----------------
    Settings for the ink to X service.

    Parameters
    ----------
    view_name: str
        The parameter for the view in which the segmentation result will be stored. The default value is 'hwr'.
    segmentation_locale: str
        An optional parameter for the segmentation language hint.
    optimized: bool
        The parameter for the segmentation processing method.
    grouping_strategy: int
        An optional parameter for the strategy by which the strokes will be grouped by when performing segmentation.
    destination_segmentation_schema: str
        An optional parameter for the WODL schema of the destination view when performing segmentation.
        Supported destination view schemas: ['ml02', 'smplseg01']. The default value is 'ml02'.
    reorder_strategy: int
        An optional parameter for the strategy by which the strokes will be reordered by when performing segmentation.
    merge_rows_vertically: bool
        An optional parameter that is representing if the rows that are closer to each other should be merged
        (vertically) when performing segmentation.
    other_separation_coef: int
        An optional parameter for the separation threshold by which the other strokes will be segmented by when
        performing segmentation.
    text_separation_coef: int
        An optional parameter for the separation threshold by which the text strokes will be segmented by when
        performing segmentation.
    math_separation_coef: int
        An optional parameter for the separation threshold by which the math strokes will be segmented by when
        performing segmentation.
    batch_size: int
        An optional parameter for the size of batches when using the optimized predictions when performing segmentation.
        Use with caution! It can lead to out of memory exceptions. The default value is 32.
    """

    def __init__(
        self,
        view_name: str = "ink-groups",
        segmentation_locale: Optional[str] = None,
        optimized: bool = False,
        grouping_strategy: Optional[int] = None,
        destination_segmentation_schema: Optional[Literal["ml02", "smplseg01"]] = None,
        reorder_strategy: Optional[int] = None,
        merge_rows_vertically: bool = False,
        other_separation_coef: Optional[int] = None,
        text_separation_coef: Optional[int] = None,
        math_separation_coef: Optional[int] = None,
        batch_size: Optional[int] = None,
    ):
        self.__segmentation_locale: Optional[str] = segmentation_locale
        self.__view_name: str = view_name
        self.__optimized: bool = optimized
        self.__destination_segmentation_schema: Optional[Literal["ml02", "smplseg01"]] = destination_segmentation_schema
        self.__merge_rows_vertically: bool = merge_rows_vertically
        self.__reorder_strategy: Optional[int] = reorder_strategy
        self.__grouping_strategy: Optional[int] = grouping_strategy
        self.__other_separation_coef: Optional[int] = other_separation_coef
        self.__text_separation_coef: Optional[int] = text_separation_coef
        self.__math_separation_coef: Optional[int] = math_separation_coef
        self.__batch_size: Optional[int] = batch_size
        self.__provider_settings: List[ProviderSettings] = []

    @property
    def segmentation_locale(self) -> Optional[str]:
        """An optional parameter for the segmentation language hint."""
        return self.__segmentation_locale

    @property
    def view_name(self) -> str:
        """
        The parameter for the view in which the segmentation result will be stored. The default value is 'hwr'.
        """
        return self.__view_name

    @property
    def grouping_strategy(self) -> Optional[int]:
        """
        An optional parameter for the strategy by which the strokes will be grouped by when performing segmentation.
        """
        return self.__grouping_strategy

    @property
    def optimized(self) -> bool:
        """The parameter for the segmentation processing method."""
        return self.__optimized

    @property
    def destination_segmentation_schema(self) -> Optional[Literal["ml02", "smplseg01"]]:
        """
        An optional parameter for the WODL schema of the destination view when performing segmentation.
        Supported destination view schemas: ['ml02', 'smplseg01']. The default value is 'ml02'.
        """
        return self.__destination_segmentation_schema

    @property
    def reorder_strategy(self) -> Optional[int]:
        """
        An optional parameter for the strategy by which the strokes will be reordered by when performing
        segmentation.
        """
        return self.__reorder_strategy

    @property
    def merge_rows_vertically(self) -> bool:
        """
        An optional parameter that is representing if the rows that are closer to each other should be merged
        (vertically) when performing segmentation.
        """
        return self.__merge_rows_vertically

    @property
    def other_separation_coef(self) -> Optional[int]:
        """
        An optional parameter for the separation threshold by which the other strokes will be segmented by when
        performing segmentation.
        """
        return self.__other_separation_coef

    @property
    def text_separation_coef(self) -> Optional[int]:
        """
        An optional parameter for the separation threshold by which the text strokes will be segmented by when
        performing segmentation.
        """
        return self.__text_separation_coef

    @property
    def math_separation_coef(self) -> Optional[int]:
        """
        An optional parameter for the separation threshold by which the math strokes will be segmented by when
        performing segmentation.
        """
        return self.__math_separation_coef

    @property
    def batch_size(self) -> Optional[int]:
        """
        An optional parameter for the size of batches when using the optimized predictions when performing segmentation.
        Use with caution! It can lead to out of memory exceptions. The default value is 32.
        """
        return self.__batch_size

    def add_provider_settings(self, provider_settings: ProviderSettings):
        """
        Add provider settings for the ink to X service.

        Parameters
        ----------
        provider_settings: ProviderSettings
            Provider settings for the ink to X service.
        """
        self.__provider_settings.append(provider_settings)

    @property
    def provider_settings(self) -> List[ProviderSettings]:
        """
        Provider settings for the ink to X service.
        """
        return self.__provider_settings


DEFAULT_INK_TO_X: InkToXSettings = InkToXSettings()
