from typing import Set


async def send_notification_to_owner(
    image: str, removed_tags: Set[str], new_tags: Set[str]
) -> None:
    """Retrieves the owner of the service and sends a notification to him/her"""
    # TODO: get owner & send email notification
    # these 2 things should be done via an API
    # for now a log is all we get
    owner = "COULD_NOT_DETERMINE_OWNER" + image
    service_readable_name = "REPLACE_" + image

    # if the user must do somthing it will be written in the email
    is_action_requested = len(new_tags) > 0
    requested_action = (
        "🚨 new service version was added please attribute permissions if needed"
        if is_action_requested
        else "✅ no new service version was added"
    )

    message_title = (
        "🚨 " if is_action_requested else "✅ "
    ) + f"Service {service_readable_name} has changed"

    print(
        f"\n{message_title}\n"
        f"💌 Informing owner '{owner}' that for image '{image}' "
        f"the following tags were removed {list(removed_tags)} "
        f"and the following tags were added '{list(new_tags)}'\n"
        f"{requested_action}\n"
    )
