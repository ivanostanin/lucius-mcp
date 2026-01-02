# CodeBlockDocumentNode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attrs** | [**Attrs**](Attrs.md) |  | [optional] 
**content** | [**List[TextParagraphNode]**](TextParagraphNode.md) |  | [optional] 

## Example

```python
from src.client.generated.models.code_block_document_node import CodeBlockDocumentNode

# TODO update the JSON string below
json = "{}"
# create an instance of CodeBlockDocumentNode from a JSON string
code_block_document_node_instance = CodeBlockDocumentNode.from_json(json)
# print the JSON string representation of the object
print(CodeBlockDocumentNode.to_json())

# convert the object into a dict
code_block_document_node_dict = code_block_document_node_instance.to_dict()
# create an instance of CodeBlockDocumentNode from a dict
code_block_document_node_from_dict = CodeBlockDocumentNode.from_dict(code_block_document_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


