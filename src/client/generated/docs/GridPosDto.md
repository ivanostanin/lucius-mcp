# GridPosDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**h** | **int** |  | [optional] 
**w** | **int** |  | [optional] 
**x** | **int** |  | [optional] 
**y** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.grid_pos_dto import GridPosDto

# TODO update the JSON string below
json = "{}"
# create an instance of GridPosDto from a JSON string
grid_pos_dto_instance = GridPosDto.from_json(json)
# print the JSON string representation of the object
print(GridPosDto.to_json())

# convert the object into a dict
grid_pos_dto_dict = grid_pos_dto_instance.to_dict()
# create an instance of GridPosDto from a dict
grid_pos_dto_from_dict = GridPosDto.from_dict(grid_pos_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


