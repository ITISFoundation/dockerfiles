from pathlib import Path
from typing import Dict, List, Tuple, Set
import csv
import json
from pprint import pprint
from dataclasses import dataclass
from collections import deque
from distutils.version import StrictVersion

from jinja2 import Template

import urllib, hashlib


@dataclass
class Collections:
    groups_list: List[Dict]
    services_access_rights_list: List[Dict]
    services_meta_data_list: List[Dict]
    users_list: List[Dict]
    projects_list: List[Dict]


@dataclass
class TransformedData:
    flattened_data: List[Dict]
    services_with_versions: Set[str]


def metadata_key(dict_data):
    return dict_data["key"] + dict_data["version"]


def get_gravatar_url(email: str, size: int = 15) -> str:
    encoded_email = hashlib.md5(email.lower().encode()).hexdigest()
    url_encoded_params = urllib.parse.urlencode({"s": str(size)})
    return f"https://www.gravatar.com/avatar/{encoded_email}?{url_encoded_params}"


def load_from_csv(path: Path) -> Collections:
    if not path.is_dir():
        raise ValueError(f"Path '{path}'is not a directory")

    result = {}
    for file in path.glob("*.csv"):
        key = file.name.replace(".csv", "_list")
        reader = csv.DictReader(open(file, "r"))
        result[key] = [x for x in reader]

    return Collections(**result)


def flatten_data(collections: Collections) -> TransformedData:
    """Acts as joins between the collections"""

    groups_list: List[Dict] = collections.groups_list
    services_access_rights_list: List[Dict] = collections.services_access_rights_list
    services_meta_data_list: List[Dict] = collections.services_meta_data_list
    users_list: List[Dict] = collections.users_list
    projects_list: List[Dict] = collections.projects_list

    # REMAPPINGS
    # - users to dict via "primary_gid"
    users_via_primary_gid = {x["primary_gid"]: x for x in users_list}

    # injecting "user" information into "groups_list" items via: "gid"
    for group in groups_list:
        group["user"] = (
            users_via_primary_gid[group["gid"]]
            if group["gid"] in users_via_primary_gid
            else None
        )

    # REMAPPINGS
    # - groups to dict via "gid"
    groups_via_gid = {x["gid"]: x for x in groups_list}

    # inject "group" information into "services_access_rights_list" items via: "gid"
    for services_access_right in services_access_rights_list:
        services_access_right["group"] = groups_via_gid[services_access_right["gid"]]

    # replace "owner" information in "services_meta_data_list" items via: "owner"
    for services_meta_data in services_meta_data_list:
        services_meta_data["owner"] = (
            groups_via_gid[services_meta_data["owner"]]
            if services_meta_data["owner"]
            else None
        )

    # REMAPPINGS
    # - services_meta_data to dict via "key" and "version"
    services_meta_data_via_key_and_version = {
        metadata_key(x): x for x in services_meta_data_list
    }

    # inject "service mete data" into "services_access_rights_list" items via "key" and "version"
    for services_access_right in services_access_rights_list:
        services_access_right[
            "service_meta_data"
        ] = services_meta_data_via_key_and_version[metadata_key(services_access_right)]

    flattened_data = services_access_rights_list

    # services_in_workbench
    services_with_versions = set()
    for project in projects_list:
        workbench = json.loads(project["workbench"])
        for entry in workbench.values():
            services_with_versions.add(entry["key"] + entry["version"])

    return TransformedData(
        flattened_data=flattened_data,
        services_with_versions=services_with_versions,
    )


def regroup_and_transform_data(transformed_data: TransformedData):
    """Needs to be transformed in and groupted to be shown to which users they are shered with
    - group via Key (and all the versions inside)
    - each version is shared with one or more groups (which can have a user)
    - each version has its owner
    """
    services = {}
    for service_access_right_entry in transformed_data.flattened_data:
        key = service_access_right_entry["key"]
        version = service_access_right_entry["version"]
        if key not in services:
            services[key] = {}
        if version not in services[key]:
            services[key][version] = deque()

        services[key][version].append(
            get_essential_service_data(service_access_right_entry)
        )

    # mark if a service is in use in the platform
    for key in services:
        for version in services[key]:
            for group in services[key][version]:
                search_key = key + version
                in_use = search_key in transformed_data.services_with_versions
                group["in_use"] = in_use

    # change deques into lists
    for key in services:
        for version in services[key]:
            services[key][version] = list(services[key][version])

    return services


