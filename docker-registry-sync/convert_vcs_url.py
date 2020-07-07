import os

# for testing
# os.environ["VCS_URL"] = "git@github.com:GitHK/dockerfiles-forked.git"


def from_git_ssh_to_https(possible_ssh_url):
    if "https://" in possible_ssh_url:
        return possible_ssh_url
    return "https://" + possible_ssh_url.replace(":", "/").split("@")[-1]


if __name__ == "__main__":
    print(from_git_ssh_to_https(os.environ["VCS_URL"]))

