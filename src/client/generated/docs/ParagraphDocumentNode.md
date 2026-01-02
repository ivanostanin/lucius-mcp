# ParagraphDocumentNode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attrs** | [**Attrs**](Attrs.md) |  | [optional] 
**content** | [**List[ParagraphDocumentNodeAllOfContent]**](ParagraphDocumentNodeAllOfContent.md) |  | [optional] 

## Example

```python
from src.client.generated.models.paragraph_document_node import ParagraphDocumentNode

# TODO update the JSON string below
json = "{}"
# create an instance of ParagraphDocumentNode from a JSON string
paragraph_document_node_instance = ParagraphDocumentNode.from_json(json)
# print the JSON string representation of the object
print(ParagraphDocumentNode.to_json())

# convert the object into a dict
paragraph_document_node_dict = paragraph_document_node_instance.to_dict()
# create an instance of ParagraphDocumentNode from a dict
paragraph_document_node_from_dict = ParagraphDocumentNode.from_dict(paragraph_document_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


