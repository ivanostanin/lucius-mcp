# WebhookValidateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | 
**endpoint** | **str** |  | 
**headers** | **Dict[str, str]** |  | [optional] 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.webhook_validate_dto import WebhookValidateDto

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookValidateDto from a JSON string
webhook_validate_dto_instance = WebhookValidateDto.from_json(json)
# print the JSON string representation of the object
print(WebhookValidateDto.to_json())

# convert the object into a dict
webhook_validate_dto_dict = webhook_validate_dto_instance.to_dict()
# create an instance of WebhookValidateDto from a dict
webhook_validate_dto_from_dict = WebhookValidateDto.from_dict(webhook_validate_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


