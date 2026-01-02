# CleanerSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**delay** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**target** | [**CleanerSchemaTargetDto**](CleanerSchemaTargetDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.cleaner_schema_dto import CleanerSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of CleanerSchemaDto from a JSON string
cleaner_schema_dto_instance = CleanerSchemaDto.from_json(json)
# print the JSON string representation of the object
print(CleanerSchemaDto.to_json())

# convert the object into a dict
cleaner_schema_dto_dict = cleaner_schema_dto_instance.to_dict()
# create an instance of CleanerSchemaDto from a dict
cleaner_schema_dto_from_dict = CleanerSchemaDto.from_dict(cleaner_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


