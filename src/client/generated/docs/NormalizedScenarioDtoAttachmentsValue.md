# NormalizedScenarioDtoAttachmentsValue


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_length** | **int** |  | [optional] 
**content_type** | **str** |  | [optional] 
**entity** | **str** |  | 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**var_base64** | **str** |  | [optional] 
**html_table** | **str** |  | [optional] 
**missed** | **bool** |  | [optional] 
**text_content** | **str** |  | [optional] 
**from_test_case** | **bool** |  | [optional] 
**storage_key** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.normalized_scenario_dto_attachments_value import NormalizedScenarioDtoAttachmentsValue

# TODO update the JSON string below
json = "{}"
# create an instance of NormalizedScenarioDtoAttachmentsValue from a JSON string
normalized_scenario_dto_attachments_value_instance = NormalizedScenarioDtoAttachmentsValue.from_json(json)
# print the JSON string representation of the object
print(NormalizedScenarioDtoAttachmentsValue.to_json())

# convert the object into a dict
normalized_scenario_dto_attachments_value_dict = normalized_scenario_dto_attachments_value_instance.to_dict()
# create an instance of NormalizedScenarioDtoAttachmentsValue from a dict
normalized_scenario_dto_attachments_value_from_dict = NormalizedScenarioDtoAttachmentsValue.from_dict(normalized_scenario_dto_attachments_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


