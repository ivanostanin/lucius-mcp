# UploadParameterDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**excluded** | **bool** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**masked** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_parameter_dto import UploadParameterDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadParameterDto from a JSON string
upload_parameter_dto_instance = UploadParameterDto.from_json(json)
# print the JSON string representation of the object
print(UploadParameterDto.to_json())

# convert the object into a dict
upload_parameter_dto_dict = upload_parameter_dto_instance.to_dict()
# create an instance of UploadParameterDto from a dict
upload_parameter_dto_from_dict = UploadParameterDto.from_dict(upload_parameter_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


