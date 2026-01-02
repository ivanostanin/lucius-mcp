# StatusCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**color** | **str** |  | 
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.status_create_dto import StatusCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of StatusCreateDto from a JSON string
status_create_dto_instance = StatusCreateDto.from_json(json)
# print the JSON string representation of the object
print(StatusCreateDto.to_json())

# convert the object into a dict
status_create_dto_dict = status_create_dto_instance.to_dict()
# create an instance of StatusCreateDto from a dict
status_create_dto_from_dict = StatusCreateDto.from_dict(status_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


