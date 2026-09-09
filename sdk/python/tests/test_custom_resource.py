# Copyright 2016-2026, Pulumi Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pulumi

registered_inputs = {}


class Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        registered_inputs[args.name] = args.inputs
        return [f"{args.name}_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(Mocks(), preview=False)

from pulumi_kubernetes.apiextensions import CustomResource, CustomResourcePatch  # noqa: E402


@pulumi.runtime.test
def test_custom_resource_passes_through_top_level_fields():
    cr = CustomResource(
        "snapclass",
        api_version="snapshot.storage.k8s.io/v1",
        kind="VolumeSnapshotClass",
        metadata={"name": "csi-aws-vsc"},
        driver="ebs.csi.aws.com",
        deletionPolicy="Delete",
    )

    def check(_):
        inputs = registered_inputs["snapclass"]
        assert inputs["apiVersion"] == "snapshot.storage.k8s.io/v1"
        assert inputs["kind"] == "VolumeSnapshotClass"
        assert inputs["metadata"] == {"name": "csi-aws-vsc"}
        assert inputs["driver"] == "ebs.csi.aws.com"
        assert inputs["deletionPolicy"] == "Delete"

    return cr.id.apply(check)


@pulumi.runtime.test
def test_custom_resource_patch_passes_through_top_level_fields():
    cr = CustomResourcePatch(
        "snapclass-patch",
        api_version="snapshot.storage.k8s.io/v1",
        kind="VolumeSnapshotClass",
        metadata={"name": "csi-aws-vsc"},
        deletionPolicy="Retain",
    )

    def check(_):
        inputs = registered_inputs["snapclass-patch"]
        assert inputs["apiVersion"] == "snapshot.storage.k8s.io/v1"
        assert inputs["kind"] == "VolumeSnapshotClass"
        assert inputs["deletionPolicy"] == "Retain"

    return cr.id.apply(check)
