"""
Integration tests for textDocument/completion.
"""
import pytest
from lsprotocol.types import COMPLETION_ITEM_RESOLVE
from lsprotocol.types import CompletionItem


# See
# https://docs.pytest.org/en/latest/example/markers.html#marking-whole-classes-or-modules
pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "file_name,line,character",
    [
        ("template.yaml", 149, 10),
        ("template.json", 275, 21),
    ],
)
@pytest.mark.asyncio
async def test_resource_completion(client, file_name, line, character):
    test_uri = client.root_uri + "/" + file_name
    result = await client.completion_request(test_uri, line=line, character=character)

    labels = [c.label for c in result.items]
    assert "AWS::ACMPCA::Certificate" in labels


@pytest.mark.asyncio
async def test_property_completion(client):
    test_uri = client.root_uri + "/template.yaml"
    result = await client.completion_request(test_uri, line=57, character=6)

    labels = [c.label for c in result.items]
    assert "Bucket" in labels
    assert "PolicyDocument" in labels


@pytest.mark.asyncio
async def test_nested_property_completion(client):
    test_uri = client.root_uri + "/template.yaml"
    result = await client.completion_request(test_uri, line=51, character=8)

    labels = [c.label for c in result.items]
    assert "LogFilePrefix" in labels
    assert "DestinationBucketName" in labels


@pytest.mark.asyncio
async def test_completion_item_resolve_adds_documentation_for_resource(client):
    resource = "AWS::S3::Bucket"
    item = CompletionItem(label=resource)

    # TODO ask upstream to add this as a client method
    result = await client.lsp.send_request_async(COMPLETION_ITEM_RESOLVE, item)
    assert resource in result.documentation


@pytest.mark.asyncio
async def test_ref_completion(client):
    test_uri = client.root_uri + "/template.yaml"
    result = await client.completion_request(test_uri, line=151, character=24)

    labels = [c.label for c in result.items]
    assert "CertificateArn" in labels  # A parameter
    assert "LogBucket" in labels  # A logical id


@pytest.mark.parametrize(
    "file_name,line,character",
    [
        ("template.yaml", 44, 15),
        ("template.json", 33, 18),
    ],
)
@pytest.mark.asyncio
async def test_no_completion(client, file_name, line, character):
    test_uri = client.root_uri + "/" + file_name
    result = await client.completion_request(test_uri, line=line, character=character)
    assert not result.items
