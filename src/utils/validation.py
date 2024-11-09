from datetime import datetime

from textual.widget import Widget


def _validate_number(value: str, field: dict, is_float: bool = False) -> tuple[bool, str | None]:
    """Validate a number field and return (is_valid, error_message)"""
    if not value:
        if field.get("isRequired", False):
            return False, f"Required"
        return True, None

    # Check if valid number
    if is_float:
        # Allow negative sign at start
        test_value = value.lstrip('-').replace('.', '', 1)
        is_valid = test_value.isdigit()
        type_name = "number"
    else:
        # Allow negative sign at start
        test_value = value.lstrip('-')
        is_valid = test_value.isdigit()
        type_name = "integer"

    if not is_valid:
        return False, f"Must be a {type_name}"

    # Convert to number for comparisons
    num_val = float(value) if is_float else int(value)

    # Check minimum
    if "min" in field:
        min_val = float(field["min"]) if is_float else int(field["min"])
        if num_val <= min_val:
            return False, f"Must be greater than {field['min']}"

    # Check maximum  
    if "max" in field:
        max_val = float(field["max"]) if is_float else int(field["max"])
        if num_val > max_val:
            return False, f"Must be less than {field['max']}"

    return True, None


def _validate_date(value: str, field: dict, auto_day: bool = False) -> tuple[datetime | None, str | None]:
    """Validate a date field and return (parsed_date, error_message)"""
    if not value or value == "":
        if field.get("isRequired", False):
            return None, f"Required"
        return None, None

    try:
        if auto_day and value.isdigit():
            # Use current month/year if not provided
            this_month = datetime.now().strftime("%m")
            this_year = datetime.now().strftime("%y")
            date = datetime.strptime(f"{value} {this_month} {this_year}", "%d %m %y")
            return date, None
        date = datetime.strptime(value, "%d %m %y")
        return date, None
    except ValueError:
        format_str = "dd (mm) (yy) format." if auto_day else "dd mm yy format"
        return None, f"Must be in {format_str}"


def _validate_autocomplete(value: str, held_value: str, field: dict) -> tuple[bool, str | None]:
    """Validate an autocomplete field and return (is_valid, error_message)"""
    if not value and not held_value:
        if field.get("isRequired", False):
            return False, f"Must be selected"
        return True, None

    if not field["options"]:
        return True, None

    if field["options"][0].get("text", ""):
        # Find matching option
        field_input_value = None
        for item in field["options"]:
            if item["text"] == value:
                field_input_value = str(item["value"])
                break

        # Verify selected value matches entered text
        if field_input_value != str(held_value):
            return False, "Invalid selection"

    return True, None


def validateForm(formComponent: Widget, formData: list[dict]) -> tuple[dict, dict, bool]:
    result = {}
    errors = {}
    isValid = True

    for field in formData:
        fieldKey = field["key"]
        fieldWidget = formComponent.query_one(f"#field-{fieldKey}")
        fieldValue = fieldWidget.heldValue if hasattr(fieldWidget, "heldValue") else fieldWidget.value

        error = None

        match field["type"]:
            case "integer":
                is_valid, error = _validate_number(fieldValue, field)
                if is_valid and fieldValue:
                    result[fieldKey] = int(fieldValue)

            case "number":
                is_valid, error = _validate_number(fieldValue, field, is_float=True)
                if is_valid and fieldValue:
                    result[fieldKey] = float(fieldValue)

            case "date":
                date, error = _validate_date(fieldValue, field)
                if date:
                    result[fieldKey] = date

            case "dateAutoDay":
                date, error = _validate_date(fieldValue, field, auto_day=True)
                if date:
                    result[fieldKey] = date

            case "autocomplete":
                is_valid, error = _validate_autocomplete(fieldWidget.value, fieldValue, field)
                if is_valid and fieldValue:
                    result[fieldKey] = fieldValue
            
            case _:
                if not fieldValue and field.get("isRequired", False):
                    error = f"Required"
                else:
                    result[fieldKey] = fieldValue

        if error:
            errors[fieldKey] = error
            isValid = False

    return result, errors, isValid
