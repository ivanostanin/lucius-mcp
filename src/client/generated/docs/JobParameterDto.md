# JobParameterDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**value** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.job_parameter_dto import JobParameterDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobParameterDto from a JSON string
job_parameter_dto_instance = JobParameterDto.from_json(json)
# print the JSON string representation of the object
print(JobParameterDto.to_json())

# convert the object into a dict
job_parameter_dto_dict = job_parameter_dto_instance.to_dict()
# create an instance of JobParameterDto from a dict
job_parameter_dto_from_dict = JobParameterDto.from_dict(job_parameter_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


