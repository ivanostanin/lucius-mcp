# AccessGroupPaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**abbr** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**is_public** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**permission_set_id** | **int** |  | 

## Example

```python
from src.client.generated.models.access_group_pa_dto import AccessGroupPaDto

# TODO update the JSON string below
json = "{}"
# create an instance of AccessGroupPaDto from a JSON string
access_group_pa_dto_instance = AccessGroupPaDto.from_json(json)
# print the JSON string representation of the object
print(AccessGroupPaDto.to_json())

# convert the object into a dict
access_group_pa_dto_dict = access_group_pa_dto_instance.to_dict()
# create an instance of AccessGroupPaDto from a dict
access_group_pa_dto_from_dict = AccessGroupPaDto.from_dict(access_group_pa_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