def markdown_for_service(service_versions: Dict, list_index: int) -> Tuple[str, str]:
    def get_used_emoji(group: Dict) -> str:
        return ":green_heart:" if group["in_use"] else ":broken_heart:"

    for groups in service_versions.values():
        for group in groups:
            service_name = group["service_name"]
            service_type = group["type"]
            service_thumbnail = group["service_thumbnail"]
            break

    sorted_version_keys = sorted(
        service_versions.keys(), key=StrictVersion, reverse=True
    )
    sorted_service_versions = [(x, service_versions[x]) for x in sorted_version_keys]

    link_service_name = service_name.strip().replace(" ", "")

    service_template = """
# <a name="{{list_index}}"></a> #{{list_index}} {{service_name}} {{service_type}}
{% if service_thumbnail %}<img width="100" alt="portfolio_view" src="{{service_thumbnail}}">{% endif %}
{% for version_name, groups in sorted_service_versions %}
### <a name="{{ link_service_name + version_name }}"></a>{{ version_name }} {{get_used_emoji(groups[0])}}

![Gravatar]({{groups[0]["owner_gravatar"]}}) **{{ groups[0]["owner"] }}** [{{ groups[0]["owner_email"] }}](mailto:{{ groups[0]["owner_email"] }})

{{ groups[0]["service_description"] }}

| Group | Description | Product | can run & can modify |
|-|-|-|-|
{% for group in groups %}| **{{group["group_name"]}}** | {{group["group_description"]}} | {{group["product_name"]}} | {{group["access_rights"]}} |
{% endfor %}
{% endfor %}
---"""
    rendered_service_template = Template(service_template).render(
        list_index=list_index,
        service_name=service_name,
        service_type=service_type,
        service_thumbnail=service_thumbnail,
        sorted_service_versions=sorted_service_versions,
        link_service_name=link_service_name,
        get_used_emoji=get_used_emoji,
    )

    index_template = "- [#{{list_index}}](#{{list_index}}) **{{service_name}}** {{versions_list}}\n\n"
    rendered_index_template = Template(index_template).render(
        list_index=list_index,
        service_name=service_name,
        versions_list=", ".join(
            [
                f"{get_used_emoji(group[0])} [{x}](#{link_service_name+x})"
                for x, group in sorted_service_versions
            ]
        ),
    )

    return rendered_index_template, rendered_service_template


def get_essential_service_data(entry: Dict) -> Dict:
    def get_type(key: str) -> str:
        if "/comp/" in key:
            return "computational"
        elif "/dynamic/" in key:
            return "dynamic"
        elif "/frontend/" in key:
            return "frontend"

        raise ValueError(f"could not determine type for '{key}'")

    def render_access_write(write: str) -> str:
        return "✅" if write == "1" else "❌"

    flat_entry = {
        "gid": entry["group"]["gid"],
        "group_name": entry["group"]["name"],
        "group_description": entry["group"]["description"],
        "service_name": entry["service_meta_data"]["name"],
        "service_thumbnail": entry["service_meta_data"]["thumbnail"],
        "service_description": entry["service_meta_data"]["description"],
        "created": entry["service_meta_data"]["created"],
        "modified": entry["service_meta_data"]["modified"],
        "owner": (
            entry["service_meta_data"]["owner"]["user"]["name"]
            if entry["service_meta_data"]["owner"]
            else "No owner"
        ),
        "owner_email": (
            entry["service_meta_data"]["owner"]["user"]["email"]
            if entry["service_meta_data"]["owner"]
            else "noreply@speag.com"
        ),
        "owner_gravatar": (
            get_gravatar_url(entry["service_meta_data"]["owner"]["user"]["email"])
            if entry["service_meta_data"]["owner"]
            else get_gravatar_url("noreply@speag.com")
        ),
        "type": get_type(entry["service_meta_data"]["key"]),
        "product_name": entry["product_name"],
        "access_rights": (
            render_access_write(entry["execute_access"])
            + "  "
            + render_access_write(entry["write_access"])
        ),
    }
    return flat_entry


def render_as_deployment(collections: Collections, deployment: str) -> Tuple[str, str]:
    transformed_data = flatten_data(collections)
    services = regroup_and_transform_data(transformed_data)

    index_items = deque()
    rendered_services = deque()
    list_index = 1
    for key, versions in sorted(services.items(), key=lambda tup: tup[0]):
        print(f"Rendering {key}")
        index, rendered_service = markdown_for_service(versions, list_index)
        index_items.append(index)
        rendered_services.append(rendered_service)
        list_index += 1

    markdown = f"# '{deployment}' deployment services index\n\n"
    for index in index_items:
        markdown += index
    markdown += "\n---\n"
    for rendered_service in rendered_services:
        markdown += rendered_service

    return markdown, json.dumps(services)


def render_from_csv_files(folder_path: str, deployment: str) -> None:
    print(f"Generating report for '{deployment}' deployment'")
    collections = load_from_csv(folder_path)
    rendered_markdown, source_data = render_as_deployment(collections, deployment)
    # storing results to file
    (folder_path / "render.md").write_text(rendered_markdown)
    (folder_path / "source_data.json").write_text(source_data)


def main():
    root_deployments = Path("/tmp/deployments")
    directories = [x for x in root_deployments.glob("*") if x.is_dir()]

    for directory in directories:
        deployment_name = str(directory).split("/")[-1]
        render_from_csv_files(directory, deployment_name)

    print("✅ done")


if __name__ == "__main__":
    main()
