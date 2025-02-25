MIN_VALID_CONFIGURATION = """
registries:
  first:
    url: first.url.here
    env_user: ENV_VAR_FIRST_USER
    env_password: ENV_VAR_FIRST_PASSWORD
  second:
    url: second.url.here
    env_user: ENV_VAR_SECOND_USER
    env_password: ENV_VAR_SECOND_PASSWORD

stages:
  - from:
      source: first
      repository: "some/repo"
    to:
      - destination: second
        repository: "other/repo"
        tags: []
    id: "test-stage"

  - from:
      source: first
      repository: "some/repo2"
    to:
      - destination: second
        repository: "other/repo2"
        tags: ["1.0.0"]
    depends_on: ["test-stage"]

  - from:
      source: first
      repository: "some/repo3"
    to:
      - destination: second
        repository: "other/repo3"
        tags: []
"""


MULTI_STAGE_IDS_CONFIGURATION = """
registries:
  first:
    url: first.url.here
    env_user: ENV_VAR_FIRST_USER
    env_password: ENV_VAR_FIRST_PASSWORD
  second:
    url: second.url.here
    env_user: ENV_VAR_SECOND_USER
    env_password: ENV_VAR_SECOND_PASSWORD

stages:
  - from:
      source: first
      repository: "some/repo"
    to:
      - destination: second
        repository: "other/repo"
        tags: []
    id: "test-stage"

  - from:
      source: first
      repository: "some/repo2"
    to:
      - destination: second
        repository: "other/repo2"
        tags: []
    id: "test-stage"
"""

STAGES_SELF_DEPENDENCY_CONFIGURATION = """
registries:
  first:
    url: first.url.here
    env_user: ENV_VAR_FIRST_USER
    env_password: ENV_VAR_FIRST_PASSWORD
  second:
    url: second.url.here
    env_user: ENV_VAR_SECOND_USER
    env_password: ENV_VAR_SECOND_PASSWORD

stages:
  - from:
      source: first
      repository: "some/repo"
    to:
      - destination: second
        repository: "other/repo"
        tags: []
    id: "test-stage"
    depends_on: ["test-stage"]
"""

NO_SUCH_STAGE_CONFIGURATION = """
registries:
  first:
    url: first.url.here
    env_user: ENV_VAR_FIRST_USER
    env_password: ENV_VAR_FIRST_PASSWORD
  second:
    url: second.url.here
    env_user: ENV_VAR_SECOND_USER
    env_password: ENV_VAR_SECOND_PASSWORD

stages:
  - from:
      source: first
      repository: "some/repo"
    to:
      - destination: second
        repository: "other/repo"
        tags: []
    depends_on: ["test-stage"]
"""

CYCLIC_DEPENDENCY_CONFIGURATION = """
registries:
  first:
    url: first.url.here
    env_user: ENV_VAR_FIRST_USER
    env_password: ENV_VAR_FIRST_PASSWORD
  second:
    url: second.url.here
    env_user: ENV_VAR_SECOND_USER
    env_password: ENV_VAR_SECOND_PASSWORD

stages:
  - from:
      source: first
      repository: "some/repo"
    to:
      - destination: second
        repository: "other/repo"
        tags: []
    id: "one"
    depends_on: ["two"]

  - from:
      source: first
      repository: "some/repo2"
    to:
      - destination: second
        repository: "other/repo2"
        tags: []
    id: "two"
    depends_on: ["one"]
"""
