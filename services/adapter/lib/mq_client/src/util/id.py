import uuid


def generate_id() -> str:
    return str(uuid.uuid4())


def generate_group_id(domain="sdk", suffix="", require_unique_id=True) -> str:
    group_id = domain

    if suffix != "":
        suffix_id = transform_to_id_format(suffix)
        group_id += f"-{suffix_id}"

    if require_unique_id:
        unique_id = generate_id()
        group_id += f"-{unique_id}"

    return group_id


def transform_to_id_format(text: str) -> str:
    return text.replace(" ", "-").lower()
