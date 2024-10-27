from datetime import datetime

from textual.widget import Widget


def validateForm(formComponent: Widget, formData: list[dict]):

    result = {}
    errors = {}
    isValid = True

    for field in formData:
        fieldKey = field["key"]
        fieldWidget = formComponent.query_one(f"#field-{fieldKey}")
        fieldValue = fieldWidget.heldValue if hasattr(fieldWidget, "heldValue") else fieldWidget.value

        try:
            match field["type"]:
                case "integer":
                    if field.get("isRequired", False) is True and fieldValue == "":
                        raise ValueError(f"{field["title"]} is required")
                    if fieldValue != "":
                        if fieldValue.isdigit():
                            if "min" in field and "max" in field and field["min"] is not None and field["max"] is not None:
                                if field["min"] <= fieldValue <= field["max"]:
                                    result[fieldKey] = fieldValue
                                else:
                                    raise ValueError(f"{field["title"]} must be between {field['min']} and {field['max']}")
                            else:
                                result[fieldKey] = fieldValue
                        else:
                            raise ValueError(f"{field["title"]} must be an integer")
                case "float":
                    if field.get("isRequired", False) is True and fieldValue == "":
                        raise ValueError(f"{field["title"]} is required")
                    if fieldValue != "":
                        if fieldValue.replace('.', '', 1).isdigit():
                            result[fieldKey] = fieldValue
                        else:
                            raise ValueError(f"{field["title"]} must be a float")
                case "date":
                    if field.get("isRequired", False) is True and fieldValue == "":
                        raise ValueError(f"{field["title"]} is required")
                    if fieldValue != "":
                        formattedDate = datetime.strptime(fieldValue, "%d %m %y")
                        if formattedDate:
                            result[fieldKey] = formattedDate
                        else:
                            raise ValueError(f"{field["title"]} must be in dd mm yy format")
                case "dateAutoDay": # dd (mm) (yy) where mm and yy are optional
                    if field.get("isRequired", False) is True and fieldValue == "":
                        raise ValueError(f"{field["title"]} is required")
                    if fieldValue != "":
                        thisMonth = datetime.now().strftime("%m")
                        thisYear = datetime.now().strftime("%y")
                        formattedDate = datetime.strptime(f"{fieldValue} {thisMonth} {thisYear}", "%d %m %y")
                        if formattedDate:
                            result[fieldKey] = formattedDate
                        else:
                            raise ValueError(f"{field["title"]} must be in dd (mm) (yy) format. (optional)")
                case "autocomplete":
                    if field.get("isRequired", False) is True and fieldValue == "":
                        raise ValueError(f"{field["title"]} must be selected")
                    if fieldValue != "":
                        if str(fieldWidget.value) != str(fieldValue):
                            raise ValueError(f"Did you press tab?")
                        result[fieldKey] = fieldValue
                case _:
                    if field.get("isRequired", False) is True and fieldValue == "":
                        raise ValueError(f"{field["title"]} is required")
                    if fieldValue != "":
                        result[fieldKey] = fieldValue
        except ValueError as e:
            errors[fieldKey] = e.args[0]
            isValid = False
        
    return result, errors, isValid
