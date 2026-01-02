# AttachmentRow


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_length** | **int** |  | [optional] 
**content_type** | **str** |  | [optional] 
**entity** | **str** |  | 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.attachment_row import AttachmentRow

# TODO update the JSON string below
json = "{}"
# create an instance of AttachmentRow from a JSON string
attachment_row_instance = AttachmentRow.from_json(json)
# print the JSON string representation of the object
print(AttachmentRow.to_json())

# convert the object into a dict
attachment_row_dict = attachment_row_instance.to_dict()
# create an instance of AttachmentRow from a dict
attachment_row_from_dict = AttachmentRow.from_dict(attachment_row_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


