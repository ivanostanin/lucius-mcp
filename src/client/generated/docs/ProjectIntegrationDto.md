# ProjectIntegrationDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_date** | **int** |  | [optional] 
**disabled** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**info** | [**IntegrationInfoDto**](IntegrationInfoDto.md) |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**settings** | **object** |  | [optional] 

## Example

```python
from src.client.generated.models.project_integration_dto import ProjectIntegrationDto

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectIntegrationDto from a JSON string
project_integration_dto_instance = ProjectIntegrationDto.from_json(json)
# print the JSON string representation of the object
print(ProjectIntegrationDto.to_json())

# convert the object into a dict
project_integration_dto_dict = project_integration_dto_instance.to_dict()
# create an instance of ProjectIntegrationDto from a dict
project_integration_dto_from_dict = ProjectIntegrationDto.from_dict(project_integration_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


