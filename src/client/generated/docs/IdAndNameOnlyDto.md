# IdAndNameOnlyDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.id_and_name_only_dto import IdAndNameOnlyDto

# TODO update the JSON string below
json = "{}"
# create an instance of IdAndNameOnlyDto from a JSON string
id_and_name_only_dto_instance = IdAndNameOnlyDto.from_json(json)
# print the JSON string representation of the object
print(IdAndNameOnlyDto.to_json())

# convert the object into a dict
id_and_name_only_dto_dict = id_and_name_only_dto_instance.to_dict()
# create an instance of IdAndNameOnlyDto from a dict
id_and_name_only_dto_from_dict = IdAndNameOnlyDto.from_dict(id_and_name_only_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


