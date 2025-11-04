from pathlib import Path
from typing import Union, Optional

from .common import _debug, _error, get_schema_file
from ..utils import open_file_in_editor


def edit_amake_schema(
    schema_file: Optional[str] = None,
    current_dir: Union[str, Path, None] = None,
    text_editor: bool = False,
) -> int:

    schema_file = get_schema_file(current_dir, schema_file)
    if not schema_file:
        print("Schema file not found.")
        return -1
    _debug(f"Found schema file '{schema_file}'")

    if text_editor:
        _debug("Edit schema using text editor...")
        try:
            open_file_in_editor(schema_file)
            return 0
        except BaseException as e:
            _error(f"Failed to open text editor: {e}")
            print(
                f"Failed to open text editor, you can open the schema file manually, the path is: {schema_file.as_posix()}"
            )
            return -1

    _debug(f"Loading schema from '{schema_file}'")

    from ..schema import AmakeSchema

    try:
        schema = AmakeSchema.load(schema_file)
    except BaseException as e:
        _error(f"Failed to load schema: {e}")
        print(f"Invalid schema file '{schema_file.as_posix()}': {e}")
        return -1

    from ..editor import AmakeSchemaEditor

    result = AmakeSchemaEditor.run(schema)
    if not result:
        _debug("Schema not saved, cancelled by user.")
        return 0
    _debug(f"Saving schema to '{schema_file.as_posix()}'")
    result.save(schema_file.as_posix(), indent=2, ensure_ascii=False, encoding="utf-8")
    _debug("Schema saved successfully.")
    return 0
