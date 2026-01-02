# IntegrationInfoDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**operations** | [**List[IntegrationOperationTypeDto]**](IntegrationOperationTypeDto.md) |  | [optional] 
**routines** | [**List[IntegrationRoutineTypeDto]**](IntegrationRoutineTypeDto.md) |  | [optional] 
**type** | [**IntegrationTypeDto**](IntegrationTypeDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.integration_info_dto import IntegrationInfoDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationInfoDto from a JSON string
integration_info_dto_instance = IntegrationInfoDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationInfoDto.to_json())

# convert the object into a dict
integration_info_dto_dict = integration_info_dto_instance.to_dict()
# create an instance of IntegrationInfoDto from a dict
integration_info_dto_from_dict = IntegrationInfoDto.from_dict(integration_info_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


