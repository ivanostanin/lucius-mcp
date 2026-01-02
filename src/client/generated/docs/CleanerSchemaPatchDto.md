# CleanerSchemaPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**delay** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**target** | [**CleanerSchemaTargetDto**](CleanerSchemaTargetDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.cleaner_schema_patch_dto import CleanerSchemaPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of CleanerSchemaPatchDto from a JSON string
cleaner_schema_patch_dto_instance = CleanerSchemaPatchDto.from_json(json)
# print the JSON string representation of the object
print(CleanerSchemaPatchDto.to_json())

# convert the object into a dict
cleaner_schema_patch_dto_dict = cleaner_schema_patch_dto_instance.to_dict()
# create an instance of CleanerSchemaPatchDto from a dict
cleaner_schema_patch_dto_from_dict = CleanerSchemaPatchDto.from_dict(cleaner_schema_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


