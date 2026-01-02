# TextParagraphNode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**marks** | [**List[TextParagraphNodeMarksInner]**](TextParagraphNodeMarksInner.md) |  | [optional] 
**text** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.text_paragraph_node import TextParagraphNode

# TODO update the JSON string below
json = "{}"
# create an instance of TextParagraphNode from a JSON string
text_paragraph_node_instance = TextParagraphNode.from_json(json)
# print the JSON string representation of the object
print(TextParagraphNode.to_json())

# convert the object into a dict
text_paragraph_node_dict = text_paragraph_node_instance.to_dict()
# create an instance of TextParagraphNode from a dict
text_paragraph_node_from_dict = TextParagraphNode.from_dict(text_paragraph_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


