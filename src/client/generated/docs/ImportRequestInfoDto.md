# ImportRequestInfoDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**headers** | [**List[OrderedValueDtoString]**](OrderedValueDtoString.md) |  | [optional] 
**records_count** | **int** |  | [optional] 
**values** | [**List[OrderedValueDtoString]**](OrderedValueDtoString.md) |  | [optional] 

## Example

```python
from src.client.generated.models.import_request_info_dto import ImportRequestInfoDto

# TODO update the JSON string below
json = "{}"
# create an instance of ImportRequestInfoDto from a JSON string
import_request_info_dto_instance = ImportRequestInfoDto.from_json(json)
# print the JSON string representation of the object
print(ImportRequestInfoDto.to_json())

# convert the object into a dict
import_request_info_dto_dict = import_request_info_dto_instance.to_dict()
# create an instance of ImportRequestInfoDto from a dict
import_request_info_dto_from_dict = ImportRequestInfoDto.from_dict(import_request_info_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


