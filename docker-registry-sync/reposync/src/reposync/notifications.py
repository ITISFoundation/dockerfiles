from typing import Set


async def send_notification_to_owner(
    image: str, removed_tags: Set[str], new_tags: Set[str]
) -> None:
    """Retrieves the owner of the service and sends a notification to him/her"""
    # TODO: get owner & send email notification
    # these 2 things should be done via an API
    # for now a log is all we get
    owner = "COULD_NOT_DETERMINE_OWNER"
    print(
        f"💌 Informing owner '{owner}' that for image '{image}'' "
        f"the following tags were removed {list(removed_tags)} "
        f"and the following tags were added '{list(new_tags)}''"
    )
