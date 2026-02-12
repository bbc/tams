def is_read(group: str) -> bool:
    # NOTE: This may be replaced with any logic to determine if a supplied "group" has Read permissions
    return group.endswith("read")


def is_write(group: str) -> bool:
    # NOTE: This may be replaced with any logic to determine if a supplied "group" has Write permissions
    return group.endswith("write")


def is_delete(group: str) -> bool:
    # NOTE: This may be replaced with any logic to determine if a supplied "group" has Delete permissions
    return group.endswith("delete")


def is_admin(group: str) -> bool:
    # NOTE: This may be replaced with any logic to determine if a supplied "group" has Admin permissions
    return group == "admin"


def is_any(group: str) -> bool:
    return is_read(group) or is_write(group) or is_delete(group) or is_admin(group)


def any_is_read(groups: list[str]) -> bool:
    return any([is_read(x) for x in groups])


def any_is_write(groups: list[str]) -> bool:
    return any([is_write(x) for x in groups])


def any_is_delete(groups: list[str]) -> bool:
    return any([is_delete(x) for x in groups])


def any_is_admin(groups: list[str]) -> bool:
    return any([is_admin(x) for x in groups])


def any_is_any(groups: list[str]) -> bool:
    return any([is_any(x) for x in groups])


def filter_read(groups: list[str]) -> list[str]:
    return list(filter(is_read, groups))


def filter_write(groups: list[str]) -> list[str]:
    return list(filter(is_write, groups))


def filter_delete(groups: list[str]) -> list[str]:
    return list(filter(is_delete, groups))
