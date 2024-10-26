from datetime import datetime
from textual.widget import Widget

def validateForm(formComponent: Widget, formData: list[dict]):

    result = {}
    errors = {}
    isValid = True

    for field in formData:
        fieldKey = field["key"]
        fieldValue = formComponent.query_one(f"#field-{fieldKey}").value

        try:
            match field["type"]:
                case "number":
                    if fieldValue != "":
                        if fieldValue.isdigit():
                            if "min" in field and "max" in field and field["min"] is not None and field["max"] is not None:
                                if field["min"] <= fieldValue <= field["max"]:
                                    result[fieldKey] = fieldValue
                                else:
                                    raise ValueError(f"Field must be between {field['min']} and {field['max']}")
                            else:
                                result[fieldKey] = fieldValue
                        else:
                            raise ValueError("Field must be a number")
                    else:
                        raise ValueError("Field is required")
                case "date":
                    if fieldValue != "":
                        formattedDate = datetime.strptime(fieldValue, "%d %m %y")
                        if formattedDate:
                            result[fieldKey] = formattedDate
                        else:
                            raise ValueError("Field must be in dd mm yy format")
                    else:
                        raise ValueError("Field is required")
                case "dateAutoDay": # dd (mm) (yy) where mm and yy are optional
                    if fieldValue != "":
                        thisMonth = datetime.now().strftime("%m")
                        thisYear = datetime.now().strftime("%y")
                        formattedDate = datetime.strptime(f"{fieldValue} {thisMonth} {thisYear}", "%d %m %y")
                        if formattedDate:
                            result[fieldKey] = formattedDate
                        else:
                            raise ValueError("Field must be in dd (mm) (yy) format. (optional)")
                    else:
                        raise ValueError("Field is required")
                case _:
                    if fieldValue != "":
                        result[fieldKey] = fieldValue
                    else:
                        raise ValueError("Field is required")
        except ValueError as e:
            errors[fieldKey] = e.args[0]
            isValid = False
        
    return result, errors, isValid

