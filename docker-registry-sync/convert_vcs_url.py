import os

# for testing
# os.environ["VCS_URL"] = "git@github.com:GitHK/dockerfiles-forked.git"


def from_git_ssh_to_https(git_url):
    if git_url.startswith("https://"):
        return git_url
    return "https://" + git_url.replace(":", "/").split("@")[-1]


if __name__ == "__main__":
    print(from_git_ssh_to_https(os.environ["VCS_URL"]))

