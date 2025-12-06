import pytest
from pydantic import ValidationError

from ml.domain.models.payload_data import MetaData, Tag


@pytest.mark.parametrize(
    ("input_data", "expected_tag", "expected_dump"),
    [
        (
            {"is_voice": True, "tag": Tag.Marketing},
            Tag.Marketing,
            {"is_voice": True, "tag": Tag.Marketing.value},
        ),
        (
            {"is_voice": False, "tag": "finance"},
            Tag.Finance,
            {"is_voice": False, "tag": Tag.Finance.value},
        ),
    ],
)
def test_metadata_accepts_valid_inputs(
    input_data: dict[str, object], expected_tag: Tag, expected_dump: dict[str, object]
) -> None:
    metadata = MetaData.model_validate(input_data)

    assert metadata.is_voice is input_data["is_voice"]
    assert metadata.tag is expected_tag
    assert metadata.model_dump() == {"is_voice": metadata.is_voice, "tag": expected_tag}
    assert metadata.model_dump(mode="json") == expected_dump


@pytest.mark.parametrize(
    "invalid_input",
    [
        {"is_voice": None, "tag": Tag.General},
        {"is_voice": True, "tag": 10},
        {"is_voice": False},
    ],
)
def test_metadata_rejects_invalid_types(invalid_input: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        MetaData.model_validate(invalid_input)
