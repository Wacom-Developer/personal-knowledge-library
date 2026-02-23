Module knowledge.base.ink
=========================

Classes
-------

`ExportFormat(*args, **kwds)`
:   Represents image export formats as an enumeration.
    
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

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `JPG`
    :   The type of the None singleton.

    `PNG`
    :   The type of the None singleton.

    `SVG`
    :   The type of the None singleton.

`HWRMode(*args, **kwds)`
:   Defines the different modes of handwriting recognition.
    
    Detailed description of the class, its purpose, and usage.
    
    Attributes
    ----------
    TEXT_MODE : str
        Mode for handling handwritten text.
    DIAGRAM_MODE : str
        Mode for handling diagrams and shapes.
    MATH_MODE : str
        Mode for handling mathematical expressions.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `DIAGRAM_MODE`
    :   The type of the None singleton.

    `MATH_MODE`
    :   The type of the None singleton.

    `TEXT_MODE`
    :   The type of the None singleton.

`InkToXSettings(view_name: str = 'ink-groups', segmentation_locale: str | None = None, optimized: bool = False, grouping_strategy: int | None = None, destination_segmentation_schema: Literal['ml02', 'smplseg01'] | None = None, reorder_strategy: int | None = None, merge_rows_vertically: bool = False, other_separation_coef: int | None = None, text_separation_coef: int | None = None, math_separation_coef: int | None = None, batch_size: int | None = None)`
:   Ink to X settings
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
        Use with caution! It can lead to out-of-memory exceptions. The default value is 32.

    ### Instance variables

    `batch_size: int | None`
    :   An optional parameter for the size of batches when using the optimized predictions when performing segmentation.
        Use with caution! It can lead to out-of-memory exceptions. The default value is 32.

    `destination_segmentation_schema: Literal['ml02', 'smplseg01'] | None`
    :   An optional parameter for the WODL schema of the destination view when performing segmentation.
        Supported destination view schemas: ['ml02', 'smplseg01']. The default value is 'ml02'.

    `grouping_strategy: int | None`
    :   An optional parameter for the strategy by which the strokes will be grouped by when performing segmentation.

    `math_separation_coef: int | None`
    :   An optional parameter for the separation threshold by which the math strokes will be segmented by when
        performing segmentation.

    `merge_rows_vertically: bool`
    :   An optional parameter that is representing if the rows that are closer to each other should be merged
        (vertically) when performing segmentation.

    `optimized: bool`
    :   The parameter for the segmentation processing method.

    `other_separation_coef: int | None`
    :   An optional parameter for the separation threshold by which the other strokes will be segmented by when
        performing segmentation.

    `provider_settings: List[knowledge.base.ink.ProviderSettings]`
    :   Provider settings for the ink to X service.

    `reorder_strategy: int | None`
    :   An optional parameter for the strategy by which the strokes will be reordered by when performing
        segmentation.

    `segmentation_locale: str | None`
    :   An optional parameter for the segmentation language hint.

    `text_separation_coef: int | None`
    :   An optional parameter for the separation threshold by which the text strokes will be segmented by when
        performing segmentation.

    `view_name: str`
    :   The parameter for the view in which the segmentation result will be stored. The default value is 'hwr'.

    ### Methods

    `add_provider_settings(self, provider_settings: knowledge.base.ink.ProviderSettings)`
    :   Add provider settings for the ink to X service.
        
        Parameters
        ----------
        provider_settings: ProviderSettings
            Provider settings for the ink to X service.

`PDFType(*args, **kwds)`
:   Represents the type of PDF document.
    
    Attributes
    ----------
    RASTER : str
        The ink is represented as raster images.
    VECTOR : str
        The ink is represented as vector graphics.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `RASTER`
    :   The type of the None singleton.

    `VECTOR`
    :   The type of the None singleton.

`Priority(*args, **kwds)`
:   Priority levels for handwriting recognition providers.
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

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `HIGH`
    :   The type of the None singleton.

    `HIGHEST`
    :   The type of the None singleton.

    `LOW`
    :   The type of the None singleton.

    `LOWEST`
    :   The type of the None singleton.

    `NORMAL`
    :   The type of the None singleton.

`Provider(*args, **kwds)`
:   Provider of handwriting recognition technology.
    
    Attributes
    ----------
    MYSCRIPT : str
        The provider is MyScript.
    ILABO : str
        The provider is ILABO.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `ILABO`
    :   The type of the None singleton.

    `MYSCRIPT`
    :   The type of the None singleton.

`ProviderSettings(locale: str, mode: knowledge.base.ink.HWRMode, provider: knowledge.base.ink.Provider, schema: knowledge.base.ink.Schema, text_direction: knowledge.base.ink.WritingOrientation, filter_brushes: List[str])`
:   Provider settings
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

    ### Instance variables

    `filter_brushes: List[str]`
    :   List of brushes that should be filtered out from the recognition process.

    `locale: str`
    :   Locale for language and country

    `mode: knowledge.base.ink.HWRMode`
    :   Handwriting recognition mode.

    `provider: knowledge.base.ink.Provider`
    :   HWR Technology provider.

    `schema: knowledge.base.ink.Schema`
    :   Schema for representing the results of the recognition.

    `text_direction: knowledge.base.ink.WritingOrientation`
    :   Writing orientation.

`Schema(*args, **kwds)`
:   Represent the various Universal Ink Model schema identifiers used in the system.
    
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

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `MATH_STRUCTURES_V01`
    :   The type of the None singleton.

    `MATH_V06`
    :   The type of the None singleton.

    `SEGMENTATION_V03`
    :   The type of the None singleton.

    `SIMPLE_SEGMENTATION_V01`
    :   The type of the None singleton.

`WritingOrientation(*args, **kwds)`
:   The WritingOrientation enumeration defines the possible orientations in which
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

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `AUTO`
    :   The type of the None singleton.

    `HORIZONTAL`
    :   The type of the None singleton.

    `VERTICAL`
    :   The type of the None singleton.