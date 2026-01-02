# ParagraphDocumentNodeAllOfContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**marks** | [**List[TextParagraphNodeMarksInner]**](TextParagraphNodeMarksInner.md) |  | [optional] 
**text** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.paragraph_document_node_all_of_content import ParagraphDocumentNodeAllOfContent

# TODO update the JSON string below
json = "{}"
# create an instance of ParagraphDocumentNodeAllOfContent from a JSON string
paragraph_document_node_all_of_content_instance = ParagraphDocumentNodeAllOfContent.from_json(json)
# print the JSON string representation of the object
print(ParagraphDocumentNodeAllOfContent.to_json())

# convert the object into a dict
paragraph_document_node_all_of_content_dict = paragraph_document_node_all_of_content_instance.to_dict()
# create an instance of ParagraphDocumentNodeAllOfContent from a dict
paragraph_document_node_all_of_content_from_dict = ParagraphDocumentNodeAllOfContent.from_dict(paragraph_document_node_all_of_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


