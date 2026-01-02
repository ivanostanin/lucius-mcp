# UploadLinkDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_link_dto import UploadLinkDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadLinkDto from a JSON string
upload_link_dto_instance = UploadLinkDto.from_json(json)
# print the JSON string representation of the object
print(UploadLinkDto.to_json())

# convert the object into a dict
upload_link_dto_dict = upload_link_dto_instance.to_dict()
# create an instance of UploadLinkDto from a dict
upload_link_dto_from_dict = UploadLinkDto.from_dict(upload_link_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


