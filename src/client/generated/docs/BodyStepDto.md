# BodyStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 

## Example

```python
from src.client.generated.models.body_step_dto import BodyStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of BodyStepDto from a JSON string
body_step_dto_instance = BodyStepDto.from_json(json)
# print the JSON string representation of the object
print(BodyStepDto.to_json())

# convert the object into a dict
body_step_dto_dict = body_step_dto_instance.to_dict()
# create an instance of BodyStepDto from a dict
body_step_dto_from_dict = BodyStepDto.from_dict(body_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


