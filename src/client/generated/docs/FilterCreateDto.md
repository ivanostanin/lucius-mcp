# FilterCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base** | **bool** |  | [optional] 
**body** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**shared** | **bool** |  | [optional] 
**type** | [**FilterTypeDto**](FilterTypeDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.filter_create_dto import FilterCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of FilterCreateDto from a JSON string
filter_create_dto_instance = FilterCreateDto.from_json(json)
# print the JSON string representation of the object
print(FilterCreateDto.to_json())

# convert the object into a dict
filter_create_dto_dict = filter_create_dto_instance.to_dict()
# create an instance of FilterCreateDto from a dict
filter_create_dto_from_dict = FilterCreateDto.from_dict(filter_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


