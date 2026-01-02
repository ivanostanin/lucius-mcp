# UploadLabelDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_label_dto import UploadLabelDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadLabelDto from a JSON string
upload_label_dto_instance = UploadLabelDto.from_json(json)
# print the JSON string representation of the object
print(UploadLabelDto.to_json())

# convert the object into a dict
upload_label_dto_dict = upload_label_dto_instance.to_dict()
# create an instance of UploadLabelDto from a dict
upload_label_dto_from_dict = UploadLabelDto.from_dict(upload_label_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


